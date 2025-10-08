from typing import Union

from PyQt6.QtCore import Qt, QSize, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QAction
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QMessageBox, QMenu, QStyle, QDialog, \
    QInputDialog, QFileDialog

from Scripts.CustomObjects.Application import Application


#TODO: With a right click, open a tab to edit some properties (name, project path, remove...)
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
        self.name_app = QLabel(application.name)
        self.name_app.setStyleSheet("font-weight: bold; font-size: 14px;")

        path_app = QLabel(application.app_path_exe)
        path_app.setStyleSheet("font-size: 10px; color: gray;")

        # TODO: Maybe put the project path instead of the .exe path
        # path_process = QLabel(application.app_project_path)

        label_layout.addWidget(self.name_app)
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

    def contextMenuEvent(self, event):
        """
        Create a context menu when right-clicking on the widget
        """
        context_menu = QMenu(self)

        change_app_action = QAction("Change application name", self)
        add_project_path_action = QAction("Add project path", self)
        remove_app_action = QAction("Remove application", self)

        context_menu.addAction(change_app_action)
        context_menu.addAction(add_project_path_action)
        context_menu.addSeparator()
        context_menu.addAction(remove_app_action)

        change_app_action.triggered.connect(self.change_application_name)
        add_project_path_action.triggered.connect(self.add_project_path)
        remove_app_action.triggered.connect(self.remove_application)

        # Get the relative position of the topright of the icon and convert it to global position of the application
        icon_top_right = self.mapToGlobal(self.icon.geometry().topRight())
        # Display the context menu at the top right of the icon
        context_menu.exec(icon_top_right)

    def change_application_name(self):
        new_name = self._ask_user_new_name()
        if new_name:
            self.name_app.setText(new_name)

    def _ask_user_new_name(self) -> Union[str, None]:
        new_name, ok = QInputDialog.getText(self, "Change name application", "Enter new name: ", text=self.name_app.text())

        if ok and new_name:
            return new_name
        return None

    def add_project_path(self):
        project_path = QFileDialog.getExistingDirectory(
            self,
            "Select Project Folder",
            ""
        )
        if project_path:
            self.application.app_project_path = project_path

    def remove_application(self):
        print(f"Removing application: {self.application.name}")
        # TODO: Implement logic to remove the application
        self.deleteLater() # Example: remove the widget from the