from typing import List

from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QLabel, QMessageBox

from Scripts.CustomObjects.Application import Application
from Scripts.Widget.CustomWidgets.QApplicationDraggable import QApplicationDraggable


class ApplicationListWidget(QWidget):

    def __init__(self, new_app_signal: pyqtSignal):
        super().__init__()
        self.setAcceptDrops(True)
        self.main_layout()

        new_app_signal.connect(self.add_application)

    def main_layout(self):
        layout = QVBoxLayout()

        self._list_application_layout = QVBoxLayout() # This will hold the list of applications
        self._list_application_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        _widget_application = QWidget() # This will be the widget that contains the list of applications
        _widget_application.setLayout(self._list_application_layout)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setMinimumHeight(200)
        self._scroll_area.setMaximumHeight(300)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self._scroll_area.setWidget(_widget_application)

        layout.addWidget(self._scroll_area)

        self.setLayout(layout)

    @pyqtSlot(Application)
    def add_application(self, application: Application):
        if application is None:
            raise ValueError("Application cannot be None")

        qt_applications = self._get_qt_application_list()
        # If the application is already in the list, do not add it
        if application.name in [a.application.name for a in qt_applications]:
            QMessageBox.warning(
                self,
                "Duplicate Application",
                f"The application {application.name} is already in the application list."
            )
            return

        qt_application = QApplicationDraggable(application)
        qt_application.remove_application_signal.connect(lambda: self.remove_application(qt_application))

        self._list_application_layout.addWidget(qt_application)
        self._list_application_layout.addSpacing(10)

    def remove_application(self, qt_application: QApplicationDraggable):
        """
        Remove the QApplicationDraggable from the list and the spacing below
        """
        index = self._list_application_layout.indexOf(qt_application)
        if index == -1:
            return
        # Get the spacing just after the qt application
        spacing = self._list_application_layout.takeAt(index + 1)
        if spacing:
            del spacing

        qt_application.deleteLater()

    def save_settings(self) -> List[QApplicationDraggable]:
        return self._get_qt_application_list()

    def load_settings(self, qt_applications: List[QApplicationDraggable]):
        self._remove_qt_applications() # Remove all applications before loading new ones
        for app in qt_applications:
            self.add_application(app.application)

    def _get_qt_application_list(self) -> List[QApplicationDraggable]:
        widgets = [self._list_application_layout.itemAt(i).widget() for i in range(self._list_application_layout.count()) if self._list_application_layout.itemAt(i).widget() is not None]
        qt_application_widgets = [w for w in widgets if isinstance(w, QApplicationDraggable)]
        return qt_application_widgets

    def _remove_qt_applications(self):
        for app in self._get_qt_application_list():
            self.remove_application(app)
