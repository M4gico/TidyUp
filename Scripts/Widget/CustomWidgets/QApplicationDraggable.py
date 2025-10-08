from PyQt6.QtCore import Qt, QSize, QMimeData, QPoint
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QMessageBox

from Scripts.CustomObjects.Application import Application


class QApplicationDraggable(QWidget):
    def __init__(self, application: Application):
        super().__init__()

        self.application = application

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.icon = QLabel()
        if application.icon:
            # QIcon choisira la meilleure taille. 32 est une bonne taille de base.
            pixmap = application.icon.pixmap(QSize(32, 32))
            self.icon.setPixmap(pixmap)
        else:
            QMessageBox.warning(self, "Icon Error", "The application does not have a valid icon.")
            return

        label_layout = QVBoxLayout()
        name_app = QLabel(application.name)
        name_app.setStyleSheet("font-weight: bold; font-size: 14px;")

        path_app = QLabel(application.app_path_exe)
        path_app.setStyleSheet("font-size: 10px; color: gray;")

        # TODO: Maybe put the project path instead of the .exe path
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

            # Stocker directement l'application dans le drag object
            drag.application = self.application
            # Utiliser un type MIME personnalisé sans données spécifiques pour reconnaitre le drop
            mime.setText("application_drag")
            drag.setMimeData(mime)

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
