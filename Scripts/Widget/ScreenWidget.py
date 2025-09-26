from typing import List

from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QApplication, QHBoxLayout

from Scripts.Widget.CustomObjects.QScreenApplication import QScreenApplication


class ScreenWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Get the list of screens on the system
        self.screens: List[QScreen] = QApplication.screens()

        self.init_UI()

    def init_UI(self):
        main_layout = QHBoxLayout()

        for screen in self.screens:
            main_layout.addWidget(QScreenApplication(screen))
            main_layout.addSpacing(10)

        self.setLayout(main_layout)