from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QLabel

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
