from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QFileDialog, QMessageBox, QInputDialog, QLineEdit)
from PySide6.QtGui import QIcon, QAction, QCloseEvent, QShortcut, QKeySequence
from PySide6.QtCore import Qt, Signal, Slot, QFile, QTextStream, QIODevice, QSettings, QThreadPool

import sys
import os
import webbrowser

from typing import List

from modules.config_handler import ConfigHandler
from modules.xml_parser import apply_xml_highlighting_to_widget, set_xml_content_to_widget

from controller import ComboboxStateHandler, CSVConversionHandler, AddXPathExpressionToListHandler, \
    SearchAndExportToCSVHandler, GenerateCSVHeaderHandler, LobsterProfileExportCleanupHandler, ParseXMLFileHandler, \
    XPathBuildHandler, CSVColumnDropHandler, SearchXMLOutputTextHandler
from widget.path_manager import CustomPathsManager

from resources.ui.XMLuvation_ui import Ui_MainWindow

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Check if the application is running in a PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in a PyInstaller bundle, BASE_DIR points to the bundle's root
    ROOT_DIR: str = sys._MEIPASS
else:
    # Running in a normal Python environment
    ROOT_DIR: str = os.path.dirname(CURRENT_DIR)
    # At work it's C:\Users\ZaricJ\Documents\Main\02_Entwicklung_und_Tools\GitHub\XMLuvation\src


# Path Constants
# LOG_FILE_PATH: str = os.path.join(ROOT_DIR, "logs","xmluvation.log")
GUI_CONFIG_FILE_PATH: str = os.path.join(CURRENT_DIR, "config", "config.json")
GUI_CONFIG_DIRECTORY: str = os.path.join(CURRENT_DIR, "config")
DARK_THEME_PATH: str = os.path.join(CURRENT_DIR, "resources", "themes", "dark_theme.qss")
LIGHT_THEME_PATH: str = os.path.join(CURRENT_DIR, "resources", "themes", "light_theme.qss")
ICON_PATH: str = os.path.join(CURRENT_DIR, "resources", "icons", "xml_256px.ico")
DARK_THEME_QMENU_ICON: str = os.path.join(CURRENT_DIR, "resources", "images", "dark.png")
LIGHT_THEME_QMENU_ICON: str = os.path.join(CURRENT_DIR, "resources", "images", "light.png")


# App related constants
APP_VERSION: str = "v1.2.1"
APP_NAME: str = "XMLuvation"
AUTHOR: str = "Jovan"


class MainWindow(QMainWindow):
    progress_updated = Signal(int)
    update_input_file_signal = Signal(str)
    update_output_file_signal = Signal(str)

    def __init__(self):
        super().__init__()

        # Create and set up the UI
        self.paths_menu = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set window title with a version
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")

        # XML Data
        self.parsed_xml_data = {}
        self.current_read_xml_file = None

        self.csv_exporter_handler = None

        # Create fixed actions ONCE and store them as instance variables
        self._add_custom_path_action = QAction("Add Custom Path", self)
        self._add_custom_path_action.triggered.connect(self.add_custom_path)

        # XML Highlighter
        self.xml_highlighter = apply_xml_highlighting_to_widget(self.ui.text_edit_xml_output)

        # Instantiate the controller with a reference to the MainWindow
        self.cb_state_controller = ComboboxStateHandler(
            main_window=self,
            parsed_xml_data=self.parsed_xml_data,
            cb_tag_name=self.ui.combobox_tag_names,
            cb_tag_value=self.ui.combobox_tag_values,
            cb_attr_name=self.ui.combobox_attribute_names,
            cb_attr_value=self.ui.combobox_attribute_values)
        
        # Instantiate the XML Output search handler
        self.xml_text_searcher = SearchXMLOutputTextHandler(
            main_window=self,
            line_edit_xml_output_find_text=self.ui.line_edit_xml_output_find_text,
            text_edit_xml_output=self.ui.text_edit_xml_output)

        # Settings file for storing application settings
        self.settings = QSettings("Jovan", "XMLuvation")

        # Window geometry restoration
        geometry = self.settings.value("geometry", bytes())
        if geometry:
            self.restoreGeometry(geometry)
            
        # Recent Xpath expressions settings
        self.recent_xpath_expressions = self.settings.value("recent_xpath_expressions", type=list)

        #  Initialize the QThreadPool for running threads
        self.thread_pool = QThreadPool()
        max_threads = self.thread_pool.maxThreadCount()  # PC's max CPU threads (I have 32 Threads on a Ryzen 9 7950X3D)
        self.set_max_threads = max_threads
        self.thread_pool.setMaxThreadCount(max_threads)

        # Keep track of active workers (optional, for cleanup)
        self.active_workers = []
        self.xpath_filters = []
        self.config_handler = ConfigHandler(
            main_window=self,
            config_directory=GUI_CONFIG_DIRECTORY,
            config_file_name=GUI_CONFIG_FILE_PATH
        )

        # Connect the custom context menu for Listbox
        self.ui.list_widget_xpath_expressions.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.list_widget_xpath_expressions.customContextMenuRequested.connect(self.show_context_menu)
        
        # Connect the Find action to the default context menu of the XML Output QTextEdit widget
        self.ui.text_edit_xml_output.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.text_edit_xml_output.customContextMenuRequested.connect(self.show_custom_context_menu)

        # Theme Icons in QMenu
        self.light_mode_icon = QIcon(LIGHT_THEME_QMENU_ICON)
        self.dark_mode_icon = QIcon(DARK_THEME_QMENU_ICON)

        # Theme files qss
        self.dark_theme_file = DARK_THEME_PATH
        self.light_theme_file = LIGHT_THEME_PATH

        # Load last used theme or default
        self.current_theme = self.settings.value("app_theme", "dark_theme.qss")
        
        # Setting for the group matches checkbox
        self.group_matches_setting = self.settings.value("group_matches", self.ui.checkbox_group_matches.isChecked(), type=bool)
        if self.group_matches_setting:
            self.ui.checkbox_group_matches.setChecked(self.group_matches_setting)

        # Apply theme and correct icon
        if self.current_theme == "dark_theme.qss":
            self.theme_icon = self.light_mode_icon
            self._initialize_theme(self.dark_theme_file)
        else:
            self.theme_icon = self.dark_mode_icon
            self._initialize_theme(self.light_theme_file)

        # Setup connections and initialize components
        self.setup_connections()
        
        # Setup statusbars and hide widgets/buttons for .iu files when editing .iu file in Qt Designer
        self.setup_widgets_and_visibility_states()

        # Create my custom menu bar
        self.create_menu_bar()

        # Check thread pool status
        # print(self.get_thread_pool_status())

    # ====================================================================================================================== #

    def _initialize_theme(self, theme_file):
        """Initialized UI theme files (.qss)

        Args:
            theme_file (str): File path to the .qss theme file
        """
        try:
            file = QFile(theme_file)
            if not file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
                return
            else:
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.setStyleSheet(stylesheet)
            file.close()
        except Exception as ex:
            QMessageBox.critical(self, "Theme load error", f"Failed to load theme: {str(ex)}")


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
            self.settings.setValue("group_matches", self.ui.checkbox_group_matches.isChecked())
            super().closeEvent(event)

    # === Menubar, Menubar Control and UI Events === #
    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        self.recent_xpath_expressions_menu = QMenu("Recent XPath expressions", self)
        self.recent_xpath_expressions_menu.clear()
        
        for expression in self.recent_xpath_expressions:
            action = QAction(expression, self)
            action.triggered.connect(lambda checked, exp=expression: self.set_xpath_expression_in_input(exp))
            self.recent_xpath_expressions_menu.addAction(action)
        
        file_menu.addMenu(self.recent_xpath_expressions_menu)
        
        clear_recent_xpath_expressions_action = QAction("Clear recent XPath expressions", self)
        clear_recent_xpath_expressions_action.triggered.connect(self.clear_recent_xpath_expressions)
        file_menu.addAction(clear_recent_xpath_expressions_action)
        
        file_menu.addSeparator()
        
        clear_action = QAction("Clear Output", self)
        clear_action.triggered.connect(self.clear_output)
        file_menu.addAction(clear_action)
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Open Menu
        open_menu = menu_bar.addMenu("&Open")
        open_input_action = QAction("Open input XML folder in file explorer", self)
        open_input_action.triggered.connect(
            lambda: self.open_folder_in_file_explorer(self.ui.line_edit_xml_folder_path_input.text()))
        open_menu.addAction(open_input_action)
        open_output_action = QAction("Open output CSV folder in file explorer", self)
        open_output_action.triggered.connect(
            lambda: self.open_folder_in_file_explorer(os.path.dirname(self.ui.line_edit_csv_output_path.text())))
        open_menu.addAction(open_output_action)
        open_menu.addSeparator()
        open_csv_conversion_input_action = QAction("Open CSV conversion input folder in file explorer", self)
        open_csv_conversion_input_action.triggered.connect(lambda: self.open_folder_in_file_explorer(os.path.dirname(self.ui.line_edit_csv_conversion_path_input.text())))
        open_menu.addAction(open_csv_conversion_input_action)

        # Path Menu
        self.paths_menu = menu_bar.addMenu("&Path")

        # Initially populate the menu. This method will now ensure the correct order.
        self.update_paths_menu()

        # Add an option to add a new custom path
        self.paths_menu.addAction(self._add_custom_path_action)

        # Settings Menu
        settings_menu = menu_bar.addMenu("&Settings")
        open_paths_manager = QAction("Manage Custom Paths", self)
        open_paths_manager.triggered.connect(self.open_paths_manager_window)
        settings_menu.addAction(open_paths_manager)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        xpath_help_action = QAction("XPath Help", self)
        xpath_help_action.setStatusTip("Open XPath Syntax Help")
        xpath_help_action.triggered.connect(self.open_web_xpath_help)
        help_menu.addAction(xpath_help_action)

        # Theme Menu
        self.toggle_theme_action = menu_bar.addAction(self.theme_icon, "Toggle Theme")
        self.toggle_theme_action.triggered.connect(self.change_theme)

    # ======= START FUNCTIONS create_menu_bar ======= #

    def add_recent_xpath_expression(self, expression: str):
        """Adds a new XPath expression to the recent expressions list and updates the menu."""
        MAX_RECENT = 10
        if expression not in self.recent_xpath_expressions:
            self.recent_xpath_expressions.insert(0, expression)
            self.recent_xpath_expressions = self.recent_xpath_expressions[:MAX_RECENT]
            self.settings.setValue("recent_xpath_expressions", self.recent_xpath_expressions)
            self.update_recent_xpath_expressions_menu()


    def set_xpath_expression_in_input(self, expression: str):
        """Sets the given XPath expression in the input field and updates the recent expressions."""
        # Clear the input field first
        self.ui.line_edit_xpath_builder.clear()
        self.ui.line_edit_xpath_builder.setText(expression)


    def update_recent_xpath_expressions_menu(self):
        """Updates the recent XPath expressions menu to reflect the current state of recent expressions."""
        self.recent_xpath_expressions_menu.clear()
        
        for expression in self.recent_xpath_expressions:
            action = QAction(expression, self)
            action.triggered.connect(lambda checked, exp=expression: self.set_xpath_expression_in_input(exp))
            self.recent_xpath_expressions_menu.addAction(action)


    def clear_recent_xpath_expressions(self):
        """Clears the recent XPath expressions list and updates the menu."""
        reply = QMessageBox.question(self, "Clear recent XPath expressions",
                                    "Are you sure you want to clear the list of recent XPath expressions?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.settings.remove("recent_xpath_expressions")
            self.recent_xpath_expressions = []
            self.update_recent_xpath_expressions_menu()


    def update_paths_menu(self):
        """
        Updates the 'Path' menu by clearing all dynamic custom path actions
        and re-adding them based on the current configuration. Fixed actions
        ('Add Custom Path', 'Remove Custom Path') are preserved.
        """
        # 1. Clear ALL actions from the menu;
        # this is the most reliable way to ensure no stale actions remain.
        self.paths_menu.clear()

        # 2. Get the latest custom paths from the config handler
        # Using the dynamic 'get' method:
        custom_paths = self.config_handler.get("custom_paths", {})

        # 3. Add dynamic custom path actions first
        for name, path in custom_paths.items():
            action = QAction(name, self)
            action.setStatusTip(f"Open {name}")
            # Connect to your desired slot, e.g., open_path or set_path_in_input
            action.triggered.connect(lambda checked, p=path: self.set_path_in_input(p))
            self.paths_menu.addAction(action)

        # 4. Add a separator for visual separation if needed
        if custom_paths:  # Only add separator if there are custom paths
            self.paths_menu.addSeparator()

        # 5. Add the fixed actions (they are created once in __init__ or setup_ui)
        self.paths_menu.addAction(self._add_custom_path_action)


    def add_custom_path(self):
        name, ok = QInputDialog.getText(self, "Add Custom Path", "Enter a name for the path:")
        if ok and name:
            existing_paths = self.config_handler.get("custom_paths", {})
            if name in existing_paths:
                QMessageBox.warning(self, "Duplicate Name", f"A path with the name '{name}' already exists.")
                return

            path, ok = QInputDialog.getText(self, "Add Custom Path", "Enter path:")
            if ok and path:
                # Use the dynamic 'set' method for nested paths
                self.config_handler.set(f"custom_paths.{name}", path)
                self.update_paths_menu()  # Refresh the menu to show the new path


    def change_theme(self):
        if self.current_theme == "dark_theme.qss":
            self.toggle_theme_action.setIcon(self.dark_mode_icon)
            self._initialize_theme(self.light_theme_file)
            self.current_theme = "light_theme.qss"
            self.current_theme_icon = "light.png"
        else:
            self.toggle_theme_action.setIcon(self.light_mode_icon)
            self._initialize_theme(self.dark_theme_file)
            self.current_theme = "dark_theme.qss"
            self.current_theme_icon = "dark.png"


    def clear_output(self):
        self.ui.text_edit_program_output.clear()
        self.ui.text_edit_csv_conversion_tab_program_output.clear()


    def open_folder_in_file_explorer(self, folder_path):
        """Helper method to open the specified folder in the file explorer."""
        if os.path.exists(folder_path):
            print("Opening folder:", folder_path)
            try:
                os.startfile(folder_path)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "An exception occurred", message)
        else:
            QMessageBox.warning(self, "Error", f"Path does not exist or is not a valid path:\n{folder_path}")


    def open_web_xpath_help(self):
        webbrowser.open("https://www.w3schools.com/xml/xpath_syntax.asp")


    def open_paths_manager_window(self):
        self.w = CustomPathsManager(main_window=self)
        self.w.show()


    def set_path_in_input(self, path: str):
        self.ui.line_edit_xml_folder_path_input.setText(path)

    # ====================================================================================================================== #

    # Setup UI Widget Actions
    def setup_connections(self):
        """Setup all signal-slot connections"""
        
        # Keyboard shortcuts
        self.shortcut_find = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_F), self)
        # Connect the shortcut's activated signal to the toggle function
        self.shortcut_find.activated.connect(self.toggle_xml_output_search_widgets)

        # QLineWidgets
        self.ui.line_edit_xml_folder_path_input.textChanged.connect(self.update_xml_file_count)
        self.ui.line_edit_profile_cleanup_csv_file_path.textChanged.connect(self.on_csv_profile_cleanup_input_changed)
        
        # Combo boxes
        self.ui.combobox_tag_names.currentTextChanged.connect(self.cb_state_controller.on_tag_name_changed)
        self.ui.combobox_attribute_names.currentTextChanged.connect(self.cb_state_controller.on_attribute_name_changed)

        # ========= START QPushButtons START ========= #
        
        # Folder browsing and XML reading
        self.ui.button_browse_xml_folder.clicked.connect(
            lambda: self.browse_folder_helper(dialog_message="Select directory that contains XML files",
                                            line_widget=self.ui.line_edit_xml_folder_path_input))
        self.ui.button_read_xml.clicked.connect(self.on_read_xml_file_event)

        # File browsing for csv evaluation export
        self.ui.button_browse_csv.clicked.connect(lambda: self.browse_save_file_as_helper(dialog_message="Save as",
                                                                                        line_widget=self.ui.line_edit_csv_output_path,
                                                                                        file_extension_filter="CSV File (*.csv)"))
        # XPath building
        self.ui.button_build_xpath.clicked.connect(self.on_build_xpath_expression_event)
        
        self.ui.button_add_xpath_to_list.clicked.connect(self.on_xpath_add_to_list_event)
        
        # CSV export
        self.ui.button_start_csv_export.clicked.connect(self.on_csv_export_event)
        
        self.ui.button_abort_csv_export.clicked.connect(self.on_csv_export_stop_event)
        
        self.ui.button_browse_csv_conversion_path_input.clicked.connect(
            lambda: self.browse_file_helper(dialog_message="Select csv file for conversion",
                                            line_widget=self.ui.line_edit_csv_conversion_path_input,
                                            file_extension_filter="CSV File (*.csv)"))
        self.ui.button_csv_conversion_convert.clicked.connect(self.on_csv_convert_event)
        
        self.ui.button_profile_cleanup_browse_csv_file_path.clicked.connect(
            lambda: self.browse_file_helper(dialog_message="Select csv file",
                                            line_widget=self.ui.line_edit_profile_cleanup_csv_file_path,
                                            file_extension_filter="CSV File (*.csv)"))
        
        self.ui.button_profile_cleanup_browse_folder_path.clicked.connect(
            lambda: self.browse_folder_helper(dialog_message="Select directory that contains XML files",
                                            line_widget=self.ui.line_edit_profile_cleanup_folder_path))
        
        self.ui.button_profile_cleanup_cleanup_start.clicked.connect(self.on_lobster_profile_cleanup_event)
        
        self.ui.button_drop_csv_header.clicked.connect(self.on_csv_header_drop_event)
        
        # Button signals for XML output search functionality
        self.ui.button_find_next.clicked.connect(self.on_xml_output_search_next)
        self.ui.button_find_previous.clicked.connect(self.on_xml_output_search_previous)
        
        # ========= END QPushButtons END ========= #
        
        # QCheckBox
        self.ui.checkbox_write_index_column.toggled.connect(self.on_write_index_toggled)
    
    
    def setup_widgets_and_visibility_states(self):
        """Setup widgets states"""
        # Hide buttons/widgets
        self.ui.button_find_next.setHidden(True)
        self.ui.button_find_previous.setHidden(True)
        self.ui.button_abort_csv_export.setHidden(True)
        self.ui.label_file_processing.setHidden(True)
        self.ui.line_edit_xml_output_find_text.setHidden(True)

    # === Helper Methods === #
    def browse_folder_helper(self, dialog_message: str, line_widget: QLineEdit) -> None:
        """File dialog for folder browsing, sets the path of the selected folder in a specified QLineEdit Widget

        Args:
            dialog_message (str): Title message for the QFileDialog to display
            line_widget (QLineEdit): The QLineEdit Widget to write to the path value as string
        """
        try:
            folder = QFileDialog.getExistingDirectory(self, dialog_message)
            if folder:
                # Set the file path in the QLineEdit Widget
                line_widget.setText(folder)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred in browse folder method", message)

    def browse_file_helper(self, dialog_message: str, line_widget: QLineEdit, file_extension_filter: str) -> None:
        """File dialog for file browsing, sets the path of the selected file in a specified QLineEdit Widget

        Args:
            dialog_message (str): Title message for the QFileDialog to display
            line_widget (QLineEdit): The QLineEdit Widget to write to the path value as string
            file_extension_filter (str): Filter files for selection based on set filter.

                - Example for only XML files:
                    - 'XML File (*.xml)'

                - Example for multiple filters:
                    - 'Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)'
        """
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, caption=dialog_message, filter=file_extension_filter)
            if file_name:
                line_widget.setText(file_name)  # Set the file path in the QLineEditWidget
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred in browse folder method", message)

    def browse_save_file_as_helper(self, dialog_message: str, line_widget: QLineEdit, file_extension_filter: str) -> None:
        """File dialog for file saving as, sets the path of the selected file in a specified QLineEdit Widget

        Args:
            dialog_message (str): Title message for the QFileDialog to display
            line_widget (QLineEdit): The QLineEdit Widget to write to the path value as string
            file_extension_filter (str): Filter files for selection based on set filter.

                - Example for only XML files:
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
            QMessageBox.critical(self, "An exception occurred in browse save file method",
                                    f"Error exporting CSV: {message}")

    # ====================================================================================================================== #

    def on_write_index_toggled(self):
        message_with_index = """
        Data will look like this:

        | Index           | Header 1   | Header 2    |
        |-------------------|-------------------|-------------------|
        | 1                  | Data...         | Data...        |
        """
        message_without_index = """
        Data will look like this:

        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Data...         |
        """
        try:
            if self.ui.checkbox_write_index_column.isChecked():
                self.ui.text_edit_csv_conversion_tab_program_output.setText(message_with_index)
            else:
                self.ui.text_edit_csv_conversion_tab_program_output.setText(message_without_index)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", f"An error occurred: {message}")


    # === XML PARSING === #
    def on_xml_parsing_event(self, xml_file_path: str):
        """Parse XML file and display content."""
        try:
            xml_parser = ParseXMLFileHandler(
                main_window=self,
                xml_file_path=xml_file_path
            )
            xml_parser.start_xml_parsing()

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception on starting to pare xml file", message)


    # On read XML file button has been clicked
    def on_read_xml_file_event(self):
        """On read XML file button clicked, opens FileDialog and after choosing a XML file, it's content is then inserted into a QTextEdit widget"""
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select XML File", "", "XML File (*.xml)")
            if file_name:
                self.on_xml_parsing_event(file_name)
                # Add the read XML files path to the XML path input field if it's not already set, improved ux
                if not self.ui.line_edit_xml_folder_path_input.text():
                    self.ui.line_edit_xml_folder_path_input.setText(os.path.dirname(file_name))
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception reading xml file", message)


    # On build xpath button has been clicked
    def on_build_xpath_expression_event(self):
        """Build XPath expression based on selected combobox values."""
        try:
            # Create an instance of XPathBuilder using the convenience function,
            # passing all necessary UI widget references.
            # This assumes 'self.ui' is an object holding references to your PySide6 UI widgets.
            builder = XPathBuildHandler(
                main_window=self,
                line_edit_xpath_builder=self.ui.line_edit_xpath_builder,
                tag_name_combo=self.ui.combobox_tag_names,
                tag_value_combo=self.ui.combobox_tag_values,
                attribute_name_combo=self.ui.combobox_attribute_names,
                attribute_value_combo=self.ui.combobox_attribute_values,
                radio_equals=self.ui.radio_button_equals,
                radio_contains=self.ui.radio_button_contains,
                radio_starts_with=self.ui.radio_button_starts_with,
                radio_greater=self.ui.radio_button_greater,
                radio_smaller=self.ui.radio_button_smaller
            )

            builder.start_xpath_build()

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception on building xpath expression", message)


    # On csv export (main core logic of the app) button has been clicked
    def on_csv_export_event(self):
        """Initializes and starts the CSV export in a new thread."""
        try:
            # Extract UI data into clean variables first
            xml_path = self.ui.line_edit_xml_folder_path_input.text()
            csv_output = self.ui.line_edit_csv_output_path.text()
            headers = self.ui.line_edit_csv_headers_input.text()
            group_matches_flag = self.ui.checkbox_group_matches.isChecked()
            max_threads = self.set_max_threads  # Already a property
            xpath_filters = self.xpath_filters  # Already a property

            # Pass into controller
            self.csv_exporter_handler = SearchAndExportToCSVHandler(
                main_window=self,
                xml_folder_path=xml_path,
                xpath_filters=xpath_filters,
                csv_folder_output_path=csv_output,
                csv_headers_input=headers,
                group_matches_flag = group_matches_flag,
                set_max_threads=max_threads
            )
            self.csv_exporter_handler.start_csv_export()

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception on starting to search and export to csv", message)


    def on_csv_export_stop_event(self):
        """Signals the currently running CSV export to stop."""
        try:
            # Check if an exporter handler instance exists and if there's an active export
            if self.csv_exporter_handler:
                self.csv_exporter_handler.stop_csv_export()
                self.csv_exporter_handler = None
            else:
                QMessageBox.information(self, "No Active Export", "There is no CSV export currently running to abort.")

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception on stopping CSV export", message)


    # On added xpath to list button has been clicked
    def on_xpath_add_to_list_event(self):
        try:
            """Adds entered XPath Expression to the QListWidget"""
            # Initialize the UI element and pass them to the class
            xpath_input: str = self.ui.line_edit_xpath_builder.text()
            xpath_filters: List[str] = self.xpath_filters  # Already a property
            csv_headers_input = self.ui.line_edit_csv_headers_input
            list_widget_xpath_expressions = self.ui.list_widget_xpath_expressions

            adder = AddXPathExpressionToListHandler(
                main_window=self,
                xpath_expression=xpath_input,
                xpath_filters=xpath_filters,
                list_widget_xpath_expressions=list_widget_xpath_expressions)

            is_added = adder.add_expression_to_list()

            # If the XPath Expression has been successfully added to the QListWidget, generate the CSV Header based on the combobox values
            if is_added:
                current_text = csv_headers_input.text()
                self.add_recent_xpath_expression(xpath_input)
                self.update_statusbar_xpath_listbox_count()

                generator = GenerateCSVHeaderHandler(self,
                                                    tag_name_combo=self.ui.combobox_tag_names,
                                                    tag_value_combo=self.ui.combobox_tag_values,
                                                    attribute_name_combo=self.ui.combobox_attribute_names,
                                                    attribute_value_combo=self.ui.combobox_attribute_values,
                                                    xpath_input=self.ui.line_edit_xpath_builder,
                                                    csv_headers_input=self.ui.line_edit_csv_headers_input)
                
                header = generator.generate_header()

                # Append with a separator (e.g., comma) if needed
                if current_text:
                    updated_text = f"{current_text}, {header}"
                else:
                    updated_text = header
                csv_headers_input.setText(updated_text)
            
                self.ui.line_edit_xpath_builder.clear() # Always clear the input field after adding xpath to list

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception on starting add xpath to list widget", message)


    # On csv convert button has been clicked in second tab
    def on_csv_convert_event(self):
        try:
            # Initialize the UI elements and pass them to the class
            csv_file_to_convert = self.ui.line_edit_csv_conversion_path_input.text()
            extension_type = self.ui.combobox_csv_conversion_output_type.currentText()
            write_index = self.ui.checkbox_write_index_column.isChecked()

            self.csv_conversion_controller = CSVConversionHandler(
                main_window=self,
                csv_file_to_convert=csv_file_to_convert,
                extension_type=extension_type,
                write_index=write_index)

            self.csv_conversion_controller.start_csv_conversion()

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception on starting csv convert to other filetype", message)


    # On cleanup lobster profiles button has been clicked
    def on_lobster_profile_cleanup_event(self):
        try:
            csv_file = self.ui.line_edit_profile_cleanup_csv_file_path.text()
            profiles_folder_path = self.ui.line_edit_profile_cleanup_folder_path.text()

            self.lobster_profile_cleaner = LobsterProfileExportCleanupHandler(
                main_window=self,
                csv_file_path=csv_file,
                profiles_folder_path=profiles_folder_path)

            self.lobster_profile_cleaner.start_lobster_profile_cleanup()

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception on starting lobster profile xml files cleanup", message)


    # On CSV header drop button has been clicked
    def on_csv_header_drop_event(self):
        csv_file_path = self.ui.line_edit_profile_cleanup_csv_file_path.text()
        column_to_drop = self.ui.combobox_csv_headers.currentText()
        column_to_drop_index = self.ui.combobox_csv_headers.currentIndex()

        drop_column = CSVColumnDropHandler(
            main_window=self,
            csv_file_path=csv_file_path,
            column_to_drop=column_to_drop,
            column_to_drop_index=column_to_drop_index
        )

        drop_column.start_csv_column_drop()


    def on_csv_profile_cleanup_input_changed(self):
        csv_file_path = self.ui.line_edit_profile_cleanup_csv_file_path.text()
        column_to_drop = self.ui.combobox_csv_headers.currentText()
        column_to_drop_index = self.ui.combobox_csv_headers.currentIndex()
        csv_header_combobox = self.ui.combobox_csv_headers
        drop_header_button = self.ui.button_drop_csv_header

        CSVColumnDropHandler(
            main_window=self,
            csv_file_path=csv_file_path,
            column_to_drop=column_to_drop,
            column_to_drop_index = column_to_drop_index,
            csv_header_combobox=csv_header_combobox,
            drop_header_button=drop_header_button
        ).on_csv_input_file_path_changed()


    def on_xml_output_search_next(self):
        self.xml_text_searcher.search_next()


    def on_xml_output_search_previous(self):
        self.xml_text_searcher.search_previous()


    # Statusbar update function
    def update_xml_file_count(self):
        """Updated the current XML Files found in the selected folder from QLineEdit' line_edit_xml_folder_path_input'
        """
        try:
            folder: str = self.ui.line_edit_xml_folder_path_input.text()
            if os.path.isdir(folder):
                xml_files_count: int = sum(1 for f in os.listdir(folder) if f.endswith(".xml"))
                if xml_files_count >= 1:
                    self.ui.statusbar_xml_files_count.setText(f"Found {xml_files_count} XML Files")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.statusbar_xml_files_count.setText(f"Error counting XML files: {message}")


    def update_statusbar_xpath_listbox_count(self):
        self.counter = self.ui.list_widget_xpath_expressions.count()
        if self.counter != 0:
            self.ui.statusbar_xpath_expressions.setText(f"XPath expressions in list: {self.counter}")


    def remove_selected_item(self):
        """Removes the selected item that has been added to the QListWidget and the xpath_filters list
        """
        try:
            current_selected_item = self.ui.list_widget_xpath_expressions.currentRow()
            if current_selected_item != -1:
                item_to_remove = self.ui.list_widget_xpath_expressions.takeItem(current_selected_item)
                self.xpath_filters.pop(current_selected_item)
                self.ui.text_edit_program_output.append(
                    f"Removed item: {item_to_remove.text()} at row {current_selected_item}")
                self.update_statusbar_xpath_listbox_count()
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
                self.update_statusbar_xpath_listbox_count()
                # Clean CSV Header Input if it has any value in it
                if len(self.ui.line_edit_csv_headers_input.text()) > 1:
                    self.ui.line_edit_csv_headers_input.clear()
            else:
                self.ui.text_edit_program_output.setText("No items to delete in list.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.text_edit_program_output.setText(f"Error removing selected all items from list: {message}")


    def show_context_menu(self, position):
        context_menu = QMenu(self)
        delete_action = QAction("Delete Selected", self)
        delete_all_action = QAction("Delete All", self)

        context_menu.addAction(delete_action)
        context_menu.addAction(delete_all_action)

        delete_action.triggered.connect(self.remove_selected_item)
        delete_all_action.triggered.connect(self.remove_all_items)

        # Show the context menu at the cursor's current position
        context_menu.exec(self.ui.list_widget_xpath_expressions.mapToGlobal(position))


    def show_custom_context_menu(self, position):
        menu = self.ui.text_edit_xml_output.createStandardContextMenu()
        find_action = QAction("Find", self, shortcut=QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_F))
        find_action.triggered.connect(self.toggle_xml_output_search_widgets)
        menu.addAction(find_action)
        
        # Show the context menu at the cursor's current position
        menu.exec(self.ui.text_edit_xml_output.mapToGlobal(position))


    def set_ui_widgets_disabled(self, state: bool):
        # Disable buttons while exporting
        self.ui.button_browse_xml_folder.setDisabled(state)
        self.ui.button_read_xml.setDisabled(state)
        self.ui.button_build_xpath.setDisabled(state)
        self.ui.button_add_xpath_to_list.setDisabled(state)
        self.ui.button_browse_csv.setDisabled(state)
        self.ui.button_browse_csv_conversion_path_input.setDisabled(state)
        self.ui.button_start_csv_export.setDisabled(state)
        self.ui.line_edit_xml_folder_path_input.setReadOnly(state)
        self.ui.line_edit_csv_output_path.setReadOnly(state)

    # ======= End FUNCTIONS FOR create_export_evaluation_group ======= #

    def get_thread_pool_status(self) -> str:
        """Get current thread pool status (useful for debugging).

        Returns:
            str: Active threads: {active_count}/{max_count}
        """
        active_count = self.thread_pool.activeThreadCount()
        max_count = self.thread_pool.maxThreadCount()
        return f"Active threads: {active_count}/{max_count}"
    
    @Slot()
    def toggle_xml_output_search_widgets(self):
        is_input_search_hidden = self.ui.line_edit_xml_output_find_text.isHidden()
        is_btn_next_hidden = self.ui.button_find_next.isHidden()
        is_btn_prev_hidden = self.ui.button_find_previous.isHidden()
        
        if is_input_search_hidden and is_btn_next_hidden and is_btn_prev_hidden:
            self.ui.line_edit_xml_output_find_text.setHidden(False)
            self.ui.button_find_next.setHidden(False)
            self.ui.button_find_previous.setHidden(False)
        else:
            self.ui.line_edit_xml_output_find_text.setHidden(True)
            self.ui.line_edit_xml_output_find_text.clear()
            self.ui.button_find_next.setHidden(True)
            self.ui.button_find_previous.setHidden(True)

    # === EVENT HANDLERS FOR QMessageBoxes === #
    @Slot(str, str)  # QMessageBox.critical type shit
    def on_error_message(self, title, message):
        """Show critical message dialog."""
        QMessageBox.critical(self, title, message)

    @Slot(str, str)  # QMessageBox.information type shit
    def on_info_message(self, title, message):
        """Show information message dialog."""
        QMessageBox.information(self, title, message)

    @Slot(str, str)  # QMessageBox.warning type shit
    def on_warning_message(self, title, message):
        """Show warning message dialog."""
        QMessageBox.warning(self, title, message)

    # === EVENT HANDLER FOR QTextEdit MAIN PROGRAM OUTPUT === #
    @Slot(str)
    def append_to_program_output(self, message: str):
        """Handle QTextEdit progress updates with .append() in any class, does the QTextEdit.append("hello world").

        Args:
            message (str): Message to send to the QTextEdit Widget
        """
        self.ui.text_edit_program_output.append(message)

    @Slot(str)
    def set_text_to_program_output(self, message: str):
        """Handle QTextEdit progress updates with .setText() in any class, does the QTextEdit.setText("hello world")

        Args:
            message (str): Message to send to the QTextEdit Widget
        """
        self.ui.text_edit_program_output.setText(message)

    @Slot(str)
    def append_to_program_output_csv_tab(self, message: str):
        """Handle QTextEdit progress updates with .append() in any class, does the QTextEdit.append("hello world").

        Args:
            message (str): Message to send to the QTextEdit Widget
        """
        self.ui.text_edit_csv_conversion_tab_program_output.append(message)

    @Slot(str)
    def set_text_to_program_output_csv_tab(self, message: str):
        """Handle QTextEdit progress updates with .setText() in any class, does the QTextEdit.setText("hello world")

        Args:
            message (str): Message to send to the QTextEdit Widget
        """
        self.ui.text_edit_csv_conversion_tab_program_output.setText(message)

    @Slot(str)
    def on_column_dropped_successfully(self, index: int):
        """Handle the QComboBox on CSV Header drop

        Args:
            column (str): Current selected text of the QComboBox widget for the CSV header
        """
        # Delete the current dropped column from the csv headers combobox in the 2nd UI tab
        self.ui.combobox_csv_headers.removeItem(index)

    # === XML PARSING ON FINISHED SLOT === #
    @Slot(dict)
    def on_xml_parsing_finished(self, result: dict):
        """Handle XML parsing completion."""
        try:
            xml_content = result.get('xml_string', '')
            # Add highlighter for XML files then add to QTextEdit
            set_xml_content_to_widget(self.ui.text_edit_xml_output, xml_content)
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

            # Save XML file in initialized variable
            self.current_read_xml_file = result.get("file_path")

            self.ui.text_edit_program_output.append(info_message)

            self.parsed_xml_data = result
            # Pass the new result data (the XML data as dict) to the ComboBoxStateController class
            self.cb_state_controller.set_parsed_data(result)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Error processing parsing results", message)

    @Slot(bool)
    def on_csv_export_started(self, state: bool):
        self.ui.button_abort_csv_export.setVisible(state)
        self.ui.label_file_processing.setVisible(state)
        #self.ui.text_edit_program_output.append(self.get_thread_pool_status())
        self.set_ui_widgets_disabled(state=True)

    @Slot()
    def on_csv_export_finished(self):
        self.ui.button_abort_csv_export.setVisible(False)
        self.ui.label_file_processing.setVisible(False)
        self.set_ui_widgets_disabled(state=False)
        self.ui.progressbar_main.reset()

    @Slot(str)
    def on_file_processing(self, message: str):
        """Handle QLabel progress updates for file processing."""
        self.ui.label_file_processing.setText(message)

    @Slot(int)
    def update_progress_bar(self, progress: int):
        self.ui.progressbar_main.setValue(progress)

    # === SIGNAL CONNECTION HELPERS === #
    def _connect_xml_parsing_signals(self, worker):
        """Connect common signals for most operations.
        """
        worker.signals.finished.connect(self.on_xml_parsing_finished)
        worker.signals.error_occurred.connect(self.on_error_message)
        worker.signals.program_output_progress.connect(self.append_to_program_output)

    def _connect_xpath_builder_signals(self, worker):
        """Connect signals for XPath building operations."""
        worker.signals.program_output_progress.connect(self.append_to_program_output)
        worker.signals.error_occurred.connect(self.on_error_message)
        worker.signals.warning_occurred.connect(self.on_warning_message)

    def _connect_csv_export_signals(self, worker):
        """Connect signals for CSV export operations.   """
        worker.signals.finished.connect(self.on_csv_export_finished)
        worker.signals.error_occurred.connect(self.on_error_message)
        worker.signals.info_occurred.connect(self.on_info_message)
        worker.signals.warning_occurred.connect(self.on_warning_message)
        worker.signals.program_output_progress_append.connect(self.append_to_program_output)
        worker.signals.program_output_progress_set_text.connect(self.set_text_to_program_output)
        worker.signals.file_processing_progress.connect(self.on_file_processing)
        worker.signals.progressbar_update.connect(self.update_progress_bar)
        worker.signals.visible_state_widget.connect(self.on_csv_export_started)

    def _connect_file_cleanup_signals(self, worker):
        worker.signals.error_occurred.connect(self.on_error_message)
        worker.signals.warning_occurred.connect(self.on_warning_message)
        worker.signals.program_output_progress_append.connect(self.append_to_program_output_csv_tab)
        worker.signals.program_output_progress_set_text.connect(self.set_text_to_program_output_csv_tab)
        worker.signals.column_dropped_successfully.connect(self.on_column_dropped_successfully)
        
    def _connect_csv_conversion_signals(self, worker):
        """Connect signals for CSV conversion operations."""
        worker.signals.error_occurred.connect(self.on_error_message)
        worker.signals.info_occurred.connect(self.on_info_message)
        worker.signals.warning_occurred.connect(self.on_warning_message)

if __name__ == "__main__":
    # Initialize the application
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
