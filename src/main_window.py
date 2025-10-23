from mixins.menu_actions_mixin import MenuActionsMixin
from mixins.button_actions_mixin import ButtonActionsMixin
from mixins.context_menu_mixin import ContextMenuMixin
from mixins.signal_slots_mixin import SignalSlotsMixin
from mixins.line_edit_actions_mixin import LineEditActionsMixin
from mixins.keyboard_shortcut_actions_mixin import KeyboardShortcutActionsMixin
from mixins.checkbox_actions_mixin import CheckboxActionsMixin
from mixins.combobox_actions_mixin import ComboboxActionsMixin

import sys
import os
from pathlib import Path
import pandas as pd
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QDialog,
    QListWidget,
    QTableWidgetItem)

from PySide6.QtGui import QIcon, QCloseEvent, QGuiApplication, QAction, QDesktopServices
from PySide6.QtCore import (
    Qt,
    QFile,
    QUrl,
    QTextStream,
    QIODevice,
    QSettings,
    QThreadPool
)

if TYPE_CHECKING:
    from controllers.state_controller import (
        ComboboxStateHandler, 
        SearchXMLOutputTextHandler,
        SearchAndExportToCSVHandler
    )
    from modules.config_handler import ConfigHandler

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

class MainWindow(QMainWindow, 
                 MenuActionsMixin, 
                 ButtonActionsMixin, 
                 ContextMenuMixin,
                 SignalSlotsMixin,
                 LineEditActionsMixin,
                 KeyboardShortcutActionsMixin,
                 CheckboxActionsMixin):
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Initialize controllers
        self._init_controllers()
        
        # Connect all signals
        self.connect_menu_actions()
        self.connect_button_actions()
        self.connect_context_menus()
    
    def _init_controllers(self):
        """Initialize all controllers"""
        from controllers.xml_controller import XMLController
        from controllers.csv_controller import CSVController
        
        self.xml_controller = XMLController(self)
        self.csv_controller = CSVController(self)
        

    # Delegate to controllers
    def on_browseXMLFolder(self):
        self.xml_controller.browse_xml_folder()
    
    def on_readXMLFile(self):
        self.xml_controller.read_xml_file()
    
    def on_startCSVSearch(self):
        self.csv_controller.start_csv_export()
    
    def on_stopCSVSearch(self):
        self.csv_controller.stop_csv_export()