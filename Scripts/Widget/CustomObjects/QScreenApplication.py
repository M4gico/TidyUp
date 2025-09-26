from typing import List

from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox

from Scripts.CustomObjects.Application import Application


class QScreenApplication(QWidget):
    def __init__(self, screen: QScreen):
        super().__init__()
        self.setAcceptDrops(True)

        self.applications: List[Application] = [] # Store all the applications drag in the screen
        self.init_UI(screen)

    def init_UI(self, screen: QScreen):
        main_layout = QVBoxLayout()

        self.number_of_applications = QLabel("0 Applications")
        main_layout.addWidget(self.number_of_applications, 85)

        screen_name = QLabel(f"Screen: {screen.name()}")
        main_layout.addWidget(screen_name, 15)

        self.setLayout(main_layout)

    def dragEnterEvent(self, event):
        self.verify_drag(event)

    def dragMoveEvent(self, event):
        self.verify_drag(event)

    def dropEvent(self, event):
        # Verify again that the drag is valid (mime text and attribute application)
        if (event.mimeData().hasText() and
                event.mimeData().text() == "application_drag" and
                hasattr(event.source(), 'application')):

            # Récupérer directement l'objet Application
            application = event.source().application
            self.applications.append(application)

            self.number_of_applications.setText(f"{len(self.applications)} Applications")
            event.acceptProposedAction()
        else:
            event.ignore()
            QMessageBox.warning(
                self,
                "Drag Error",
                "The dropped item is not a valid application."
            )

    def verify_drag(self, event):
        # Vérifier que c'est bien un drag d'application
        if (event.mimeData().hasText() and
                event.mimeData().text() == "application_drag" and
                hasattr(event.source(), 'application')):
            event.acceptProposedAction()
        else:
            event.ignore()
