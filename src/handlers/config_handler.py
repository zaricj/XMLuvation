from PySide6.QtWidgets import QMessageBox, QMainWindow
from pathlib import Path
import json

class ConfigHandler:
    def __init__(self, config_directory: Path, config_file_name: Path, main_window: QMainWindow = None):
        """Initializes the ConfigHandler with a specific JSON configuration file."""
        self.config_directory: Path = config_directory
        self.config_file_name: Path = config_file_name
        self.main_window = main_window

        Path.mkdir(self.config_directory, exist_ok=True)
        self.data = self._load_config()

    def _load_config(self) -> dict:
        """Loads configuration from the JSON file. If the file is missing or
        invalid, it resets the configuration and returns an empty dictionary.
        """
        if self.config_file_name.exists():
            try:
                with open(self.config_file_name, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                parent_widget = self.main_window if self.main_window else None
                QMessageBox.warning(parent_widget, "Load config warning",
                                    f"Warning: {self.config_file_name} contains invalid JSON. Resetting configuration file.")
        self.reset_config()
        return {}

    def save_config(self):
        """Saves the current configuration to the JSON file."""
        with open(self.config_file_name, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def _get_nested_key(self, keys: list[str]):
        """Helper to navigate to the correct nested dictionary."""
        current_data = self._load_config()
        for i, key in enumerate(keys):
            if key not in current_data:
                return None, None # Key not found, or not a dict
            if i < len(keys) - 1: # Not the last key, expect a dictionary
                if not isinstance(current_data[key], dict):
                    # Path broken: trying to access sub-key of a non-dict
                    return None, None
                current_data = current_data[key]
        return current_data, keys[-1] # Return parent dict and the actual key

    def set(self, key_path: str, value: any):
        """
        Sets a configuration value, handling nested keys using dot notation. (e.g., 'section.subsection.key').

        The method updates the in-memory 'self.data' and automatically
        saves the entire configuration to the disk afterward. Non-existent
        intermediate keys will be created as new dictionaries.

        Args:
            key_path (str): The configuration key path (e.g., 'key' or 'section.subkey').
            value (any): The value to assign to the key.

        Example:
            If the current config is {}.
            >>> config_handler.set('app_version', '1.0.0')
            # Resulting config: {"app_version": "1.0.0"}

            If the current config is {"app_version": "1.0.0"}.
            >>> config_handler.set('custom_paths.docs', '/home/user/documents')
            # Resulting config: {
            #     "app_version": "1.0.0",
            #     "custom_paths": {
            #         "docs": "/home/user/documents"
            #     }
            # }
        """
        keys = key_path.split('.')
        parent_data = self.data
        for i, key in enumerate(keys):
            if i == len(keys) - 1: # Last key in the path
                parent_data[key] = value
            else: # Not the last key, ensure it's a dictionary
                if key not in parent_data or not isinstance(parent_data[key], dict):
                    parent_data[key] = {} # Create dict if it doesn't exist or is not a dict
                parent_data = parent_data[key]
        self.save_config()

    def get(self, key_path: str, default: any = None):
        """Gets a configuration value, handling nested keys (e.g., 'section.subsection.key')."""
        keys = key_path.split('.')
        current_data = self._load_config()
        for key in keys:
            if isinstance(current_data, dict) and key in current_data:
                current_data = current_data[key]
            else:
                return default
        return current_data

    def delete(self, key_path: str):
        """Deletes a key from the configuration, handling nested keys (e.g., 'section.subsection.key')."""
        keys = key_path.split('.')
        if not keys: return # Nothing to delete

        parent_data = self.data
        for i, key in enumerate(keys):
            if i == len(keys) - 1: # Last key in the path
                if isinstance(parent_data, dict) and key in parent_data:
                    del parent_data[key]
                    self.save_config()
                return # Key not found or parent is not a dict
            else: # Not the last key, navigate deeper
                if isinstance(parent_data, dict) and key in parent_data and isinstance(parent_data[key], dict):
                    parent_data = parent_data[key]
                else:
                    return # Path broken, key or parent not found, or not a dict

    def reset_config(self):
        """Resets the configuration file to an empty dictionary and saves it."""
        self.data = {}
        self.save_config()

    def switch_config_file(self, new_config_file_name: str):
        """Switches to a different JSON configuration file and loads its data."""
        self.config_file_name = new_config_file_name
        self.config_file_name = self.config_directory / self.config_file_name
        self.data = self._load_config()

    # get_all_keys needs to decide if it returns all top-level keys
    # or keys of a specific nested section. Let's make it more flexible.
    def get_all_keys(self, key_path: str = None) -> list[str]:
        """
        Gets all keys from the configuration.
        If key_path is provided (e.g., 'custom_paths'), returns keys of that nested dictionary.
        Otherwise, returns all top-level keys.
        """
        if key_path:
            nested_data = self.get(key_path, {})
            if isinstance(nested_data, dict):
                return list(nested_data.keys())
            return [] # If key_path leads to a non-dict value
        return list(self.data.keys())

    # The specific custom_path methods are now redundant with the new set/get/delete
    # but I'll leave them commented out for now to show the transition.
    # def add_custom_path(self, config_name: str, name: str, path: str):
    #     self.set(f"{config_name}.{name}", path)

    # def get_custom_paths(self, config_name: str) -> dict[str, str]:
    #     return self.get(config_name, {})

    # def remove_custom_path(self, config_name: str, name: str):
    #     self.delete(f"{config_name}.{name}")
