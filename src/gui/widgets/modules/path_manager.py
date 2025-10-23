from PySide6.QtWidgets import QWidget, QMessageBox, QLineEdit, QFileDialog
from PySide6.QtCore import Slot, QFile, QIODevice, QTextStream
from PySide6.QtGui import QCloseEvent
from pathlib import Path

from modules.config_handler import ConfigHandler
from gui.widgets.CustomPathsManager_ui import Ui_CustomPathsManagerWidget

from typing import TYPE_CHECKING, Any, List
if TYPE_CHECKING:
    from src.main import MainWindow


# Determine the path of the current file and resolve it to handle symlinks/etc.
FILE_PATH = Path(__file__).resolve()

# Get the project src directory
SRC_ROOT_DIR = FILE_PATH.parents[3]

# Path Constants
GUI_CONFIG_DIRECTORY: Path = SRC_ROOT_DIR / "config"
GUI_CONFIG_FILE_PATH: Path = SRC_ROOT_DIR / "config" / "config.json"

class CustomPathsManager(QWidget):
    def __init__(self, main_window: "MainWindow"):
        super().__init__()
        self.main_window = main_window
        # Create and setup ui from .ui file
        self.ui = Ui_CustomPathsManagerWidget() # Assuming Ui_Form is correctly imported and available
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
        self.ui.button_create_custom_path.clicked.connect(self.create_custom_path_event)
        self.ui.button_browse_path_folder.clicked.connect(lambda: self.browse_folder("Select a folder for the custom path value", self.ui.line_edit_custom_path_value))
        self.ui.button_open_config_directory.clicked.connect(lambda: self.main_window._open_folder_in_file_explorer(GUI_CONFIG_DIRECTORY))

        # Initialize theme for app
        self._initialize_theme()
        
        # Initial population of the combobox
        self.update_combobox()

    def _initialize_theme(self):
        """Initialize UI theme files (.qss)"""
        try:
            if self.main_window.current_theme == "dark_theme.qss":
                theme_file = self.main_window.dark_theme_file
            else:
                theme_file = self.main_window.light_theme_file

            file = QFile(theme_file)
            if not file.open(QIODevice.ReadOnly | QIODevice.Text):
                return
            stylesheet = QTextStream(file).readAll()
            self.setStyleSheet(stylesheet)
            file.close()
        except Exception as ex:
            QMessageBox.critical(
                self, "Theme load error", f"Failed to load theme: {str(ex)}"
            )

        
    # An input validator
    def _validate_inputs(self, inputs_to_validate: List[Any]) -> bool:
        try:
            for input in inputs_to_validate:
                # Check if not empty:
                if len(input) > 0:
                    return True
                else:
                    raise ValueError
                
        except Exception as ex:
            QMessageBox.warning(self, "Input validation failed", f"Something went wrong: {str(ex)}")
            return False
        
    # Create Path section
    @Slot()
    def create_custom_path_event(self) -> None:
        sub_key = self.ui.line_edit_custom_path_name.text()
        value = self.ui.line_edit_custom_path_value.text()
        
        valid = self._validate_inputs([sub_key, value])
        
        if valid:
            # Construct the full key path for "custom_paths"
            full_key_path = f"custom_paths.{sub_key}"
            self.config_handler.set(full_key_path, value)
            self.update_combobox()
            QMessageBox.information(self, "Success", f"Successfully created a new custom path:\nKey:{sub_key}\nValue:{value}")
            
    def browse_folder(self, dialog_message: str, line_widget: QLineEdit):
        """Helper for folder browsing dialogs."""
        try:
            folder = QFileDialog.getExistingDirectory(self, dialog_message)
            if folder:
                line_widget.setText(folder)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred in browse folder method", message)

    @Slot()
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
            self.main_window._update_paths_menu() # Notify the main window to refresh its menu

            QMessageBox.information(self, "Action saved", f"Custom path '{path_name}' has been saved successfully.")
            self.clear_all_inputs()
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the custom path: {str(ex)}")
            
    @Slot()
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

    @Slot()
    def delete_custom_path_event(self):
        try:
            custom_path_name = self.ui.combobox_path_names.currentText()
            custom_path_name_index = self.ui.combobox_path_names.currentIndex()

            if not custom_path_name:
                QMessageBox.information(self, "No configuration to delete", "Please select a configuration that you want to delete first from the combobox.")
                return

            reply = QMessageBox.question(self, "Confirm Delete",
                    f"Are you sure you want to delete the path '{custom_path_name}'?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                # *** Dynamic usage: Direct delete for a nested path ***
                self.config_handler.delete(f"custom_paths.{custom_path_name}")
                self.ui.combobox_path_names.removeItem(custom_path_name_index)
                self.clear_all_inputs()
                self.main_window._update_paths_menu()

        except Exception as ex:
            QMessageBox.critical(self, "Error while trying to delete action",
                f"An error has occurred while trying to delete the custom path. {str(ex)}")

    @Slot()
    def update_combobox(self):
        """Updated the combobox in the custom paths manager combobox by re-loading the config file again.
        """
        self.ui.combobox_path_names.clear()
        # *** Dynamic usage: Get keys of the nested section ***
        config_file_values = self.config_handler.get_all_keys("custom_paths")
        if config_file_values:
            self.ui.combobox_path_names.addItems(config_file_values)
            
    @Slot()
    def clear_all_inputs(self):
        inputs = [self.ui.line_edit_path_name, self.ui.line_edit_path_value]
        for input in inputs:
            input.clear()
            
    # Close event
    def closeEvent(self, event: QCloseEvent):
        # Always update paths_menu
        self.main_window._update_paths_menu()
