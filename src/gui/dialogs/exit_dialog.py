from gui.dialogs.ui.exit_dialog_box_ui import Ui_ExitAppDialog
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Slot, QFile, QIODevice, QTextStream

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.main import MainWindow
    
# Constants
# Determine the path of the current file and resolve it to handle symlinks/etc.
FILE_PATH = Path(__file__).resolve()

# Get the project src directory
SRC_ROOT_DIR = FILE_PATH.parents[3]

class ExitDialog(QDialog):
    def __init__(self, main_window: "MainWindow"):
        super().__init__()
        self.main_window = main_window
        # Create and setup ui from .ui file
        self.ui = Ui_ExitAppDialog()
        self.ui.setupUi(self)
        
        self._initialize_theme()
        
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