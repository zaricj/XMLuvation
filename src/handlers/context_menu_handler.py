# File: controllers/context_menu_handler.py
"""Handler for context menu events."""
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QKeySequence, Qt, QAction
from PySide6.QtCore import Slot, QPoint
from typing import TYPE_CHECKING

from handlers.keyboard_shortcut_handler import KeyboardShortcutHandler

if TYPE_CHECKING:
    from main import MainWindow


class ContextMenuHandler:
    """Handles all context menu events."""
    
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window
        
    def connect_signals(self):
        """Connect all context menu signals to their handlers."""
        ui = self.main_window.ui
        
        # Connect context menu signals
        ui.list_widget_main_xpath_expressions.customContextMenuRequested.connect(
            self.on_show_xpath_context_menu
        )
        ui.text_edit_xml_output.customContextMenuRequested.connect(
            self.on_show_xml_output_context_menu
        )
        ui.text_edit_program_output.customContextMenuRequested.connect(
            self.on_context_menu_event_program_output
        )
        ui.text_edit_csv_output.customContextMenuRequested.connect(
            self.on_context_menu_event_csv_output
        )
    
    # === Context Menu Handlers ===
    
    @Slot(QPoint)
    def on_show_xpath_context_menu(self, position: QPoint):
        """Show context menu for XPath list widget."""
        menu = QMenu(self.main_window)
        
        remove_selected_action = menu.addAction("Remove Selected")
        remove_all_action = menu.addAction("Remove All")
        
        action = menu.exec_(
            self.main_window.ui.list_widget_main_xpath_expressions.mapToGlobal(position)
        )
        
        if action == remove_selected_action:
            self.remove_selected_xpath_item()
        elif action == remove_all_action:
            self.remove_all_xpath_items()
            
    def remove_selected_xpath_item(self):
        """Remove selected XPath item from list."""
        try:
            current_selected_item = self.main_window.ui.list_widget_main_xpath_expressions.currentRow()
            if current_selected_item != -1:
                item_to_remove = self.main_window.ui.list_widget_main_xpath_expressions.takeItem(current_selected_item)
                self.main_window.ui.text_edit_program_output.append(
                    f"Removed item: {item_to_remove.text()} at row {current_selected_item}"
                )
            else:
                self.main_window.ui.text_edit_program_output.append("No item selected to delete.")
        except IndexError:
            self.main_window.ui.text_edit_program_output.append("Nothing to delete.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.main_window.ui.text_edit_program_output.setText(f"Error removing selected item from list: {message}")

    def remove_all_xpath_items(self):
        """Remove all XPath items from list."""
        try:
            if self.main_window.ui.list_widget_main_xpath_expressions.count() > 0:
                self.main_window.ui.list_widget_main_xpath_expressions.clear()
                self.main_window.ui.text_edit_program_output.setText("Deleted all items from the list.")
                # Clean CSV Header Input if it has any value in it
                if len(self.main_window.ui.line_edit_csv_headers_input.text()) > 1:
                    self.main_window.ui.line_edit_csv_headers_input.clear()
            else:
                self.main_window.ui.text_edit_program_output.setText("No items to delete in list.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.main_window.ui.text_edit_program_output.setText(f"Error removing all items from list: {message}")
    
    @Slot(QPoint)
    def on_show_xml_output_context_menu(self, position: QPoint):
        """Show context menu for XML output text edit."""
        menu = QMenu(self.main_window)
        keyboard_shortcut_handler = KeyboardShortcutHandler(self.main_window)
        copy_action = menu.addAction("Copy")
        select_all_action = menu.addAction("Select All")
        menu.addSeparator()
        # Find action
        find_action = QAction(
            "Find",
            self.main_window,
            shortcut=QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_F),
        )
        menu.addAction(find_action)
        
        action = menu.exec_(
            self.main_window.ui.text_edit_xml_output.mapToGlobal(position)
        )
        
        if action == copy_action:
            self.main_window.ui.text_edit_xml_output.copy()
        elif action == select_all_action:
            self.main_window.ui.text_edit_xml_output.selectAll()
        elif action == find_action:
            keyboard_shortcut_handler.on_toggle_xml_output_search_widgets()

    @Slot(QPoint)
    def on_context_menu_event_program_output(self, position: QPoint):
        """Show context menu for program output text edit."""
        menu = QMenu(self.main_window)
        
        copy_action = menu.addAction("Copy")
        select_all_action = menu.addAction("Select All")
        menu.addSeparator()
        clear_action = menu.addAction("Clear")
        
        action = menu.exec_(
            self.main_window.ui.text_edit_program_output.mapToGlobal(position)
        )
        
        if action == copy_action:
            self.main_window.ui.text_edit_program_output.copy()
        elif action == select_all_action:
            self.main_window.ui.text_edit_program_output.selectAll()
        elif action == clear_action:
            self.main_window.ui.text_edit_program_output.clear()
    
    @Slot(QPoint)
    def on_context_menu_event_csv_output(self, position: QPoint):
        """Show context menu for CSV output text edit."""
        menu = QMenu(self.main_window)
        
        copy_action = menu.addAction("Copy")
        select_all_action = menu.addAction("Select All")
        menu.addSeparator()
        clear_action = menu.addAction("Clear")
        
        action = menu.exec_(
            self.main_window.ui.text_edit_csv_output.mapToGlobal(position)
        )
        
        if action == copy_action:
            self.main_window.ui.text_edit_csv_output.copy()
        elif action == select_all_action:
            self.main_window.ui.text_edit_csv_output.selectAll()
        elif action == clear_action:
            self.main_window.ui.text_edit_csv_output.clear()
