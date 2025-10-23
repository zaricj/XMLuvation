# File: modules/signal_handlers.py
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt, Slot, QPoint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

class ContextMenuMixin:
    """Handles context menu events only"""
    
    def connect_context_menus(self: "MainWindow"):
        self.ui.list_widget_main_xpath_expressions.customContextMenuRequested.connect(self.on_showXPathContextMenu)
        self.ui.text_edit_xml_output.customContextMenuRequested.connect(self.on_showXMLOutputContextMenu)
        
        # Context menu signals for program output and csv output
        self.ui.text_edit_program_output.customContextMenuRequested.connect(self.on_contextMenuEventProgramOutput)
        self.ui.text_edit_csv_output.customContextMenuRequested.connect(self.on_contextMenuEventCSVOutput)
        

    @Slot(QPoint)
    def on_showXPathContextMenu(self: "MainWindow", position: QPoint):
        """Show context menu for XPath expressions list."""
        context_menu = QMenu(self)
        remove_action = QAction("Remove Selected", self)
        remove_all_action = QAction("Remove All", self)

        context_menu.addAction(remove_action)
        context_menu.addAction(remove_all_action)

        remove_action.triggered.connect(self.remove_selected_xpath_item)
        remove_all_action.triggered.connect(self.remove_all_xpath_items)

        context_menu.exec(self.ui.list_widget_main_xpath_expressions.mapToGlobal(position))
        
    @Slot(QPoint)
    def on_showXMLOutputContextMenu(self: "MainWindow", position: QPoint):
        """Show context menu for XML output."""
        menu = self.ui.text_edit_xml_output.createStandardContextMenu()
        # Find action
        find_action = QAction(
            "Find",
            self,
            shortcut=QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_F),
        )
        find_action.triggered.connect(self.on_toggleXMLOutputSearchWidgets)
        menu.addAction(find_action)

        menu.exec(self.ui.text_edit_xml_output.mapToGlobal(position))
        
    @Slot(QPoint) # For the main Program Output Text Edit
    def on_contextMenuEventProgramOutput(self: "MainWindow", position: QPoint):
        # Create standard context menu for Text Edit
        menu = self.ui.text_edit_program_output.createStandardContextMenu()
        
        # Clear output action
        clear_output_action = QAction("Clear output", self)
        clear_output_action.triggered.connect(lambda: self.on_clearOutput(self.ui.text_edit_program_output))
        
        # Add clear output action to standard QMenu (context menu)
        menu.addAction(clear_output_action)
        # Map the position of the context menu to the mouse position
        menu.exec(self.ui.text_edit_program_output.mapToGlobal(position))
        
    @Slot(QPoint) # For the CSV Output Text Edit
    def on_contextMenuEventCSVOutput(self: "MainWindow", position: QPoint):
        # Create standard context menu for Text Edit
        menu = self.ui.text_edit_csv_output.createStandardContextMenu()
        
        # Clear output action
        clear_output_action = QAction("Clear output", self)
        clear_output_action.triggered.connect(lambda: self.on_clearOutput(self.ui.text_edit_csv_output))
        
        # Add clear output action to standard QMenu (context menu)
        menu.addAction(clear_output_action)
        # Map the position of the context menu to the mouse position
        menu.exec(self.ui.text_edit_csv_output.mapToGlobal(position))
        
    def remove_selected_xpath_item(self: "MainWindow"):
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

    def remove_all_xpath_items(self: "MainWindow"):
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