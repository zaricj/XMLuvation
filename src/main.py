# main.py
# REMOVE WHEN PROD READY:
from fix_qrc_import import fix_qrc_import
fix_qrc_import()
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QDialog
)
from PySide6.QtGui import QIcon, QCloseEvent
from PySide6.QtCore import (
    Qt,
    QFile,
    QTextStream,
    QIODevice,
    QSettings,
    QThreadPool,
)
from PySide6.QtGui import QGuiApplication

if TYPE_CHECKING:
    from controllers.state_controller import (
        ComboboxStateHandler, 
        SearchXMLOutputTextHandler,
        SearchAndExportToCSVHandler
    )
    from modules.config_handler import ConfigHandler

from gui.main.XMLuvation_ui import Ui_MainWindow
from controllers.signal_handlers import SignalHandlerMixin
from dialogs.exit_dialog import ExitDialog
    

# ----------------------------
# Constants
# ----------------------------
CURRENT_DIR = Path(__file__).parent
GUI_CONFIG_DIRECTORY: Path = CURRENT_DIR / "config"
GUI_CONFIG_FILE_PATH: Path = GUI_CONFIG_DIRECTORY / "config.json"

DARK_THEME_PATH: Path = CURRENT_DIR / "resources" / "styles" / "dark_theme_redesign.qss"
LIGHT_THEME_PATH: Path = CURRENT_DIR / "resources" / "styles" / "light_theme.qss"

ICON_PATH: Path = CURRENT_DIR / "resources" / "icons" / "xml_256px.ico"

DARK_THEME_QMENU_ICON: Path = CURRENT_DIR / "resources" / "images" / "dark.png"
LIGHT_THEME_QMENU_ICON: Path = CURRENT_DIR / "resources" / "images" / "light.png"

APP_VERSION: str = "v1.3.2"
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
    parsed_xml_data: Dict[str, Any]
    current_read_xml_file: Optional[str]
    csv_exporter_handler: Optional['SearchAndExportToCSVHandler']
    xpath_filters: List[str]
    active_workers: List[Any]
    recent_xpath_expressions: List[str]

    settings: QSettings
    thread_pool: QThreadPool
    set_max_threads: int

    cb_state_controller: 'ComboboxStateHandler'
    xml_text_searcher: 'SearchXMLOutputTextHandler'
    config_handler: 'ConfigHandler'

    current_theme: str
    dark_theme_file: str
    light_theme_file: str

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")

        self.initialize_attributes()
        self.setup_application()
        self._initialize_theme()
        self.setup_widgets_and_visibility_states()

    def initialize_attributes(self):
        from controllers.state_controller import ComboboxStateHandler
        from controllers.state_controller import SearchXMLOutputTextHandler
        from modules.config_handler import ConfigHandler

        self.parsed_xml_data = {}
        self.current_read_xml_file = None
        self.csv_exporter_handler = None

        self.cb_state_controller = ComboboxStateHandler(
            main_window=self,
            parsed_xml_data=self.parsed_xml_data,
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
        self.xpath_filters = []
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

# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
