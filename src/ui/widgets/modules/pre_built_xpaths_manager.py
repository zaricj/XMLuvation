from PySide6.QtWidgets import QWidget, QMessageBox, QListWidget, QLineEdit, QListWidgetItem, QApplication
from PySide6.QtCore import Slot, QFile, QIODevice, QTextStream
from PySide6.QtGui import QCloseEvent
from pathlib import Path

from gevent import config

from controllers.state_controller import AddXPathExpressionToListHandler

from modules.config_handler import ConfigHandler
from ui.widgets.PreBuiltXPathsManager_ui import Ui_PreBuiltXPathsManagerWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.main import MainWindow


# Determine the path of the current file and resolve it to handle symlinks/etc.
FILE_PATH = Path(__file__).resolve()

# Get the project src directory
SRC_ROOT_DIR = FILE_PATH.parents[3]
#print(SRC_ROOT_DIR)

# Path Constants
GUI_CONFIG_DIRECTORY: Path = SRC_ROOT_DIR / "config"
GUI_CONFIG_FILE_PATH: Path = SRC_ROOT_DIR / "config" / "config.json"

# Theme files
DARK_THEME_PATH: Path = SRC_ROOT_DIR / "resources" / "styles" / "dark_theme.qss"
LIGHT_THEME_PATH: Path = SRC_ROOT_DIR / "resources" / "styles" / "light_theme.qss"

ICON_PATH: Path = SRC_ROOT_DIR / "resources" / "icons" / "xml_256px.ico"

# Theme file icons
DARK_THEME_QMENU_ICON: Path = SRC_ROOT_DIR / "resources" / "images" / "dark.png"
LIGHT_THEME_QMENU_ICON: Path = SRC_ROOT_DIR / "resources" / "images" / "light.png"


class PreBuiltXPathsManager(QWidget):
    def __init__(self, main_window: "MainWindow"):
        super().__init__()

        self.main_window = main_window
        # Create and setup ui from .ui file
        self.ui = Ui_PreBuiltXPathsManagerWidget() # Assuming Ui_Form is correctly imported and available
        self.ui.setupUi(self)
        
        self.active_list_widget = None # Active widget tracking variable

        # Initialize ConfigHandler, passing self (CustomPathsManager) as the parent for QMessageBox
        # and also the main_window as the optional parent for the QMessageBox within ConfigHandler
        self.config_handler = ConfigHandler(
            config_directory=GUI_CONFIG_DIRECTORY,
            config_file_name=GUI_CONFIG_FILE_PATH,
            main_window=self # Pass self as the parent for QMessageBox in ConfigHandler
        )
        
        # TODO Continue development, UI file is built.
        # Connect signals/slots
        self.ui.button_add_xpath_to_list.clicked.connect(self.onAddXpathToList)
        self.ui.button_add_csv_header_to_list.clicked.connect(self.onAddCSVHeaderToList)
        self.ui.button_save_config.clicked.connect(self.onSaveConfig)
        self.ui.button_save_changes.clicked.connect(self.onSaveChanges)
        self.ui.button_load_config.clicked.connect(self.onLoadConfig)
        self.ui.button_delete_config.clicked.connect(self.onDeleteConfig)
        self.ui.button_remove_selected.clicked.connect(self.onRemoveSelected)
        self.ui.button_remove_all.clicked.connect(self.onRemoveAll)
        
        # 2. Connect list widget signals to update the active_list_widget
        self.ui.list_widget_xpath_expressions.itemClicked.connect(
            lambda: self._set_active_list(self.ui.list_widget_xpath_expressions)
        )
        self.ui.list_widget_csv_headers.itemClicked.connect(
            lambda: self._set_active_list(self.ui.list_widget_csv_headers)
        )
        self.ui.list_widget_edit_xpath_expressions.itemClicked.connect(
            lambda: self._set_active_list(self.ui.list_widget_edit_xpath_expressions)
        )
        self.ui.list_widget_edit_csv_headers.itemClicked.connect(
            lambda: self._set_active_list(self.ui.list_widget_edit_csv_headers)
        )
        
        # Initialize current app theme
        self._initialize_theme()
        # Update combobox with configuration values
        self.update_combobox("custom_xpaths_autofill")
        
    # You might need to set the initial focus to the first list widget if one starts populated by default.
    def _set_active_list(self, list_widget: QListWidget):
        """Sets the list widget that was just clicked/selected."""
        self.active_list_widget = list_widget
        
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

    # ===== Slots for App logic =====
    
    @Slot() # On button click event add xpath expression to list
    def onAddXpathToList(self): 

        xpath_expression = self.ui.line_edit_xpath_expression.text()
        list_widget_xpath_expressions = self.ui.list_widget_xpath_expressions
        
        # Add entered XPath expression to list widget
        self._add_items_to_list_widget(xpath_expression, list_widget_xpath_expressions)
        self.ui.line_edit_xpath_expression.clear()
        
    @Slot() # On button click event add csv header to list
    def onAddCSVHeaderToList(self):
        csv_header_to_add = self.ui.line_edit_csv_header.text()
        list_widget_csv_headers = self.ui.list_widget_csv_headers
        
        # Add entered CSV Header to list widget
        self._add_items_to_list_widget(csv_header_to_add, list_widget_csv_headers)
        self.ui.line_edit_csv_header.clear()
        
    @Slot(str) # On button click event save config
    def onSaveConfig(self):
        """Saves the config with the added XPaths expressions and csv headers.

        Args:
            config_name (str): The name which will be saved for the config.
        """
        # Check list widgets and inputs
        list_widgets_to_validate = [self.ui.list_widget_xpath_expressions, self.ui.list_widget_csv_headers, self.ui.line_edit_config_name]
        valid_widgets = self._validate_inputs(list_widgets_to_validate)

        if valid_widgets:
            xpath_expressions = self._listwidget_to_list(self.ui.list_widget_xpath_expressions)
            csv_headers = self._listwidget_to_list(self.ui.list_widget_csv_headers)
            config_name = self.ui.line_edit_config_name.text()

            self.config_handler.set(f"custom_xpaths_autofill.{config_name}.xpath_expression", xpath_expressions)
            self.config_handler.set(f"custom_xpaths_autofill.{config_name}.csv_header", csv_headers)

            # Update combobox
            self.update_combobox("custom_xpaths_autofill")
            QMessageBox.information(
                self,
                "Configuration saved",
                f"Your configuration '{config_name}' has been successfully saved!"
            )
            
            # Clear all list widgets after successful creation of the config
            self.clear_list_widgets(list_widgets_to_validate)
            
    @Slot() # On button click event save changes
    def onSaveChanges(self):
        """Saves the changes that have been made to the loaded configuration, mainly with the 'Remove' buttons at the bottom."""
        # Check list widgets if valid
        list_widgets_to_validate = [self.ui.list_widget_edit_xpath_expressions, self.ui.list_widget_edit_csv_headers]
        valid_widgets = self._validate_inputs(list_widgets_to_validate)

        if valid_widgets:
            xpath_expressions = self._listwidget_to_list(self.ui.list_widget_edit_xpath_expressions)
            csv_headers = self._listwidget_to_list(self.ui.list_widget_edit_csv_headers)
            config_name = self.ui.combobox_xpath_configs.currentText()
            
            self.config_handler.set(f"custom_xpaths_autofill.{config_name}.xpath_expression", xpath_expressions)
            self.config_handler.set(f"custom_xpaths_autofill.{config_name}.csv_header", csv_headers)
            
            # Update combobox
            self.update_combobox("custom_xpaths_autofill")
            QMessageBox.information(
                self,
                "Configuration changes saved",
                f"Your changes to the configuration '{config_name}' has been successfully saved!"
            )
            
            # Clear all list widgets after successful changes of the config
            self.clear_list_widgets(list_widgets_to_validate)
            # Update autofill menubar
            self.main_window._update_autofill_menu()
            
    # ===== Load and Delete buttons =====
    
    @Slot()
    def onLoadConfig(self):
        """Load all values from the currently selected configuration that is in the combobox."""
        try:
            config_name = self.ui.combobox_xpath_configs.currentText()
            if not config_name:
                return

            # *** Dynamic usage: Direct get for a nested path ***
            # Both variables should return a list of strings
            xpath_expressions = self.config_handler.get(f"custom_xpaths_autofill.{config_name}.xpath_expression", [])
            csv_headers = self.config_handler.get(f"custom_xpaths_autofill.{config_name}.csv_header", [])

            if xpath_expressions and csv_headers is not None:
                # Clear list widgets in order to omit duplicate entries, because each load adds items xD
                self.clear_list_widgets([self.ui.list_widget_edit_xpath_expressions, self.ui.list_widget_edit_csv_headers])
                self.ui.list_widget_edit_xpath_expressions.addItems(xpath_expressions)
                self.ui.list_widget_edit_csv_headers.addItems(csv_headers)
            else:
                QMessageBox.warning(self, "Configuration not found", f"The configuration name '{config_name}' was not found in the configuration.")

        except Exception as ex:
            QMessageBox.critical(self, "Load custom pre built XPaths", f"An error occurred while trying to load configuration file: {str(ex)}")
            
    @Slot()
    def onDeleteConfig(self) -> None:
        try:
            config_name = self.ui.combobox_xpath_configs.currentText()
            config_name_index = self.ui.combobox_xpath_configs.currentIndex()

            if not config_name:
                QMessageBox.information(self, "No action to delete", "Please select an action from the combobox first.")
                return

            reply = QMessageBox.question(self, "Confirm Delete",
                    f"Are you sure you want to delete the config '{config_name}'?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    # *** Dynamic usage: Direct delete for a nested path ***
                    self.config_handler.delete(f"custom_xpaths_autofill.{config_name}")
                    self.ui.combobox_xpath_configs.removeItem(config_name_index)
                    # Clear all list widgets after successful delete
                    self.clear_list_widgets([self.ui.list_widget_edit_xpath_expressions, self.ui.list_widget_edit_csv_headers])
                    # Update autofill menubar
                    self.main_window._update_autofill_menu()
                except TypeError as te:
                    QMessageBox.critical(self, "TypeError occurred", f"Error message: {str(te)}")
                    return

        except Exception as ex:
            QMessageBox.critical(self, "Error while trying to delete config",
                f"An error has occurred while trying to delete the custom config: {str(ex)}")
            
    # ========================================================================================== 
                
    # ===== Remove buttons events =====
    
    @Slot()
    def onRemoveSelected(self) -> None:
        # Check all list widgets for a selected item
        list_of_widgets = [self.ui.list_widget_xpath_expressions, 
                        self.ui.list_widget_csv_headers, 
                        self.ui.list_widget_edit_xpath_expressions, 
                        self.ui.list_widget_edit_csv_headers]
        
        for lw in list_of_widgets:
            current_row = lw.currentRow()
            if current_row != -1:
                lw.takeItem(current_row)
                return  # remove only one item per click

        # If no item is selected
        QMessageBox.information(self, "No selection", "Please select an item to remove.")

    @Slot()
    def onRemoveAll(self):
        # 3. Use the stored active_list_widget
        list_to_clear = self.active_list_widget

        if list_to_clear and list_to_clear.count() > 0:
            reply = QMessageBox.question(self, "Confirm Remove All",
                                         f"Are you sure you want to remove all {list_to_clear.count()} items from this list?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                list_to_clear.clear()

        elif list_to_clear and list_to_clear.count() == 0:
            QMessageBox.information(
                self, "List is empty", "The selected list is already empty."
            )

        else:
            QMessageBox.information(
                self, "No List Selected", 
                "Please click on an item in the list you wish to clear before clicking 'Remove All'."
            )

    # ===== Helper Methods =====
    
    @Slot(list)
    def clear_list_widgets(self, list_of_widgets_to_clear: list) -> None:
        """A list of widgets which should be cleared."""
        for widget in list_of_widgets_to_clear:
            widget.clear()
    
    @Slot()
    def update_combobox(self, config_name: str):
        """Updated the combobox in the custom paths manager combobox by re-loading the config file again.
        """
        self.ui.combobox_xpath_configs.clear()
        # *** Dynamic usage: Get keys of the nested section ***
        config_file_values = self.config_handler.get_all_keys(config_name)
        if config_file_values:
            self.ui.combobox_xpath_configs.addItems(config_file_values)
    
    # A widget input validator
    def _validate_inputs(self, widgets_to_validate: list) -> bool:
        """Validate that QLineEdit and QListWidget inputs are not empty."""

        list_widgets = []

        for widget in widgets_to_validate:
            if isinstance(widget, QLineEdit):
                if not widget.text().strip():
                    QMessageBox.warning(
                        self, "Input validation failed!",
                        "Please set a name for the configuration."
                    )
                    return False
            elif isinstance(widget, QListWidget):
                list_widgets.append(widget)
            else:
                QMessageBox.warning(
                    self, "Input validation failed!",
                    f"Unsupported widget type: {type(widget).__name__}"
                )
                return False    

        # Check QListWidgets
        if list_widgets:
            lengths = [w.count() for w in list_widgets]
            if len(set(lengths)) != 1:  # not same length
                QMessageBox.warning(
                    self, "Input validation failed!",
                    "All lists must have the same number of items."
                )
                return False
            if any(l == 0 for l in lengths):  # no empty lists
                QMessageBox.warning(
                    self, "Input validation failed!",
                    "Please add at least one item to each list."
                )
                return False    

        return True
    
    def _listwidget_to_list(self, widget: QListWidget) -> list[str]:
        """Helper method to convert QItems from a specified QListWidget to a list of strings.

        Args:
            widget (QListWidget): The specified list widget.

        Returns:
            list[str]: Returns a list of QItems from a QListWidget as strings.
        """
        return [widget.item(i).text() for i in range(widget.count())]
    
    def _is_duplicate(self, text: str, list_to_check: list) -> bool:
        """Checks if string to add to a QListWidget is not already in. Prevents from adding same duplicate strings to QListWidget.

        Args:
            text (str): String from the QLineEdit widget.
            list_to_check (list): A list that contains all the user added strings.

        Returns:
            bool: Returns True if string already exists in the list_to_check list, else False.
        """
        return text in list_to_check

    def _add_items_to_list_widget(self, item: str, list_widget: QListWidget):
        """Adds the strings to the specified QListWidget.

        Args:
            item (str): The string that will be added to the list widget.
            list_widget (QListWidget): The list widget that strings will be added to.
        """
        if item == "":
            QMessageBox.information(self, "Empty String", "Please enter a string that you want to add to the list.")
            return
        if item and not self._is_duplicate(item, self._listwidget_to_list(list_widget)):
            list_widget.addItem(QListWidgetItem(item))
        else:
            QMessageBox.warning(self, "Duplicate string in list", f"Cannot add duplicate string '{item}' into list:")
            
    # Close event
    def closeEvent(self, event: QCloseEvent):
        # Always update autofill menu
        self.main_window._update_autofill_menu()