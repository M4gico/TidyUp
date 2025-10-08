import subprocess
import time
from typing import List, Dict, Union

import psutil
import win32con
import win32gui
import win32process
from PyQt6.QtCore import QRect
from difflib import SequenceMatcher

from Scripts.Widget.CustomWidgets.QScreenApplication import QScreenApplication

def launch_applications(screen_applications: List[QScreenApplication]):
    for screen in screen_applications:
        # Give the offest in the 2 first parameters and the screen size in the 2 last parameters
        screen_size = screen.screen.geometry()

        for application in screen.applications:
            try:
                application.open_application()

                time.sleep(5) #TODO: Change it after /to put it in a thread and wait until the app is sucessfully opened
                # process.wait(timeout=timeout_seconds)

                _move_app_to_screen(application.name, screen_size)

            except Exception as e:
                raise RuntimeError(f"Failed to open application {application.name}: {e}")

def _move_app_to_screen(app_name: str, screen_geometry):
    """
    Take the application to maximize it on the screen
    """
    # Get all visible windows on the screen
    windows_on_screen = _get_windows_visible(screen_geometry)

    # Get the handler of the specific application
    window_handler: Union[int, None] = _get_handler_of_the_app(windows_on_screen, app_name)

    if window_handler is None:
        print("Window handler not found for app:", app_name)
        return

    # Move the application to the screen and maxize it
    _maximize_window_on_screen(window_handler, screen_geometry, app_name)

def _maximize_window_on_screen(hwnd, screen_geomtry, app_name):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    # win32con.HWND_TOP parameter put the window at the top of the Z order, meaning in front of other windows
    # Move the window in the center of the screen not maximized to avoid issues for maximize it after on the right screen
    # The last parameter can handle some rights but 0 is ok for now, can be used to free threads
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, int(screen_geomtry.x() + screen_geomtry.width()/2),
                          int(screen_geomtry.y() + screen_geomtry.height()/2),
                          int(screen_geomtry.width()/2), int(screen_geomtry.height()/2),
                          0)

    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

def _get_handler_of_the_app(windows_on_screen: Dict[str, int], app_name: str) -> Union[int, None]:
    for window_name, handler in windows_on_screen.items():
        window_name_possibility = _split_name(window_name)
        app_name_possibility = _split_name(app_name)
        # Check match between window name and app name
        if any(part in window_name_possibility for part in app_name_possibility):
            return handler
    return None


# def _get_handler_of_the_app(windows_on_screen: Dict[str, int], app_name: str) -> Union[int, None]:
#     best_match = None
#     best_ratio = 0.0
#     threshold = 0.6  # Minimum similarity score
#
#     app_name_lower = app_name.lower()
#
#     for window_name, handler in windows_on_screen.items():
#         window_name_lower = window_name.lower()
#
#         # Calculate similarity ratio
#         ratio = SequenceMatcher(None, app_name_lower, window_name_lower).ratio()
#
#         # Also check if app name is substring of window name
#         if app_name_lower in window_name_lower:
#             ratio = max(ratio, 0.8)
#
#         if ratio > best_ratio and ratio >= threshold:
#             best_ratio = ratio
#             best_match = handler
#
#     return best_match

def _split_name(name: str) -> List[str]:
    """
    Split the name of the application in several parts to find a better match
    :param name: the name of the application
    :return: a list of string with the different parts of the name
    """
    name = name.lower()
    for sep in [' ', '_', '-']:
        name = name.replace(sep, ' ')
    name_list = name.split()
    name_list.append(name[:4]) # Add the first 4 letters as a possibility
    return name_list


def _get_windows_visible(screen_geometry):
    """
    :return: all large visible windows name associated with their handler
    """
    windows: Dict[str, int] = {}
    def enum_windows_callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            window_name = win32gui.GetWindowText(hwnd)
            if window_name != "" and _check_window_size(screen_geometry, hwnd):
                windows[window_name] = hwnd

    win32gui.EnumWindows(enum_windows_callback, None)
    return windows

def _check_window_size(screen_geometry, app_hwnd) -> bool:
    """
    Check if the window take at least half of the screen
    :param screen_geometry: the geometry of the screen
    :param app_hwnd: the specific application handler
    :return: if the window take at least half of the screen
    """
    #TODO: Get the size of the screen where is the app and not the screen we want to put it

    #TODO: If the window is lower than half screen, put it in a list if the name match
    #TODO: and check a several times if the app is still visible
    #TODO: If it's the case, take it and move it to the screen
    left, top, right, bottom = win32gui.GetWindowRect(app_hwnd)
    window_width = right - left
    window_height = bottom - top

    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    return window_width >= screen_width/2 and window_height >= screen_height/2
