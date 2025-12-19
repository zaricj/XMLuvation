from PySide6.QtWidgets import QMessageBox, QFileDialog, QLineEdit
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from main import MainWindow

class HelperMethods:
    def __init__(self, main_window: "MainWindow" ):
        """Accepts a reference to the main window so dialogs have a valid parent."""
        self.main_window = main_window
        self.ui = self.main_window.ui
        
    def open_folder_in_file_explorer(self, folder_path: str):
        """Helper method to open folder in file explorer."""
        if folder_path and os.path.exists(folder_path):
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self.main_window, "An exception occurred", message)
        else:
            self.main_window.ui.text_edit_program_output.setText(f"Invalid or missing path: Could not open directory: {folder_path}")

    def open_file_directly(self, file_path: str):
        """Helper method to open file in default application."""
        if file_path and os.path.exists(file_path):
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self.main_window, "An exception occurred", message)
        else:
            self.main_window.ui.text_edit_program_output.setText(f"Invalid or missing path: Could not open file: {file_path}")

    def browse_folder_helper(self, dialog_message: str, line_widget: QLineEdit):
        """Helper for folder browsing dialogs."""
        try:
            input_text = line_widget.text()
            if len(input_text) > 0:
                folder = QFileDialog.getExistingDirectory(self.main_window, dialog_message, input_text)
            else:
                folder = QFileDialog.getExistingDirectory(self.main_window, dialog_message)
            if folder:
                line_widget.setText(folder)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window,
                "An exception occurred in browse folder method",
                message,
            )

    def browse_file_helper_non_input(self, dialog_message: str, file_extension_filter: str) -> str:
        """Helper for file browsing dialogs.
        
        Returns:
            Path of selected file as string.
        """
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self.main_window, caption=dialog_message, filter=file_extension_filter
            )
            if file_name:
                return file_name
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window,
                "An exception occurred in browse file method",
                message,
            )

    def browse_file_helper(
        self, dialog_message: str, line_widget: QLineEdit, file_extension_filter: str
    ):
        """Helper for file browsing dialogs."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self.main_window, caption=dialog_message, filter=file_extension_filter
            )
            if file_name:
                line_widget.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window,
                "An exception occurred in browse file method",
                message,
            )

    def browse_save_file_as_helper(
        self,
        dialog_message: str,
        line_widget: QLineEdit,
        file_extension_filter: str,
        filename_placeholder: str = "",
    ):
        """Helper for save file dialogs."""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self.main_window,
                caption=dialog_message,
                dir=filename_placeholder,
                filter=file_extension_filter,
            )
            if file_name:
                line_widget.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window,
                "An exception occurred in browse save file method",
                message,
            )
