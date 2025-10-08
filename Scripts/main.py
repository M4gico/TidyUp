import os.path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel
import sys
from PyQt6.QtWidgets import QApplication

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
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tidy Up")
        logo_path = r".\Resources\Tidy_up_logo.png"
        self.setWindowIcon(QIcon(logo_path))

        self.init_UI()

    def init_UI(self):
        main_layout = QHBoxLayout()

        left_layout = self.left_layout()

        right_layout = self.right_layout()

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

    def left_layout(self) -> QVBoxLayout:
        left_layout = QVBoxLayout()

        title = QLabel("Choose Application")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        choose_app_widget = ChooseAppWidget()

        application_list_widget = ApplicationListWidget(choose_app_widget.new_application_added)

        left_layout.addWidget(title)
        left_layout.addWidget(choose_app_widget)
        left_layout.addWidget(application_list_widget)

        ##TEMP## Add a default application for testing purposes
        path = r"C:\Users\a.binner\AppData\Local\Zen Browser\zen.exe" #Laptop path
        if not os.path.exists(path):
            path = r"D:\Applications\Steam\steam.exe"
        try:
            choose_app_widget.add_application(r"C:\Applications\Obsidian\Obsidian.exe")
        except:
            pass

        try:
            choose_app_widget.add_application(path)
            choose_app_widget.add_application(r"C:\Users\magic\AppData\Local\Programs\Microsoft VS Code\Code.exe")
            choose_app_widget.add_application(r"D:\Applications\Unity\6000.2.6f2\Editor\Unity.exe")
            choose_app_widget.add_application(r"C:\Users\magic\AppData\Local\GitHubDesktop\GitHubDesktop.exe")
            choose_app_widget.add_application(r"C:\Users\magic\AppData\Local\Programs\BeeperTexts\Beeper.exe")
        except:
            pass

        return left_layout

    def right_layout(self) -> QVBoxLayout:
        right_layout = QVBoxLayout()

        title = QLabel("Detected Screens")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        screen_widget = ScreenWidget()

        right_layout.addWidget(title)
        right_layout.addWidget(screen_widget)

        return right_layout

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())