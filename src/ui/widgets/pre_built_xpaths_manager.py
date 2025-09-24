from PySide6.QtWidgets import QWidget, QMessageBox, QMainWindow
from PySide6.QtCore import Slot
from pathlib import Path

from modules.config_handler import ConfigHandler
from ui.widgets.PreBuiltXPathsManager_ui import Ui_Form

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.main import MainWindow


CURRENT_DIR = Path(__file__).parent # \XMLuvation\src\ui\widgets
ROOT_DIR = CURRENT_DIR.parent.parent

# Path Constants
GUI_CONFIG_DIRECTORY: Path = ROOT_DIR / "config"
GUI_CONFIG_FILE_PATH: Path = ROOT_DIR / "config" / "config.json"

# Theme files
DARK_THEME_PATH: Path = ROOT_DIR / "resources" / "styles" / "dark_theme.qss"
LIGHT_THEME_PATH: Path = ROOT_DIR / "resources" / "styles" / "light_theme.qss"

ICON_PATH: Path = ROOT_DIR / "resources" / "icons" / "xml_256px.ico"

# Theme file icons
DARK_THEME_QMENU_ICON: Path = ROOT_DIR / "resources" / "images" / "dark.png"
LIGHT_THEME_QMENU_ICON: Path = ROOT_DIR / "resources" / "images" / "light.png"

class PreBuiltXPathsManager(QWidget):
    def __init__(self, main_window: "MainWindow"):
        super().__init__()

        self.main_window = main_window
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
        
        # TODO Continue development, UI file is built.
        # Connect signals/slots
        self.ui.button_pre_built_xpaths_load_config.clicked.connect()
        self.ui.button_pre_built_xpaths_delete_config.clicked.connect()
        self.ui.button_pre_built_remove_selected.clicked.connect()
        self.ui.button_pre_built_remove_all.clicked.connect()