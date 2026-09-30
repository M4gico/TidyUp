from threading import Lock

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QTabWidget, QPushButton, \
    QInputDialog
import sys
from PyQt6.QtWidgets import QApplication

from Scripts.CustomObjects.ResourcePath import resource_path
from Scripts.CustomObjects.SettingsHandler import SettingsHandler
from Scripts.Widget.ApplicationListWidget import ApplicationListWidget
from Scripts.Widget.ChooseAppWidget import ChooseAppWidget
from Scripts.Widget.CustomWidgets.QTabApplication import QTabApplication
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
        self.setWindowIcon(QIcon(resource_path("Tidy_up_logo.png")))

        # Structure like this: [{"name": "Tab Name", "screenList": [...]}]
        # The application list is not stored per tab, it's shared and kept in application_list_widget
        self.tabs_data = []
        self.current_tab_index = 0

        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout()

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

        # Restore the tabs of the previous session (create the default tab if nothing is saved)
        self.load_settings()

# region Tab Layout
    def tab_layout(self) -> QHBoxLayout:
        layout_tab = QHBoxLayout()
        self.tab_widget = QTabApplication()

        self.tab_widget.currentChanged.connect(self.on_tab_changed) # Call when tab is changed
        self.tab_widget.tab_rename.connect(self.handle_tab_rename) # Call when tab is renamed
        self.tab_widget.tab_remove.connect(self.handle_tab_remove) # Call when tab is removed

        add_tab_btn = QPushButton("Create set applications")
        add_tab_btn.clicked.connect(lambda: self.create_new_tab()) # Name asked to the user

        layout_tab.addWidget(add_tab_btn)
        layout_tab.addWidget(self.tab_widget)
        return layout_tab

    def create_new_tab(self, name=None):
        if name is None:
            name, ok = QInputDialog.getText(self, "New Set", "Enter the name of the new set:")
            if not ok or not name:
                return

        self._create_specific_tab(name)

    def _create_specific_tab(self, name):
        # Don't override the add_tab method of QTabWidget to avoid issues

        # Save the actual tab data if there is at least one tab
        if self.tab_widget.count() > 0:
            self.save_tab_data(self.current_tab_index)

        new_data = {"name": name, "screenList": []}
        self.tabs_data.append(new_data)

        self.tab_widget.addTab(QWidget(), name)
        # Select to the new tab (not do automatically)
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    def on_tab_changed(self, index):
        # Same tab (ex: index shifted after removing a tab before the current one)
        if index == -1 or index == self.current_tab_index:
            return

        # Save the data of the previous tab (-1 when the previous tab has been removed)
        if 0 <= self.current_tab_index < len(self.tabs_data):
            self.save_tab_data(self.current_tab_index)
        self.load_tab_data(index)
        self.current_tab_index = index

        # Also called when a tab is created or removed
        self.save_settings()

    @pyqtSlot(int, str)
    def handle_tab_rename(self, index, new_name):
        """Call when a tab is renamed from the context menu"""
        self.tabs_data[index]["name"] = new_name
        self.save_settings()

    @pyqtSlot(int)
    def handle_tab_remove(self, index):
        """Call when a tab is removed from the context menu, just before the tab is removed from the widget"""
        del self.tabs_data[index]

        if self.current_tab_index == index:
            # The data of the removed tab must not be saved, the new current tab will be loaded by on_tab_changed
            self.current_tab_index = -1
        elif self.current_tab_index > index:
            # If the current tab is after the removed one, decrement the index
            self.current_tab_index -= 1

        # on_tab_changed doesn't save when the current tab stays the same (tab removed before it)
        self.save_settings()

    def save_tab_data(self, index):
        # The application list is shared between the tabs, only the screens are saved per tab
        self.tabs_data[index]["screenList"] = self.screen_widget.save_settings()

    def load_tab_data(self, index):
        data = self.tabs_data[index]
        # Give empty list if no data to avoid errors
        self.screen_widget.load_settings(data.get("screenList", []))

# endregion

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
        #     choose_app_widget.add_application(r"C:\Program Files\Zen Browser\zen.exe")
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
        self.save_settings()
        event.accept()

    def save_settings(self):
        """Save all the tabs between sessions"""
        # The widgets contain the last changes of the current tab (applications dropped, renamed...)
        if 0 <= self.current_tab_index < len(self.tabs_data):
            self.save_tab_data(self.current_tab_index)

        application_list = self.application_list_widget.save_settings()
        SettingsHandler().save(application_list, self.tabs_data, max(self.current_tab_index, 0))

    def load_settings(self):
        """Create the tabs and the application list saved in the previous session, and load the selected tab"""
        application_list, tabs_data, current_tab_index = SettingsHandler().load()
        if not tabs_data:
            tabs_data = [{"name": "Default Set", "screenList": []}]
            current_tab_index = 0

        self.tabs_data = tabs_data
        self.application_list_widget.load_settings(application_list)

        # No on_tab_changed during the creation of the tabs, the data are loaded after
        self.tab_widget.blockSignals(True)
        for tab in self.tabs_data:
            self.tab_widget.addTab(QWidget(), tab["name"])
        self.tab_widget.setCurrentIndex(current_tab_index)
        self.tab_widget.blockSignals(False)

        self.current_tab_index = current_tab_index
        self.load_tab_data(current_tab_index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())