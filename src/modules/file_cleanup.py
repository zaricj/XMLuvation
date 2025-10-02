from PySide6.QtCore import QObject, QRunnable, Signal, Slot
import pandas as pd
import os
import csv
import re


class FileCleanupSignals(QObject):
    """Signals class for FileCleanupThread operations."""

    error_occurred = Signal(str, str)  # QMessageBox.critical
    warning_occurred = Signal(str, str)  # QMessageBox.warning
    tab2_program_output_append = Signal(str)  # Program Output aka self.ui.text_edit_program_output.append
    column_dropped_successfully = Signal(int)  # Indicate column drop completion


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

            self.signals.tab2_program_output_append.emit(f"Successfully dropped column '{selected_column}' and saved the updated CSV.")
            self.signals.column_dropped_successfully.emit(column_index)  # Emit the columns index to remove from the combo box
        except pd.errors.EmptyDataError:
            self.signals.error_occurred.emit("CSV Error", "The CSV file is empty or malformed.")
        except FileNotFoundError:
            self.signals.error_occurred.emit("File Error", f"CSV file not found at '{self.csv_file_path}'.")
        except Exception as e:
            self.signals.error_occurred.emit("CSV Operation Failed", f"An error occurred while dropping the column: {str(e)}")

    def _cleanup_files_matching_in_csv(self):
        """
        Deletes files from the selected folder if their names don't match entries in the csv file.
        Handles Windows filename sanitization (removes invalid characters like *).
        """
        if not self.csv_file_path:
            self.signals.warning_occurred.emit("CSV file not found",
                                               "Please select the CSV file that contains the current export of all Lobster profiles")
            return

        if not self.profiles_folder_path:
            self.signals.warning_occurred.emit("Folder path not found",
                                               "Please select the folder that contains all exported Lobster profiles as XML files")
            return

        def sanitize_filename_for_windows(filename):
            """
            Sanitize filename to match what Windows does automatically.
            Removes invalid characters and applies your specific regex transformation.
            """
            try:
                # First apply your specific regex transformation: _*FB* -> _FB
                # This handles the pattern _*<letters>* at the end of filenames
                filename = re.sub(r'_\*([^*]+)\*$', r'_\1', filename)
                
                # Windows forbidden characters
                forbidden_chars = '<>:"|?*'
                for char in forbidden_chars:
                    filename = filename.replace(char, '')
                
                return filename
            except Exception as e:
                self.signals.tab2_program_output_append.emit(f"Error sanitizing filename '{filename}': {e}")
                return filename  # Return original if sanitization fails

        valid_files = set()
        valid_files_original = set()  # Keep original names for debugging
        files_to_keep_debug = []  # For debugging

        try:
            # Use pandas for more robust CSV reading
            df = pd.read_csv(self.csv_file_path)

            # Get the first column values (assuming filenames are in first column)
            if len(df.columns) == 0:
                self.signals.error_occurred.emit("CSV Error", "CSV file appears to be empty or has no columns")
                return

            first_column = df.iloc[:, 0]  # Get first column regardless of header name

            for value in first_column:
                if pd.notna(value):  # Skip NaN/empty values
                    original_name = str(value).strip()  # Convert to string and strip whitespace
                    if original_name:  # Only process non-empty strings
                        # Add .xml extension if not present
                        if not original_name.lower().endswith('.xml'):
                            original_name += '.xml'

                        # Sanitize the filename to match Windows behavior
                        sanitized_name = sanitize_filename_for_windows(original_name)

                        valid_files.add(sanitized_name)
                        valid_files_original.add(original_name)
                        files_to_keep_debug.append(f"'{original_name}' -> '{sanitized_name}'")

            self.signals.tab2_program_output_append.emit(f"Found {len(valid_files)} valid file entries in CSV")

            # Debug: Show first few filename transformations
            if files_to_keep_debug:
                sample_files = files_to_keep_debug[:3]  # Show fewer to avoid spam
                self.signals.tab2_program_output_append.emit("Sample filename transformations:")
                for transformation in sample_files:
                    self.signals.tab2_program_output_append.emit(transformation)

        except Exception as e:
            self.signals.error_occurred.emit("CSV Reading Error", f"Failed to read CSV file: {str(e)}")
            return

        # Get all files in the target folder
        try:
            folder_files = [f for f in os.listdir(self.profiles_folder_path) 
                           if os.path.isfile(os.path.join(self.profiles_folder_path, f))]

            self.signals.tab2_program_output_append.emit(f"Found {len(folder_files)} files in folder")

            # Debug: Check for case mismatches
            valid_files_lower = {f.lower() for f in valid_files}

            # Files that exist in folder but not in CSV (case-insensitive check)
            files_to_delete = []
            files_to_keep_count = 0

            for file_name in folder_files:
                file_path = os.path.join(self.profiles_folder_path, file_name)

                # Check if file should be kept (case-insensitive)
                if file_name.lower() in valid_files_lower:
                    files_to_keep_count += 1
                    # Optional: Check for exact case match
                    if file_name not in valid_files:
                        self.signals.tab2_program_output_append.emit(f"Case mismatch found - File: '{file_name}' vs CSV entries")
                else:
                    files_to_delete.append((file_name, file_path))

            self.signals.tab2_program_output_append.emit(f"Files to keep: {files_to_keep_count}, Files to delete: {len(files_to_delete)}")

            # Perform deletion
            deleted_count = 0
            for file_name, file_path in files_to_delete:
                try:
                    os.unlink(file_path)
                    self.signals.tab2_program_output_append.emit(f"Deleted file: '{file_name}'")
                    deleted_count += 1
                except Exception as e:
                    self.signals.tab2_program_output_append.emit(f"Failed to delete '{file_name}': {e}")

            self.signals.tab2_program_output_append.emit(f"Cleanup completed. Deleted {deleted_count} files.")

        except Exception as e:
            self.signals.error_occurred.emit("Folder Access Error", f"Failed to access folder: {str(e)}")

    @staticmethod
    def sanitize_filename_for_windows(filename):
        """
        Public method to sanitize filename to match what Windows does automatically.
        Useful for testing filename transformations.

        Args:
            filename (str): Original filename from CSV

        Returns:
            str: Sanitized filename as it would appear in Windows
        """
        # Apply your specific regex transformation: _*FB* -> _FB
        # This handles the pattern _*<letters>* at the end of filenames
        filename = re.sub(r'_\*([^*]+)\*$', r'_\1', filename)

        # Windows forbidden characters
        forbidden_chars = '<>:"|?*'
        for char in forbidden_chars:
            filename = filename.replace(char, '')

        return filename


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