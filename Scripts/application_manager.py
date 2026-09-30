import subprocess
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from Scripts.CustomObjects.Application import Application
from Scripts.CustomObjects.WindowUtils import MonitorInfo, ProcessCache, monitor_for_qscreen, find_app_windows, \
    is_window_hung, place_maximized, is_placed
from Scripts.Widget.CustomWidgets.QScreenApplication import QScreenApplication

POLL_INTERVAL = 0.3  # Seconds between two scans of the windows
LAUNCH_TIMEOUT = 120  # Maximum time to wait all the windows (Unity can be long to open a project)
EXISTING_GRACE = 2  # Time to wait a new window after the launched process exited before moving the existing ones
RETRY_DELAY = 0.6  # Time given to the application to apply the move before trying again
STABILIZE = 3  # The window has to stay on the screen this time (some apps restore their own position after opening)
MAX_ATTEMPTS = 6  # Maximum number of moves for one window


@dataclass
class WindowState:
    attempts: int = 0
    last_attempt: float = 0.0
    placed_since: Optional[float] = None


@dataclass
class LaunchTarget:
    name: str
    application: Application
    monitor: MonitorInfo

    process: Optional[subprocess.Popen] = None
    process_exit_time: Optional[float] = None
    pre_existing: Set[int] = field(default_factory=set)  # Windows already opened before the launch
    windows: Dict[int, WindowState] = field(default_factory=dict)
    done: bool = False
    error: Optional[str] = None

    @property
    def launched_pids(self) -> List[int]:
        return [self.process.pid] if self.process else []


def build_targets(screen_applications: List[QScreenApplication]) -> List[LaunchTarget]:
    """Must be called in the main thread: read the Qt widgets to create plain data for the worker"""
    targets = []
    for screen in screen_applications:
        monitor = monitor_for_qscreen(screen.screen)
        for qt_application in screen.qt_applications:
            targets.append(LaunchTarget(qt_application.name_app.text(), qt_application.application, monitor))
    return targets


class LaunchWorker(QObject):
    """Launch the applications and move their windows on their screen without blocking the UI"""
    app_status = pyqtSignal(str, str)  # Name of the application, status message
    finished = pyqtSignal(list)  # List of error messages

    def __init__(self, targets: List[LaunchTarget]):
        super().__init__()
        self._targets = targets
        self._cancelled = False
        # Know which target moved a window to not move it on 2 screens if the same app is on several screens
        self._window_owner: Dict[int, LaunchTarget] = {}

    def cancel(self):
        self._cancelled = True

    @pyqtSlot()
    def run(self):
        try:
            self._launch_all()
            self._place_windows()
        except Exception as e:
            self.finished.emit([f"Unexpected error: {e}"])
            return

        errors = [f"{t.name}: {t.error}" for t in self._targets if t.error]
        self.finished.emit(errors)

    def _launch_all(self):
        """Launch all the applications at the same time, the windows are waited after"""
        cache = ProcessCache()
        for target in self._targets:
            try:
                existing = find_app_windows(target.application.app_path_exe, cache=cache)
                target.pre_existing = set(existing)

                # Already running: just move it, except if a project has to be opened
                if existing and not target.application.app_project_path:
                    self.app_status.emit(target.name, "already running, moving it")
                    continue

                target.process = target.application.open_application()
                self.app_status.emit(target.name, "launched, waiting for the window")
            except Exception as e:
                target.error = f"failed to launch ({e})"
                target.done = True
                self.app_status.emit(target.name, target.error)

    def _place_windows(self):
        start = time.time()
        while not self._cancelled and not all(t.done for t in self._targets):
            if time.time() - start > LAUNCH_TIMEOUT:
                for target in self._targets:
                    if not target.done:
                        self._finish_target_on_timeout(target)
                return

            cache = ProcessCache()
            for target in self._targets:
                if not target.done:
                    try:
                        self._update_target(target, cache)
                    except Exception as e:
                        target.error = str(e)
                        target.done = True
                        self.app_status.emit(target.name, target.error)

            time.sleep(POLL_INTERVAL)

    def _update_target(self, target: LaunchTarget, cache: ProcessCache):
        now = time.time()
        candidates = self._get_candidate_windows(target, cache, now)

        for hwnd in candidates:
            self._window_owner[hwnd] = target
            state = target.windows.setdefault(hwnd, WindowState())

            if is_placed(hwnd, target.monitor):
                if state.placed_since is None:
                    state.placed_since = now
                continue

            state.placed_since = None
            # Wait the async move of the previous attempt and don't send moves to a frozen application
            if state.attempts < MAX_ATTEMPTS and now - state.last_attempt >= RETRY_DELAY and not is_window_hung(hwnd):
                place_maximized(hwnd, target.monitor)
                state.attempts += 1
                state.last_attempt = now

        if not candidates:
            return

        states = [target.windows[hwnd] for hwnd in candidates]
        stable = [s for s in states if s.placed_since is not None and now - s.placed_since >= STABILIZE]
        exhausted = [s for s in states if s.placed_since is None and s.attempts >= MAX_ATTEMPTS
                     and now - s.last_attempt >= RETRY_DELAY]

        # Finish when every window is stable on the screen or can't be moved anymore
        if len(stable) + len(exhausted) == len(states):
            target.done = True
            if stable:
                self.app_status.emit(target.name, "placed")
            else:
                target.error = "the window could not be moved (the application may run as administrator)"
                self.app_status.emit(target.name, target.error)

    def _get_candidate_windows(self, target: LaunchTarget, cache: ProcessCache, now: float) -> List[int]:
        windows = find_app_windows(target.application.app_path_exe, target.launched_pids, cache)
        windows = [w for w in windows if self._window_owner.get(w, target) is target]

        # Not launched: the application was already running, take its windows
        if target.process is None:
            return windows

        new_windows = [w for w in windows if w not in target.pre_existing]
        if new_windows:
            return new_windows

        # The launched process gave the work to the instance already running (single instance apps) and exited,
        # so the existing windows are the ones to move
        if target.process_exit_time is None and target.process.poll() is not None:
            target.process_exit_time = now
        if target.process_exit_time is not None and now - target.process_exit_time >= EXISTING_GRACE:
            return windows
        return []

    def _finish_target_on_timeout(self, target: LaunchTarget):
        target.done = True
        if any(s.placed_since is not None for s in target.windows.values()):
            self.app_status.emit(target.name, "placed")
        elif target.windows:
            target.error = "the window could not be moved on the screen"
        else:
            target.error = f"no window found after {LAUNCH_TIMEOUT} seconds"

        if target.error:
            self.app_status.emit(target.name, target.error)


def launch_applications(screen_applications: List[QScreenApplication], parent: QObject):
    """
    Start the launch in a thread
    :return: the thread and the worker, the caller has to keep a reference on them
    """
    targets = build_targets(screen_applications)

    thread = QThread(parent)
    worker = LaunchWorker(targets)
    worker.moveToThread(thread)

    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    return thread, worker
