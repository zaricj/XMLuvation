# File: main.py
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QMessageBox,
)
from PySide6.QtGui import QIcon, QAction, QCloseEvent
from PySide6.QtCore import (
    Qt,
    QFile,
    QTextStream,
    QIODevice,
    QSettings,
    QThreadPool,
)

import sys
import os
from pathlib import Path

from ui.main.XMLuvation_ui import Ui_MainWindow
from controllers.signal_handlers import SignalHandlerMixin

from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.state_controller import (
        ComboboxStateHandler, 
        SearchXMLOutputTextHandler,
        SearchAndExportToCSVHandler
    )
    from modules.config_handler import ConfigHandler


# Path Constants
CURRENT_DIR = Path(__file__).parent
GUI_CONFIG_DIRECTORY: Path = CURRENT_DIR / "config"
GUI_CONFIG_FILE_PATH: Path = CURRENT_DIR / "config" / "config.json"

# Theme files
DARK_THEME_PATH: Path = CURRENT_DIR / "resources" / "styles" / "dark_theme.qss"
LIGHT_THEME_PATH: Path = CURRENT_DIR / "resources" / "styles" / "light_theme.qss"

ICON_PATH: Path = CURRENT_DIR / "resources" / "icons" / "xml_256px.ico"

# Theme file icons
DARK_THEME_QMENU_ICON: Path = CURRENT_DIR / "resources" / "images" / "dark.png"
LIGHT_THEME_QMENU_ICON: Path = CURRENT_DIR / "resources" / "images" / "light.png"

# App related constants
APP_VERSION: str = "v1.2.2"
APP_NAME: str = "XMLuvation"
AUTHOR: str = "Jovan"

# Check if the application is running in a PyInstaller bundle
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    ROOT_DIR: str = sys._MEIPASS
else:
    ROOT_DIR: str = os.path.dirname(CURRENT_DIR)


class MainWindow(QMainWindow, SignalHandlerMixin):
    # Type hints for all attributes
    parsed_xml_data: Dict[str, Any]
    current_read_xml_file: Optional[str]
    csv_exporter_handler: Optional['SearchAndExportToCSVHandler']
    xpath_filters: List[str]
    active_workers: List[Any]
    recent_xpath_expressions: List[str]
    
    # Settings and threading
    settings: QSettings
    thread_pool: QThreadPool
    set_max_threads: int
    
    # Controllers
    cb_state_controller: 'ComboboxStateHandler'
    xml_text_searcher: 'SearchXMLOutputTextHandler'
    config_handler: 'ConfigHandler'
    
    # Theme attributes
    current_theme: str
    dark_theme_file: str
    light_theme_file: str

    def __init__(self):
        super().__init__()

        # Create and set up the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set window title with a version
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")

        # Initialize all attributes
        self.initialize_attributes()

        # Setup application
        self.setup_application()

        # Initialize theme
        self._initialize_theme()

        # Setup widgets and visibility states
        self.setup_widgets_and_visibility_states()

    def setup_application(self):
        """Initialize the application components"""
        self.create_menu_bar()
        self.connect_ui_events()  # From mixin
        self.connect_menu_bar_actions()  # From mixin
        self._update_paths_menu() # From mixing

    def initialize_attributes(self):
        """Initialize all application attributes"""
        # Import required classes
        from controllers.state_controller import ComboboxStateHandler
        from controllers.state_controller import SearchXMLOutputTextHandler
        from modules.config_handler import ConfigHandler

        # XML Data
        self.parsed_xml_data = {}
        self.current_read_xml_file = None
        self.csv_exporter_handler = None

        # Create fixed actions ONCE and store them as instance variables
        self._add_custom_path_action = QAction("Add Custom Path", self)

        # Instantiate the controller with a reference to the MainWindow
        self.cb_state_controller = ComboboxStateHandler(
            main_window=self,
            parsed_xml_data=self.parsed_xml_data,
            cb_tag_name=self.ui.combobox_tag_names,
            cb_tag_value=self.ui.combobox_tag_values,
            cb_attr_name=self.ui.combobox_attribute_names,
            cb_attr_value=self.ui.combobox_attribute_values,
        )

        # Instantiate the XML Output search handler
        self.xml_text_searcher = SearchXMLOutputTextHandler(
            main_window=self,
            line_edit_xml_output_find_text=self.ui.line_edit_xml_output_find_text,
            text_edit_xml_output=self.ui.text_edit_xml_output,
        )

        # Settings file for storing application settings
        self.settings = QSettings("Jovan", "XMLuvation")

        # Window geometry restoration
        geometry = self.settings.value("geometry", bytes())
        if geometry:
            self.restoreGeometry(geometry)

        # Recent Xpath expressions settings
        self.recent_xpath_expressions = self.settings.value(
            "recent_xpath_expressions", type=list
        )
        if self.recent_xpath_expressions is None:
            self.recent_xpath_expressions = []

        # Initialize the QThreadPool for running threads
        self.thread_pool = QThreadPool()
        max_threads = self.thread_pool.maxThreadCount()
        self.set_max_threads = max_threads
        self.thread_pool.setMaxThreadCount(max_threads)

        # Keep track of active workers
        self.active_workers = []
        self.xpath_filters = []
        self.config_handler = ConfigHandler(
            main_window=self,
            config_directory=GUI_CONFIG_DIRECTORY,
            config_file_name=GUI_CONFIG_FILE_PATH,
        )

        # Connect the custom context menu for Listbox
        self.ui.list_widget_xpath_expressions.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.text_edit_xml_output.setContextMenuPolicy(Qt.CustomContextMenu)

        # Theme Icons in QMenu
        self.light_mode_icon = QIcon(LIGHT_THEME_QMENU_ICON.__str__())
        self.dark_mode_icon = QIcon(DARK_THEME_QMENU_ICON.__str__())

        # Theme files qss
        self.dark_theme_file = DARK_THEME_PATH.__str__()
        self.light_theme_file = LIGHT_THEME_PATH.__str__()

        # Load last used theme or default
        self.current_theme = self.settings.value("app_theme", "dark_theme.qss")

        # Setting for the group matches checkbox
        self.group_matches_setting = self.settings.value(
            "group_matches", self.ui.checkbox_group_matches.isChecked(), type=bool
        )
        if self.group_matches_setting:
            self.ui.checkbox_group_matches.setChecked(self.group_matches_setting)

        # Set theme icon based on current theme
        if self.current_theme == "dark_theme.qss":
            self.theme_icon = self.light_mode_icon
        else:
            self.theme_icon = self.dark_mode_icon

    def _initialize_theme(self):
        """Initialize UI theme files (.qss)"""
        try:
            if self.current_theme == "dark_theme.qss":
                theme_file = self.dark_theme_file
            else:
                theme_file = self.light_theme_file

            file = QFile(theme_file)
            if not file.open(
                QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text
            ):
                return
            else:
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.setStyleSheet(stylesheet)
            file.close()
        except Exception as ex:
            QMessageBox.critical(
                self, "Theme load error", f"Failed to load theme: {str(ex)}"
            )

    def create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        self.recent_xpath_expressions_menu = QMenu("Recent XPath expressions", self)
        self.recent_xpath_expressions_menu.clear()

        for expression in self.recent_xpath_expressions:
            action = QAction(expression, self)
            self.recent_xpath_expressions_menu.addAction(action)

        file_menu.addMenu(self.recent_xpath_expressions_menu)

        self.clear_recent_xpath_expressions_action = QAction(
            "Clear recent XPath expressions", self
        )
        file_menu.addAction(self.clear_recent_xpath_expressions_action)
        file_menu.addSeparator()

        self.clear_action = QAction("Clear Output", self)
        file_menu.addAction(self.clear_action)
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Open Menu
        open_menu = menu_bar.addMenu("&Open")
        self.open_input_action = QAction("Open input XML folder in file explorer", self)
        open_menu.addAction(self.open_input_action)
        
        self.open_output_action = QAction("Open output CSV folder in file explorer", self)
        open_menu.addAction(self.open_output_action)
        open_menu.addSeparator()
        
        self.open_csv_conversion_input_action = QAction(
            "Open CSV conversion input folder in file explorer", self
        )
        open_menu.addAction(self.open_csv_conversion_input_action)

        # Path Menu
        self.paths_menu = menu_bar.addMenu("&Path")
        self.paths_menu.addAction(self._add_custom_path_action)

        # Settings Menu
        settings_menu = menu_bar.addMenu("&Settings")
        self.open_paths_manager = QAction("Manage Custom Paths", self)
        settings_menu.addAction(self.open_paths_manager)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        self.xpath_help_action = QAction("XPath Help", self)
        self.xpath_help_action.setStatusTip("Open XPath Syntax Help")
        help_menu.addAction(self.xpath_help_action)

        # Theme Menu
        self.toggle_theme_action = menu_bar.addAction(self.theme_icon, "Toggle Theme")

    def setup_widgets_and_visibility_states(self):
        """Setup widgets states"""
        # Hide buttons/widgets
        self.ui.button_find_next.setHidden(True)
        self.ui.button_find_previous.setHidden(True)
        self.ui.button_abort_csv_export.setHidden(True)
        self.ui.label_file_processing.setHidden(True)
        self.ui.line_edit_xml_output_find_text.setHidden(True)

    def get_thread_pool_status(self) -> str:
        """Get current thread pool status (useful for debugging)."""
        active_count = self.thread_pool.activeThreadCount()
        max_count = self.thread_pool.maxThreadCount()
        return f"Active threads: {active_count}/{max_count}"

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self,
            "Exit Program",
            "Are you sure you want to exit the program?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.No:
            event.ignore()
            return
        else:
            self.settings.setValue("app_theme", self.current_theme)
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue(
                "group_matches", self.ui.checkbox_group_matches.isChecked()
            )
            super().closeEvent(event)


if __name__ == "__main__":
    # Initialize the application
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
