# src/workers.py
import os
import csv
import pandas as pd
from PySide6.QtCore import QRunnable, Signal, QObject, Slot

class CSVConversionSignals(QObject):
    """Pure data pipelines communicating background operations safely to the Controller."""
    log_message = Signal(str)        # Replaces tab2_program_output_append
    file_converted = Signal(str)     # Replaces set_file_open_path
    error_occurred = Signal(str)     # Replaces explicit pop-up commands
    warning_occurred = Signal(str)   # Replaces explicit pop-up commands
    started = Signal()
    finished = Signal()


class CSVConversionWorker(QRunnable):
    """Handles heavy-duty CSV transformations safely off the GUI event loop."""
    
    def __init__(self, csv_file_to_convert: str, extension_type: str, write_index: bool):
        super().__init__()
        self.csv_file_to_convert = csv_file_to_convert
        self.extension_type = extension_type
        self.write_index = write_index
        self.signals = CSVConversionSignals()
        self.setAutoDelete(True)

    @Slot()
    def run(self) -> None:
        try:
            self.signals.started.emit()
            self._start_csv_conversion()
        except FileNotFoundError:
            self.signals.warning_occurred.emit(
                "No CSV file has been selected for conversion.\nPlease select a valid CSV file."
            )
        except Exception as ex:
            self.signals.error_occurred.emit(f"{type(ex).__name__}: {ex}")
        finally:
            self.signals.finished.emit()

    def get_extension_type(self) -> str:
        match self.extension_type.upper():
            case "EXCEL": return "xlsx"
            case "HTML": return "html"
            case "JSON": return "json"
            case "MARKDOWN": return "md"
        raise ValueError(f"Unsupported output type: {self.extension_type}")

    def _detect_delimiter(self, file_path: str) -> str:
        candidate_delimiters = [",", ";", "\t", "|"]
        with open(file_path, newline="", encoding="utf-8-sig") as file:
            sample = file.read(4096)

        if not sample.strip():
            raise ValueError("The selected CSV file is empty.")

        try:
            return csv.Sniffer().sniff(sample, delimiters="".join(candidate_delimiters)).delimiter
        except csv.Error:
            lines = [line for line in sample.splitlines() if line.strip()]
            if not lines:
                raise ValueError("The selected CSV file does not contain readable rows.")

            ranked_delimiters = []
            for delimiter in candidate_delimiters:
                counts = [line.count(delimiter) for line in lines[:10]]
                non_zero_counts = [count for count in counts if count > 0]
                if not non_zero_counts:
                    continue
                ranked_delimiters.append((len(non_zero_counts), sum(non_zero_counts), delimiter))

            if not ranked_delimiters:
                return ","

            ranked_delimiters.sort(reverse=True)
            return ranked_delimiters[0][2]

    def _load_csv_dataframe(self, file_path: str, delimiter: str) -> pd.DataFrame:
        read_attempts = [
            {"sep": delimiter, "encoding": "utf-8-sig", "engine": "python", "quotechar": '"', "skipinitialspace": True},
            {"sep": delimiter, "encoding": "utf-8", "engine": "python", "quotechar": '"', "skipinitialspace": True},
            {"sep": delimiter, "encoding": "latin-1", "engine": "python", "quotechar": '"', "skipinitialspace": True},
        ]

        last_exception = None
        for read_kwargs in read_attempts:
            try:
                return pd.read_csv(file_path, **read_kwargs)
            except Exception as ex:
                last_exception = ex

        raise ValueError(f"Unable to read the CSV file with delimiter '{delimiter}': {last_exception}")

    def _build_output_file_path(self, file_path: str, output_ext: str) -> str:
        input_dir = os.path.dirname(file_path)
        input_filename = os.path.splitext(os.path.basename(file_path))[0]
        return os.path.join(input_dir, input_filename + "." + output_ext)

    def _get_excel_sheet_name(self, file_path: str) -> str:
        input_filename = os.path.splitext(os.path.basename(file_path))[0]
        invalid_chars = set('[]:*?/\\')
        sanitized_name = "".join("_" if char in invalid_chars else char for char in input_filename).strip()
        return (sanitized_name or "Result")[:31]

    def _start_csv_conversion(self) -> None:
        if not self.csv_file_to_convert or not os.path.isfile(self.csv_file_to_convert):
            raise FileNotFoundError

        delimiter = self._detect_delimiter(self.csv_file_to_convert)
        self.signals.log_message.emit(f"Detected delimiter: '{delimiter}'")

        df = self._load_csv_dataframe(self.csv_file_to_convert, delimiter)
        if df.empty and len(df.columns) == 0:
            raise ValueError("The CSV file could be read, but it does not contain any columns.")

        _, input_ext = os.path.splitext(self.csv_file_to_convert)
        output_ext = self.get_extension_type()
        input_ext = input_ext.lower().lstrip(".")

        sheet_name = self._get_excel_sheet_name(self.csv_file_to_convert)
        output_file_path = self._build_output_file_path(self.csv_file_to_convert, output_ext)

        # Local mapping functions
        def to_html(dataframe: pd.DataFrame, path: str) -> None:
            dataframe.to_html(path, index=self.write_index)

        def to_json(dataframe: pd.DataFrame, path: str) -> None:
            dataframe.to_json(path, orient="records", force_ascii=False, indent=2)

        def to_md(dataframe: pd.DataFrame, path: str) -> None:
            dataframe.to_markdown(path, index=self.write_index)

        def to_xlsx(dataframe: pd.DataFrame, path: str) -> None:
            with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                dataframe.to_excel(writer, sheet_name=sheet_name, index=self.write_index)
                worksheet = writer.sheets[sheet_name]
                max_row, max_col = dataframe.shape
                column_settings = [{"header": col} for col in dataframe.columns]
                if self.write_index:
                    max_col += 1
                    column_settings.insert(0, {"header": dataframe.index.name or "Index"})

                worksheet.add_table(
                    0, 0, max_row, max_col - 1,
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
            self.signals.error_occurred.emit(f"Cannot convert from '{input_ext}' to '{output_ext}'.")
            return

        self.signals.log_message.emit("Starting conversion, please wait...")
        convert_func(df, output_file_path)

        self.signals.log_message.emit(
            f"Successfully converted:\n{os.path.basename(self.csv_file_to_convert)} -> {os.path.basename(output_file_path)}"
        )
        self.signals.file_converted.emit(output_file_path)