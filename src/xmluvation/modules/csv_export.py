from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from lxml import etree as ET
import csv
import os
import traceback
import re
from typing import List, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import threading
from functools import partial

def write_string_value(xpath: str) -> bool:
    """ Determine if the XPath expression should write string values.
    Args:
        xpath: XPath expression to check

    Returns:
        True if matches actual value (string) from the tag or attribute should be written, otherwise False and the match count should be written.
    """
    # Check if xpath ends with /text() or /@some_attribute this determines if we should write the actual value (string) from the tag or attribute
    return (xpath.strip().endswith('/text()') or
        re.search(r'/@\w+$', xpath.strip()))
        
def execute_xpath(root: ET._Element, xpath: str) -> List[Any]:
    """
    Execute XPath expression on XML root element.

    Args:
        root: Root element of XML
        xpath: XPath expression to execute

    Returns:
        List of matching elements/values
    """
    try:
        return root.xpath(xpath)
    except Exception as e:
        print(f"Warning: XPath '{xpath}' failed: {str(e)}")
        return []

def format_match_value(match: Any) -> str:
    """
    Format a match result into a string representation.

    Args:
        match: Match result from XPath query

    Returns:
        String representation of the match
    """
    if isinstance(match, str):
        return match.strip()
    elif isinstance(match, (int, float)):
        return str(match)
    elif hasattr(match, 'text'):
        return match.text.strip() if match.text else ""
    elif hasattr(match, 'tag'):
        return f"<{match.tag}>"
    else:
        return str(match)

def parse_xml_file(xml_file: str) -> ET._Element:
    """
    Parse an XML file and return its root element.

    Args:
        xml_file: Path to the XML file

    Returns:
        Root element of the parsed XML
    """
    try:
        parser = ET.XMLParser()
        tree = ET.parse(xml_file, parser)
        return tree.getroot()
    except (ET.XMLSyntaxError, Exception) as e:
        print(f"Error parsing XML file {xml_file}: {e}")
        return None

def process_single_xml(
    xml_file: str,
    folder: str,
    xpath_expressions: List[str],
    headers: List[str],
    group_matches_flag: bool,
    terminate_event: threading.Event
) -> Tuple[List[Dict[str, str]], int, int]:
    """
    Process a single XML file with all XPath expressions.
    
    Args:
        xml_file: Name of the XML file to process
        folder: Folder path containing the XML file
        xpath_expressions: List of XPath expressions to evaluate
        headers: List of custom headers corresponding to XPath expressions
        terminate_event: Threading event to signal termination
    
    Returns:
        Tuple of (result_row_dict, total_matches, file_had_matches_flag)
    """
    if terminate_event.is_set():
        return [], 0, 0

    xml_file_path: str = os.path.join(folder, xml_file)
    xml_file_name = os.path.basename(xml_file_path)
    xml_file_total_matches: int = 0
    xml_file_had_any_matches: int = 0
    
    # Initialize the result row with filename
    result_rows: List[Dict[str, str]] = []

    try:
        parsed_xml = parse_xml_file(xml_file_path)
    except (ET.XMLSyntaxError, Exception) as e:
        print(f"Error parsing XML file {xml_file}: {e}")
        return [], 0, 0

    # Process each XPath expression for this file
    for expression, header in zip(xpath_expressions, headers):
        if terminate_event.is_set():
            return [], 0, 0

        try:
            matches = execute_xpath(parsed_xml, expression)
            print(f"XPath: {expression}, Matches: {matches}")
            
            if not matches:
                continue

            # Check if we should group matches for this XPath
            if write_string_value(expression):
                # Group all matches for this file and xpath
                if group_matches_flag:
                    grouped_values = []
                    for match in matches:
                        formatted_value = format_match_value(match)
                        if formatted_value:  # Only add non-empty values
                            grouped_values.append(formatted_value)

                    if grouped_values:
                        # Join all values with the semicolon delimiter
                        combined_value = ";".join(grouped_values)
                        row = {"Filename": xml_file_name, header: combined_value}
                        result_rows.append(row)
                        xml_file_total_matches += len(grouped_values)
                        xml_file_had_any_matches = 1
                else:
                    for match in matches:
                        formatted_value = format_match_value(match)
                        if formatted_value:
                            match_row = {"Filename": xml_file_name, header: formatted_value}
                            result_rows.append(match_row)
                            xml_file_total_matches += 1
                            xml_file_had_any_matches = 1

            else:       
                # Individual matches - just count them
                match_count = len(matches)
                if match_count > 0:
                    count_header = f"{header} Match Count"
                    row = {"Filename": xml_file_name, count_header: str(match_count)}
                    result_rows.append(row)
                    xml_file_total_matches += match_count
                    xml_file_had_any_matches = 1
                    
        except Exception as e:
            print(f"Error processing XPath '{expression}' in {xml_file_path}: {str(e)}")
            continue
    
    # Only return result if file had any matches
    if xml_file_had_any_matches:
        return result_rows, xml_file_total_matches, xml_file_had_any_matches
    else:
        return [], 0, 0


class CSVExportSignals(QObject):
    """Signals class for CSVExportThread operations."""
    finished = Signal()
    error_occurred = Signal(str, str) # QMessageBox.critical
    info_occurred = Signal(str, str) # QMessageBox.information
    warning_occurred = Signal(str, str) # QMessageBox.warning
    program_output_progress_append = Signal(str) # Program Output aka self.ui.text_edit_program_output.append
    program_output_progress_set_text = Signal(str) # Program Output aka self.ui.text_edit_program_output.setText
    file_processing_progress = Signal(str) # File processed update for self.ui.label_file_processing
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
        self.xpath_expressions_list: List[str] = kwargs.get("xpath_expressions_list", [])
        self.output_path_for_csv_export: str = kwargs.get("output_save_path_for_csv_export", "")
        self.csv_headers_list: List[str] = kwargs.get("csv_headers_list", [])
        self.group_matches_flag: bool = kwargs.get("group_matches_flag", True) # Not used in this version
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

    def _generate_csv_headers(self) -> List[str]:
        """Generate the appropriate CSV headers based on XPath expressions."""
        headers: List[str] = ["Filename"]

        for expression, header in zip(self.xpath_expressions_list, self.csv_headers_list):
            if write_string_value(expression):
                # For text/attribute expressions, use original header
                if header not in headers:
                    headers.append(header)
            else:
                # For count-based expressions, add "Match Count" suffix
                count_header = f"{header} Match Count"
                if count_header not in headers:
                    headers.append(count_header)

        return headers

    def _export_search_to_csv(self):
        """Start searching all XML files in the specified folder and write its results to a specified output CSV file."""
        if not os.path.exists(self.folder_path_containing_xml_files) or not os.path.isdir(self.folder_path_containing_xml_files):
            self.signals.warning_occurred.emit("XML Folder not found", "Please set the path to the folder that contains XML files to process.")
            self.signals.finished.emit() # Ensure finished signal is emitted on early exit
            return

        xpath_expressions_size: int = len(self.xpath_expressions_list)
        csv_headers_size: int = len(self.csv_headers_list)
        xml_files_list = [f for f in os.listdir(self.folder_path_containing_xml_files) if f.lower().endswith('.xml')]
        total_xml_files_count = len(xml_files_list)

        # Check if the csv output folder path has been set
        if not self.output_path_for_csv_export:
            self.signals.warning_occurred.emit("CSV Output Path is Empty", "Please set an output folder path for the csv file.")
            self.signals.finished.emit()
            return
        # Check if csv headers and xpath expressions list length is 0 on both
        if csv_headers_size == 0 and xpath_expressions_size == 0:
            self.signals.warning_occurred.emit("Headers and Expressions empty", "No csv headers and XPath expression found, please add some.")
            self.signals.finished.emit()
            return
        # Check if csv headers length is different from the length of xpath expressions
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
            with open(self.output_path_for_csv_export, 'w', newline='', encoding='utf-8') as csvfile:
                # Generate appropriate headers based on XPath expressions
                all_csv_headers = self._generate_csv_headers()

                writer = csv.DictWriter(csvfile, fieldnames=all_csv_headers, extrasaction='ignore')
                writer.writeheader()

                # Use partial to pass the additional arguments including the terminate_event
                # to the process_single_xml function that will be executed by the threads.
                thread_func = partial(
                    process_single_xml,
                    folder=self.folder_path_containing_xml_files,
                    xpath_expressions=self.xpath_expressions_list,
                    headers=self.csv_headers_list,
                    group_matches_flag=self.group_matches_flag,
                    terminate_event=self._terminate_event # Pass the threading.Event instance
                )

                # Initialize ThreadPoolExecutor
                self._pool = ThreadPoolExecutor(max_workers=self.max_threads)

                total_sum_matches = 0
                total_matching_files = 0
                processed_files_count = 0
                files_with_results_written = 0

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
                        result_row, file_matches, matching_file_flag = future.result()

                        # Only write row if there are actual results
                        if result_row and matching_file_flag:
                            for row in result_row:
                                writer.writerow(row)
                            files_with_results_written += 1

                        total_sum_matches += file_matches
                        total_matching_files += matching_file_flag
                        processed_files_count += 1

                        progress = int((processed_files_count / total_xml_files_count) * 100)
                        self.signals.progressbar_update.emit(progress)
                        self.signals.file_processing_progress.emit(f"Processed file {processed_files_count} of {total_xml_files_count}")

                    except Exception as future_exception:
                        # Handle exceptions that occurred in the worker thread
                        self.signals.file_processing_progress.emit(f"Error processing a file: {future_exception}")
                        processed_files_count += 1 # Still count it as processed for progress bar

                if not self._terminate_event.is_set(): # Only show a completion message if not aborted
                    self.signals.program_output_progress_set_text.emit(
                        f"CSV export finished.\nTotal XML files processed: {total_xml_files_count}\n"
                        f"Total matches found: {total_sum_matches}\n"
                        f"Files with matches: {total_matching_files}\n"
                        f"Files written to CSV: {files_with_results_written}\n"
                        f"Output saved to: {self.output_path_for_csv_export}"
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
                self._pool.shutdown(wait=True)
            self.signals.finished.emit() # Emit always finished, even on abort or error


# Convenience function for creating threaded operations
def create_csv_exporter(folder_path_containing_xml_files: str, xpath_expressions_list: list, output_save_path_for_csv_export: str, csv_headers_list: list, group_matches_flag: bool, max_threads: int) -> CSVExportThread:
    """Create a CSV export thread for extracting data from multiple XML files

    Args:
        folder_path_containing_xml_files (str): Folder path that contains the XML files
        xpath_expressions_list (list): List of XPath expressions to use and search XML file
        output_save_path_for_csv_export (str): File path where the search result should be exported as CSV
        csv_headers_list (list): List of the entered CSV headers for the export process
        max_threads (int): The maximum number of threads to use in the thread pool

    Returns:
        CSVExportThread: Worker thread for exporting XML XPath evaluation results to a CSV file
    """
    return CSVExportThread(
        "export",
        folder_path_containing_xml_files=folder_path_containing_xml_files,
        xpath_expressions_list=xpath_expressions_list,
        output_save_path_for_csv_export=output_save_path_for_csv_export,
        csv_headers_list=csv_headers_list,
        group_matches_flag=group_matches_flag,
        max_threads=max_threads
    )
