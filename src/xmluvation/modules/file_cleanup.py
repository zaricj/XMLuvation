from PySide6.QtCore import QObject, QRunnable, Signal, Slot
import pandas as pd
import os
import csv


class FileCleanupSignals(QObject):
    """Signals class for FileCleanupThread operations."""

    error_occurred = Signal(str, str)  # QMessageBox.critical
    warning_occurred = Signal(str, str)  # QMessageBox.warning
    program_output_progress_append = Signal(str)  # Program Output aka self.ui.text_edit_program_output.append
    program_output_progress_set_text = Signal(str)  # Program Output aka self.ui.text_edit_program_output.setText
    column_dropped_successfully = Signal(int) # Indicate column drop completion


class FileCleanupThread(QRunnable):
    """Worker thread for cleaning up lobster profile export which is XML files."""

    def __init__(self, operation: str, csv_file_path: str = None, profiles_folder_path: str = None, column_to_drop: str = None, column_to_drop_index: int = None):
        super().__init__()
        self.operation = operation
        self.signals = FileCleanupSignals()
        self.setAutoDelete(True)

        # Operation parameters
        self.csv_file_path: str = csv_file_path
        self.profiles_folder_path: str = profiles_folder_path
        self.column_to_drop: str = column_to_drop
        self.column_to_drop_index: int = column_to_drop_index

    @Slot()
    def run(self):
        """Main execution method that routes to specific operations."""
        try:
            if self.operation == "cleanup":
                self._cleanup_files_matching_in_csv()
            elif self.operation == "drop_csv_column":
                self._drop_column()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")

        except Exception as e:
            self.signals.error_occurred.emit("Operation Error", f"{str(e)}")

    def _drop_column(self) -> None:
        if not self.csv_file_path:
            self.signals.warning_occurred.emit("CSV file not found", "Please select a CSV file first.")
            return

        selected_column = self.column_to_drop
        column_index = self.column_to_drop_index

        if not selected_column:
            self.signals.warning_occurred.emit("Header not selected", "Please select a header from the combobox first.")
            return

        try:
            self.signals.program_output_progress_append.emit(f"Attempting to drop column '{selected_column}' from '{self.csv_file_path}'...")
            # Read the CSV file into a pandas data frame
            data = pd.read_csv(self.csv_file_path)
            
            # Check if header has been selected from the combobox
            if selected_column not in data.columns:
                self.signals.warning_occurred.emit("Column Not Found", f"Column '{selected_column}' does not exist in the CSV file.")
                return
            
            # Drop selected column from the combobox
            data.drop(selected_column, inplace=True, axis=1)
            # Save the modified DataFrame back to the CSV
            data.to_csv(self.csv_file_path, index=False) 

            self.signals.program_output_progress_append.emit(f"Successfully dropped column '{selected_column}' and saved the updated CSV.")
            self.signals.column_dropped_successfully.emit(column_index) # Emit the columns index to remove from the combo box
        except pd.errors.EmptyDataError:
            self.signals.error_occurred.emit("CSV Error", "The CSV file is empty or malformed.")
        except FileNotFoundError:
            self.signals.error_occurred.emit("File Error", f"CSV file not found at '{self.csv_file_path}'.")
        except Exception as e:
            self.signals.error_occurred.emit("CSV Operation Failed", f"An error occurred while dropping the column: {str(e)}")

    def _cleanup_files_matching_in_csv(self):
        """
        Deletes files from the selected folder if their names match entries in the csv file.
        """

        if not self.csv_file_path:
            self.signals.warning_occurred.emit("CSV file not found",
                                               "Please select the CSV file that contains the current export of all Lobster profiles")
            return

        if not self.profiles_folder_path:
            self.signals.warning_occurred.emit("Folder path not found",
                                               "Please select the folder that contains all exported Lobster profiles as XML files")
            return

        with open(self.csv_file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Check if the row is not empty
                    file_name = row[0].strip()  # Get the first column value
                    # Add .xml extension if not present to file names
                    if not file_name.endswith('.xml'):
                        file_name += '.xml'
                    to_delete = os.path.join(self.profiles_folder_path, file_name)
                    if os.path.isfile(to_delete):
                        try:
                            os.unlink(to_delete)
                            self.signals.program_output_progress_append.emit(f"Deleted file: '{to_delete}'")
                        except Exception as e:
                            self.signals.program_output_progress_append.emit(f"Failed to delete '{to_delete}': {e}")
                    else:
                        self.signals.program_output_progress_append.emit(f"File not found, skipping: '{to_delete}'")


# Convenience function for creating threaded operations
def create_lobster_profile_cleaner(csv_file_path: str, profiles_folder_path: str) -> FileCleanupThread:
    return FileCleanupThread(operation="cleanup",
                             csv_file_path=csv_file_path,
                             profiles_folder_path=profiles_folder_path)
    
def create_csv_column_dropper(csv_file_path: str, column_to_drop: str, column_to_drop_index: int) -> FileCleanupThread:
    return FileCleanupThread(operation="drop_csv_column",
                             csv_file_path=csv_file_path,
                             column_to_drop=column_to_drop,
                             column_to_drop_index=column_to_drop_index)
