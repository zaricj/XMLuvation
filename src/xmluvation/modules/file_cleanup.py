from PySide6.QtCore import QObject, QRunnable, Signal, Slot
import csv
import os


class FileCleanupSignals(QObject):
    """Signals class for FileCleanupThread operations."""
        
    error_occurred = Signal(str, str) # QMessageBox.critical
    warning_occurred = Signal(str, str) # QMessageBox.warning
    program_output_progress_append = Signal(str) # Program Output aka self.ui.text_edit_program_output.append
    program_output_progress_set_text = Signal(str) # Program Output aka self.ui.text_edit_program_output.setText


class FileCleanupThread(QRunnable):
    """Worker thread for cleaning up lobster profile export which are xml files."""
    
    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.signals = FileCleanupSignals()
        self.setAutoDelete(True)
        
        # Operation parameters
        self.csv_file_path = kwargs.get("csv_file_path")
        self.profiles_folder_path = kwargs.get("profiles_folder_path")


    @Slot()
    def run(self):
        """Main execution method that routes to specific operations."""
        try:
            if self.operation == "cleanup":
                self._cleanup_files_matching_in_csv()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")

        except Exception as e:
            self.signals.error_occurred.emit("Operation Error", f"{str(e)}")


    def _cleanup_files_matching_in_csv(self):
        """
        Deletes files from the selected folder if their names match entries in the csv file.
        """
        
        if not self.csv_file_path:
            self.signals.warning_occurred.emit("CSV file not found", "Please select the CSV file that contains the current export all Lobster profiles")
            return
        
        if not self.profiles_folder_path:
            self.signals.warning_occurred.emit("Folder path not found", "Please select the folder that contains all exported Lobster profiles as XML files")
            return
        
        with open(self.csv_file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Check if row is not empty
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
    return FileCleanupThread("cleanup",
                            csv_file_path=csv_file_path,
                            profiles_folder_path=profiles_folder_path)
