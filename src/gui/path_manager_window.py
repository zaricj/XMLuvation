from PySide6.QtWidgets import QWidget, QMessageBox
import os
from PySide6.QtGui import QCloseEvent

from utils.config_handler import ConfigHandler
from gui.resources.ui.CustomPathsManager_ui import Ui_Form

# Path Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Folder path to path_manager_window.py
print(f"OTHER: {BASE_DIR}")
# At work it's C:\Users\ZaricJ\Documents\Main\02_Entwicklung_und_Tools\GitHub\XMLuvation\src\gui

LOG_FILE_PATH: str = os.path.join(BASE_DIR,"logs","xmluvation.log")
GUI_CONFIG_FILE_PATH: str = os.path.join(BASE_DIR, "config","config.json")
GUI_CONFIG_DIRECTORY: str = os.path.join(BASE_DIR, "config")
DARK_THEME_PATH = os.path.join(BASE_DIR, "resources", "themes", "dark_theme.qss")
LIGHT_THEME_PATH = os.path.join(BASE_DIR, "resources", "themes", "light_theme.qss")
ICON_PATH = os.path.join(BASE_DIR, "resources", "icons", "xml_256px.ico")
DARK_THEME_QMENU_ICON = os.path.join(BASE_DIR, "resources", "images", "dark.png")
LIGHT_THEME_QMENU_ICON = os.path.join(BASE_DIR, "resources", "images", "light.png")

# Resource and UI Paths
UI_RESOURCES: str = os.path.join("gui", "resources", "qrc", "xmluvation_resources.qrc")

# App related constants
APP_NAME: str = "Custom Paths Manager"

class CustomPathsManager(QWidget):
    def __init__(self, main_window: object):
        super().__init__()
        self.main_window = main_window # Keep reference to main window
        
        # Create and setup ui from .ui file
        self.ui = Ui_Form() # Assuming Ui_Form is correctly imported and available
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
            self.main_window.update_paths_menu() # Notify main window to refresh its menu

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

            # *** Dynamic usage: Direct get for nested path ***
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
                # *** Dynamic usage: Direct delete for nested path ***
                self.config_handler.delete(f"custom_paths.{custom_path_name}")
                
                self.ui.combobox_path_names.removeItem(custom_path_name_index)
                self.main_window.update_paths_menu() 
                self.clear_all_inputs()
                
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
