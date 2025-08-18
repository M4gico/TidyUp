from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from typing import List
from Scripts.CustomObjects.Application import Application


class ApplicationListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Added Applications:")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        main_layout.addWidget(title_label)

        # Scroll area for the application list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        self.scroll_area.setMaximumHeight(300)

        # Container widget for the scrollable content
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.container_widget)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)

    def add_application(self, application: Application):
        """Add a new application to the list display"""
        app_item_widget = self.create_application_item(application)
        self.container_layout.addWidget(app_item_widget)

    def create_application_item(self, application: Application) -> QWidget:
        """Create a widget for a single application item"""
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)

        # Icon label
        icon_label = QLabel()
        if hasattr(application, 'icon') and application.icon:
            # Convert QIcon to QPixmap and scale it
            pixmap = application.icon.pixmap(32, 32)
            icon_label.setPixmap(pixmap)
        else:
            # Placeholder if no icon
            icon_label.setText("No Icon")
            icon_label.setFixedSize(32, 32)
            icon_label.setStyleSheet("border: 1px solid gray; text-align: center;")

        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Application name and path
        info_layout = QVBoxLayout()

        name_label = QLabel(application.name if application.name else "Unknown Application")
        name_label.setStyleSheet("font-weight: bold;")

        path_label = QLabel(application._app_path_exe if application._app_path_exe else "No path")
        path_label.setStyleSheet("color: gray; font-size: 10px;")
        path_label.setWordWrap(True)

        info_layout.addWidget(name_label)
        info_layout.addWidget(path_label)

        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.setMaximumWidth(80)
        remove_btn.clicked.connect(lambda: self.remove_application_item(item_widget, application))

        # Add components to layout
        item_layout.addWidget(icon_label)
        item_layout.addLayout(info_layout)
        item_layout.addWidget(remove_btn)

        # Style the item
        item_widget.setStyleSheet("""
            QWidget {
                border: 1px solid lightgray;
                border-radius: 5px;
                background-color: white;
                margin: 2px;
            }
            QWidget:hover {
                background-color: #f0f0f0;
            }
        """)

        return item_widget

    def remove_application_item(self, item_widget: QWidget, application: Application):
        """Remove an application item from the display"""
        self.container_layout.removeWidget(item_widget)
        item_widget.deleteLater()
        # Emit signal or call parent method to remove from the actual list
        self.application_removed.emit(application) if hasattr(self, 'application_removed') else None

    def clear_applications(self):
        """Clear all application items from the display"""
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_applications(self, applications: List[Application]):
        """Update the display with a new list of applications"""
        self.clear_applications()
        for app in applications:
            self.add_application(app)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    from Scripts.CustomObjects.Application import Application
    from PyQt6.QtGui import QIcon

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("ApplicationListWidget Test")
    window.setGeometry(100, 100, 400, 350)

    app_list_widget = ApplicationListWidget()
    window.setCentralWidget(app_list_widget)

    # Create dummy applications
    dummy_apps = [
        Application(name="App One", app_path_exe="C:/Program Files/AppOne/appone.exe"),
        Application(name="App Two", app_path_exe="C:/Program Files/AppTwo/apptwo.exe"),
        Application(name="App Three", app_path_exe="C:/AppThree/appthree.exe")
    ]
    app_list_widget.update_applications(dummy_apps)

    window.show()
    sys.exit(app.exec())
