from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QApplication, QHBoxLayout, QLabel
from typing import List

from Scripts.Widget.CustomObjects.QScreenFrame import QScreenFrame


class ScreenListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.screens: List[QScreen] = QApplication.screens()

        self.init_UI()

    def init_UI(self):
        """
        Create screens icons compared of the number of screens of the os
        """
        layout = QHBoxLayout()

        for screen in self.screens:
            screen_widget = QScreenFrame(screen)
            layout.addWidget(screen_widget)

        self.setLayout(layout)