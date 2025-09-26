from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QScrollArea, QHBoxLayout

from Scripts.CustomObjects.Application import Application


class QScreenApplication(QWidget):
    def __init__(self, screen: QScreen):
        super().__init__()
        self.setAcceptDrops(True)

        self.applications: List[Application] = [] # Store all the applications drag in the screen
        self.init_UI(screen)

    def init_UI(self, screen: QScreen):
        main_layout = QVBoxLayout()

        # Scrollable area for application icons
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Container widget for icons to have the layout left-aligned
        self.icons_widget = QWidget()
        self.icons_layout = QHBoxLayout()
        self.icons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.icons_widget.setLayout(self.icons_layout)

        self.scroll_area.setWidget(self.icons_widget)
        main_layout.addWidget(self.scroll_area, 85)

        screen_name = screen.name()
        # Detect if the screen is a laptop screen (name starts with \\)
        if screen_name.startswith(r"\\"):
            screen_name = "Laptop Screen"

        screen_name_label = QLabel(f"Screen: {screen_name}")
        main_layout.addWidget(screen_name_label, 15)

        self.setLayout(main_layout)

    def add_application_icon(self, application: Application):
        """
        Add the icon of the application to the scroll area
        :param application: Application received from the drag and drop
        """
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setToolTip(application.name)  # Show the name on hover
        # Prevent icon cropping
        icon_label.setScaledContents(True)  # Allow the image to fit the label size
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the icon

        if application.icon:
            pixmap = application.icon.pixmap(32, 32)
            if not pixmap.isNull():
                # Resize the pixmap to fit in the QLabel
                scaled_pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
            else:
                QMessageBox.warning(
                    self,
                    "Icon Error",
                    f"The application {application.name} does not have a valid icon."
                )
                self.applications.remove(application)
                return

            icon_label.setPixmap(application.icon.pixmap(32, 32))
        else:
            QMessageBox.warning(
                self,
                "Icon Error",
                f"The application {application.name} does not have a valid icon."
            )
            self.applications.remove(application) # Remove the application if it has no icon
            return

        # Add the icon to the layout of the scroll area
        self.icons_layout.addWidget(icon_label)

    #region Drag and Drop Events
    def dragEnterEvent(self, event):
        self.verify_drag(event)

    def dragMoveEvent(self, event):
        self.verify_drag(event)

    def dropEvent(self, event):
        # Verify again that the drag is valid (mime text and attribute application)
        if (event.mimeData().hasText() and
                event.mimeData().text() == "application_drag" and
                hasattr(event.source(), 'application')):

            # Directly retrieve the Application object
            application = event.source().application
            self.applications.append(application)

            self.add_application_icon(application)

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
    #endregion