# File: modules/signal_handlers.py
import os
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

class LineEditActionsMixin:
    """Handles menu bar actions only"""
    
    def connect_line_edit_actions(self: "MainWindow"):
        self.ui.line_edit_xml_folder_path_input.textChanged.connect(self.on_XMLFolderPathChanged)
        self.ui.line_edit_profile_cleanup_csv_file_path.textChanged.connect(self.on_CSVProfileCleanupInputChanged)
        self.ui.line_edit_filter_table.textChanged.connect(self.on_filterTable)
        
    @Slot()
    def on_XMLFolderPathChanged(self: "MainWindow"):
        """Update XML file count when folder path changes."""
        try:
            folder = self.ui.line_edit_xml_folder_path_input.text()
            if os.path.isdir(folder):
                xml_files_count = sum(
                    1 for f in os.listdir(folder) if f.endswith(".xml")
                )
                if xml_files_count >= 1:
                    self.ui.statusbar_xml_files_count.setText(
                        f"Found {xml_files_count} XML Files"
                    )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.statusbar_xml_files_count.setText(
                f"Error counting XML files: {message}"
            )

    @Slot()
    def on_CSVProfileCleanupInputChanged(self: "MainWindow"):
        """Handle CSV profile cleanup input changes."""
        from controllers.state_controller import CSVColumnDropHandler
        
        csv_file_path = self.ui.line_edit_profile_cleanup_csv_file_path.text()
        column_to_drop = self.ui.combobox_csv_headers.currentText()
        column_to_drop_index = self.ui.combobox_csv_headers.currentIndex()
        csv_header_combobox = self.ui.combobox_csv_headers
        drop_header_button = self.ui.button_drop_csv_header

        handler = CSVColumnDropHandler(
            main_window=self,
            csv_file_path=csv_file_path,
            column_to_drop=column_to_drop,
            column_to_drop_index=column_to_drop_index,
            csv_header_combobox=csv_header_combobox,
            drop_header_button=drop_header_button,
        )
        handler.on_csv_input_file_path_changed()
        
    @Slot()
    def on_filterTable(self: "MainWindow", text: str):
        """Filter QTableView rows based on the search text"""
        text = text.strip().lower()

        for row in range(self.ui.table_csv_data.rowCount()):
            row_match = False
            for col in range(self.ui.table_csv_data.columnCount()):
                item = self.ui.table_csv_data.item(row, col)
                if item and text in item.text().lower():
                    row_match = True
                    break

            self.ui.table_csv_data.setRowHidden(row, not row_match)