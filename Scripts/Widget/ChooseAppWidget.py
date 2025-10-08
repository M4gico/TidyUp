import os
from typing import List, Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QMessageBox, \
    QDialog

from Scripts.CustomObjects.Application import Application
from Scripts.Widget.ApplicationListWidget import ApplicationListWidget


class ChooseAppWidget(QWidget):
    new_application_added = pyqtSignal(Application)

    def __init__(self):
        super().__init__()

        self._applications: List[Application] = []

        main_layout = self.choose_app_layout()

        self.setLayout(main_layout)

    def choose_app_layout(self) -> QHBoxLayout:
        """
        Layout for choosing the application to add to the list
        """
        layout = QHBoxLayout()

        layout.addWidget(QLabel("File: "))

        self.app_path = QLineEdit()
        self.app_path.setEnabled(False)

        self.add_application_btn = QPushButton("Add Application")
        self.add_application_btn.clicked.connect(self.choose_app)

        layout.addWidget(self.app_path)
        layout.addWidget(self.add_application_btn)
        return layout

    def choose_app(self):
        app_path = QFileDialog.getOpenFileName(
            self,
            "Choose Application",
            "",
            "Executable Files (*.exe)"
        )[0]

        if not app_path:
            return

        if not os.path.isfile(app_path):
            QMessageBox.warning(self, "Choose application error", "The selected file is not a valid executable.")
            return

        self.add_application(app_path)

    def add_application(self, app_path: str, project_path: Optional[str] = None):
        self.app_path.setText(app_path)
        if not project_path:
            new_app = Application(app_path)
        else:
            new_app = Application(app_path, app_project_path=project_path)
        self._applications.append(new_app)
        self.new_application_added.emit(new_app)

    @property
    def applications(self) -> List[Application]:
        return self._applications