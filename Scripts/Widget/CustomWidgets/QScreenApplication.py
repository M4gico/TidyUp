import copy
from typing import List

from PyQt6.QtCore import Qt, QSize
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

        screen_name = self.screen.name()
        # Detect if the screen is a laptop screen (name starts with \\)
        if screen_name.startswith(r"\\"):
            screen_name = "Laptop Screen"

        screen_name_label = QLabel(f"Screen: {screen_name}")
        screen_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.app_list_widget)
        main_layout.addWidget(screen_name_label)

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

        if qt_application.application.name in [a.application.name for a in self.qt_applications]:
            QMessageBox.information(
                self,
                "Duplicate Application",
                f"The application {qt_application.application.name} is already added to this screen."
            )
            return

        self.qt_applications.append(qt_application)

        list_item = QListWidgetItem(self.app_list_widget)
        list_item.setSizeHint(qt_application.sizeHint())
        self.app_list_widget.addItem(list_item)
        self.app_list_widget.setItemWidget(list_item, qt_application)

        qt_application.remove_application_signal.connect(lambda: self.remove_application_from_list(qt_application, list_item))

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

    def dragLeaveEvent(self, event):
        """
        Call when a widget is dragged out
        """
        #TODO: Arreter ici =>
        #TODO: Quand on drag out une application, il faut enlever le QListWidgetItem et enlever le widget de
        #TODO: la liste des qt applications
        event.accept()

    def dropEvent(self, event):
        try:
            # Verify again that the drag is valid (mime text and attribute application)
            if event.mimeData().hasText() and event.mimeData().text() == "application_drag":

                # Directly retrieve the QApplicationDraggable from the source
                source_widget: QApplicationDraggable = event.source()

                if not isinstance(source_widget, QApplicationDraggable):
                    event.ignore()
                    QMessageBox.warning(
                        self,
                        "Drag Error",
                        "The dropped item is not a valid application."
                    )
                    return
                is_copy = event.dropAction() == Qt.DropAction.CopyAction
                if is_copy:
                    app = copy.copy(source_widget.application)
                    app_name = copy.copy(source_widget.name_app.text())

                    qt_application = QApplicationDraggable(app, app_name)
                    qt_application.is_move_copy = False
                else:
                    qt_application = source_widget

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