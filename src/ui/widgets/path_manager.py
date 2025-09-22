from PySide6.QtWidgets import QWidget, QMessageBox, QMainWindow
from pathlib import Path

from modules.config_handler import ConfigHandler
from ui.designer.CustomPathsManager_ui import Ui_Settings

CURRENT_DIR = Path(__file__).parent # \XMLuvation\src\ui\widgets
ROOT_DIR = CURRENT_DIR.parent.parent

# Path Constants
GUI_CONFIG_DIRECTORY: Path = ROOT_DIR / "config"
GUI_CONFIG_FILE_PATH: Path = ROOT_DIR / "config" / "config.json"

# Theme files
DARK_THEME_PATH: Path = ROOT_DIR / "resources" / "styles" / "dark_theme.qss"
LIGHT_THEME_PATH: Path = ROOT_DIR / "resources" / "styles" / "light_theme.qss"

ICON_PATH: Path = ROOT_DIR / "resources" / "icons" / "xml_256px.ico"

# Theme file icons
DARK_THEME_QMENU_ICON: Path = ROOT_DIR / "resources" / "images" / "dark.png"
LIGHT_THEME_QMENU_ICON: Path = ROOT_DIR / "resources" / "images" / "light.png"


# App related constants
APP_NAME: str = "Custom Paths Manager"

class CustomPathsManager(QWidget):
    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.main_window = main_window # Keep reference to the main window

        # Create and setup ui from .ui file
        self.ui = Ui_Settings() # Assuming Ui_Form is correctly imported and available
        self.ui.setupUi(self)

        # Initialize ConfigHandler, passing self (CustomPathsManager) as the parent for QMessageBox
        # and also the main_window as the optional parent for the QMessageBox within ConfigHandler
        self.config_handler = ConfigHandler(
            config_directory=GUI_CONFIG_DIRECTORY,
            config_file_name=GUI_CONFIG_FILE_PATH,
            main_window=self # Pass self as the parent for QMessageBox in ConfigHandler
        )

        # Connect signals/slots if not already done in setupUi
        self.ui.button_save_changes.clicked.connect(self.save_changes_event)
        self.ui.button_load_action.clicked.connect(self.load_custom_path_event)
        self.ui.button_delete_action.clicked.connect(self.delete_custom_path_event)

        # Initial population of the combobox
        self.update_combobox()

    def save_changes_event(self):
        try:
            path_name = self.ui.line_edit_path_name.text().strip()
            path_value = self.ui.line_edit_path_value.text().strip()

            if not path_name:
                QMessageBox.warning(self, "Missing path name", "Please fill in the path name in order to save the custom action.")
                return

            if not path_value:
                QMessageBox.warning(self, "Missing path value", "Please fill in the path value in order to save the custom action.")
                return

            # *** Dynamic usage: Direct set for nested path ***
            self.config_handler.set(f"custom_paths.{path_name}", path_value)

            self.update_combobox()
            self.main_window.update_paths_menu() # Notify the main window to refresh its menu

            QMessageBox.information(self, "Action saved", f"Custom path '{path_name}' has been saved successfully.")
            self.clear_all_inputs()
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the custom path: {str(ex)}")

    def load_custom_path_event(self):
        try:
            combobox_path_name = self.ui.combobox_path_names.currentText()
            if not combobox_path_name:
                self.clear_all_inputs()
                return

            # *** Dynamic usage: Direct get for a nested path ***
            path_value = self.config_handler.get(f"custom_paths.{combobox_path_name}")

            if path_value is not None:
                self.ui.line_edit_path_name.setText(combobox_path_name)
                self.ui.line_edit_path_value.setText(path_value)
            else:
                self.clear_all_inputs()
                QMessageBox.warning(self, "Path Not Found", f"The path '{combobox_path_name}' was not found in the configuration.")

        except Exception as ex:
            QMessageBox.critical(self, "Load custom path error", f"An error occurred: {str(ex)}")

    def delete_custom_path_event(self):
        try:
            custom_path_name = self.ui.combobox_path_names.currentText()
            custom_path_name_index = self.ui.combobox_path_names.currentIndex()

            if not custom_path_name:
                QMessageBox.information(self, "No action to delete", "Please select an action from the combobox first.")
                return

            reply = QMessageBox.question(self, "Confirm Delete",
                    f"Are you sure you want to delete the path '{custom_path_name}'?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                # *** Dynamic usage: Direct delete for a nested path ***
                self.config_handler.delete(f"custom_paths.{custom_path_name}")

                self.ui.combobox_path_names.removeItem(custom_path_name_index)
                self.clear_all_inputs()
                self.main_window.update_paths_menu()

        except Exception as ex:
            QMessageBox.critical(self, "Error while trying to delete action",
                f"An error has occurred while trying to delete the custom path. {str(ex)}")

    def update_combobox(self):
        self.ui.combobox_path_names.clear()
        # *** Dynamic usage: Get keys of the nested section ***
        config_file_values = self.config_handler.get_all_keys("custom_paths")
        if config_file_values:
            self.ui.combobox_path_names.addItems(config_file_values)

    def clear_all_inputs(self):
        inputs = [self.ui.line_edit_path_name, self.ui.line_edit_path_value]
        for input in inputs:
            input.clear()
