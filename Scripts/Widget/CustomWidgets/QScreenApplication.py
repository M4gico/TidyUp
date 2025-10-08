from typing import List

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QListWidget, QListWidgetItem, QGridLayout, \
    QScrollArea

from Scripts.CustomObjects.Application import Application
from Scripts.Widget.CustomWidgets.QApplicationDraggable import QApplicationDraggable


#TODO: Get a list of QApplicationDraggable in the side and keep the applications in a list
class QScreenApplication(QWidget):
    def __init__(self, screen: QScreen):
        super().__init__()
        self.setAcceptDrops(True)

        self.qt_applications: List[QApplicationDraggable] = [] # Store all the applications drag in the screen
        self.screen = screen

        # Grid layout settings
        self.grid_layout = None
        self.num_columns = 4  # Define how many applications per row
        self.current_row = 0
        self.current_col = self.num_columns - 1  # Start from the rightmost column

        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout()

        # Container widget and grid layout for applications
        app_container = QWidget()
        self.grid_layout = QGridLayout(app_container)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.grid_layout.setSpacing(10)

        # Scroll area to contain the app grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(app_container)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        main_layout.addWidget(scroll_area)

        screen_name = self.screen.name()
        # Detect if the screen is a laptop screen (name starts with \\)
        if screen_name.startswith(r"\\"):
            screen_name = "Laptop Screen"

        screen_name_label = QLabel(f"Screen: {screen_name}")
        screen_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(screen_name_label)
        main_layout.setStretch(0, 1)

        self.setLayout(main_layout)

    def add_application(self, qt_application: QApplicationDraggable):
        """
        Add the QApplicationDraggable to the scroll area
        :param qt_application: QApplicationDraggable received from the drag and drop
        """
        if not qt_application.application.icon or qt_application.application.icon.isNull():
            QMessageBox.warning(
                self,
                "Icon Error",
                f"The application {qt_application.application.name} does not have a valid icon."
            )
            return

        if qt_application in self.qt_applications:
            QMessageBox.information(
                self,
                "Duplicate Application",
                f"The application {qt_application.application.name} is already added to this screen."
            )
            return

        self.qt_applications.append(qt_application)

        # Add widget to the grid
        self.grid_layout.addWidget(qt_application, self.current_row, self.current_col)

        # Update column and row for the next widget
        self.current_col -= 1
        if self.current_col < 0:
            self.current_col = self.num_columns - 1
            self.current_row += 1


    #region Drag and Drop Events
    def dragEnterEvent(self, event):
        self.verify_drag(event)

    def dragMoveEvent(self, event):
        self.verify_drag(event)

    def dropEvent(self, event):
        try:
            # Verify again that the drag is valid (mime text and attribute application)
            if event.mimeData().hasText() and event.mimeData().text() == "application_drag":

                # Directly retrieve the Application object
                qt_application: QApplicationDraggable = event.source()

                self.add_application(qt_application)

                event.acceptProposedAction()
            else:
                event.ignore()
                QMessageBox.warning(
                    self,
                    "Drag Error",
                    "The dropped item is not a valid application."
                )
        except Exception as e:
            print(e)

    def verify_drag(self, event):
        # Vérifier que c'est bien un drag application
        if event.mimeData().hasText() and event.mimeData().text() == "application_drag":
            event.acceptProposedAction()
        else:
            event.ignore()
    #endregion