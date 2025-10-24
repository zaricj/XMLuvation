# File: controllers/context_menu_handler.py
"""Handler for context menu events."""
from PySide6.QtWidgets import QMenu, QMessageBox
from PySide6.QtCore import Slot, QPoint
from typing import TYPE_CHECKING

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
            self.main_window._remove_selected_xpath_item()
        elif action == remove_all_action:
            self.main_window._remove_all_xpath_items()
    
    @Slot(QPoint)
    def on_show_xml_output_context_menu(self, position: QPoint):
        """Show context menu for XML output text edit."""
        menu = QMenu(self.main_window)
        
        copy_action = menu.addAction("Copy")
        select_all_action = menu.addAction("Select All")
        menu.addSeparator()
        clear_action = menu.addAction("Clear")
        
        action = menu.exec_(
            self.main_window.ui.text_edit_xml_output.mapToGlobal(position)
        )
        
        if action == copy_action:
            self.main_window.ui.text_edit_xml_output.copy()
        elif action == select_all_action:
            self.main_window.ui.text_edit_xml_output.selectAll()
        elif action == clear_action:
            self.main_window.ui.text_edit_xml_output.clear()
    
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
