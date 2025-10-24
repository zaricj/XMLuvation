# File: controllers/keyboard_shortcut_handler.py
"""Handler for keyboard shortcuts."""
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt, Slot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


class KeyboardShortcutHandler:
    """Handles all keyboard shortcuts."""
    
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window
        
    def connect_signals(self):
        """Connect all keyboard shortcuts to their handlers."""
        # Ctrl+F for search
        self.shortcut_find = QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_F), 
            self.main_window
        )
        self.shortcut_find.activated.connect(self.on_toggle_xml_output_search_widgets)
    
    @Slot()
    def on_toggle_xml_output_search_widgets(self):
        """Toggle XML output search widgets visibility."""
        self.main_window.ui_state_manager.toggle_search_widgets_visibility()
