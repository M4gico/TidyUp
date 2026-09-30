from typing import List, Dict, Optional

from PyQt6.QtCore import QThread, pyqtSlot
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QApplication, QHBoxLayout, QPushButton, QVBoxLayout, QMessageBox, QLabel

from Scripts.Widget.CustomWidgets.QScreenApplication import QScreenApplication
from Scripts.application_manager import launch_applications, LaunchWorker


class ScreenWidget(QWidget):
    LAUNCH_TEXT = "Launch Applications"
    STOP_TEXT = "Stop launch"

    def __init__(self):
        super().__init__()

        # Sort by physical position (left to right, top to bottom) to match the Windows Display Settings arrangement,
        # instead of the arbitrary order returned by the OS
        self.screens: List[QScreen] = sorted(QApplication.screens(), key=lambda s: (s.geometry().x(), s.geometry().y()))
        self.screen_applications: List[QScreenApplication] = [] # List of all the screen with their applications
        # Saved screens not connected now (ex: laptop without its external screen), kept to not lose them when saving
        self._undetected_screens: List[Dict] = []

        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout()

        self.screen_layout = QHBoxLayout()

        self.create_screens()

        self.launch_app_btn = QPushButton(self.LAUNCH_TEXT)
        self.launch_app_btn.clicked.connect(self.on_launch_button_clicked)

        self.launch_status_label = QLabel()
        self.launch_status_label.setStyleSheet("color: gray;")

        main_layout.addLayout(self.screen_layout)
        main_layout.addWidget(self.launch_app_btn)
        main_layout.addWidget(self.launch_status_label)

        self.setLayout(main_layout)

        # Keep a reference on the thread and the worker during the launch to avoid the garbage collector
        self._launch_thread: Optional[QThread] = None
        self._launch_worker: Optional[LaunchWorker] = None
        self._launch_cancelled = False
        self._launch_status: Dict[str, str] = {}  # Last status of each application during the launch
        QApplication.instance().aboutToQuit.connect(self.stop_launch)

    # region Launch applications
    @pyqtSlot()
    def on_launch_button_clicked(self):
        # The button stops the current launch, so a launch waiting for a window never blocks the next one
        if self._launch_thread is not None:
            self.cancel_launch()
        else:
            self.start_launch()

    def start_launch(self):
        if self._launch_thread is not None:
            return

        if not any(screen.qt_applications for screen in self.screen_applications):
            QMessageBox.information(self, "Launch Applications", "Drop applications on the screens first.")
            return

        try:
            self._launch_thread, self._launch_worker = launch_applications(self.screen_applications, self)
        except Exception as e:
            QMessageBox.warning(self, "Launch Error", f"Can't launch the applications: {e}")
            return

        self._launch_worker.app_status.connect(self.on_launch_status)
        self._launch_worker.finished.connect(self.on_launch_finished)

        self._launch_cancelled = False
        self._launch_status.clear()
        self.launch_app_btn.setText(self.STOP_TEXT)
        self.launch_status_label.setText("Launching applications...")
        self._launch_thread.start()

    def cancel_launch(self):
        self._launch_cancelled = True
        self._launch_worker.cancel()
        # Wait the worker to stop (less than one poll interval) before allowing a new launch
        self.launch_app_btn.setEnabled(False)
        self.launch_status_label.setText("Stopping the launch...")

    @pyqtSlot(str, str)
    def on_launch_status(self, app_name: str, message: str):
        self._launch_status[app_name] = message
        self.launch_status_label.setText("\n".join(f"{name}: {msg}" for name, msg in self._launch_status.items()))

    @pyqtSlot(list)
    def on_launch_finished(self, errors: List[str]):
        self._launch_thread = None
        self._launch_worker = None
        self.launch_app_btn.setText(self.LAUNCH_TEXT)
        self.launch_app_btn.setEnabled(True)

        if self._launch_cancelled:
            self.launch_status_label.setText("Launch stopped")
        elif errors:
            self.launch_status_label.setText("Launch finished with errors")
            QMessageBox.warning(self, "Launch Applications", "Some applications had a problem:\n\n" + "\n".join(errors))
        else:
            self.launch_status_label.setText("All applications are placed")

    @pyqtSlot()
    def stop_launch(self):
        """Stop the launch thread properly when the application is closed"""
        if self._launch_thread is not None:
            self._launch_worker.cancel()
            self._launch_thread.quit()
            self._launch_thread.wait(3000)
    # endregion

    def create_screens(self):
        """
        Create the screens on the UI
        :param screens_applications: List of QScreenApplication if it calls by load settings
        """

        for screen in self.screens:
            screen_app = QScreenApplication(screen)

            self.screen_applications.append(screen_app)

            self.screen_layout.addWidget(screen_app)
            self.screen_layout.addSpacing(10)

    def load_settings(self, screens_applications: List[Dict]):
        # Remove the applications of the previous tab, even if the new tab is empty
        for screen_app in self.screen_applications:
            screen_app.clear_applications()

        # Screens not detected anymore are skipped with a warning in load_qt_applications_to_qt_screen
        self.load_qt_applications_to_qt_screen(screens_applications)

    def load_qt_applications_to_qt_screen(self, screens_applications: List[Dict]):
        """Add QApplicationDraggable to each QScreenApplication from the saved settings"""
        self._undetected_screens = []

        for screen_dict in screens_applications:
            # Get the screen to create the object
            screen_name = screen_dict["screen_name"]
            if screen_name not in ([s.name() for s in self.screens] + ["Laptop Screen"]):
                self._undetected_screens.append(screen_dict)
                QMessageBox.warning(
                    self,
                    "Screen Error",
                    f"The screen {screen_name} saved in the settings is not detected on the system."
                )
                continue

            # Get the QScreen reference from the screen name save
            q_screen = None
            for screen in self.screens:
                if screen.name() == screen_name:
                    q_screen = screen
                    break

                # Check for laptop screen
                if screen.name().startswith(r"\\") and screen_name == "Laptop Screen":
                    q_screen = screen
                    break

            # Get the QScreenApplication reference
            qt_screen = None
            for screen_app in self.screen_applications:
                if screen_app.screen == q_screen:
                    qt_screen = screen_app
                    break

            if qt_screen is None:
                continue

            # Add applications saved in the screen
            qt_screen.load_settings(screen_dict)

    def save_settings(self) -> List[Dict]:
        """
        Save the QApplicationDraggable for each screens
        For each screen, get the list of QApplicationDraggable and save them in a list of QScreenApplication
        To know which screen is it, just get the screen name from QScreenApplication
        """
        screen_applications_dict: List[Dict] = []
        for qt_screens in self.screen_applications:
            screen_applications_dict.append(qt_screens.save_settings())

        # Keep the applications of the screens not connected, they will be loaded when the screen is back
        return screen_applications_dict + self._undetected_screens


