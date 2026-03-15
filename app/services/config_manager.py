import json
import os
import shutil
import sys


def get_app_dir():
    """Get the directory where the app (exe or script) resides."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_bundled_dir():
    """Get the directory where bundled resources are stored (PyInstaller temp dir)."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return get_app_dir()


def _init_config():
    """Ensure config.json exists in app dir; copy from bundled default and hide on Windows."""
    app_dir = get_app_dir()
    config_path = os.path.join(app_dir, "config.json")

    if not os.path.exists(config_path):
        bundled = os.path.join(_get_bundled_dir(), "config.json")
        if os.path.exists(bundled):
            shutil.copy2(bundled, config_path)
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(config_path, 0x02)

    return config_path


class ConfigManager:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = _init_config()
        self.file_path = config_path
        self.data = self._read_json()

    def _read_json(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Config error: {e}")
            return {}

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    @property
    def year(self):
        return self.data.get("THIS_YEAR", "2024")

    @property
    def account_kinds(self):
        return self.data.get("勘定種別", [])

    def get_account_items(self, kind):
        return self.data.get(kind, [])

    @property
    def payment_methods(self):
        return self.data.get("支払方式", [])

    @property
    def journal_columns(self):
        return self.data.get("仕訳帳カラム", [])

    @property
    def journal_headers(self):
        return [col["header"] for col in self.journal_columns]

    @property
    def journal_fields(self):
        return [col["field"] for col in self.journal_columns]
