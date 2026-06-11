from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from PySide6.QtWidgets import QLabel
import csv
import os
from typing import Any

import pandas as pd


class CSVConversionSignals(QObject):
    """Signals class for CSVConversionThread operations."""

    error_occurred = Signal(str, str)  # QMessageBox.critical
    warning_occurred = Signal(str, str)  # QMessageBox.warning
    info_occurred = Signal(str, str)  # QMessageBox.information
    tab2_program_output_append = Signal(str)  # Append to CSV Output QTextEdit
    set_file_open_path = Signal(str)  # Set converted file path in the UI
    start_gif = Signal()  # Tell Main Thread to start the GIF
    stop_gif = Signal()   # Tell Main Thread to stop the GIF


class CSVConversionThread(QRunnable):
    """Handles methods and logic for csv_conversion_groupbox."""

    def __init__(self, operation: str, csv_file_to_convert: str, extension_type: str, write_index: bool, label_loading_gif: QLabel):
        super().__init__()
        self.operation = operation
        self.csv_file_to_convert = csv_file_to_convert
        self.extension_type = extension_type
        self.write_index = write_index
        self.label_loading_gif = label_loading_gif

        self.signals = CSVConversionSignals()
        self.setAutoDelete(True)

    @Slot()
    def run(self):
        try:
            if self.operation == "convert_csv":
                self._start_csv_conversion()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
        except Exception as e:
            self.signals.error_occurred.emit("Operation Error", f"{str(e)}")

    def get_extension_type(self) -> str:
        """Returns the extension type for the conversion."""
        match self.extension_type:
            case "EXCEL":
                return "xlsx"
            case "HTML":
                return "html"
            case "JSON":
                return "json"
            case "MARKDOWN":
                return "md"
        raise ValueError(f"Unsupported output type: {self.extension_type}")

    def _detect_delimiter(self, file_path: str) -> str:
        """Detect a delimiter and fall back safely for irregular CSV files."""
        candidate_delimiters = [",", ";", "\t", "|"]

        with open(file_path, newline="", encoding="utf-8-sig") as file:
            sample = file.read(4096)

        if not sample.strip():
            raise ValueError("The selected CSV file is empty.")

        try:
            return csv.Sniffer().sniff(
                sample,
                delimiters="".join(candidate_delimiters),
            ).delimiter
        except csv.Error:
            lines = [line for line in sample.splitlines() if line.strip()]
            if not lines:
                raise ValueError("The selected CSV file does not contain readable rows.")

            ranked_delimiters: list[tuple[int, int, str]] = []
            for delimiter in candidate_delimiters:
                counts = [line.count(delimiter) for line in lines[:10]]
                non_zero_counts = [count for count in counts if count > 0]
                if not non_zero_counts:
                    continue

                # Prefer delimiters that appear in more rows, then by total count.
                ranked_delimiters.append(
                    (len(non_zero_counts), sum(non_zero_counts), delimiter)
                )

            if not ranked_delimiters:
                return ","

            ranked_delimiters.sort(reverse=True)
            return ranked_delimiters[0][2]

    def _load_csv_dataframe(self, file_path: str, delimiter: str) -> pd.DataFrame:
        """Read CSV data with conservative parser settings and encoding fallbacks."""
        read_attempts: list[dict[str, Any]] = [
            {
                "sep": delimiter,
                "encoding": "utf-8-sig",
                "engine": "python",
                "quotechar": '"',
                "skipinitialspace": True,
            },
            {
                "sep": delimiter,
                "encoding": "utf-8",
                "engine": "python",
                "quotechar": '"',
                "skipinitialspace": True,
            },
            {
                "sep": delimiter,
                "encoding": "latin-1",
                "engine": "python",
                "quotechar": '"',
                "skipinitialspace": True,
            },
        ]

        last_exception: Exception | None = None
        for read_kwargs in read_attempts:
            try:
                return pd.read_csv(file_path, **read_kwargs)
            except Exception as ex:
                last_exception = ex

        raise ValueError(
            f"Unable to read the CSV file with delimiter '{delimiter}': {last_exception}"
        )

    def _build_output_file_path(self, file_path: str, output_ext: str) -> str:
        input_dir = os.path.dirname(file_path)
        input_filename = os.path.splitext(os.path.basename(file_path))[0]
        return os.path.join(input_dir, input_filename + "." + output_ext)

    def _get_excel_sheet_name(self, file_path: str) -> str:
        """Excel sheet names must be <= 31 chars and avoid reserved characters."""
        input_filename = os.path.splitext(os.path.basename(file_path))[0]
        invalid_chars = set('[]:*?/\\')
        sanitized_name = "".join(
            "_" if char in invalid_chars else char for char in input_filename
        ).strip()
        return (sanitized_name or "Result")[:31]

    def _start_csv_conversion(self) -> None:
        try:
            if not self.csv_file_to_convert:
                raise FileNotFoundError

            if not os.path.isfile(self.csv_file_to_convert):
                raise FileNotFoundError(self.csv_file_to_convert)

            try:
                delimiter = self._detect_delimiter(self.csv_file_to_convert)
                self.signals.tab2_program_output_append.emit(
                    f"Detected delimiter: '{delimiter}'"
                )
            except Exception as e:
                message = (
                    "An error exception occurred while detecting the delimiter: "
                    f"{e}. Please ensure the file is a valid CSV."
                )
                self.signals.warning_occurred.emit(
                    "Delimiter Detection Error",
                    message,
                )
                return

            df = self._load_csv_dataframe(self.csv_file_to_convert, delimiter)
            if df.empty and len(df.columns) == 0:
                raise ValueError(
                    "The CSV file could be read, but it does not contain any columns."
                )

            _, input_ext = os.path.splitext(self.csv_file_to_convert)
            output_ext = self.get_extension_type()
            input_ext = input_ext.lower().lstrip(".")

            sheet_name = self._get_excel_sheet_name(self.csv_file_to_convert)
            output_file_path = self._build_output_file_path(
                self.csv_file_to_convert,
                output_ext,
            )

            def to_html(df: pd.DataFrame, path: str) -> None:
                df.to_html(path, index=self.write_index)

            def to_json(df: pd.DataFrame, path: str) -> None:
                df.to_json(path, orient="records", force_ascii=False, indent=2)

            def to_md(df: pd.DataFrame, path: str) -> None:
                df.to_markdown(path, index=self.write_index)

            def to_xlsx(df: pd.DataFrame, path: str) -> None:
                with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                    df.to_excel(writer, sheet_name=sheet_name,
                                index=self.write_index)
                    worksheet = writer.sheets[sheet_name]

                    max_row, max_col = df.shape
                    column_settings = [{"header": col} for col in df.columns]
                    if self.write_index:
                        max_col += 1
                        column_settings.insert(
                            0,
                            {"header": df.index.name or "Index"},
                        )

                    worksheet.add_table(
                        0,
                        0,
                        max_row,
                        max_col - 1,
                        {
                            "columns": column_settings,
                            "style": "Table Style Medium 16",
                            "name": f"{sheet_name[:30]}",
                            "autofilter": True,
                        },
                    )
                    worksheet.set_column(0, max_col - 1, 18)

            conversion_map = {
                ("csv", "html"): to_html,
                ("csv", "json"): to_json,
                ("csv", "md"): to_md,
                ("csv", "xlsx"): to_xlsx,
            }

            convert_func = conversion_map.get((input_ext, output_ext))
            if not convert_func:
                self.signals.error_occurred.emit(
                    "Unsupported Conversion",
                    f"Cannot convert from '{input_ext}' to '{output_ext}'.",
                )
                return

            self.signals.tab2_program_output_append.emit(
                "Starting conversion, please wait..."
            )
            self.signals.start_gif.emit()

            try:
                convert_func(df, output_file_path)
            finally:
                self.signals.stop_gif.emit()

            self.signals.tab2_program_output_append.emit(
                "Successfully converted:\n"
                f"{os.path.basename(self.csv_file_to_convert)} -> "
                f"{os.path.basename(output_file_path)}"
            )
            self.signals.set_file_open_path.emit(output_file_path)

        except FileNotFoundError:
            self.signals.warning_occurred.emit(
                "CSV Input File Error",
                "No CSV file has been selected for conversion.\nPlease select a CSV file.",
            )
        except Exception as ex:
            msg = f"{type(ex).__name__}: {ex}"
            self.signals.error_occurred.emit("Conversion Error", msg)


def create_csv_conversion_thread(operation: str, csv_file_to_convert: str, extension_type: str, write_index: bool, label_loading_gif: QLabel) -> CSVConversionThread:
    """Factory function to create a CSVConversionThread instance."""
    return CSVConversionThread(operation, csv_file_to_convert, extension_type, write_index, label_loading_gif)
