from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu,QFileDialog, QMessageBox, QInputDialog)
from PySide6.QtGui import QIcon, QAction, QCloseEvent
from PySide6.QtCore import Qt, Signal, Slot, QFile, QTextStream, QSettings, QThreadPool

import sys
import os
import webbrowser
import multiprocessing
from functools import partial

from utils.config_handler import ConfigHandler
from utils.xml_parser import (XMLUtils, 
    create_xml_parser, create_structure_analyzer
)
from utils.xpath_builder import create_xpath_builder, create_xpath_validator
from utils.csv_export import CSVExportThread
from gui.logic.controller import ComboBoxStateController, CSVConversionController

from gui.resources.ui.XMLuvation_ui import Ui_MainWindow

# Path Constants

ConfigHandler.print_file_path(ConfigHandler())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE_PATH: str = os.path.join("src","gui","logs","xmluvation.log")
GUI_CONFIG_FILE_PATH: str = os.path.join("src","gui","config","config.json")
DARK_THEME_PATH = os.path.join(BASE_DIR, "resources", "themes", "dark_theme.qss")
LIGHT_THEME_PATH = os.path.join(BASE_DIR, "resources", "themes", "light_theme.qss")
ICON_PATH = os.path.join(BASE_DIR, "resources", "icons", "xml_256px.ico")
DARK_THEME_QMENU_ICON = os.path.join(BASE_DIR, "resources", "images", "dark.png")
LIGHT_THEME_QMENU_ICON = os.path.join(BASE_DIR, "resources", "images", "light.png")

# Resource and UI Paths
UI_FILE_NAME: str = os.path.join("gui", "resources", "ui", "XMLuvation.ui")
UI_RESOURCES: str = os.path.join("gui", "resources", "qrc", "xmluvation_resources.qrc")

# App related constants
APP_VERSION: str = "v1.3.1"

def initialize_theme(parent, theme_file):
    try:
        file = QFile(theme_file)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            stylesheet = stream.readAll()
            parent.setStyleSheet(stylesheet)
        file.close()
    except Exception as ex:
        QMessageBox.critical(parent, "Theme load error", f"Failed to load theme: {str(ex)}")


class MainWindow(QMainWindow):
    progress_updated = Signal(int)
    update_input_file_signal = Signal(str)
    update_output_file_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        self.current_read_xml_file = None
        
        # Create and setup the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Set window title with version
        self.setWindowTitle(f"XMLuvation {APP_VERSION}")
        
        # XML Data
        self.parsed_xml_data = {}
        
        # Instantiate the controller with a reference to the MainWindow
        self.cb_state_controller = ComboBoxStateController(self, self.parsed_xml_data)
        
        # Settings file for storing application settings
        self.settings = QSettings("Jovan", "XMLuvation")
        
        # Window geometry restoration
        geometry = self.settings.value("geometry", bytes())
        if geometry:
            self.restoreGeometry(geometry)
        
        #  Initialize the QThreadPool for running threads
        self.thread_pool = QThreadPool()
        max_threads = self.thread_pool.maxThreadCount() # PC's max CPU threads (I have 32 Threads on a Ryzen 9 7950X3D)
        
        # Keep track of active workers (optional, for cleanup)
        self.active_workers = []
        
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.config_handler = ConfigHandler()
        
        self.xpath_filters = []
        
        # Connect the custom context menu for Listbox
        self.ui.list_widget_xpath_expressions.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.list_widget_xpath_expressions.customContextMenuRequested.connect(self.show_context_menu)
        
        # Theme Icons in QMenu
        self.light_mode_icon = QIcon(LIGHT_THEME_QMENU_ICON)
        self.dark_mode_icon = QIcon(DARK_THEME_QMENU_ICON)

        # Theme files qss
        self.dark_theme_file = DARK_THEME_PATH
        self.light_theme_file = LIGHT_THEME_PATH
        
        # Load last used theme or default
        self.current_theme = self.settings.value("app_theme", "dark_theme.qss")
        
        # Apply theme and correct icon
        if self.current_theme == "dark_theme.qss":
            self.theme_icon = self.light_mode_icon
            initialize_theme(self, self.dark_theme_file)
        else:
            self.theme_icon = self.dark_mode_icon
            initialize_theme(self, self.light_theme_file)
        
        # Setup connections and initialize components
        self.setup_connections()
        
        # Create my custom menu bar
        self.create_menu_bar()
    
        self.print_widget_status()
        
        # Check thread pool status
        status = self.get_thread_pool_status()
        print(status) 
        
# ====================================================================================================================== #
# === Menubar, Menubar Control and UI Events === #
    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self, 'Exit Program', 'Are you sure you want to exit the program?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        if reply == QMessageBox.No:
            event.ignore()
            return
        else:
            self.settings.setValue("app_theme", self.current_theme)
            self.settings.setValue("geometry", self.saveGeometry())
            super().closeEvent(event)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        clear_action = QAction("Clear Output", self)
        clear_action.setStatusTip("Clear the output")
        clear_action.triggered.connect(self.clear_output)
        file_menu.addAction(clear_action)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Open Menu
        open_menu = menu_bar.addMenu("&Open")
        open_input_action = QAction("Open XML Input Folder", self)
        open_input_action.setStatusTip("Open the XML input folder")
        open_input_action.triggered.connect(lambda: self.open_folder_in_file_explorer(self.ui.line_edit_xml_folder_path_input.text()))
        open_menu.addAction(open_input_action)
        open_output_action = QAction("Open CSV Output Folder", self)
        open_output_action.setStatusTip("Open the CSV output folder")
        open_output_action.triggered.connect(lambda: self.open_folder_in_file_explorer(self.ui.line_edit_csv_output_path.text()))
        open_menu.addAction(open_output_action)
        open_menu.addSeparator()
        open_csv_conversion_input_action = QAction("Open CSV Conversion Input Folder", self)
        open_csv_conversion_input_action.setStatusTip("Open CSV Conversion Input Folder")
        open_csv_conversion_input_action.triggered.connect(lambda: self.open_folder_in_file_explorer(self.ui.line_edit_csv_conversion_path_input.text()))
        open_menu.addAction(open_csv_conversion_input_action)
        open_csv_conversion_output_action = QAction("Open CSV Conversion Output Folder", self)
        open_csv_conversion_output_action.setStatusTip("Open CSV Conversion Output Folder")
        open_csv_conversion_output_action.triggered.connect(lambda: self.open_folder_in_file_explorer(self.ui.line_edit_csv_conversion_path_output.text()))
        open_menu.addAction(open_csv_conversion_output_action)

        # Path Menu
        self.paths_menu = menu_bar.addMenu("&Path")
        
        # Add custom paths
        self.load_custom_paths()

        # Add option to add new custom path
        add_custom_path_action = QAction("Add Custom Path", self)
        add_custom_path_action.triggered.connect(self.add_custom_path)
        self.paths_menu.addAction(add_custom_path_action)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        xpath_help_action = QAction("XPath Help", self)
        xpath_help_action.setStatusTip("Open XPath Syntax Help")
        xpath_help_action.triggered.connect(self.open_web_xpath_help)
        help_menu.addAction(xpath_help_action)
        about = QAction("About", self)
        about.setStatusTip("About this program")
        about.triggered.connect(self.about_message)
        help_menu.addAction(about)
        #help_menu.addAction(xpath_cheatsheet_action)
        
        # Theme Menu
        self.toggle_theme_action = menu_bar.addAction(self.theme_icon, "Toggle Theme")
        self.toggle_theme_action.triggered.connect(self.change_theme)
        
    # ======= START FUNCTIONS create_menu_bar ======= #

    def update_paths_menu(self):
        # Clear existing path actions, except the last one (Add Custom Path)
        for action in self.paths_menu.actions()[:-1]:
            self.paths_menu.removeAction(action)

        # Add custom paths
        custom_paths = self.config_handler.get_custom_paths()
        for name, path in custom_paths.items():
            action = QAction(name, self)
            action.setStatusTip(f"Open {name}")
            action.triggered.connect(lambda checked, p=path: self.open_path(p))
            self.paths_menu.insertAction(self.paths_menu.actions()[0], action)

    def add_custom_path(self):
        name, ok = QInputDialog.getText(self, "Add Custom Path", "Enter a name for the path:")
        if ok and name:
            path, ok = QInputDialog.getText(self, "Add Custom Path", "Enter path:")
            if ok and path:
                self.config_handler.add_custom_path(name, path)
                self.update_paths_menu()

    def load_custom_paths(self):
        custom_paths = self.config_handler.get_custom_paths()
        for name, path in custom_paths.items():
            action = QAction(name, self)
            action.setStatusTip(f"Open {name}")
            action.triggered.connect(lambda checked, p=path: self.open_path(p))
            self.paths_menu.addAction(action)

    def about_message(self):
        # About Message
        program_info = "Name: XMLuvation\nVersion: 1.3.1\nCredit: Jovan\nFramework: PySide6"
        about_message = """XMLuvation is a Python application designed to parse and evaluate XML files and use XPath to search for matches which matching results will be saved in a csv file."""
        about_box = QMessageBox()
        about_box.setText("About this program...")
        about_box.setInformativeText(about_message)
        about_box.setDetailedText(program_info)
        about_box.exec()

    def change_theme(self):
        if self.current_theme == "dark_theme.qss":
            self.toggle_theme_action.setIcon(self.dark_mode_icon)
            initialize_theme(self, self.light_theme_file)
            self.current_theme = "light_theme.qss"
            self.current_theme_icon = "light.png"
        else:
            self.toggle_theme_action.setIcon(self.light_mode_icon)
            initialize_theme(self, self.dark_theme_file)
            self.current_theme = "dark_theme.qss"
            self.current_theme_icon = "dark.png"

    def clear_output(self):
        self.ui.text_edit_program_output.clear()

    def open_folder_in_file_explorer(self, folder_path):
        """Helper method to open the specified folder in the file explorer."""
        if os.path.exists(folder_path):
            try:
                os.startfile(folder_path)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "An exception occurred", message)
        else:
            QMessageBox.warning(self, "Error", f"Path does not exist or is not a valid path:\n{folder_path}")

    def open_web_xpath_help(self):
        webbrowser.open("https://www.w3schools.com/xml/xpath_syntax.asp")

# ====================================================================================================================== #

    # Setup UI Widget Actions
    def setup_connections(self):
        """Setup all signal-slot connections"""
        
        # === XML TAB - Direct widget access via self.ui ===
        
        # QLineWdigets
        
        self.ui.line_edit_xml_folder_path_input.textChanged.connect(self.update_xml_file_count) 
        
        # Folder browsing and XML reading
        self.ui.button_browse_xml_folder.clicked.connect(lambda: self.browse_folder_helper(dialog_message="Select directory that contains XML files", line_widget= self.ui.line_edit_xml_folder_path_input))
        self.ui.button_read_xml.clicked.connect(self.read_xml_file)
        
        # File browsing for csv evaluation export
        self.ui.button_browse_csv.clicked.connect(lambda: self.browse_folder_helper(dialog_message="Select csv evaluation export path", line_widget=self.ui.line_edit_csv_output_path))
        
        # XPath building
        #self.ui.line_edit_xpath_builder
        self.ui.button_build_xpath.clicked.connect(self.start_build_xpath_expression)
        self.ui.button_add_xpath_to_list.clicked.connect(self.add_xpath_to_list)
        
        # CSV export
        #self.ui.button_browse_csv.clicked.connect(self.browse_csv_output)
        #self.ui.button_export_csv.clicked.connect(self.export_to_csv)
        
        # Combo boxes
        self.ui.combobox_tag_names.currentTextChanged.connect(self.cb_state_controller.on_tag_name_changed)
        self.ui.combobox_attribute_names.currentTextChanged.connect(self.cb_state_controller.on_attribute_name_changed)
        
        # Radio buttons
        self.ui.radio_button_equals.toggled.connect(lambda checked: self.on_function_changed("equals", checked))
        self.ui.radio_button_contains.toggled.connect(lambda checked: self.on_function_changed("contains", checked))
        self.ui.radio_button_starts_with.toggled.connect(lambda checked: self.on_function_changed("starts_with", checked))
        self.ui.radio_button_greater.toggled.connect(lambda checked: self.on_function_changed("greater", checked))
        self.ui.radio_button_smaller.toggled.connect(lambda checked: self.on_function_changed("smaller", checked))
        
        # List widget
        self.ui.list_widget_xpath_expressions.itemClicked.connect(self.on_xpath_item_clicked)
        
        # Tab widget
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)
        
        # === CSV TAB ===
        self.ui.button_browse_csv_conversion_path_input.clicked.connect(lambda: self.browse_file_helper(dialog_message="Select csv file for conversion", line_widget=self.ui.line_edit_csv_conversion_path_input, file_extension_filter="CSV File (*.csv)"))
        self.ui.button_browse_csv_conversion_path_output.clicked.connect(lambda: self.browse_save_file_as_helper(dialog_message="Save as", line_widget=self.ui.line_edit_csv_conversion_path_output, file_extension_filter="Excel file (*.xlsx);;JSON file (*.json);;Markdown file (*.md);;HTML file (*.html)"))
        self.ui.button_csv_conversion_convert.clicked.connect(self.csv_convert)
        self.ui.checkbox_write_index_column.toggled.connect(self.on_write_index_toggled)
        
    # === Helper Methods === #
    def browse_folder_helper(self, dialog_message:str, line_widget:object) -> None:
        """File dialog for folder browsing, sets the path of the selected folder in a specified QLineEdit Widget

        Args:
            dialog_message (str): Title message for the QFileDialog to display 
            line_widget (object): The QLineEdit Widget to write to the path value as string
        """
        try:
            folder = QFileDialog.getExistingDirectory(self, dialog_message)
            if folder:
                # Set the file path in the QLineEdit Widget
                line_widget.setText(folder)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred in browse folder method", message)
            
    
    def browse_file_helper(self, dialog_message:str, line_widget:object, file_extension_filter:str) -> None:
        """File dialog for file browsing, sets the path of the selected file in a specified QLineEdit Widget

        Args:
            dialog_message (str): Title message for the QFileDialog to display
            line_widget (object): The QLineEdit Widget to write to the path value as string
            file_extension_filter (str): Filter files for selection based on set filter. 
            
                - Example for only xml files: 
                    - 'XML File (*.xml)'
                    
                    
                - Example for multiple filters:
                    - 'Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)'
        """
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, caption=dialog_message, filter=file_extension_filter)
            if file_name:
                line_widget.setText(file_name) # Set the file path in the QLineEditWidget
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred in browse folder method", message)
    
    def browse_save_file_as_helper(self, dialog_message:str, line_widget:object, file_extension_filter:str) -> None:
        """File dialog for file saving as, sets the path of the selected file in a specified QLineEdit Widget

        Args:
            dialog_message (str): Title message for the QFileDialog to display
            line_widget (object): The QLineEdit Widget to write to the path value as string
            file_extension_filter (str): Filter files for selection based on set filter. 
            
                - Example for only xml files: 
                    - 'XML File (*.xml)'
                    
                    
                - Example for multiple filters:
                    - 'Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)'
        """
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, caption=dialog_message, filter=file_extension_filter)
            if file_name:
                line_widget.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred in browse save file method", f"Error exporting CSV: {message}")
    
# ====================================================================================================================== #

    # === XPATH BUILDING HANDLER VIA BUTTON EVENT === #
    def start_build_xpath_expression(self):
        """Build XPath expression based on selected combobox values."""
        try:
            builder = create_xpath_builder() # XPathBuilder Instance

            # Assign UI references
            builder.tag_name_combo = self.ui.combobox_tag_names
            builder.tag_value_combo = self.ui.combobox_tag_values
            builder.attribute_name_combo = self.ui.combobox_attribute_names
            builder.attribute_value_combo = self.ui.combobox_attribute_values
            builder.xpath_input = self.ui.line_edit_xpath_builder

            # Assign radio buttons
            builder.radio_equals = self.ui.radio_button_equals
            builder.radio_contains = self.ui.radio_button_contains
            builder.radio_starts_with = self.ui.radio_button_starts_with
            builder.radio_greater = self.ui.radio_button_greater
            builder.radio_smaller = self.ui.radio_button_smaller

            # Connect signals
            self._connect_xpath_builder_signals(builder)

            # Build expression
            xpath_expression = builder.build_xpath_expression()
            # Add built XPath Expression to the QLineEdit Widget for the XPath
            self.ui.line_edit_xpath_builder.setText(xpath_expression)
            
        except Exception as ex:
            self.on_error_message("Error building XPath expression", str(ex))
    
    # === QListWidget HANDLER ===
    def add_xpath_to_list(self):
        """Add the entered or built XPath expression from the QLineEdit to the QListWidget for later searching
        
        Has a built in XPath validator before adding the XPath to the QListWidget
        """
        print("Add XPath to list clicked")
        try:
            # Check if the XPath input is not empty:
            expression = self.ui.line_edit_xpath_builder.text().strip()
            if not expression: 
                QMessageBox.information(self, "Empty XPath", "Please enter a valid XPath expression before adding it to the list.")
            elif expression and not self.is_duplicate(expression):
                validator = create_xpath_validator()
                self._connect_xpath_builder_signals(validator)
                # Validate the XPath expression
                validator.xpath_expression = expression
                is_valid = validator.validate_xpath_expression()
                if is_valid:
                    self.xpath_filters.append(expression)
                    self.ui.list_widget_xpath_expressions.addItem(expression)
            else:
                QMessageBox.warning(self, "Duplicate XPath Expression", f"Cannot add duplicate XPath expression:\n{expression}")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception adding XPath Expression to List Widget", message)


    def on_function_changed(self, function_type, checked):
        if checked:
            print(f"Function changed to: {function_type}")
    
    
    def on_xpath_item_clicked(self, item):
        print(f"XPath item clicked: {item.text()}")
    
    
    def on_tab_changed(self, index):
        print(f"Tab changed to index: {index}")
    
    
    def csv_browse_input(self):
        print("CSV browse input clicked")
        # Set CSV input path:
        # self.ui.lineEdit.setText("path/to/input.csv")
    
    
    def csv_browse_output(self):
        print("CSV browse output clicked")
        # Set CSV output path:
        # self.ui.lineEdit_2.setText("path/to/output")
    
    
    def csv_convert(self):
        print("CSV convert clicked")
        # Initialized object 
        self.csv_conversion_controller = CSVConversionController(self)
        self.csv_conversion_controller.start_csv_conversion()
    
    
    def on_write_index_toggled(self, checked):
        print(f"Write index column: {checked}")
        message_with_index = """
        Data will look like  this:
        
        | Index           | Header 1   | Header 2    |
        |-------------------|-------------------|-------------------|
        | 1                  | Data...         | Data...        |
        """
        message_without_index = """
        Data will look like  this:
        
        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Data...         |
        """
        try:
            if self.ui.checkbox_write_index_column.isChecked():
                self.ui.text_edit_csv_conversion_output.setText(message_with_index)
            else:
                self.ui.text_edit_csv_conversion_output.setText(message_without_index)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", f"An error occurred: {message}")

    # === EVENT HANDLERS FOR QMessageBoxes === #
    
    @Slot(str, str) # QMessageBox.critical type shit
    def on_error_message(self, title, message):
        """Show critical message dialog."""
        QMessageBox.critical(self, title, message)
    
    @Slot(str, str) # QMessageBox.information type shit
    def on_info_message(self, title, message):
        """Show information message dialog."""
        QMessageBox.information(self, title, message)
        
    @Slot(str, str) # QMessageBox.warning type shit
    def show_warning_message(self, title, message):
        """Show warning message dialog."""
        QMessageBox.warning(self, title, message)
        
    # === END EVENT HANDLERS FOR QMessageBoxes END === #
    
    # === EVENT HANDLER FOR QTextEdit MAIN PROGRAM OUTPUT === #
    
    @Slot(str)
    def append_to_program_output(self, message:str):
        """Handle QTextEdit progress updates with .append() in any class, does the QTextEdit.append("hello world").
        
        Args:
            message (str): Message to send to the QTextEdit Widget
        """
        self.ui.text_edit_program_output.append(message)
        
    @Slot(str)
    def set_text_to_program_output(self, message:str):
        """Handle QTextEdit progress updates with .setText() in any class, does the QTextEdit.setText("hello world")

        Args:
            message (str): Message to send to the QTextEdit Widget
        """
        self.ui.text_edit_program_output.setText(message)

    # === END EVENT HANDLER FOR QTextEdit MAIN PROGRAM OUTPUT END === #
    
    # === EVENT HANDLERS FOR XML EVALUATION GROUPBOX ===
    
    # === XML PARSING EVENT TRIGGER BUTTON === #
    def read_xml_file(self):
        print("Read XML files clicked")
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select XML File", "", "XML File (*.xml)")
            if file_name:
                self.start_xml_parsing(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", message)
    
    # === XML PARSING === #
    def start_xml_parsing(self, xml_file_path: str):
        """Parse XML file and display content."""
        try:
            xml_parser_worker = create_xml_parser(xml_file_path)
            self._connect_xml_parsing_signals(xml_parser_worker)
            self.thread_pool.start(xml_parser_worker)
            
            # Optional: Keep track of the worker
            self.active_workers.append(xml_parser_worker)
        except Exception as ex:
            self.on_error_message("Error starting XML parsing", ex)

    # === XML PARSING ON FINISHED SLOT === #
    @Slot(dict)
    def on_xml_parsing_finished(self, result: dict):
        """Handle XML parsing completion."""
        try:
            xml_content = result.get('xml_string', '')
            self.ui.text_edit_xml_output.setPlainText(xml_content)
            
            # Fill the combo boxes with unique tags and attributes
            tags = result.get('tags', [])
            attributes = result.get('attributes', [])
            
            tag_values = result.get('tag_values', [])
            attribute_values = result.get('attribute_values', [])
            
            self.ui.combobox_tag_names.clear()
            self.ui.combobox_tag_names.addItems(tags)
            self.ui.combobox_attribute_names.clear()
            self.ui.combobox_attribute_names.addItems(attributes)
            
            self.ui.combobox_tag_values.clear()
            self.ui.combobox_tag_values.addItems(tag_values)
            self.ui.combobox_attribute_values.clear()
            self.ui.combobox_attribute_values.addItems(attribute_values)
            
            # Enable ComboBoxes
            self.ui.combobox_tag_names.setDisabled(False)
            self.ui.combobox_attribute_names.setDisabled(False)
            self.ui.combobox_tag_values.setDisabled(False)
            self.ui.combobox_attribute_values.setDisabled(False)
            
            # Display additional info
            info_message = f"File: {result.get('file_path', 'Unknown')}\n"
            info_message += f"Root element: {result.get('root_tag', 'Unknown')}\n"
            info_message += f"Total elements: {result.get('element_count', 0)}\n"
            info_message += f"Unique tags: {len(result.get('tags', []))}\n"
            info_message += f"Encoding: {result.get('encoding', 'Unknown')}"
            
            # Save xml file in initialized variable
            self.current_read_xml_file = result.get("file_path")
            
            #self.on_info_message("Parsing Complete", info_message) # QMessageBox info popup
            self.ui.text_edit_program_output.append(info_message)
            
            self.parsed_xml_data = result
            # Pass the new result data (the xml data as dict) to the ComboBoxStateController class
            self.cb_state_controller.set_parsed_data(result)
            
        except Exception as ex:
            self.on_error_message(ex, "Error processing parsing results")
            
    # Statusbar update function
    def update_xml_file_count(self):
        """Updated the current XML Files found in the selected folder from  QLineEdit' line_edit_xml_folder_path_input'
        """
        try:
            folder: str = self.ui.line_edit_xml_folder_path_input.text()
            if os.path.isdir(folder):
                xml_files_count: int = sum(1 for f in os.listdir(folder) if f.endswith(".xml"))
                if xml_files_count > 1:
                    self.ui.statusbar_xml_files_count.setStyleSheet("color: #47de65")
                    self.ui.statusbar_xml_files_count.showMessage(f"Found {xml_files_count} XML Files")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.statusbar_xml_files_count.setStyleSheet("color: #ed2828")
            self.ui.statusbar_xml_files_count.showMessage(f"Error counting XML files: {message}")
    
    # === CSV Exporting Process === #
    

    # === SIGNAL CONNECTION HELPERS === #
    
    def _connect_xml_parsing_signals(self, worker):
        """Connect common signals for most operations.
        """
        worker.signals.finished.connect(self.on_xml_parsing_finished)
        worker.signals.error_occurred.connect(self.on_error_message)
        worker.signals.progress.connect(self.append_to_program_output)


    def _connect_xpath_builder_signals(self, worker):
        """Connect signals for XPath building operations."""
        worker.signals.progress.connect(self.append_to_program_output)
        worker.signals.error_occurred.connect(self.on_error_message)
    
    
    def _connect_csv_export_signals(self, worker):
        pass
    
    # === END SIGNAL CONNECTION HELPERS END === #
        
    # ======= END FUNCTIONS create_menu_bar ======= #

    # ======= Start FUNCTIONS FOR create_matching_filter_group ======= #

    def update_statusbar_xpath_listbox_count(self):
        self.counter = self.ui.list_widget_xpath_expressions.count()
        if self.counter != 0:
            self.ui.statusbar_xpath_expressions.showMessage(f"Total number of items in List: {self.counter}", 5000)
        
    
    def remove_selected_items(self):
        """Removes the selected item that has been added to the QListWidget and the xpath_filters list
        """
        try:
            current_selected_item = self.ui.list_widget_xpath_expressions.currentRow()
            if current_selected_item != -1:
                item_to_remove = self.ui.list_widget_xpath_expressions.takeItem(current_selected_item)
                self.xpath_filters.pop(current_selected_item)
                self.ui.text_edit_program_output.append(f"Removed item: {item_to_remove.text()} at row {current_selected_item}")
            else:
                self.ui.text_edit_program_output.append("No item selected to delete.")
        except IndexError:
            self.ui.text_edit_program_output.append("Nothing to delete.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.text_edit_program_output.setText(f"Error removing selected item from list: {message}")


    def remove_all_items(self):
        """Removes all items that have been added to the QListWidget and the xpath_filters list
        """
        try:
            if self.ui.list_widget_xpath_expressions.count() > 0:
                self.xpath_filters.clear()
                self.ui.list_widget_xpath_expressions.clear()
                self.ui.text_edit_program_output.setText("Deleted all items from the list.")
            else:
                self.ui.text_edit_program_output.setText("No items to delete.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.text_edit_program_output.setText(f"Error removing selected all items from list: {message}")


    def show_context_menu(self, position):
        context_menu = QMenu(self)
        delete_action = QAction("Delete Selected", self)
        delete_all_action = QAction("Delete All", self)

        context_menu.addAction(delete_action)
        context_menu.addAction(delete_all_action)

        delete_action.triggered.connect(self.remove_selected_items)
        delete_all_action.triggered.connect(self.remove_all_items)

        # Show the context menu at the cursor's current position
        context_menu.exec(self.ui.list_widget_xpath_expressions.mapToGlobal(position))


    def is_duplicate(self, xpath_expression):
        """Checks if the XPath expressions is a duplicate. Prevents of adding same XPath expressions to QListWidget

        Args:
            xpath_expression (str): XPath expression from the QLineEdit widget (line_edit_xpath_builder)

        Returns:
            bool: If XPath expression already exists in xpath_filters list, returns True if it exists, else False.
        """
        return xpath_expression in self.xpath_filters
    
    def start_csv_export(self, folder_path: str, xpath_expressions: list, output_csv_path: str):
        """Initializes and starts the CSV export in a new thread."""
        if not hasattr(self, 'csv_export_thread') or not self.csv_export_thread.isRunning():
            self.csv_export_thread = QThread()
            self.csv_export_worker = CSVExportThread(
                folder_path=folder_path,
                xpath_expressions=xpath_expressions,
                output_csv_path=output_csv_path
            )
            self.csv_export_worker.moveToThread(self.csv_export_thread)#

            self.csv_export_thread.started.connect(self.csv_export_worker.run)#

            # Connect worker signals to main window slots
            self.csv_export_worker.output_set_text.connect(self.output_set_text)
            self.csv_export_worker.progress_updated.connect(self.update_progress_bar)
            self.csv_export_worker.finished.connect(self.on_csv_export_finished)
            self.csv_export_worker.show_error_message.connect(self.show_error_message)
            self.csv_export_worker.show_info_message.connect(self.show_info_message)#

            # Connect for cleanup
            self.csv_export_worker.finished.connect(self.csv_export_thread.quit)
            self.csv_export_worker.finished.connect(self.csv_export_worker.deleteLater)
            self.csv_export_thread.finished.connect(self.csv_export_thread.deleteLater)#

            self.csv_export_thread.start()
        else:
            self.program_output.setText("CSV export is already running or thread is busy.")


    # ======= End FUNCTIONS FOR create_matching_filter_group ======= #

#    def stop_csv_export_thread(self):
#        if hasattr(self, "csv_export_worker"):
#            self.csv_export_worker.stop()
#            self.program_output.setText("Export task aborted successfully.")
        
    
   # @Slot()
   # def on_csv_export_finished(self):
   #     self.csv_export_thread = None # Clear reference after use
   #     self.csv_export_worker = None # Clear reference
   #     self.set_ui_enabled(False)
   #     self.progressbar.reset()
   #     self.csv_abort_export_button.setHidden(True)

    
    def set_ui_enabled(self, enabled):
        # Disable buttons while exporting
        self.ui.button_browse_xml_folder.setDisabled(enabled)
        self.ui.button_browse_csv.setDisabled(enabled)
        self.ui.button_read_xml.setDisabled(enabled)
        self.ui.button_build_xpath.setDisabled(enabled)
        self.ui.button_add_xpath_to_list.setDisabled(enabled)
        self.ui.button_browse_csv_conversion_path_input.setDisabled(enabled)
        self.ui.button_browse_csv_conversion_path_output.setDisabled(enabled)
        self.ui.line_edit_xml_folder_path_input.setReadOnly(enabled)
        self.ui.line_edit_csv_output_path.setReadOnly(enabled)
        
    # ======= End FUNCTIONS FOR create_export_evaluation_group ======= #
    

    def print_widget_status(self):
        """Print which widgets were successfully found"""
        print("=== XMLuvation UI Widgets Status ===")
        print(f"XML Folder Input: {'✓' if self.ui.line_edit_xml_folder_path_input else '✗'}")
        print(f"Browse Button: {'✓' if self.ui.button_browse_xml_folder else '✗'}")
        print(f"Read XML Button: {'✓' if self.ui.button_read_xml else '✗'}")
        print(f"CSV Output Path: {'✓' if self.ui.line_edit_csv_output_path else '✗'}")
        print(f"Browse CSV Output Button: {'✓' if self.ui.button_browse_csv else '✗'}")
        print(f"Export CSV Button: {'✓' if self.ui.button_start_csv_export else '✗'}")
        print(f"Button CSV Conversion Input: {'✓' if self.ui.button_browse_csv_conversion_path_input else '✗'}")
        print(f"Button CSV Conversion Output: {'✓' if self.ui.button_browse_csv_conversion_path_output else '✗'}")
        print(f"Button CSV Conversion Convert: {'✓' if self.ui.button_csv_conversion_convert else '✗'}")
        print(f"Tag Names Combo: {'✓' if self.ui.combobox_tag_names else '✗'}")
        print(f"Tag Values Combo: {'✓' if self.ui.combobox_tag_values else '✗'}")
        print(f"Attribute Names Combo: {'✓' if self.ui.combobox_attribute_names else '✗'}")
        print(f"Attribute Values Combo: {'✓' if self.ui.combobox_attribute_values else '✗'}")
        print(f"XPath Builder Input: {'✓' if self.ui.line_edit_xpath_builder else '✗'}")
        print(f"Build XPath Button: {'✓' if self.ui.button_build_xpath else '✗'}")
        print(f"XPath List Widget: {'✓' if self.ui.list_widget_xpath_expressions else '✗'}")
        print(f"Progress Bar: {'✓' if self.ui.progressbar_main else '✗'}")
        print(f"Program Output: {'✓' if self.ui.text_edit_program_output else '✗'}")
        print(f"XML Output: {'✓' if self.ui.text_edit_xml_output else '✗'}")
        print("=====================================")
    
    def get_thread_pool_status(self):
        """Get current thread pool status (useful for debugging)."""
        active_count = self.thread_pool.activeThreadCount()
        max_count = self.thread_pool.maxThreadCount()
        return f"Active threads: {active_count}/{max_count}"

if __name__ == "__main__":
    # Initialize the application
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    
    # No more QUiLoader needed! Just create the MainWindow directly
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
