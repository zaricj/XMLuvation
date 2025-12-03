from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QLabel
import pandas as pd
import csv
import os

class CSVConversionSignals(QObject):
    """Signals class for CSVConversionThread operations."""
    
    error_occurred = Signal(str, str)  # QMessageBox.critical
    warning_occurred = Signal(str, str)  # QMessageBox.warning
    info_occurred = Signal(str, str)  # QMessageBox.information
    tab2_program_output_append = Signal(str) # Append to CSV Output QTextEdit
    set_file_open_path = Signal(str)  # Set the file path of the converted file in the "Open File" QLineEdit
    start_gif = Signal()  # Tell Main Thread to start the GIF
    stop_gif = Signal()   # Tell Main Thread to stop the GIF

class CSVConversionThread(QRunnable):
    """Handles methods and logic for csv_conversion_groupbox"""
    def __init__(self, operation: str, csv_file_to_convert: str, extension_type: str, write_index: bool, label_loading_gif: QLabel):
        super().__init__() # Initialize QRunnable
        self.operation = operation
        # Operation parameters
        self.csv_file_to_convert = csv_file_to_convert
        self.extension_type = extension_type # Value of the combobox self.ui.combobox_csv_conversion_output_type
        self.write_index = write_index
        self.label_loading_gif = label_loading_gif
        
        self.signals = CSVConversionSignals()
        self.setAutoDelete(True)
        
    @Slot()
    def run(self):
        try:
            """Main execution method that routes to specific operations."""
            if self.operation == "convert_csv":
                self._start_csv_conversion()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
        except Exception as e:
            self.signals.error_occurred.emit("Operation Error", f"{str(e)}")
        
    def get_extension_type(self) -> str:
        """Returns the extension type for the conversion. """
        match self.extension_type:
            case "EXCEL":
                return "xlsx"
            case "HTML":
                return "html"
            case "JSON":
                return "json"
            case "MARKDOWN":
                return "md"

    def _start_csv_conversion(self) -> None:
        try:
            # Check if QLineEdit widgets aren't empty
            if not self.csv_file_to_convert:
                raise FileNotFoundError
            try:
                # Detect delimiter
                with open(self.csv_file_to_convert, newline="",encoding="utf-8") as file:
                    sample = file.read(2048)
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                    self.signals.tab2_program_output_append.emit(f"Detected delimiter: '{delimiter}'")
            except Exception as e:
                message = f"An error exception occurred while detecting the delimiter: {e}. Please ensure the file is a valid CSV."
                self.signals.warning_occurred.emit("Delimiter Detection Error", message)
                return

            # Load CSV
            df = pd.read_csv(self.csv_file_to_convert, delimiter=delimiter, encoding="utf-8", engine="pyarrow")

            # Get extensions
            _, input_ext = os.path.splitext(self.csv_file_to_convert)
            output_ext = self.get_extension_type()
            input_ext = input_ext.lower().lstrip(".")
            
            # Sheet name for Excel output
            if output_ext == "xlsx":
                sheet_name = "Result"
            
            # Define output file path in the same folder
            input_dir = os.path.dirname(self.csv_file_to_convert)
            input_filename = os.path.splitext(os.path.basename(self.csv_file_to_convert))[0]
            output_file_path = os.path.join(input_dir, input_filename + "." + output_ext)
            
            # Define conversion functions
            def to_html(df, path): df.to_html(path, index=self.write_index)
            def to_json(df, path): df.to_json(path, orient="records", force_ascii=False)
            def to_md(df, path): df.to_markdown(path, index=self.write_index)
            def to_xlsx(df, path):
                with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=self.write_index)
                    worksheet = writer.sheets[sheet_name]
                    max_row, max_col = df.shape
                    column_settings = [{"header": col} for col in df.columns]
                    worksheet.add_table(0, 0, max_row, max_col - 1, {
                        "columns": column_settings,
                        "style": "Table Style Medium 16",
                        "name": f"{sheet_name[:30]}",
                        "autofilter": True
                    })
                    worksheet.set_column(0, max_col - 1, 18)

            conversion_map = {
                ("csv", "html"): to_html,
                ("csv", "json"): to_json,
                ("csv", "md"): to_md,
                ("csv", "xlsx"): to_xlsx,
            }

            convert_func = conversion_map.get((input_ext, output_ext))
            
            if not convert_func:
                self.signals.error_occurred.emit("Unsupported Conversion", f"Cannot convert from '{input_ext}' to '{output_ext}'.")
                return

            # Execute conversion
            self.signals.tab2_program_output_append.emit("Starting conversion, please wait...")
            
            # Signal the main thread to START the GIF
            self.signals.start_gif.emit()

            # The conversion function will now run while the Main Thread is animating the GIF
            convert_func(df, output_file_path) # Conversion runs here (can take a long time)

            # Signal the main thread to STOP the GIF
            self.signals.stop_gif.emit()
                
            self.signals.tab2_program_output_append.emit(f"Successfully converted:\n{os.path.basename(self.csv_file_to_convert)} → {os.path.basename(output_file_path)}")
            
            # Set the file path of the converted file in the "Open File" QLineEdit
            self.signals.set_file_open_path.emit(output_file_path)

        except FileNotFoundError:
            self.signals.warning_occurred.emit("CSV Input File Error", "No CSV file has been selected for conversion.\nPlease select a CSV file.")

        except Exception as ex:
            msg = f"{type(ex).__name__}: {ex}"
            self.signals.error_occurred.emit("Conversion Error", msg)
            
def create_csv_conversion_thread(operation: str, csv_file_to_convert: str, extension_type: str, write_index: bool, label_loading_gif: QLabel) -> CSVConversionThread:
    """Factory function to create a CSVConversionThread instance."""
    return CSVConversionThread(operation, csv_file_to_convert, extension_type, write_index, label_loading_gif)