import os
import platform
from xdg import xdg_data_home


def get_downloads_path():
    system = platform.system()
    if system == "Windows":
        path = os.path.join(os.path.expanduser("~"), "Downloads")
    elif system == "Darwin":
        path = os.path.join(os.path.expanduser("~"), "Downloads")
    elif system == "Linux":
        path = os.path.join(xdg_data_home(), "Downloads")
    else:
        return None
    return path if os.path.isdir(path) else None


downloads_path = get_downloads_path()
