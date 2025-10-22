from PySide6.QtWidgets import QMessageBox, QFileDialog, QLineEdit


class HelperMethods:
    def __init__(self, main_window):
        """Accepts a reference to the main window so dialogs have a valid parent."""
        self.main_window = main_window

    def _browse_folder_helper(self, dialog_message: str, line_widget: QLineEdit):
        """Helper for folder browsing dialogs."""
        try:
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

    def _browse_file_helper(
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
                "An exception occurred in browse folder method",
                message,
            )

    def _browse_save_file_as_helper(
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
