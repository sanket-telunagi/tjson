import json
import os
from pathlib import Path


class ConfigStore:
    """Manages persistent state (like last opened directory)."""

    # Save file in the user's home directory so it works globally
    CONFIG_FILE = Path.home() / ".tjson_config.json"

    @staticmethod
    def get_last_path() -> str:
        """Returns last used path, or current working directory if none exists."""
        try:
            if ConfigStore.CONFIG_FILE.exists():
                with open(ConfigStore.CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    path = data.get("last_path", "")
                    if path and os.path.exists(path):
                        return path
        except Exception:
            pass  # Ignore errors, fallback to default

        return os.getcwd()

    @staticmethod
    def save_last_path(path: str) -> None:
        """Saves the directory of the selected file."""
        try:
            # If a file path is passed, get its parent directory
            if os.path.isfile(path):
                path = os.path.dirname(path)

            data = {"last_path": path}
            with open(ConfigStore.CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass
