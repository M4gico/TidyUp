from PyQt6.QtCore import Qt, QSize, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QMessageBox

from Scripts.CustomObjects.Application import Application


class QApplicationDraggable(QWidget):
    def __init__(self, application: Application):
        super().__init__()

        self.application = application

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.icon = QLabel()
        self.icon.setFixedSize(32, 32)
        if application.icon:
            self.icon.setPixmap(application.icon.pixmap(QSize(32, 32)))
            # Keep ratio of the icon
            # self.icon.setScaledContents(True)
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

        layout.addWidget(self.icon)
        layout.addLayout(label_layout)
        # Add the draggable functionality

        self.setLayout(layout)

    def mouseMoveEvent(self, e):
        # Drag if the button is pressed and moved
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime) # This is where you can set data to be transferred

            # Add visual for dragging with icon and name
            temp_widget = QWidget()
            temp_layout = QHBoxLayout()

            # Can't use existing icon because it will instantly delete it after drag the application
            temp_icon = QLabel()
            if self.application.icon:
                temp_icon.setPixmap(self.application.icon.pixmap(QSize(32, 32)))
            temp_layout.addWidget(temp_icon)

            temp_name = QLabel(self.application.name)
            temp_name.setStyleSheet("font-weight: bold; font-size: 14px; padding-left: 5px;")
            temp_layout.addWidget(temp_name)

            temp_widget.setLayout(temp_layout)

            # Convertir le widget en pixmap
            temp_widget.resize(temp_widget.sizeHint())
            pixmap = temp_widget.grab()

            drag.setPixmap(pixmap)
            center_x = pixmap.width() // 2
            # Set the mouse at the top of the drag visual
            drag.setHotSpot(QPoint(center_x, 0))

            drag.exec(Qt.DropAction.MoveAction) # Execute the drag operation with move icon

