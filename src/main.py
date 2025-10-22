# main.py
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QDialog,
    QListWidget
)
from PySide6.QtGui import QIcon, QCloseEvent, QGuiApplication, QAction, QDesktopServices
from PySide6.QtCore import (
    Qt,
    QFile,
    QUrl,
    QTextStream,
    QIODevice,
    QSettings,
    QThreadPool,
)

if TYPE_CHECKING:
    from controllers.state_controller import (
        ComboboxStateHandler, 
        SearchXMLOutputTextHandler,
        SearchAndExportToCSVHandler
    )
    from modules.config_handler import ConfigHandler

from gui.main.XMLuvation_ui import Ui_MainWindow
from controllers.signal_handlers import SignalHandlerMixin
from controllers.helper_methods import HelperMethods
from dialogs.exit_dialog import ExitDialog

# ----------------------------
# Constants
# ----------------------------
CURRENT_DIR = Path(__file__).parent
GUI_CONFIG_DIRECTORY: Path = CURRENT_DIR / "config"
GUI_CONFIG_FILE_PATH: Path = GUI_CONFIG_DIRECTORY / "config.json"

DARK_THEME_PATH: Path = CURRENT_DIR / "resources" / "styles" / "dark_theme.qss"
LIGHT_THEME_PATH: Path = CURRENT_DIR / "resources" / "styles" / "light_theme.qss"

ICON_PATH: Path = CURRENT_DIR / "resources" / "icons" / "xml_256px.ico"

DARK_THEME_QMENU_ICON: Path = CURRENT_DIR / "resources" / "images" / "dark.png"
LIGHT_THEME_QMENU_ICON: Path = CURRENT_DIR / "resources" / "images" / "light.png"

APP_VERSION: str = "v1.3.3"
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
    dark_theme_file: str
    light_theme_file: str

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
        self.setup_application()
        self._initialize_theme()
        self.setup_widgets_and_visibility_states()

    def initialize_attributes(self):
        from controllers.state_controller import ComboboxStateHandler
        from controllers.state_controller import SearchXMLOutputTextHandler
        from modules.config_handler import ConfigHandler

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

        self.settings = QSettings("Jovan", "XMLuvation")

        # Restore geometry safely
        restore_window_state(self, self.settings)

        self.recent_xpath_expressions = self.settings.value(
            "recent_xpath_expressions", type=list
        ) or []

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

        self.light_mode_icon = QIcon(str(LIGHT_THEME_QMENU_ICON))
        self.dark_mode_icon = QIcon(str(DARK_THEME_QMENU_ICON))

        self.dark_theme_file = str(DARK_THEME_PATH)
        self.light_theme_file = str(LIGHT_THEME_PATH)

        self.current_theme = self.settings.value("app_theme", "dark_theme.qss")

        self.group_matches_setting = self.settings.value(
            "group_matches",
            self.ui.checkbox_group_matches.isChecked(),
            type=bool
        )
        # Apply the setting unconditionally to the checkbox
        self.ui.checkbox_group_matches.setChecked(self.group_matches_setting)

        # Current theme setting load
        if self.current_theme == "dark_theme.qss":
            self.theme_icon = self.light_mode_icon
        else:
            self.theme_icon = self.dark_mode_icon
        
        # Prompt on exit setting load
        prompt_value = self.settings.value("prompt_on_exit",
                                        self.ui.prompt_on_exit_action.isChecked(),
                                        type=bool)
        # Apply the setting unconditionally to the QAction
        self.ui.prompt_on_exit_action.setChecked(bool(prompt_value))
        
    def _initialize_theme_file(self, theme_file: str):
        """Initialize theme from file."""
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

    def _initialize_theme(self):
        try:
            theme_file = (
                self.dark_theme_file
                if self.current_theme == "dark_theme.qss"
                else self.light_theme_file
            )
            file = QFile(theme_file)
            if file.open(QIODevice.ReadOnly | QIODevice.Text):
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.setStyleSheet(stylesheet)
                file.close()
        except Exception as ex:
            QMessageBox.critical(self, "Theme load error", f"Failed to load theme: {ex}")

    def setup_application(self):
        self.connect_ui_events()
        self.connect_menu_bar_actions()
        self._update_paths_menu()
        self._update_autofill_menu()

    def setup_widgets_and_visibility_states(self):
        self.ui.button_find_next.hide()
        self.ui.button_find_previous.hide()
        self.ui.button_abort_csv_export.hide()
        self.ui.progressbar_main.hide()
        self.ui.label_file_processing.hide()
        self.ui.line_edit_xml_output_find_text.hide()
        
    # Helper method to save apps settings in a more DRY way
    def _save_app_settings(self):
        self.settings.setValue("app_theme", self.current_theme)
        self.settings.setValue("group_matches", self.ui.checkbox_group_matches.isChecked())
        self.settings.setValue("prompt_on_exit", self.ui.prompt_on_exit_action.isChecked())
        save_window_state(self, self.settings) # Save windows location and state
        # optional: force write to disk
        self.settings.sync()

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



    def _parse_xml_file(self, xml_file_path: str):
        """Parse XML file and display content."""
        try:
            from controllers.state_controller import ParseXMLFileHandler
            
            xml_parser = ParseXMLFileHandler(main_window=self, xml_file_path=xml_file_path)
            xml_parser.start_xml_parsing()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception on starting to parse xml file", message)

    def _open_folder_in_file_explorer(self, folder_path: str):
        """Helper method to open folder in file explorer."""
        if folder_path and os.path.exists(folder_path):
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "An exception occurred", message)
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Path does not exist or is not a valid path:\n{folder_path}"
            )

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

    def _remove_selected_xpath_item(self):
        """Remove selected XPath item from list."""
        try:
            current_selected_item = self.ui.list_widget_main_xpath_expressions.currentRow()
            if current_selected_item != -1:
                item_to_remove = self.ui.list_widget_main_xpath_expressions.takeItem(current_selected_item)
                self.ui.text_edit_program_output.append(
                    f"Removed item: {item_to_remove.text()} at row {current_selected_item}"
                )
            else:
                self.ui.text_edit_program_output.append("No item selected to delete.")
        except IndexError:
            self.ui.text_edit_program_output.append("Nothing to delete.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.text_edit_program_output.setText(f"Error removing selected item from list: {message}")

    def _remove_all_xpath_items(self):
        """Remove all XPath items from list."""
        try:
            if self.ui.list_widget_main_xpath_expressions.count() > 0:
                self.ui.list_widget_main_xpath_expressions.clear()
                self.ui.text_edit_program_output.setText("Deleted all items from the list.")
                # Clean CSV Header Input if it has any value in it
                if len(self.ui.line_edit_csv_headers_input.text()) > 1:
                    self.ui.line_edit_csv_headers_input.clear()
            else:
                self.ui.text_edit_program_output.setText("No items to delete in list.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.text_edit_program_output.setText(f"Error removing all items from list: {message}")

    def _listwidget_to_list(self, widget: QListWidget) -> list[str]:
        """Helper method to convert QItems from a specified QListWidget to a list of strings.

        Args:
            widget (QListWidget): The specified list widget.

        Returns:
            list[str]: Returns a list of QItems from a QListWidget as strings.
        """
        return [widget.item(i).text() for i in range(widget.count())]

# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
