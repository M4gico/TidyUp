from typing import List

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

    def create_screens(self, screens_applications: List[QScreenApplication] = None):
        """
        Create the screens on the UI
        :param screens_applications: List of QScreenApplication if it calls by load settings
        """
        if screens_applications:
            if len(screens_applications) != len(self.screens):
                QMessageBox.warning(
                    self,
                    "Screen Error",
                    "The number of screens on the system is not the same as the saved configuration."
                )
                return

        for i, screen in enumerate(self.screens):
            if screens_applications:
                screen_app = screens_applications[i]
            else:
                screen_app = QScreenApplication(screen)

            self.screen_applications.append(screen_app)

            self.screen_layout.addWidget(screen_app)
            self.screen_layout.addSpacing(10)

    def load_settings(self, screens_applications: List[QScreenApplication]):
        self.create_screens(screens_applications)

    def save_settings(self) -> List[QScreenApplication]:
        return self.screen_applications


