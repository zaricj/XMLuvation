from PySide6.QtGui import QShortcut, QKeySequence, Qt
from PySide6.QtCore import Qt, Slot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow
    
class KeyboardShortcutActionsMixin:
    """Handles menu bar actions only"""
    
    def connect_keyboard_shortcut_actions(self):
        self.shortcut_find = QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_F), self
        )
        self.shortcut_find.activated.connect(self.on_toggleXMLOutputSearchWidgets)
        

    @Slot()
    def on_toggleXMLOutputSearchWidgets(self: "MainWindow"):
        """Toggle XML output search widgets visibility."""
        is_hidden = self.ui.line_edit_xml_output_find_text.isHidden()
        
        self.ui.line_edit_xml_output_find_text.setHidden(not is_hidden)
        self.ui.button_find_next.setHidden(not is_hidden)
        self.ui.button_find_previous.setHidden(not is_hidden)
        
        if not is_hidden:
            self.ui.line_edit_xml_output_find_text.clear()