"""
Entry point used to build the standalone exe with PyInstaller.
Kept at the root of the project so `from Scripts.xxx import ...` resolves the same way as
when running `python -m Scripts.main`.
"""

import sys

from PyQt6.QtWidgets import QApplication

from Scripts.main import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
