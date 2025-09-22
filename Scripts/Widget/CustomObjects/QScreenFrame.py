from PyQt6.QtCore import Qt
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel


class QScreenFrame(QFrame):

    def __init__(self, screen: QScreen, parent = None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        self.screen = screen
        self.apps = []

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("background-color: #f0f0f0; border: 1px solid #999;")

        # Ajouter un layout
        self.layout = QVBoxLayout(self)

        # Afficher les informations de l'écran
        screen_info = f"{screen.name()}\n{screen.geometry().width()}x{screen.geometry().height()}"
        self.info_label = QLabel(screen_info)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.info_label)