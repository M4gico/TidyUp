from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
import sys
from PyQt6.QtWidgets import QApplication

from Scripts.Widget.ChooseAppWidget import ChooseAppWidget

"""
Stucture of the app: 
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
        right_layout = QVBoxLayout()
        right_layout.addWidget(ChooseAppWidget())

        main_widget = QWidget()
        main_widget.setLayout(right_layout)
        self.setCentralWidget(main_widget)

    def btn_clicked(self):
        print("Button was clicked")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())