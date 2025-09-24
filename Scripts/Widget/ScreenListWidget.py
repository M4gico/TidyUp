from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QApplication, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from typing import List

from Scripts.Widget.CustomObjects.QBackgroundWidget import QBackgroundWidget
from Scripts.Widget.CustomObjects.QScreenFrame import QScreenFrame


class ScreenListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.screens: List[QScreen] = QApplication.screens()

        self.init_UI()
        self.set_size_to_match_app_widgets()

    def init_UI(self):
        """
        Create screens icons based on the number of screens detected in the OS
        """
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(5)

        # Title label
        title_label = QLabel("Detected Screens:")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Horizontal layout for screens
        screens_layout = QHBoxLayout()
        screens_layout.setSpacing(10)
        screens_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        for screen in self.screens:
            screen_widget = QScreenFrame(screen)
            screen_overlay = QBackgroundWidget(screen_widget, r"Resources/screen_icon.png")
            screen_widget.setMinimumSize(150, 200)  # Minimum size for each screen
            screens_layout.addWidget(screen_overlay)

        main_layout.addLayout(screens_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def set_size_to_match_app_widgets(self):
        """
        Set the size to match the combined height of ChooseAppWidget and ApplicationListWidget
        Based on the ApplicationListWidget scroll area (200-300px) + ChooseAppWidget layout (~50px)
        """
        # Match the combined size: ChooseAppWidget (~80px) + ApplicationListWidget (200-300px)
        self.setMinimumHeight(280)
        self.setMaximumHeight(380)
        self.setMinimumWidth(320)
