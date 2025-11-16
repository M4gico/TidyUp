import copy
from typing import List

from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QListWidget, QListWidgetItem, QGridLayout, \
    QScrollArea, QAbstractItemView

from Scripts.CustomObjects.Application import Application
from Scripts.Widget.CustomWidgets.QApplicationDraggable import QApplicationDraggable


#TODO: Get a list of QApplicationDraggable in the side and keep the applications in a list
class QScreenApplication(QWidget):
    def __init__(self, screen: QScreen):
        super().__init__()
        self.setAcceptDrops(True)

        self.qt_applications: List[QApplicationDraggable] = [] # Store all the applications drag in the screen
        self.screen = screen

        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout()

        self.app_list_widget = QListWidget()
        self.app_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.app_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.screen_name = self.screen.name()
        # Detect if the screen is a laptop screen (name starts with \\)
        if self.screen_name.startswith(r"\\"):
            self.screen_name = "Laptop Screen"

        screen_name_label = QLabel(f"Screen: {self.screen_name}")
        screen_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.app_list_widget)
        main_layout.addWidget(screen_name_label)

        self.setLayout(main_layout)

    def add_application(self, qt_application: QApplicationDraggable) -> bool:
        """
        Add the QApplicationDraggable to the scroll area
        :param qt_application: QApplicationDraggable received from the drag and drop
        :return: True if the application was added, False otherwise
        """
        if not qt_application.application.icon or qt_application.application.icon.isNull():
            QMessageBox.warning(
                self,
                "Icon Error",
                f"The application {qt_application.application.name} does not have a valid icon."
            )
            return False

        if qt_application.application.name in [a.application.name for a in self.qt_applications]:
            QMessageBox.warning(
                self,
                "Duplicate Application",
                f"The application {qt_application.application.name} is already added to this screen."
            )
            return False

        self.qt_applications.append(qt_application)

        # Add a new item in the list widget
        list_item = QListWidgetItem(self.app_list_widget)
        # Set the size that will be used to display the widget
        list_item.setSizeHint(qt_application.sizeHint())
        # Add the widget to the list item
        self.app_list_widget.addItem(list_item)
        # Insert the widget in the list item
        self.app_list_widget.setItemWidget(list_item, qt_application)

        qt_application.remove_application_signal.connect(lambda: self.remove_application_from_list(qt_application, list_item))

        return True

    @pyqtSlot()
    def remove_application_from_list(self, qt_application: QApplicationDraggable, list_item: QListWidgetItem):
        """
        Remove the application from the list and the widget from the QListWidget.
        """
        # Find the row corresponding to the list_item
        row = self.app_list_widget.row(list_item)
        if row != -1:
            # Remove the item from the QListWidget
            self.app_list_widget.takeItem(row)

        # Remove the application from the internal list
        if qt_application in self.qt_applications:
            self.qt_applications.remove(qt_application)

        # The widget will be deleted by the caller of the signal
        qt_application.deleteLater()

    #region Drag and Drop Events
    def dragEnterEvent(self, event):
        self.verify_drag(event)

    def dragMoveEvent(self, event):
        self.verify_drag(event)

    def dropEvent(self, event):
        try:
            # Verify again that the drag is valid (mime text and attribute application)
            if event.mimeData().hasText() and event.mimeData().text() == "application_drag":

                # Directly retrieve the QApplicationDraggable from the source
                source_widget: QApplicationDraggable = event.source()

                if source_widget in self.qt_applications:
                    # If the source widget is re drop in the same screen, cancel it
                    event.ignore()
                    return

                if not isinstance(source_widget, QApplicationDraggable):
                    event.ignore()
                    QMessageBox.warning(
                        self,
                        "Drag Error",
                        "The dropped item is not a valid application."
                    )
                    return

                app = copy.copy(source_widget.application)
                app_name = copy.copy(source_widget.name_app.text())

                qt_application = QApplicationDraggable(app, app_name)
                # To prevent to delete the original widget in the application list widget
                qt_application.is_move_copy = False

                success = self.add_application(qt_application)

                if not success:
                    event.ignore()
                    return

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

    def save_settings(self) -> dict:
        """
        Save the QApplicationDraggable for this screen
        :return: List of dictionaries representing each QApplicationDraggable
        """
        # Create the screen name to find the right screen during load settings
        dict_to_return = {
            "screen_name": self.screen_name,
        }

        # Store the list of QApplicationDraggable in the screen
        for i, qt_application in enumerate(self.qt_applications):
            dict_to_return[f"qt_app_{i}"] = qt_application.save_settings()

        return dict_to_return

    def load_settings(self, save_dict: dict):
        """
        Load all QApplicationDraggable saved in the dictionary for the specific screen
        """
        for key in save_dict.keys():
             if key.startswith("qt_app_"):
                # Get the dictionary to create the QApplicationDraggable
                qt_application_dict = save_dict[key]

                application = Application(
                    qt_application_dict["app_path_exe"],
                    qt_application_dict["app_name"],
                    qt_application_dict["app_project_path"]
                )
                qt_application = QApplicationDraggable(application, qt_application_dict["name_qt"])
                self.add_application(qt_application)
