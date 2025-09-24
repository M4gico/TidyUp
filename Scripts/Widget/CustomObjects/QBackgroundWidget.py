from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class QBackgroundWidget(QWidget):
    def __init__(self, widget: QWidget, image_path: str):
        super().__init__()

        background = QLabel()
        background.setPixmap(QPixmap(image_path))
        background.setScaledContents(True) # Scale dynamically the size of the image

        self.overlay_widget = QWidget()
        self.overlay_widget.setStyleSheet("background-color: rgba(255, 255, 255, 50);") # Add a little transparency

        overlay_layout = QVBoxLayout(self.overlay_widget) # Add a layout to overlay widget parent
        overlay_layout.addWidget(widget)

        # Main layout - stack background and overlay
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(background)
        self.setLayout(main_layout)

        # Position overlay widget on top
        self.overlay_widget.setParent(self)
        self.overlay_widget.move(0, 0)
        self.overlay_widget.resize(self.size())

    def resizeEvent(self, event):
        # Keep overlay widget sized to match the background
        if hasattr(self, 'overlay_widget'):
            self.overlay_widget.resize(self.size())
        super().resizeEvent(event)