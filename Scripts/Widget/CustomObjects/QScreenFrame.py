from PyQt6.QtCore import Qt
from PyQt6.QtGui import QScreen, QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget
import os

"""
TODO: To delete
Pour ajouter un layout qui dépend d'un widget, rajouter le widget en paramètre de la déclaration du layout
"""

class QScreenFrame(QWidget):

    def __init__(self, screen: QScreen, parent = None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Create drop box at the top (85%)
        drop_box = QWidget()
        drop_box.setStyleSheet("""
                    QWidget {
                        background-color: rgba(255, 255, 255, 30);
                    }
                    """)
        drop_box.setAcceptDrops(True)

        # Screen information at the bottom (15%)
        screen_information = QLabel(f"Screen: {screen.name()}\n{screen.geometry().width()}x{screen.geometry().height()}")
        screen_information.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets with stretch factors (85% and 15%)
        layout.addWidget(drop_box, 85)
        layout.addWidget(screen_information, 15)
