import os
import sys


def resource_path(*parts: str) -> str:
    """
    Absolute path to a file in the Resources folder.
    Works when running from source and when packaged as a single exe with PyInstaller,
    where --add-data files are extracted to a temp folder given by sys._MEIPASS.
    """
    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    else:
        # Scripts/CustomObjects/ResourcePath.py -> Scripts -> project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return os.path.join(base_dir, "Resources", *parts)
