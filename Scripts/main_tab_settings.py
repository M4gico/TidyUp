import os.path
import sys
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton, \
    QInputDialog, QApplication

from Scripts.Widget.ApplicationListWidget import ApplicationListWidget
from Scripts.Widget.ChooseAppWidget import ChooseAppWidget
from Scripts.Widget.CustomWidgets.QTabApplication import QTabApplication
from Scripts.Widget.ScreenWidget import ScreenWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tidy Up")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        logo_path = os.path.join(project_root, "Resources", "Tidy_up_logo.png")
        self.setWindowIcon(QIcon(logo_path))

        # Structure de données pour les onglets
        # Liste de dicts : [{"name": "Nom", "applicationList": [...], "screenList": [...]}]
        self.tabs_data = []
        self.current_tab_index = -1

        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout()
        self.settings = QSettings("M4gico", "TidyUp")

        layout_application = QHBoxLayout()
        layout_application.addLayout(self.left_layout())
        layout_application.addLayout(self.right_layout())

        main_layout.addLayout(self.tab_layout())
        main_layout.addLayout(layout_application)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.load_settings()

    def tab_layout(self) -> QHBoxLayout:
        layout_tab = QHBoxLayout()
        self.tab_widget = QTabApplication()

        # Connexions
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.tab_renamed.connect(self.update_tab_name_data)
        self.tab_widget.tab_delete_requested.connect(self.handle_tab_deletion)

        add_tab_btn = QPushButton("Create set applications")
        add_tab_btn.clicked.connect(self.create_new_tab)

        layout_tab.addWidget(add_tab_btn)
        layout_tab.addWidget(self.tab_widget)
        return layout_tab

    def create_new_tab(self):
        """Crée un nouvel onglet et initialise ses données"""
        name, ok = QInputDialog.getText(self, "New Set", "Enter the name of the new set:")
        if ok and name:
            # Sauvegarder l'onglet actuel avant de changer
            self.save_current_tab_data_to_memory()

            # Créer les données pour le nouvel onglet
            new_data = {"name": name, "applicationList": [], "screenList": []}
            self.tabs_data.append(new_data)

            # Ajouter l'onglet (cela déclenchera on_tab_changed)
            self.tab_widget.addTab(QWidget(), name)
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    def on_tab_changed(self, index):
        """Gère le changement d'onglet : sauvegarde l'ancien, charge le nouveau"""
        if index == -1: return

        # 1. Sauvegarder les données de l'onglet précédent (si valide)
        if self.current_tab_index != -1 and self.current_tab_index < len(self.tabs_data):
            # On vérifie que l'index précédent n'est pas celui qu'on vient de supprimer
            # (géré par handle_tab_deletion, mais double sécurité ici)
            self.save_tab_data_to_memory(self.current_tab_index)

        # 2. Charger les données du nouvel onglet
        self.load_tab_data_from_memory(index)

        # 3. Mettre à jour l'index courant
        self.current_tab_index = index

    def save_current_tab_data_to_memory(self):
        if 0 <= self.current_tab_index < len(self.tabs_data):
            self.save_tab_data_to_memory(self.current_tab_index)

    def save_tab_data_to_memory(self, index):
        """Récupère l'état des widgets et le stocke dans la liste tabs_data"""
        if 0 <= index < len(self.tabs_data):
            self.tabs_data[index]["applicationList"] = self.application_list_widget.save_settings()
            self.tabs_data[index]["screenList"] = self.screen_widget.save_settings()

    def load_tab_data_from_memory(self, index):
        """Récupère les données de la liste tabs_data et met à jour les widgets"""
        if 0 <= index < len(self.tabs_data):
            data = self.tabs_data[index]
            self.application_list_widget.load_settings(data.get("applicationList", []))
            self.screen_widget.load_settings(data.get("screenList", []))

    def update_tab_name_data(self, index, new_name):
        if 0 <= index < len(self.tabs_data):
            self.tabs_data[index]["name"] = new_name

    def handle_tab_deletion(self, index):
        if 0 <= index < len(self.tabs_data):
            del self.tabs_data[index]

        # Ajustement de l'index courant
        if index < self.current_tab_index:
            self.current_tab_index -= 1
        elif index == self.current_tab_index:
            self.current_tab_index = -1  # Force le rechargement au prochain changement

        self.tab_widget.removeTab(index)

    def left_layout(self) -> QVBoxLayout:
        left_layout = QVBoxLayout()
        title = QLabel("Choose Application")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        choose_app_widget = ChooseAppWidget()
        self.application_list_widget = ApplicationListWidget(choose_app_widget.new_application_added)
        left_layout.addWidget(title)
        left_layout.addWidget(choose_app_widget)
        left_layout.addWidget(self.application_list_widget)
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
        self.save_settings()
        event.accept()

    def save_settings(self):
        """Sauvegarde globale sur le disque"""
        self.save_current_tab_data_to_memory()  # Assure que l'onglet actif est sauvegardé
        self.settings.setValue("tabs_data", self.tabs_data)

    def load_settings(self):
        """Chargement global depuis le disque"""
        saved_data = self.settings.value("tabs_data")

        self.tab_widget.blockSignals(True)  # Évite les triggers inutiles pendant l'init
        self.tab_widget.clear()
        self.tabs_data = []

        if saved_data and isinstance(saved_data, list):
            self.tabs_data = saved_data
            for tab in self.tabs_data:
                self.tab_widget.addTab(QWidget(), tab.get("name", "Set"))
        else:
            # Défaut si rien n'est sauvegardé
            self.tabs_data = [{"name": "Default Set", "applicationList": [], "screenList": []}]
            self.tab_widget.addTab(QWidget(), "Default Set")

        self.tab_widget.blockSignals(False)

        # Charger le premier onglet
        if self.tabs_data:
            self.current_tab_index = 0
            self.load_tab_data_from_memory(0)
            print("Settings loaded successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
