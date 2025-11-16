import os.path
from threading import Lock

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QTabWidget, QPushButton
import sys
from PyQt6.QtWidgets import QApplication

from Scripts.CustomObjects.SettingsHandler import SettingsHandler
from Scripts.Widget.ApplicationListWidget import ApplicationListWidget
from Scripts.Widget.ChooseAppWidget import ChooseAppWidget
from Scripts.Widget.ScreenWidget import ScreenWidget

"""
Structure of the app: 
Choose application that we want to launch
Create different tabs with different set of applications
Number of screens available 
Drop the applications in screens 
"""

class MainWindow(QMainWindow):
    #Singlton of the main window

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tidy Up")
        # Get the absolute path to the directory containing main.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the directory of the main project
        project_root = os.path.dirname(script_dir)
        # Construct the path to the logo
        logo_path = os.path.join(project_root, "Resources", "Tidy_up_logo.png")

        self.setWindowIcon(QIcon(logo_path))

        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout()

        # Save settings between sessions automatically
        self.settings = QSettings("M4gico", "TidyUp")

        layout_application = QHBoxLayout()

        left_layout = self.left_layout()

        right_layout = self.right_layout()

        layout_application.addLayout(left_layout)
        layout_application.addLayout(right_layout)

        layout_tab = self.tab_layout()

        main_layout.addLayout(layout_tab)
        main_layout.addLayout(layout_application)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        self.load_settings()

    def tab_layout(self) -> QHBoxLayout:
        layout_tab = QHBoxLayout()
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(QWidget(), "Tab 1")

        add_tab_btn = QPushButton("Create set applications")
        add_tab_btn.clicked.connect(self.create_new_tab)

        layout_tab.addWidget(add_tab_btn)
        layout_tab.addWidget(self.tab_widget)
        return layout_tab

    def create_new_tab(self):
        # self.save_settings_tab()
        self.tab_widget.addTab(QWidget(), f"Tab {self.tab_widget.count() + 1}")

    def left_layout(self) -> QVBoxLayout:
        left_layout = QVBoxLayout()

        title = QLabel("Choose Application")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        choose_app_widget = ChooseAppWidget()

        self.application_list_widget = ApplicationListWidget(choose_app_widget.new_application_added)

        left_layout.addWidget(title)
        left_layout.addWidget(choose_app_widget)
        left_layout.addWidget(self.application_list_widget)

        # TODO: ##TEMP## Add a default application for testing purposes
        # path = r"C:\Users\a.binner\AppData\Local\Zen Browser\zen.exe" #Laptop path
        # if not os.path.exists(path):
        #     path = r"D:\Applications\Steam\steam.exe"
        # try:
        #     choose_app_widget.add_application(r"C:\Applications\Obsidian\Obsidian.exe")
        # except:
        #     pass
        #
        # try:
        #     choose_app_widget.add_application(path)
        #     choose_app_widget.add_application(r"C:\Users\magic\AppData\Local\Programs\Microsoft VS Code\Code.exe")
        #     choose_app_widget.add_application(r"D:\Applications\Unity\6000.2.6f2\Editor\Unity.exe")
        #     choose_app_widget.add_application(r"C:\Users\magic\AppData\Local\GitHubDesktop\GitHubDesktop.exe")
        #     choose_app_widget.add_application(r"C:\Users\magic\AppData\Local\Programs\BeeperTexts\Beeper.exe")
        # except:
        #     pass

        return left_layout

    def right_layout(self) -> QVBoxLayout:
        right_layout = QVBoxLayout()

        title = QLabel("Detected Screens")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.screen_widget = ScreenWidget()

        right_layout.addWidget(title)
        right_layout.addWidget(self.screen_widget)

        return right_layout

    def closeEvent(self, event):
        """Override the close event to save settings from all tabs before application closed"""
        # TODO: Save settings for each tabs separately
        self.save_settings()
        event.accept()

    def save_settings_tab(self):
        """Save settings of a tab"""
        #TODO: Save the settings compared of the tab select
        self.settings.setValue("applicationList", self.application_list_widget.save_settings())
        self.settings.setValue("screenList", self.screen_widget.save_settings())

    def load_settings_tab(self):
        """Load setting of a tab"""
        # Return None if no settings found
        application_list = self.settings.value("applicationList", None)
        screen_list = self.settings.value("screenList", None)
        if any(setting is None for setting in [application_list, screen_list]):
            return None, None
        return application_list, screen_list

    def load_settings(self):
        application_list, screen_list = self.load_settings_tab()
        if application_list and screen_list:
            self.application_list_widget.load_settings(application_list)
            self.screen_widget.load_settings(screen_list)
            print("Settings loaded successfully.")

    def save_settings(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())