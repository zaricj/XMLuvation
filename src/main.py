# main.py
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QDialog)

from PySide6.QtGui import QIcon, QCloseEvent, QGuiApplication, QAction
from PySide6.QtCore import (
    Qt,
    QFile,
    QTextStream,
    QIODevice,
    QSettings,
    QThreadPool
)

if TYPE_CHECKING:
    from controllers.modules_controller import (
        ComboboxStateHandler, 
        SearchXMLOutputTextHandler,
        SearchAndExportToCSVHandler
    )
    from handlers.config_handler import ConfigHandler

from gui.main.XMLuvation_ui import Ui_MainWindow
from handlers.signal_handlers import SignalHandlerMixin
from utils.helper_methods import HelperMethods
from services.ui_state_manager import UIStateManager
from gui.dialogs.exit_dialog import ExitDialog

# ----------------------------
# Constants
# ----------------------------
CURRENT_DIR = Path(__file__).parent
GUI_CONFIG_DIRECTORY: Path = CURRENT_DIR / "config"
GUI_CONFIG_FILE_PATH: Path = GUI_CONFIG_DIRECTORY / "config.json"

# Dictionary of all theme files in the directory under gui/resources/styles
THEME_FILES: Dict[str, Path] = {
    "dark_theme_default": CURRENT_DIR / "gui" / "resources" / "styles" / "dark_theme.qss",
    "light_theme_default": CURRENT_DIR / "gui" / "resources" / "styles" / "light_theme.qss",
    "dark_theme_yellow": CURRENT_DIR / "gui" / "resources" / "styles" / "other" / "dark_theme_yellow.qss",
    "dark_theme_peach": CURRENT_DIR / "gui" / "resources" / "styles" / "other" / "dark_theme_peach.qss",
    "dark_theme_qlementine": CURRENT_DIR / "gui" / "resources" / "styles" / "other" / "dark_theme_qlementine.qss",
    "dark_theme_metallic_spaceship": CURRENT_DIR / "gui" / "resources" / "styles" / "other" / "dark_theme_metallic_spaceship.qss",
}

# Application icon path
ICON_PATH: Path = CURRENT_DIR / "gui" / "resources" / "icons" / "xml_256px.ico"

# Theme icons for menubar
DARK_THEME_QMENU_ICON: Path = CURRENT_DIR / "gui" / "resources" / "images" / "dark.png"
LIGHT_THEME_QMENU_ICON: Path = CURRENT_DIR / "gui" / "resources" / "images" / "light.png"

# Application versioning and metadata
APP_VERSION: str = "v1.3.5"
APP_NAME: str = "XMLuvation"
AUTHOR: str = "Jovan"

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    ROOT_DIR: str = sys._MEIPASS
else:
    ROOT_DIR: str = os.path.dirname(CURRENT_DIR)


# ----------------------------
# Helpers for window state
# ----------------------------
def save_window_state(window: QMainWindow, settings: QSettings):
    settings.setValue("geometry", window.saveGeometry())
    settings.setValue("windowState", window.saveState())


def restore_window_state(window: QMainWindow, settings: QSettings):
    geometry = settings.value("geometry")
    if geometry:
        window.restoreGeometry(geometry)
    state = settings.value("windowState")
    if state:
        window.restoreState(state)

    # Clamp window into current screen space
    screen = QGuiApplication.primaryScreen()
    available = screen.availableGeometry()
    win_geom = window.frameGeometry()

    if not available.contains(win_geom, proper=False):
        window.resize(
            min(win_geom.width(), available.width()),
            min(win_geom.height(), available.height())
        )
        window.move(
            max(available.left(), min(win_geom.left(), available.right() - window.width())),
            max(available.top(), min(win_geom.top(), available.bottom() - window.height()))
        )


# ----------------------------
# MainWindow class
# ----------------------------
class MainWindow(QMainWindow, SignalHandlerMixin):
    # type hints...
    _parsed_xml_data_ref: Dict[str, Any]
    _current_read_xml_file_ref: Optional[str]
    _csv_exporter_handler_ref: Optional['SearchAndExportToCSVHandler']
    active_workers: List[Any]
    recent_xpath_expressions: List[str]

    settings: QSettings
    thread_pool: QThreadPool
    set_max_threads: int

    cb_state_controller: 'ComboboxStateHandler'
    xml_text_searcher: 'SearchXMLOutputTextHandler'
    config_handler: 'ConfigHandler'
    helper: 'HelperMethods'

    current_theme: str


    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.helper = HelperMethods(main_window=self)

        self._parsed_xml_data_ref = {}
        self._current_read_xml_file_ref = None
        self._csv_exporter_handler_ref = None
        self._main_thread_loading_movie_ref = None

        self.initialize_attributes()
        self.initialize_handlers()  # Initialize specialized handlers
        self.setup_application()
        self.initialize_theme()
        self.setup_widgets_and_visibility_states()

    def initialize_attributes(self):
        from controllers.modules_controller import ComboboxStateHandler
        from controllers.modules_controller import SearchXMLOutputTextHandler
        from handlers.config_handler import ConfigHandler
        
        self.cb_state_controller = ComboboxStateHandler(
            main_window=self,
            parsed_xml_data=self._parsed_xml_data_ref,
            cb_tag_name=self.ui.combobox_tag_names,
            cb_tag_value=self.ui.combobox_tag_values,
            cb_attr_name=self.ui.combobox_attribute_names,
            cb_attr_value=self.ui.combobox_attribute_values,
        )

        self.xml_text_searcher = SearchXMLOutputTextHandler(
            main_window=self,
            line_edit_xml_output_find_text=self.ui.line_edit_xml_output_find_text,
            text_edit_xml_output=self.ui.text_edit_xml_output,
        )
        
        # Initialize UI state manager
        self.ui_state_manager = UIStateManager(main_window=self)
        
        self.settings = QSettings("Jovan", "XMLuvation")


        self.thread_pool = QThreadPool()
        max_threads = self.thread_pool.maxThreadCount()
        self.set_max_threads = max_threads
        self.thread_pool.setMaxThreadCount(max_threads)

        self.active_workers = []
        self.config_handler = ConfigHandler(
            main_window=self,
            config_directory=GUI_CONFIG_DIRECTORY,
            config_file_name=GUI_CONFIG_FILE_PATH,
        )

        self.ui.list_widget_main_xpath_expressions.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.text_edit_xml_output.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.text_edit_program_output.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.text_edit_csv_output.setContextMenuPolicy(Qt.CustomContextMenu)

        # Default theme KEY (must be one of THEME_FILES keys)
        self.current_theme = "dark_theme_default"

        # Load saved settings (this will override current_theme if user saved one)
        self.load_app_settings()
        
    def setup_application(self):
        self.connect_ui_events()
        self.connect_menu_bar_actions()
        self._update_paths_menu()
        self._update_autofill_menu()
        self._update_themes_menu()

    def setup_widgets_and_visibility_states(self):
        # Use UIStateManager for initial setup
        self.ui_state_manager.setup_initial_widget_states()
        
    def initialize_theme(self):
        try:
            # Determine theme files
            theme_path = THEME_FILES.get(self.current_theme, THEME_FILES.get("dark_theme_default"))
            file = QFile(str(theme_path))
            if file.open(QIODevice.ReadOnly | QIODevice.Text):
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.setStyleSheet(stylesheet)
                file.close()
        except Exception as ex:
            QMessageBox.critical(self, "Theme load error", f"Failed to load theme: {ex}")
            
    def initialize_theme_file(self, theme_file_path: Path):
        """Initialize theme from file."""
        try:
            file = QFile(str(theme_file_path))  # Path gets transformed to string as QFile supports strings only
            if not file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
                return
            stream = QTextStream(file)
            stylesheet = stream.readAll()
            self.setStyleSheet(stylesheet)
            file.close()
        except Exception as ex:
            QMessageBox.critical(self, "Theme load error", f"Failed to load theme: {str(ex)}")
            
    # Helper method to save apps settings in a more DRY way
    def _save_app_settings(self):
        # Save the theme KEY (one of THEME_FILES). This is stable vs saving filenames.
        self.settings.setValue("app_theme", self.current_theme)
        self.settings.setValue("group_matches", self.ui.checkbox_group_matches.isChecked())
        self.settings.setValue("prompt_on_exit", self.ui.prompt_on_exit_action.isChecked())
        self.settings.setValue("recent_xpath_expressions", self.recent_xpath_expressions)
        save_window_state(self, self.settings) # Save windows location and state
        # optional: force write to disk
        self.settings.sync()
        
    def load_app_settings(self):
        """Load application settings from QSettings."""
        # Restore geometry safely
        restore_window_state(self, self.settings)

        self.recent_xpath_expressions = self.settings.value(
            "recent_xpath_expressions", type=list
        ) or []

        self._update_recent_xpath_expressions_menu()

        # Current theme setting load (store theme KEY, not filename)
        self.current_theme = self.settings.value("app_theme", "dark_theme_default")
        if self.current_theme not in THEME_FILES:
            self.current_theme = "dark_theme_default"

        self.group_matches_setting = self.settings.value(
            "group_matches",
            self.ui.checkbox_group_matches.isChecked(),
            type=bool
        )
        
        # Group matches checkbox
        self.ui.checkbox_group_matches.setChecked(self.group_matches_setting)

        # Prompt on exit setting load
        prompt_value = self.settings.value("prompt_on_exit",
                                        self.ui.prompt_on_exit_action.isChecked(),
                                        type=bool)
        
        # Apply the setting unconditionally to the QAction
        self.ui.prompt_on_exit_action.setChecked(bool(prompt_value))
        
        # Prompt on exit checkbox in menubar
        prompt_on_exit = self.settings.value(
            "prompt_on_exit",
            self.ui.prompt_on_exit_action.isChecked(),
            type=bool
        )
        self.ui.prompt_on_exit_action.setChecked(prompt_on_exit)

    def closeEvent(self, event: QCloseEvent):
        if self.ui.prompt_on_exit_action.isChecked():
            exit_dialog = ExitDialog(self)
            if exit_dialog.exec() == QDialog.Rejected:
                event.ignore()
                return

            # if user checked "Don't ask again", update the QAction (and settings)
            if exit_dialog.ui.check_box_dont_ask_again.isChecked():
                self.ui.prompt_on_exit_action.setChecked(False)
                self.settings.setValue("prompt_on_exit", False)
                self.settings.sync()

        # always save other app settings once here
        self._save_app_settings()
        super().closeEvent(event)

    # ============= HELPER METHODS =============

    def _add_recent_xpath_expression(self, expression: str):
        """Add XPath expression to recent expressions."""
        MAX_RECENT = 10
        if expression not in self.recent_xpath_expressions:
            self.recent_xpath_expressions.insert(0, expression)
            self.recent_xpath_expressions = self.recent_xpath_expressions[:MAX_RECENT]
            self.settings.setValue("recent_xpath_expressions", self.recent_xpath_expressions)
            self._update_recent_xpath_expressions_menu()

    def _update_recent_xpath_expressions_menu(self):
        """Update recent XPath expressions menu."""
        self.ui.recent_xpath_expressions_menu.clear()
        for expression in self.recent_xpath_expressions:
            action = QAction(expression, self)
            action.triggered.connect(
                lambda checked, exp=expression: self.on_setXPathExpressionInInput(exp)
            )
            self.ui.recent_xpath_expressions_menu.addAction(action)

    # ===== Update Menubars =====
    def _update_paths_menu(self):
        """Update the paths menu with custom paths."""
        self.ui.paths_menu.clear()
        
        custom_paths = self.config_handler.get("custom_paths", {})
        for name, path in custom_paths.items():
            action = QAction(name, self)
            action.setStatusTip(f"Open {name}")
            action.triggered.connect(lambda checked, p=path: self._set_path_in_input(p))
            self.ui.paths_menu.addAction(action)
    
    def _update_autofill_menu(self):
        """Update the autofill menu with custom pre-built xpaths and csv headers"""
        self.ui.menu_autofill.clear()

        custom_autofill = self.config_handler.get("custom_xpaths_autofill", {})
        for key, value in custom_autofill.items():
            action = QAction(key, self)
            action.triggered.connect(
                lambda checked, v=value: self._set_autofill_xpaths_and_csv_headers(
                    v.get("xpath_expression", []),
                    v.get("csv_header", [])
                )
            )
            self.ui.menu_autofill.addAction(action)
            
    def _update_themes_menu(self):
        """Update the themes menu with available themes."""
        self.ui.theme_menu.clear()

        for theme_name, theme_path in THEME_FILES.items():
            action = QAction(theme_name.replace("_", " ").title(), self)
            # Use the theme key so selection persists; call helper to apply and save
            action.triggered.connect(
                lambda checked, key=theme_name: self.set_theme_by_key(key)
            )
            self.ui.theme_menu.addAction(action)
            # Add a separator between right after the light theme, should always be second after the default dark theme
            if theme_name.endswith("light_theme_default"):
                self.ui.theme_menu.addSeparator()

    def set_theme_by_key(self, theme_key: str, save: bool = True):
        """Apply a theme by its key from THEME_FILES and optionally save the choice.

        Args:
            theme_key: key present in THEME_FILES
            save: if True, persist the selection to QSettings
        """
        if theme_key not in THEME_FILES:
            QMessageBox.warning(self, "Theme Error", f"Unknown theme: {theme_key}")
            return

        theme_path = THEME_FILES[theme_key]
        try:
            self.initialize_theme_file(theme_path)
            self.current_theme = theme_key
            if save:
                self._save_app_settings()
        except Exception as ex:
            QMessageBox.critical(self, "Theme Error", f"Failed to set theme {theme_key}: {ex}")
            
    def _set_path_in_input(self, path: str):
        """Set path in input field."""
        self.ui.line_edit_xml_folder_path_input.setText(path)

    def _set_autofill_xpaths_and_csv_headers(self, xpaths: list[str], csv_headers: list[str]):
        """Adds the values for xpaths expressions and csv headers to the main list widget and line edit widget.

        Args:
            xpaths (list[str]): List of xpaths expressions in the config
            csv_headers (list[str]): List of csv headers in the config
        """
        # Clear all existing items in the list widget and csv header input
        self.ui.list_widget_main_xpath_expressions.clear()
        self.ui.line_edit_csv_headers_input.clear()
        
        for xpath in xpaths:
            self.ui.list_widget_main_xpath_expressions.addItem(xpath)
        if csv_headers:
            self.ui.line_edit_csv_headers_input.setText(', '.join(csv_headers))

# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
