from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QMessageBox

from Scripts.CustomObjects.Application import Application


class QApplicationDraggable(QWidget):
    def __init__(self, application: Application):
        super().__init__()

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        icon = QLabel()
        if application.icon:
            icon.setPixmap(application.icon.pixmap(32, 32))
        else:
            QMessageBox.warning(self, "Icon Error", "The application does not have a valid icon.")

        # icon.setFixedSize(32, 32)

        label_layout = QVBoxLayout()
        name_app = QLabel(application.name)
        name_app.setStyleSheet("font-weight: bold; font-size: 14px;")

        path_app = QLabel(application.app_path_exe)
        path_app.setStyleSheet("font-size: 10px; color: gray;")

        #TODO: Maybe put the project path instead of the .exe path
        # path_process = QLabel(application.app_project_path)

        label_layout.addWidget(name_app)
        label_layout.addWidget(path_app)

        layout.addWidget(icon)
        layout.addLayout(label_layout)
        # Add the draggable functionality

        self.setLayout(layout)

