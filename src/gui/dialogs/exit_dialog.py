from gui.dialogs.ui.exit_dialog_box_ui import Ui_ExitAppDialog
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import QFile, QIODevice, QTextStream
from typing import Dict

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.main import MainWindow
    
# Constants
# Determine the path of the current file and resolve it to handle symlinks/etc.
FILE_PATH = Path(__file__).resolve()
# Get the project src directory
SRC_ROOT_DIR = FILE_PATH.parents[2]

# Dictionary of all theme files in the directory under gui/resources/styles
THEME_FILES: Dict[str, Path] = {
    "dark_theme_default": SRC_ROOT_DIR / "gui" / "resources" / "styles" / "dark_theme.qss",
    "light_theme_default": SRC_ROOT_DIR / "gui" / "resources" / "styles" / "light_theme.qss",
    "dark_theme_yellow": SRC_ROOT_DIR / "gui" / "resources" / "styles" / "other" / "dark_theme_yellow.qss",
    "dark_theme_peach": SRC_ROOT_DIR / "gui" / "resources" / "styles" / "other" / "dark_theme_peach.qss",
    "dark_theme_qlementine": SRC_ROOT_DIR / "gui" / "resources" / "styles" / "other" / "dark_theme_qlementine.qss",
    "dark_theme_metallic_spaceship": SRC_ROOT_DIR / "gui" / "resources" / "styles" / "other" / "dark_theme_metallic_spaceship.qss",
}

class ExitDialog(QDialog):
    def __init__(self, main_window: "MainWindow"):
        super().__init__()
        self.main_window = main_window
        # Create and setup ui from .ui file
        self.ui = Ui_ExitAppDialog()
        self.ui.setupUi(self)
        
        self.initialize_theme()
        
    def initialize_theme(self):
        try:
            # Determine theme files
            theme_path = THEME_FILES.get(self.main_window.current_theme, THEME_FILES.get("dark_theme_default"))
            file = QFile(str(theme_path))
            if file.open(QIODevice.ReadOnly | QIODevice.Text):
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.setStyleSheet(stylesheet)
                file.close()
        except Exception as ex:
            QMessageBox.critical(self, "Theme load error", f"Failed to load theme: {ex}")