from typing import List, Dict

from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QApplication, QHBoxLayout, QPushButton, QVBoxLayout, QMessageBox

from Scripts.Widget.CustomWidgets.QScreenApplication import QScreenApplication
from Scripts.application_manager import launch_applications


class ScreenWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.screens: List[QScreen] = QApplication.screens() # Get the list of screens on the system
        self.screen_applications: List[QScreenApplication] = [] # List of all the screen with their applications

        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout()

        self.screen_layout = QHBoxLayout()

        self.create_screens()

        launch_app_btn = QPushButton("Launch Applications")
        launch_app_btn.clicked.connect(lambda : launch_applications(self.screen_applications))

        main_layout.addLayout(self.screen_layout)
        main_layout.addWidget(launch_app_btn)

        self.setLayout(main_layout)

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
        if screens_applications:
            if len(screens_applications) != len(self.screens):
                QMessageBox.warning(
                    self,
                    "Screen Error",
                    "The number of screens on the system is not the same as the saved configuration."
                )
                return
        #TODO: Remove all the QApplicationDraggable from each QScreenApplication before loading the settings
        self.load_qt_applications_to_qt_screen(screens_applications)

    def load_qt_applications_to_qt_screen(self, screens_applications: List[Dict]):
        """Add QApplicationDraggable to each QScreenApplication from the saved settings"""

        for screen_dict in screens_applications:
            # Get the screen to create the object
            screen_name = screen_dict["screen_name"]
            if screen_name not in ([s.name() for s in self.screens] + ["Laptop Screen"]):
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

        return screen_applications_dict


