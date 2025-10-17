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

    def save_settings(self):
        #TODO: Save the settings compared of the tab select
        self.settings.setValue("applicationList", self.application_list.save_settings())
        self.settings.setValue("screenList", self.screen_list.save_settings())

    def load_settings(self):
        # Return None if no settings found
        application_list = self.settings.value("applicationList", None)
        screen_list = self.settings.value("screenList", None)
        return application_list, screen_list

if __name__ == '__main__':
    settings = SettingsHandler()