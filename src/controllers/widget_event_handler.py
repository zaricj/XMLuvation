# File: controllers/widget_event_handler.py
"""Handler for widget events (ComboBox, LineEdit, CheckBox)."""
import os
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMessageBox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


class WidgetEventHandler:
    """Handles all widget events (comboboxes, line edits, checkboxes)."""
    
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window
        
    def connect_signals(self):
        """Connect all widget events to their handlers."""
        ui = self.main_window.ui
        
        # Line Edit events
        ui.line_edit_xml_folder_path_input.textChanged.connect(self.on_xml_folder_path_changed)
        ui.line_edit_profile_cleanup_csv_file_path.textChanged.connect(self.on_csv_profile_cleanup_input_changed)
        ui.line_edit_filter_table.textChanged.connect(self.on_filter_table)
        
        # ComboBox events
        ui.combobox_tag_names.currentTextChanged.connect(
            self.main_window.cb_state_controller.on_tag_name_changed
        )
        ui.combobox_attribute_names.currentTextChanged.connect(
            self.main_window.cb_state_controller.on_attribute_name_changed
        )
        
        # CheckBox events
        ui.checkbox_write_index_column.toggled.connect(self.on_write_index_checkbox_toggled)
        ui.checkbox_group_matches.toggled.connect(self.on_group_matches_checkbox_toggled)
    
    # === Widget Event Handlers ===
    
    @Slot()
    def on_xml_folder_path_changed(self):
        """Update XML file count when folder path changes."""
        try:
            folder = self.main_window.ui.line_edit_xml_folder_path_input.text()
            if os.path.isdir(folder):
                xml_files_count = sum(
                    1 for f in os.listdir(folder) if f.endswith(".xml")
                )
                if xml_files_count >= 1:
                    self.main_window.ui.statusbar_xml_files_count.setText(
                        f"Found {xml_files_count} XML Files"
                    )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.main_window.ui.statusbar_xml_files_count.setText(
                f"Error counting XML files: {message}"
            )
    
    @Slot()
    def on_csv_profile_cleanup_input_changed(self):
        """Handle CSV profile cleanup input changes."""
        from controllers.modules_controller import CSVColumnDropHandler
        
        csv_file_path = self.main_window.ui.line_edit_profile_cleanup_csv_file_path.text()
        column_to_drop = self.main_window.ui.combobox_csv_headers.currentText()
        column_to_drop_index = self.main_window.ui.combobox_csv_headers.currentIndex()
        csv_header_combobox = self.main_window.ui.combobox_csv_headers
        drop_header_button = self.main_window.ui.button_drop_csv_header

        handler = CSVColumnDropHandler(
            main_window=self.main_window,
            csv_file_path=csv_file_path,
            column_to_drop=column_to_drop,
            column_to_drop_index=column_to_drop_index,
            csv_header_combobox=csv_header_combobox,
            drop_header_button=drop_header_button,
        )
        handler.on_csv_input_file_path_changed()
    
    @Slot(str)
    def on_filter_table(self, text: str):
        """Filter QTableView rows based on the search text."""
        text = text.strip().lower()

        for row in range(self.main_window.ui.table_csv_data.rowCount()):
            row_match = False
            for col in range(self.main_window.ui.table_csv_data.columnCount()):
                item = self.main_window.ui.table_csv_data.item(row, col)
                if item and text in item.text().lower():
                    row_match = True
                    break

            self.main_window.ui.table_csv_data.setRowHidden(row, not row_match)
    
    @Slot()
    def on_write_index_checkbox_toggled(self):
        """Handle write index checkbox toggle."""
        message_with_index = """
        Data will look like this:

        | Index           | Header 1   | Header 2    |
        |-------------------|-------------------|-------------------|
        | 1                  | Data...         | Data...        |
        """
        message_without_index = """
        Data will look like this:

        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Data...         |
        """
        try:
            if self.main_window.ui.checkbox_write_index_column.isChecked():
                self.main_window.ui.text_edit_csv_output.setText(message_with_index)
            else:
                self.main_window.ui.text_edit_csv_output.setText(message_without_index)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception in Program", f"An error occurred: {message}")
            
    @Slot()
    def on_group_matches_checkbox_toggled(self):
        """Handle group matches checkbox toggle."""
        example_on = """
        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Match 1; Match 2; Match 3 |"""
        
        example_off = """
        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Match 1         |
        | Data...       | Match 2         |
        | Data...       | Match 3         |"""
        
        try:
            if self.main_window.ui.checkbox_group_matches.isChecked():
                self.main_window.ui.text_edit_program_output.setText(
                    f"Group Matches is enabled. All matches for each XPath expression will be grouped together in the CSV output.\n{example_on}"
                )
            else:
                self.main_window.ui.text_edit_program_output.setText(
                    f"Group Matches is disabled. Each match will be listed separately in the CSV output.\n{example_off}"
                )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception in Program", f"An error occurred: {message}")
