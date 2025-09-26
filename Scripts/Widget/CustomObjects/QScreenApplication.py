from typing import List

from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from Scripts.CustomObjects.Application import Application


class QScreenApplication(QWidget):
    def __init__(self, screen: QScreen):
        super().__init__()
        self.setAcceptDrops(True)

        self.applications: List[Application] = [] # Store all the applications drag in the screen
        self.init_UI(screen)

    def init_UI(self, screen: QScreen):
        main_layout = QVBoxLayout()

        self.number_of_applications = QLabel("0 Applications")
        main_layout.addWidget(self.number_of_applications, 85)

        screen_name = QLabel(f"Screen: {screen.name()}")
        main_layout.addWidget(screen_name, 15)

        self.setLayout(main_layout)

    def dragEnterEvent(self, event):
        pass
