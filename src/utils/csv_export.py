from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from lxml import etree as ET
import csv
import os
import traceback
import re
from typing import List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor # Changed from multiprocessing
import threading # Used for the Event object
from functools import partial

# The _terminate_event is now an instance of threading.Event and will be managed
# within the CSVExportThread instance, rather than a global multiprocessing.Event.
# It will be passed to the process_single_xml function via partial.

def process_single_xml(
    xml_file: str,
    folder: str,
    xpath_expressions: List[str],
    headers: List[str],
    terminate_event: threading.Event # Pass the terminate event directly
) -> Tuple[List[Dict[str, str]], int, int]:
    """Process a single XML file and return its results as a list of dictionaries,
    where each dictionary represents a single XPath match for a CSV row.
    """
    if terminate_event.is_set():
        # Early exit if termination is requested
        return [], 0, 0

    file_path: str = os.path.join(folder, xml_file)
    file_rows: List[Dict[str, str]] = [] # Will store dictionaries for CSV rows
    file_total_matches: int = 0
    file_matched_any_xpath: int = 0 # 1 if any XPath matches in this file, 0 otherwise

    try:
        # ET.parse involves file I/O, which often releases the GIL,
        # allowing other threads to run concurrently.
        tree = ET.parse(file_path)
        root = tree.getroot()
    except (ET.XMLSyntaxError, Exception) as e: # Catching general Exception for file read errors
        # Log the error for debugging, but continue processing other files
        print(f"Error parsing XML file {xml_file}: {e}")
        return [], 0, 0 # Return empty results if file cannot be parsed

    for expression, header in zip(xpath_expressions, headers):
        if terminate_event.is_set():
            # Check for termination before processing each XPath expression
            return [], 0, 0

        try:
            # root.xpath can also release the GIL as it's a C-level operation
            results = root.xpath(expression)
            match_count = len(results)

            if match_count > 0:
                file_matched_any_xpath = 1 # Mark this file as having at least one match
                file_total_matches += match_count

            # Determine if the XPath ends with /text() or /@attribute
            # This regex needs to be compiled once for efficiency if called many times
            # in a loop, but for per-file processing, it's acceptable here.
            pattern_text_or_attribute_end = r"(.*?/text\(\)$|.*?/@[a-zA-Z_][a-zA-Z0-9_]*$)"
            ends_with_text_or_attribute = bool(re.match(pattern_text_or_attribute_end, expression))

            if results:
                for i, result in enumerate(results):
                    match_content = ""
                    if isinstance(result, ET._Element):
                        # For element nodes, we need to decide what content to extract.
                        # Original logic: if ends_with_text_or_attribute is true,
                        # it converts the Element object itself to string.
                        # Otherwise, it gets the .text attribute.
                        if ends_with_text_or_attribute:
                            # If the XPath explicitly asks for text() or @attribute,
                            # the result might directly be a string or a more specific type.
                            # The original code's `str(result)` here might be intended
                            match_content = str(result)
                        else:
                            match_content = result.text.strip() if result.text else result.tag
                    elif isinstance(result, str):
                        match_content = result.strip()
                    elif isinstance(result, (int, float)):
                        match_content = str(result)
                    # Handle other potential types from XPath results (e.g., boolean, list of results for complex XPaths)
                    else:
                        match_content = str(result) # Fallback for any other type

                    row: dict[str, str] = {
                        "Filename": xml_file,
                        header: match_content,
                        "Match_Index": str(i + 1) # 1-based index for matches
                    }
                    file_rows.append(row)
            # else: no results, pass as before
        except Exception as e:
            # Log the error for a specific XPath expression, but continue with others
            print(f"Error evaluating XPath '{expression}' in {xml_file}: {e}")
            pass # Continue to the next XPath expression or file

    return file_rows, file_total_matches, file_matched_any_xpath


class CSVExportSignals(QObject):
    """Signals class for CSVExportThread operations."""
    finished = Signal()
    error_occurred = Signal(str, str) # QMessageBox.critical
    info_occurred = Signal(str, str) # QMessageBox.information
    warning_occurred = Signal(str, str) # QMessageBox.warning
    program_output_progress_append = Signal(str) # Program Output aka self.ui.text_edit_program_output.append
    program_output_progress_set_text = Signal(str) # Program Output aka self.ui.text_edit_program_output.setText
    progressbar_update = Signal(int) # Progressbar aka self.ui.progressbar_main
    visible_state_widget = Signal(bool) # For hiding/unhiding button widgets

class CSVExportThread(QRunnable):
    """Worker thread for exporting XML XPath evaluation results to a CSV file."""

    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.signals = CSVExportSignals()
        self.setAutoDelete(True)

        # Create a threading Event for signaling termination
        self._terminate_event = threading.Event()
        self._pool = None # To store the ThreadPoolExecutor instance

        # Operation parameters
        self.folder_path_containing_xml_files: str = kwargs.get("folder_path_containing_xml_files", "")
        self.xpath_expressions_list: list = kwargs.get("xpath_expressions_list", [])
        self.output_save_path_for_csv_export: str = kwargs.get("output_save_path_for_csv_export", "")
        self.csv_headers_list: list = kwargs.get("csv_headers_list", [])
        self.max_threads: int = kwargs.get("max_threads", os.cpu_count() or 2) # Default to CPU count or 2

    def stop(self):
        """Signals the worker to stop its processing by setting the threading event."""
        self.signals.program_output_progress_append.emit("Aborting CSV export...")
        self._terminate_event.set() # Set the event to signal termination
        if self._pool:
            # Shutdown the pool, optionally cancelling ongoing futures
            # Setting wait=False to not block and cancel_futures=True to stop pending tasks
            self._pool.shutdown(wait=False, cancel_futures=True)

    @Slot()
    def run(self):
        """Main execution method that routes to specific operations."""
        try:
            if self.operation == "export":
                self._export_search_to_csv()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")

        except Exception as e:
            detailed_error = traceback.format_exc()
            self.signals.error_occurred.emit("Operation Error", f"{str(e)}\n\nDetails:\n{detailed_error}")

    def _export_search_to_csv(self):
        """Start searching all XML files in the specified folder and write its results to a specified output CSV file."""
        print(f"Using {self.max_threads} threads...")

        if not os.path.exists(self.folder_path_containing_xml_files) or not os.path.isdir(self.folder_path_containing_xml_files):
            self.signals.warning_occurred.emit("XML Folder not found", "Please set the path to the folder that contains XML files to process.")
            self.signals.finished.emit() # Ensure finished signal is emitted on early exit
            return

        xpath_expressions_size: int = len(self.xpath_expressions_list)
        csv_headers_size: int = len(self.csv_headers_list)
        xml_files_list = [f for f in os.listdir(self.folder_path_containing_xml_files) if f.lower().endswith('.xml')]
        total_xml_files_count = len(xml_files_list)

        # Check if csv output folder path has been set
        if not self.output_save_path_for_csv_export:
            self.signals.warning_occurred.emit("CSV Output Path is Empty", "Please set an output folder path for the csv file.")
            self.signals.finished.emit()
            return
        # Check if csv headers and xpath expressions list length is 0 on both
        if csv_headers_size == 0 and xpath_expressions_size == 0:
            self.signals.warning_occurred.emit("Headers and Expressions empty", "No csv headers and XPath expression found, please add some.")
            self.signals.finished.emit()
            return
        # Check if csv headers length is not the same as the length of xpath expressions
        elif csv_headers_size != xpath_expressions_size:
            self.signals.warning_occurred.emit(
                "CSV Header Size Warning",
                f"Input of CSV headers is not the same length as the XPath expressions\nCSV {csv_headers_size} / XPath {xpath_expressions_size}"
            )
            self.signals.finished.emit()
            return

        self.signals.program_output_progress_append.emit("Starting CSV export...")

        # Show the Abort button
        self.signals.visible_state_widget.emit(True) # self.ui.button_abort_csv_export in main.py

        if total_xml_files_count == 0:
            self.signals.info_occurred.emit("Export Finished", "No XML files found to export.")
            self.signals.finished.emit()
            return

        try:
            with open(self.output_save_path_for_csv_export, 'w', newline='', encoding='utf-8') as csvfile:
                # Define the fixed headers that will always be present in the CSV
                fixed_headers = ["Filename", "Match_Index"]
                # Combine fixed headers with the dynamic XPath headers
                # Ensure no duplicates if a dynamic header happens to be one of the fixed ones.
                # Using a set to preserve uniqueness, then converting back to list to maintain order.
                all_csv_headers = fixed_headers + [
                    h for h in self.csv_headers_list if h not in fixed_headers
                ]

                writer = csv.DictWriter(csvfile, fieldnames=all_csv_headers, extrasaction='ignore')
                writer.writeheader()

                # Use partial to pass the additional arguments including the terminate_event
                # to the process_single_xml function that will be executed by the threads.
                thread_func = partial(
                    process_single_xml,
                    folder=self.folder_path_containing_xml_files,
                    xpath_expressions=self.xpath_expressions_list,
                    headers=self.csv_headers_list,
                    terminate_event=self._terminate_event # Pass the threading.Event instance
                )

                # Initialize ThreadPoolExecutor
                self._pool = ThreadPoolExecutor(max_workers=self.max_threads)

                total_sum_matches = 0
                total_matching_files = 0
                processed_files_count = 0

                # Submit tasks to the thread pool
                futures = [self._pool.submit(thread_func, xml_file) for xml_file in xml_files_list]

                for future in futures:
                    if self._terminate_event.is_set():
                        self.signals.program_output_progress_append.emit("Export task aborted.")
                        # Cancel remaining futures if any
                        for remaining_future in futures:
                            remaining_future.cancel()
                        break # Exit the loop immediately

                    try:
                        # Get the result from the completed future
                        file_rows, file_matches, matching_file_flag = future.result()

                        if file_rows:
                            writer.writerows(file_rows)

                        total_sum_matches += file_matches
                        total_matching_files += matching_file_flag
                        processed_files_count += 1

                        progress = int((processed_files_count / total_xml_files_count) * 100)
                        self.signals.progressbar_update.emit(progress)
                        self.signals.program_output_progress_append.emit(f"Processed file {processed_files_count} of {total_xml_files_count}")

                    except Exception as future_exception:
                        # Handle exceptions that occurred in the worker thread
                        self.signals.program_output_progress_append.emit(f"Error processing a file: {future_exception}")
                        # Optionally, you can add more detailed error reporting here
                        processed_files_count += 1 # Still count it as processed for progress bar

                if not self._terminate_event.is_set(): # Only show completion message if not aborted
                    self.signals.program_output_progress_set_text.emit(
                        f"CSV export finished.\nTotal XML files processed: {total_xml_files_count}\n"
                        f"Total matches found: {total_sum_matches}\n"
                        f"Total files with matches: {total_matching_files}\n"
                        f"Output saved to: {self.output_save_path_for_csv_export}"
                    )

        except Exception as ex:
            detailed_error = traceback.format_exc()
            self.signals.error_occurred.emit(
                "CSV Export Error",
                f"An error occurred during CSV export:\n{str(ex)}\n\nDetails:\n{detailed_error}"
            )

        finally:
            if self._pool:
                # Proper shutdown for ThreadPoolExecutor
                # This ensures all submitted tasks are completed or cancelled.
                # Setting wait=True ensures that all threads have finished before proceeding.
                self._pool.shutdown(wait=True)
            self.signals.finished.emit() # Always emit finished, even on abort or error


# Convenience function for creating threaded operations
def create_csv_exporter(folder_path_containing_xml_files:str, xpath_expressions_list:list, output_save_path_for_csv_export:str, csv_headers_list:list, max_threads:int) -> CSVExportThread:
    """Create a CSV export thread for extracting data from multiple XML files

    Args:
        folder_path_containing_xml_files (str): Folder path that contains the XML files, use self.ui.line_edit_xml_folder_path_input
        xpath_expressions_list (list): List of XPath expressions to use and search XML file, use self.ui.list_widget_xpath_expressions
        output_save_path_for_csv_export (str): Folder path where the search result should be exported to as a CSV file, use self.ui.line_edit_csv_output_path
        max_threads (int): The maximum number of threads to use in the thread pool.

    Returns:
        CSVExportThread: Worker thread for exporting XML XPath evaluation results to a CSV file.
    """
    return CSVExportThread(
        "export",
        folder_path_containing_xml_files=folder_path_containing_xml_files,
        xpath_expressions_list=xpath_expressions_list,
        output_save_path_for_csv_export=output_save_path_for_csv_export,
        csv_headers_list=csv_headers_list,
        max_threads=max_threads # Renamed from max_proccesses to max_threads for clarity
    )
