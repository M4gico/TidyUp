from threading import Lock

from PyQt6.QtCore import QSettings


class SettingsHandler:
    _instance = None
    _lock = Lock()
    _initialized = False

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SettingsHandler, cls).__new__(cls)
        return cls._instance


    def __init__(self, application_list=None, screen_list=None):
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            self.settings = QSettings("M4gico", "TidyUp")
            self.application_list = application_list
            self.screen_list = screen_list



if __name__ == '__main__':
    settings = SettingsHandler()