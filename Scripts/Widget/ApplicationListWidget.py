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

        self._list_application = QVBoxLayout() # This will hold the list of applications
        self._list_application.setAlignment(Qt.AlignmentFlag.AlignTop)

        _widget_application = QWidget() # This will be the widget that contains the list of applications
        _widget_application.setLayout(self._list_application)

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

        self._list_application.addWidget(QApplicationDraggable(application))
        self._list_application.addSpacing(10)
