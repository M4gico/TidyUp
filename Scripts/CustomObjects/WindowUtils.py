"""
Low level Win32 helpers to find the windows of an application and place them on a monitor.
Only plain Win32 / psutil calls are used here so the functions can safely run in a worker thread.
"""
import ctypes
import os
from ctypes import wintypes
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import psutil
import win32api
import win32con
import win32gui
import win32process

user32 = ctypes.WinDLL("user32", use_last_error=True)
dwmapi = ctypes.WinDLL("dwmapi")

user32.ShowWindowAsync.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindowAsync.restype = wintypes.BOOL
user32.IsZoomed.argtypes = [wintypes.HWND]
user32.IsZoomed.restype = wintypes.BOOL
user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL
user32.IsHungAppWindow.argtypes = [wintypes.HWND]
user32.IsHungAppWindow.restype = wintypes.BOOL
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_uint]
user32.SetWindowPos.restype = wintypes.BOOL
dwmapi.DwmGetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
dwmapi.DwmGetWindowAttribute.restype = ctypes.c_long

DWMWA_CLOAKED = 14
SWP_ASYNCWINDOWPOS = 0x4000
# Number of parent processes checked to link a window to the launched application (ex: steam.exe -> steamwebhelper.exe)
MAX_PARENT_DEPTH = 4

Rect = Tuple[int, int, int, int]  # left, top, right, bottom in physical pixels


@dataclass(frozen=True)
class MonitorInfo:
    hmonitor: int
    device: str
    monitor_rect: Rect
    work_rect: Rect  # Monitor area without the taskbar


# region Monitors
def get_monitors() -> List[MonitorInfo]:
    monitors = []
    for hmonitor, _, _ in win32api.EnumDisplayMonitors():
        info = win32api.GetMonitorInfo(hmonitor)
        monitors.append(MonitorInfo(int(hmonitor), info["Device"], tuple(info["Monitor"]), tuple(info["Work"])))
    return monitors


def monitor_for_qscreen(qscreen) -> MonitorInfo:
    """
    Get the Win32 monitor of a QScreen.
    Qt6 keeps the native position of the screen (only the size is scaled), so the top left corner identifies the monitor.
    """
    geometry = qscreen.geometry()
    top_left = (geometry.x(), geometry.y())

    monitors = get_monitors()
    for monitor in monitors:
        if monitor.monitor_rect[:2] == top_left:
            return monitor

    # Fallback: take the monitor the closest of the top left corner of the screen
    hmonitor = int(win32api.MonitorFromPoint(top_left, win32con.MONITOR_DEFAULTTONEAREST))
    for monitor in monitors:
        if monitor.hmonitor == hmonitor:
            return monitor
    raise RuntimeError(f"No monitor found for the screen {qscreen.name()}")
# endregion


# region Windows detection
def is_main_window(hwnd: int) -> bool:
    """
    Check if the window is a main application window (the one we can see in the taskbar and maximize).
    Minimized windows are accepted, splash screens, tool windows, dialogs and hidden UWP windows are rejected.
    """
    if not win32gui.IsWindowVisible(hwnd):
        return False
    # Owned windows are dialogs / popups of another window
    if win32gui.GetWindow(hwnd, win32con.GW_OWNER):
        return False

    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if ex_style & win32con.WS_EX_TOOLWINDOW:
        return False

    # Splash screens can't be resized or maximized
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    if not style & (win32con.WS_MAXIMIZEBOX | win32con.WS_THICKFRAME):
        return False

    return not _is_cloaked(hwnd)


def _is_cloaked(hwnd: int) -> bool:
    """Cloaked windows are 'visible' for Windows but not displayed (UWP background windows, other virtual desktops)"""
    cloaked = wintypes.DWORD()
    result = dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked))
    return result == 0 and cloaked.value != 0


def get_window_pid(hwnd: int) -> int:
    return win32process.GetWindowThreadProcessId(hwnd)[1]


def normalize_path(path: str) -> str:
    return os.path.normcase(os.path.normpath(path))


class ProcessCache:
    """Cache the exe path and the parents of the processes during one scan of the windows"""
    def __init__(self):
        self._exe: Dict[int, Optional[str]] = {}
        self._parents: Dict[int, List[Tuple[int, Optional[str]]]] = {}

    def exe(self, pid: int) -> Optional[str]:
        if pid not in self._exe:
            try:
                self._exe[pid] = normalize_path(psutil.Process(pid).exe())
            except (psutil.Error, OSError, ValueError):
                self._exe[pid] = None
        return self._exe[pid]

    def parents(self, pid: int) -> List[Tuple[int, Optional[str]]]:
        """:return: list of (pid, exe) of the parents of the process, the closest first"""
        if pid not in self._parents:
            parents = []
            try:
                for parent in psutil.Process(pid).parents()[:MAX_PARENT_DEPTH]:
                    parents.append((parent.pid, self.exe(parent.pid)))
            except (psutil.Error, OSError):
                pass
            self._parents[pid] = parents
        return self._parents[pid]


def window_matches_app(hwnd: int, exe_path: str, launched_pids: Iterable[int], cache: ProcessCache) -> bool:
    """
    Check if the window belongs to the application:
    - the process of the window is the exe of the application
    - or one of its parents is the exe / the launched process (ex: steam.exe -> steamwebhelper.exe)
    - or it's the same exe name installed in a sub folder of the application (ex: GitHubDesktop.exe -> app-3.4\\GitHubDesktop.exe)
    """
    target_exe = normalize_path(exe_path)
    pid = get_window_pid(hwnd)
    window_exe = cache.exe(pid)
    if window_exe is None:
        return False

    if window_exe == target_exe:
        return True

    target_dir = os.path.dirname(target_exe)
    if os.path.basename(window_exe) == os.path.basename(target_exe) and window_exe.startswith(target_dir + os.sep):
        return True

    launched_pids = set(launched_pids)
    for parent_pid, parent_exe in cache.parents(pid):
        if parent_pid in launched_pids or parent_exe == target_exe:
            return True
    return False


def find_app_windows(exe_path: str, launched_pids: Iterable[int] = (), cache: Optional[ProcessCache] = None) -> List[int]:
    """:return: all the main windows handlers of the application"""
    cache = cache or ProcessCache()
    own_pid = os.getpid()
    launched_pids = list(launched_pids)
    windows: List[int] = []

    def enum_windows_callback(hwnd, _):
        try:
            if is_main_window(hwnd) and get_window_pid(hwnd) != own_pid \
                    and window_matches_app(hwnd, exe_path, launched_pids, cache):
                windows.append(hwnd)
        except win32gui.error:
            pass  # The window has been closed during the scan
        return True

    win32gui.EnumWindows(enum_windows_callback, None)
    return windows


def is_window_hung(hwnd: int) -> bool:
    return bool(user32.IsHungAppWindow(hwnd))
# endregion


# region Window placement
def place_maximized(hwnd: int, monitor: MonitorInfo):
    """
    Move the window on the monitor and maximize it.
    Async calls are used to never block if the application is busy (ex: Unity during the loading),
    so the result has to be checked later with is_placed.
    """
    if user32.IsIconic(hwnd) or user32.IsZoomed(hwnd):
        # A maximized window can't be moved, it has to be restored first
        user32.ShowWindowAsync(hwnd, win32con.SW_RESTORE)

    # Put the window fully inside the monitor, then Windows maximizes it on the monitor where it is
    left, top, right, bottom = monitor.work_rect
    width, height = right - left, bottom - top
    user32.SetWindowPos(hwnd, None, left + 40, top + 40, int(width * 0.6), int(height * 0.6),
                        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | SWP_ASYNCWINDOWPOS)

    user32.ShowWindowAsync(hwnd, win32con.SW_MAXIMIZE)


def is_placed(hwnd: int, monitor: MonitorInfo) -> bool:
    """Check if the window is maximized on the monitor"""
    if not win32gui.IsWindow(hwnd) or not user32.IsZoomed(hwnd):
        return False
    return int(win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)) == monitor.hmonitor
# endregion


if __name__ == "__main__":
    # Debug: list all the main windows with their process and their monitor
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))  # Per monitor v2, same as Qt6

    for m in get_monitors():
        print(f"Monitor {m.device}: {m.monitor_rect} work area {m.work_rect}")
    print()

    process_cache = ProcessCache()

    def print_window(hwnd, _):
        if is_main_window(hwnd):
            pid = get_window_pid(hwnd)
            monitor = win32api.GetMonitorInfo(win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST))
            print(f"{hwnd:>10} pid={pid:<6} {monitor['Device']:<14} maximized={bool(user32.IsZoomed(hwnd))!s:<5} "
                  f"{process_cache.exe(pid)} | {win32gui.GetWindowText(hwnd)!r}")
        return True

    win32gui.EnumWindows(print_window, None)
