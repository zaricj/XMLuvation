# File: services/csv_service_handlers.py
import os
import pandas as pd
from PySide6.QtWidgets import QMessageBox, QComboBox, QPushButton, QLabel
from modules.csv_converter import create_csv_conversion_thread
from modules.xpath_search_and_csv_export import create_xpath_searcher_and_csv_exporter
from modules.file_cleanup import create_lobster_profile_cleaner, create_csv_column_dropper
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow  # import only for type hints, not at runtime


class CSVConversionHandler:
    """
    Service Orchestrator: Manages CSV file conversion operations.
    
    This class orchestrates CSV conversion by:
    - Creating and configuring CSV conversion worker threads
    - Managing conversion lifecycle
    - Handling conversion signal connections
    
    Architectural Role: Service Orchestrator (not a UI event handler)
    The name "Handler" is maintained for backward compatibility.
    """

    def __init__(self, main_window: "MainWindow", csv_file_to_convert: str, extension_type: str, write_index: bool, label_loading_gif: QLabel):
        self.main_window = main_window
        self.csv_file_to_convert = csv_file_to_convert
        # Value of the combobox self.ui.combobox_csv_conversion_output_type
        self.extension_type = extension_type
        self.write_index = write_index
        self.label_loading_gif = label_loading_gif

    def start_csv_conversion(self) -> None:
        try:
            """Initializes and starts the CSV conversion in a new thread."""
            # Create the conversion thread
            converter = create_csv_conversion_thread(
                "convert_csv", self.csv_file_to_convert, self.extension_type, self.write_index, self.label_loading_gif)
            self.main_window.connect_csv_conversion_signals(converter)
            # Start the conversion thread
            self.main_window.thread_pool.start(converter)
            # Optional: Keep track of the worker
            self.main_window.active_workers.append(converter)
        except FileNotFoundError as e:
            QMessageBox.warning(self.main_window, "Input File Error", str(e))


class SearchAndExportToCSVHandler:
    """
    Service Orchestrator: Manages CSV export operations.
    
    This class orchestrates the CSV export process by:
    - Creating and configuring CSV export worker threads
    - Managing thread lifecycle (start/stop)
    - Coordinating between UI and background workers
    
    Architectural Role: Service Orchestrator (not a UI event handler)
    The name "Handler" is maintained for backward compatibility, but this class
    functions as a service that orchestrates business logic.
    """

    def __init__(self, main_window: "MainWindow", xml_folder_path: str, xpath_filters: list, csv_folder_output_path: str, csv_headers_input: str, group_matches_flag: bool, set_max_threads: int):
        self.main_window = main_window
        self.xml_folder_path = xml_folder_path
        self.xpath_filters = xpath_filters
        self.csv_folder_output_path = csv_folder_output_path
        self.csv_headers_input = csv_headers_input
        self.group_matches_flag = group_matches_flag
        self.set_max_threads = set_max_threads
        self.current_exporter = None

    # === CSV Exporting Process === #
    def start_csv_export(self) -> None:
        """Initializes and starts the CSV export in a new thread."""
        try:
            exporter = create_xpath_searcher_and_csv_exporter(self.xml_folder_path, self.xpath_filters, self.csv_folder_output_path, self._parse_csv_headers(
                self.csv_headers_input), self.group_matches_flag, self.set_max_threads)
            self.current_exporter = exporter
            self.main_window.connect_csv_export_signals(self.current_exporter)
            self.main_window.thread_pool.start(self.current_exporter)

            # Optional: Keep track of the worker
            self.main_window.active_workers.append(self.current_exporter)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception on starting to export results to csv file", message)

    def stop_csv_export(self) -> None:
        """Signals the currently running CSV export to stop."""
        if self.current_exporter:
            # Check if the thread is still running before attempting to stop it
            # QThreadPool.activeThreadCount() or check if the QRunnable is still in pool
            # For simplicity, we just call stop() and rely on the QRunnable's internal logic
            self.current_exporter.stop()
            self.current_exporter = None  # Clear the reference once stopped

    def _parse_csv_headers(self, raw_headers: str) -> list:
        """Splits comma-separated string into a list of headers."""
        return [h.strip() for h in raw_headers.split(",") if h.strip()]


class LobsterProfileExportCleanupHandler:
    """Handles methods and logic of the lobster profile cleanup based on the selected csv file and the folder path that contains all lobster profile exports as XML files."""

    def __init__(self, main_window: "MainWindow", csv_file_path: str, profiles_folder_path: str):
        self.main_window = main_window
        self.csv_file_path = csv_file_path
        self.profiles_folder_path = profiles_folder_path

    def start_lobster_profile_cleanup(self) -> None:
        """Initializes and starts the lobster profile cleanup as a new thread."""
        try:
            cleaner = create_lobster_profile_cleaner(
                self.csv_file_path, self.profiles_folder_path)
            self.main_window.connect_file_cleanup_signals(cleaner)
            self.main_window.thread_pool.start(cleaner)
            # Optional: Keep track of the worker
            self.main_window.active_workers.append(cleaner)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception on starting to clean up lobster xml files in specified folder", message)


class CSVColumnDropHandler:
    """_summary_"""

    def __init__(self, main_window: "MainWindow" = None, csv_file_path: str = None, column_to_drop: str = None, column_to_drop_index: int = None, csv_header_combobox: QComboBox = None, drop_header_button: QPushButton = None):
        self.main_window = main_window
        self.csv_file_path = csv_file_path
        self.column_to_drop = column_to_drop
        self.column_to_drop_index = column_to_drop_index
        self.csv_header_combobox = csv_header_combobox
        self.drop_header_button = drop_header_button

    def start_csv_column_drop(self) -> None:
        try:
            dropper = create_csv_column_dropper(
                self.csv_file_path, self.column_to_drop, self.column_to_drop_index)
            self.main_window.connect_file_cleanup_signals(dropper)
            self.main_window.thread_pool.start(dropper)
            # Optional: Keep track of the worker
            self.main_window.active_workers.append(dropper)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception on starting to drop selected CSV header", message)

    def on_csv_input_file_path_changed(self) -> None:
        try:
            if not self.csv_file_path:
                self.csv_header_combobox.setDisabled(True)
                self.drop_header_button.setDisabled(True)
                self.csv_header_combobox.clear()
                return
            else:
                if os.path.isfile(self.csv_file_path) and self.csv_file_path.endswith(".csv"):
                    # Get headers of CSV file
                    headers = pd.read_csv(self.csv_file_path).columns
                    self.csv_header_combobox.addItems(
                        headers)  # Add headers to the combo box
                    self.csv_header_combobox.setDisabled(False)
                    self.drop_header_button.setDisabled(False)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception adding read csv headers to the combobox", message)
