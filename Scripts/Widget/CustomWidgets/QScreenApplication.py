from typing import List

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QListWidget, QListWidgetItem

from Scripts.CustomObjects.Application import Application

#TODO: Get a list of QApplicationDraggable in the side and keep the applications in a list
class QScreenApplication(QWidget):
    def __init__(self, screen: QScreen):
        super().__init__()
        self.setAcceptDrops(True)

        self.applications: List[Application] = [] # Store all the applications drag in the screen
        self.screen = screen
        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout()

        self.app_list = QListWidget()
        self.app_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.app_list.setMovement(QListWidget.Movement.Static) # Prevent items from being moved
        self.app_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.app_list.setIconSize(QSize(32, 32))
        self.app_list.setSpacing(15)
        self.app_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)

        main_layout.addWidget(self.app_list)

        screen_name = self.screen.name()
        # Detect if the screen is a laptop screen (name starts with \\)
        if screen_name.startswith(r"\\"):
            screen_name = "Laptop Screen"

        screen_name_label = QLabel(f"Screen: {screen_name}")
        screen_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(screen_name_label, 15)

        self.setLayout(main_layout)

    def add_application(self, application: Application):
        """
        Add the icon of the application to the scroll area
        :param application: Application received from the drag and drop
        """
        if not application.icon or application.icon.isNull():
            QMessageBox.warning(
                self,
                "Icon Error",
                f"The application {application.name} does not have a valid icon."
            )
            return

        if application in self.applications:
            QMessageBox.information(
                self,
                "Duplicate Application",
                f"The application {application.name} is already added to this screen."
            )
            return

        item = QListWidgetItem(application.icon, application.name)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        # Add the item to the list widget
        self.app_list.addItem(item)
        self.applications.append(application)

    #region Drag and Drop Events
    def dragEnterEvent(self, event):
        self.verify_drag(event)

    def dragMoveEvent(self, event):
        self.verify_drag(event)

    def dropEvent(self, event):
        # Verify again that the drag is valid (mime text and attribute application)
        if (event.mimeData().hasText() and
                event.mimeData().text() == "application_drag" and
                hasattr(event.source(), 'application')):

            # Directly retrieve the Application object
            application = event.source().application

            self.add_application(application)

            event.acceptProposedAction()
        else:
            event.ignore()
            QMessageBox.warning(
                self,
                "Drag Error",
                "The dropped item is not a valid application."
            )

    def verify_drag(self, event):
        # Vérifier que c'est bien un drag d'application
        if (event.mimeData().hasText() and
                event.mimeData().text() == "application_drag" and
                hasattr(event.source(), 'application')):
            event.acceptProposedAction()
        else:
            event.ignore()
    #endregion