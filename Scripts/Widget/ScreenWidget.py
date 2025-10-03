from typing import List

from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QApplication, QHBoxLayout, QPushButton, QVBoxLayout

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

        screen_layout = QHBoxLayout()

        for screen in self.screens:
            screen_app = QScreenApplication(screen)
            self.screen_applications.append(screen_app)

            screen_layout.addWidget(screen_app)
            screen_layout.addSpacing(10)

        launch_app_btn = QPushButton("Launch Applications")
        launch_app_btn.clicked.connect(self.launch_applications_btn)

        main_layout.addLayout(screen_layout)
        main_layout.addWidget(launch_app_btn)

        self.setLayout(main_layout)

    def launch_applications_btn(self):
        launch_applications(self.screen_applications)