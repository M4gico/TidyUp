from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtWidgets import QTabWidget, QMenu, QInputDialog, QMessageBox


class QTabApplication(QTabWidget):
    tab_rename = pyqtSignal(int, str)  # Gives the index of the renamed tab and its new name
    tab_remove = pyqtSignal(int)  # Gives the index of the removed tab

    def __init__(self):
        super().__init__()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu) # Enable custom signal when asking for context menu
        self.customContextMenuRequested.connect(self.show_context_menu) # Connect the signal to the slot
        self.name = ""

    def show_context_menu(self, position: QPoint):
        tab_index = self.tabBar().tabAt(position)
        if tab_index != -1:
            menu = QMenu(self)

            rename_action = menu.addAction("Rename Tab")
            rename_action.triggered.connect(lambda: self.rename_tab(tab_index))

            close_action = menu.addAction("Close Tab")
            close_action.triggered.connect(lambda: self.close_tab(tab_index))

            menu.exec(self.mapToGlobal(position))

    def addTab(self, widget, name=None):
        """If a name is not provided, ask the user for it"""
        if name is None:
            name, ok = QInputDialog.getText(self, "New Set of Applications", "Enter the name of the new set:")
            if ok and name:
                self.name = name
                super().addTab(widget, name)
        else:
            self.name = name
            super().addTab(widget, name)

    def rename_tab(self, index):
        current_name = self.tabText(index)
        new_name, ok = QInputDialog.getText(self, "Rename Tab", "Enter the new name for the tab:", text=current_name)
        if ok and new_name:
            self.name = new_name
            self.setTabText(index, new_name)
            self.tab_rename.emit(index, new_name)

    def close_tab(self, index):
        if self.count() <= 1:
            QMessageBox.warning(self, "Cannot Close Tab", "At least one tab must remain.")
            return # Prevent closing the last tab

        confirm = QMessageBox.question(self, "Close Tab",
                                     f"Sure to close '{self.tabText(index)}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            self.removeTab(index)
            self.tab_remove.emit(index)