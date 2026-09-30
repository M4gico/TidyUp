import json
from threading import Lock
from typing import Dict, List, Tuple

from PyQt6.QtCore import QSettings


class SettingsHandler:
    """
    Singleton to save and load the settings of the application between sessions.
    The data are stored in JSON in QSettings (Windows registry: HKEY_CURRENT_USER\\Software\\M4gico\\TidyUp),
    because QSettings doesn't keep correctly nested lists / dicts with None values.
    """
    _instance = None
    _lock = Lock()
    _initialized = False

    VERSION = 2  # v2: the application list is shared between the tabs instead of being saved per tab
    KEY_VERSION = "version"
    KEY_APP_LIST = "application_list"
    KEY_TABS = "tabs_data"
    KEY_CURRENT_TAB = "current_tab_index"
    LEGACY_KEYS = ["applicationList", "screenList"]  # Keys of the first version, before the tabs

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SettingsHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            self.settings = QSettings("M4gico", "TidyUp")

    def save(self, application_list: List[Dict], tabs_data: List[Dict], current_tab_index: int):
        """
        Save the whole session
        :param application_list: the applications available to drop on the screens, shared between the tabs
        :param tabs_data: [{"name": "Tab Name", "screenList": [...]}]
        :param current_tab_index: the tab selected, to reopen the application on it
        """
        self.settings.setValue(self.KEY_VERSION, self.VERSION)
        self.settings.setValue(self.KEY_APP_LIST, json.dumps(application_list))
        self.settings.setValue(self.KEY_TABS, json.dumps(tabs_data))
        self.settings.setValue(self.KEY_CURRENT_TAB, current_tab_index)

        for key in self.LEGACY_KEYS:
            self.settings.remove(key)

        # Write now on the disk, the application can be killed before the automatic write
        self.settings.sync()

    def load(self) -> Tuple[List[Dict], List[Dict], int]:
        """:return: the application list, the list of the tabs data, and the selected tab"""
        tabs_data = self._load_tabs()
        application_list = self._load_application_list(tabs_data)

        # The application list used to be saved inside each tab, it's not needed there anymore
        for tab in tabs_data:
            tab.pop("applicationList", None)

        try:
            current_tab_index = int(self.settings.value(self.KEY_CURRENT_TAB, 0))
        except (TypeError, ValueError):
            current_tab_index = 0
        if not 0 <= current_tab_index < len(tabs_data):
            current_tab_index = 0

        return application_list, tabs_data, current_tab_index

    def _load_tabs(self) -> List[Dict]:
        raw_tabs = self.settings.value(self.KEY_TABS, None)
        if not raw_tabs:
            return []

        try:
            tabs_data = json.loads(raw_tabs)
        except (TypeError, ValueError) as e:
            print(f"Settings corrupted, they are ignored: {e}")
            return []

        if not isinstance(tabs_data, list):
            return []

        # Keep only valid tabs and give default values to avoid errors when loading them
        valid_tabs = []
        for tab in tabs_data:
            if isinstance(tab, dict):
                valid_tabs.append({
                    "name": str(tab.get("name") or "Set"),
                    "applicationList": tab.get("applicationList") or [],  # Only read here for the migration below
                    "screenList": tab.get("screenList") or [],
                })
        return valid_tabs

    def _load_application_list(self, tabs_data: List[Dict]) -> List[Dict]:
        raw_app_list = self.settings.value(self.KEY_APP_LIST, None)
        if raw_app_list:
            try:
                application_list = json.loads(raw_app_list)
                if isinstance(application_list, list):
                    return application_list
            except (TypeError, ValueError) as e:
                print(f"Application list corrupted, they are ignored: {e}")

        # Migration from before the application list was shared: merge the list of every tab, keep only one
        # entry per exe (a tab may have added the same application with a different display name)
        merged: Dict[str, Dict] = {}
        for tab in tabs_data:
            for app in tab.get("applicationList", []):
                if isinstance(app, dict) and app.get("app_path_exe"):
                    merged.setdefault(app["app_path_exe"], app)
        return list(merged.values())


if __name__ == '__main__':
    # Debug: print the saved settings
    apps, tabs, current = SettingsHandler().load()
    print(f"Current tab: {current}")
    print("Application list:")
    print(json.dumps(apps, indent=2))
    print("Tabs:")
    print(json.dumps(tabs, indent=2))
