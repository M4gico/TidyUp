import ctypes
import os
import subprocess
from typing import Optional

from PyQt6.QtGui import QIcon, QImage, QPixmap

from Scripts.CustomObjects.ExtractIconExe import extract_icon, IconSize


class Application:
    def __init__(self, app_path_exe: str, name: Optional[str] = None,
                 app_project_path: Optional[str] = None):

        self.name = name
        self._app_project_path = app_project_path
        self.icon: Optional[QIcon] = None

        self.add_application_exe(app_path_exe)

    def add_application_exe(self, app_path_exe: str):
        if isinstance(app_path_exe, str) and os.path.isfile(app_path_exe):
            self._app_path_exe = app_path_exe

            if self.name is None:
                # Get the name without extension and put the first letter in uppercase
                self.name = os.path.splitext(os.path.basename(app_path_exe))[0].capitalize()

            try:
                self.icon = self._extract_icon_from_exe(app_path_exe)
            except Exception as e:
                print(f"Error extracting icon: {e}")
                self.icon = QIcon("../Resources/default_icon_32x32.png")
        else:
            raise ValueError(f"Invalid application path: {app_path_exe}")

    def open_application(self) -> subprocess.Popen:
        """
        Open the application compared of the parameters of the object
        :return: Popen object of the opened application
        """
        if self._app_project_path:
            # Open app with project path
            app = [self._app_path_exe, self._app_project_path]
        else:
            app = [self._app_path_exe]

        # cwd is to set the working directory for avoid issues with relative paths
        process = subprocess.Popen(app, cwd=os.path.dirname(self._app_path_exe))

        return process

    def _extract_icon_from_exe(self, exe_path: str) -> QIcon:
        """
        Extract the icon from the executable file and set it to the icon property
        :param exe_path:
        :return: QIcon object with the extracted icon
        """
        try:
            # Assuming that is a large icon
            icon_app = extract_icon(exe_path, IconSize.LARGE)
        except OSError:
            try:
                # If the large icon fails, try the small icon
                icon_app = extract_icon(exe_path, IconSize.SMALL)
            except OSError:
                print(f"Failed to extract icon from {exe_path}. Using default icon.")
                return QIcon(r"Resources/default_icon_32x32.png")
        icon_data = ctypes.string_at(icon_app, 32 * 32 * 4)
        image = QImage(icon_data, 32, 32, QImage.Format.Format_ARGB32)

        return QIcon(QPixmap.fromImage(image))

    #region Properties
    @property
    def app_path_exe(self):
        return self._app_path_exe
            
    @property
    def app_project_path(self):
        return self._app_project_path
    
    @app_project_path.setter
    def app_project_path(self, path):
        if isinstance(path, str) and (os.path.isdir(path) or os.path.isfile(path)):
            self._app_project_path = path

    #endregion Properties
