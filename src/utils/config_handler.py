import os
import json

class ConfigHandler:
    """Handles loading, saving, and managing application configuration,
    specifically custom paths.
    """
    def __init__(self):
        # Path to config.json relative to the project root
        # Assuming the project root is two levels up from src/utils/config_handler.py
        base_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = os.path.join(base_src_dir, "gui", "config")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Ensure the configuration directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.config = self.load_config()


    def print_file_path(self):
        """Prints the path to the configuration file."""
        print(f"Base source directory: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
        print(f"Configuration file path: {self.config_file}")


    def load_config(self):
        """Loads configuration from the JSON file. If the file is missing or
        invalid, it returns a default configuration.
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {self.config_file} is empty or contains invalid JSON. Using default configuration.")
        return self.get_default_config()


    def get_default_config(self):
        """Returns the default application configuration."""
        return {"custom_paths": {}}


    def save_config(self):
        """Saves the current configuration to the JSON file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)


    def add_custom_path(self, name, path):
        """Adds a new custom path to the configuration and saves it."""
        self.config["custom_paths"][name] = path
        self.save_config()


    def get_custom_paths(self):
        """Returns all custom paths from the configuration."""
        return self.config["custom_paths"]


    def remove_custom_path(self, name):
        """Removes a custom path from the configuration and saves it."""
        if name in self.config["custom_paths"]:
            del self.config["custom_paths"][name]
            self.save_config()