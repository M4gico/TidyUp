from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel
import sys
from PyQt6.QtWidgets import QApplication

from Scripts.Widget.ChooseAppWidget import ChooseAppWidget

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
        self.setWindowIcon(QIcon('Resources/Tidy_up_logo.png'))

        self.init_UI()

    def init_UI(self):
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(ChooseAppWidget())

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Detected Screens")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        right_layout.addWidget(title)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

    def btn_clicked(self):
        print("Button was clicked")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())