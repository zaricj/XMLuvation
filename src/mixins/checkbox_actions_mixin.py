from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

class CheckboxActionsMixin:
    """Handles checkbox actions only"""
    
    def connect_checkbox_actions(self: "MainWindow"):
        self.ui.checkbox_write_index_column.toggled.connect(self.on_writeIndexCheckBoxToggled)
        self.ui.checkbox_group_matches.toggled.connect(self.on_groupMatchesCheckBoxToggled)
        

    @Slot()
    def on_writeIndexCheckBoxToggled(self: "MainWindow"):
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
            if self.ui.checkbox_write_index_column.isChecked():
                self.ui.text_edit_csv_output.setText(message_with_index)
            else:
                self.ui.text_edit_csv_output.setText(message_without_index)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", f"An error occurred: {message}")
    
    @Slot()
    def on_groupMatchesCheckBoxToggled(self: "MainWindow"):
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
            if self.ui.checkbox_group_matches.isChecked():
                self.ui.text_edit_program_output.setText(
                    f"Group Matches is enabled. All matches for each XPath expression will be grouped together in the CSV output.\n{example_on}"
                )
            else:
                self.ui.text_edit_program_output.setText(
                    f"Group Matches is disabled. Each match will be listed separately in the CSV output.\n{example_off}"
                )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", f"An error occurred: {message}")