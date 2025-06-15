from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from lxml import etree as ET
import csv
import os
import traceback
import multiprocessing
from functools import partial
import re
from typing import List, Tuple, Dict, Any

# We'll use a global event for all worker processes to check for termination
# This needs to be managed carefully as multiprocessing.Event instances cannot be directly passed to QRunnable
# Instead, the main process will set the event, and worker processes will periodically check it.
_terminate_event = None

def worker_init(terminate_event):
    """Initializer function for multiprocessing pool workers."""
    global _terminate_event
    _terminate_event = terminate_event

def process_single_xml(xml_file: str, folder: str, xpath_expressions: List[str], headers: List[str]) -> Tuple[List[Dict[str, str]], int, int]:
    """Process a single XML file and return its results as a list of dictionaries,
    where each dictionary represents a single XPath match for a CSV row.
    """
    global _terminate_event
    if _terminate_event and _terminate_event.is_set():
        # Early exit if termination is requested
        return [], 0, 0

    file_path: str = os.path.join(folder, xml_file)
    file_rows: List[Dict[str, str]] = [] # Will store dictionaries for CSV rows
    file_total_matches: int = 0
    file_matched_any_xpath: int = 0 # 1 if any XPath matches in this file, 0 otherwise

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except (ET.XMLSyntaxError, Exception): # Catching general Exception for file read errors
        return [], 0, 0 # Return empty results if file cannot be parsed

    for expression, header in zip(xpath_expressions, headers):
        if _terminate_event and _terminate_event.is_set():
            # Check for termination before processing each XPath expression
            return [], 0, 0

        try:
            results = root.xpath(expression)
            match_count = len(results)
            
            if match_count > 0:
                file_matched_any_xpath = 1 # Mark this file as having at least one match
                file_total_matches += match_count
            
            # Determine if the XPath ends with /text() or /@attribute
            pattern_text_or_attribute_end = r"(.*?/text\(\)$|.*?/@[a-zA-Z_][a-zA-Z0-9_]*$)"
            ends_with_text_or_attribute = bool(re.match(pattern_text_or_attribute_end, expression))

            if results:
                for i, result in enumerate(results):
                    match_content = ""
                    if isinstance(result, ET._Element):
                        if ends_with_text_or_attribute:
                            match_content = str(result)
                        else:
                            match_content = result.text.strip() if result.text else result.tag
                    elif isinstance(result, str):
                        match_content = result.strip()
                    elif isinstance(result, (int, float)):
                        match_content = str(result)
                    
                    row: dict[str, str]= {
                        "Filename": xml_file,
                        "XPath_Expression": expression,
                        header: match_content,
                        "Match_Index": str(i + 1) # 1-based index for matches
                    }
                    file_rows.append(row)
            else:
                pass

        except Exception:
            pass

    return file_rows, file_total_matches, file_matched_any_xpath


class CSVExportSignals(QObject):
    """Signals class for CSVExportThread operations."""
    finished = Signal()
    error_occurred = Signal(str, str) # QMessageBox.critical
    info_occurred = Signal(str, str) # QMessageBox.information
    warning_occured = Signal(str, str) # QMessageBox.warning
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
        
        # Create a multiprocessing Event for signaling termination
        self._terminate_event = multiprocessing.Event()
        self._pool = None # To store the multiprocessing pool instance
        
        # Operation parameters
        self.folder_path_containing_xml_files: str = kwargs.get("folder_path_containing_xml_files", "")
        self.xpath_expressions_list: list = kwargs.get("xpath_expressions_list", [])
        self.output_save_path_for_csv_export: str = kwargs.get("output_save_path_for_csv_export", "")
        self.csv_headers_list: list = kwargs.get("csv_headers_list", [])
        self.max_proccesses: int = kwargs.get("max_proccesses", 2)

    def stop(self):
        """Signals the worker to stop its processing by setting the multiprocessing event."""
        self.signals.program_output_progress_append.emit("Aborting CSV export...")
        self._terminate_event.set() # Set the event to signal termination
        if self._pool:
            self._pool.terminate() # Forcefully terminate processes in the pool
            self._pool.join() # Wait for the pool to terminate
    
    @Slot()
    def run(self):
        """Main execution method that routes to specific operations."""
        try:
            if self.operation == "export":
                self._export_serach_to_csv()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
                
        except Exception as e:
            self.signals.error_occurred.emit("Operation Error", str(e))


    def _export_serach_to_csv(self):
        """Start seraching all xml files in the specified folder and write it's results to a specified output csv file
        """
        print(f"Using {self.max_proccesses} Proccesses...")
        
        if not os.path.exists(self.folder_path_containing_xml_files) and not os.path.isdir(self.folder_path_containing_xml_files):
            self.signals.warning_occured.emit("XML Folder not found", "Please set the path to the folder that contains XML files to process.")
            return
        
        xpath_expressions_size: int = len(self.xpath_expressions_list)
        csv_headers_size: int = len(self.csv_headers_list)
        xml_files_list = [f for f in os.listdir(self.folder_path_containing_xml_files) if f.lower().endswith('.xml')]
        total_xml_files_count = len(xml_files_list)
        
        # Check if csv output folder path has been set
        if not self.output_save_path_for_csv_export:
            self.signals.warning_occured.emit("CSV Output Path is Empty", "Please set an output folder path for the csv file.")
            return
        # Check if csv headers and xpath expressions list lenght is 0 on both
        if csv_headers_size == 0 and xpath_expressions_size == 0:
            self.signals.warning_occured.emit("Headers and Expressions empty", "No csv headers and XPath expression found, please add some.")
            return
        # Check if csv headers lenght is not the same as the lenght of xpath expressions
        elif csv_headers_size != xpath_expressions_size:
            self.signals.warning_occured.emit("CSV Header Size Warning", f"Input of CSV headers is not the same lenght as the XPath expressions\nCSV {csv_headers_size} / XPath {xpath_expressions_size}")
            return
        
        self.signals.program_output_progress_append.emit("Starting CSV export...")
        
        # Show the Abort button
        self.signals.visible_state_widget.emit(True) # self.ui.button_abort_csv_export in main.py

        if total_xml_files_count == 0:
            self.signals.info_occurred.emit("Export Finished", "No XML files found to export.")
            self.signals.finished.emit()
            return

        # TODO Work on new write logic)
        try:
            with open(self.output_save_path_for_csv_export, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.csv_headers_list, extrasaction='ignore')
                writer.writeheader()

                pool_func = partial(
                    process_single_xml,
                    folder=self.folder_path_containing_xml_files,
                    xpath_expressions=self.xpath_expressions_list,
                    headers=self.csv_headers_list
                )

                # Initialize the pool with the worker_init function and the terminate event
                self._pool = multiprocessing.Pool(processes=self.max_proccesses, initializer=worker_init, initargs=(self._terminate_event,))
                
                total_sum_matches = 0
                total_matching_files = 0

                for i, (file_rows, file_matches, matching_file_flag) in enumerate(
                    self._pool.imap_unordered(pool_func, xml_files_list)
                ):
                    if self._terminate_event.is_set():
                        self.signals.program_output_progress_append.emit("Export task aborted successfully.")
                        break # Exit the loop immediately

                    if file_rows:
                        writer.writerows(file_rows)
                    
                    total_sum_matches += file_matches
                    total_matching_files += matching_file_flag
                    
                    progress = int(((i + 1) / total_xml_files_count) * 100)
                    self.signals.progressbar_update.emit(progress)
                    self.signals.program_output_progress_append.emit(f"Processed file {i + 1} of {total_xml_files_count}")
                
                if not self._terminate_event.is_set(): # Only show completion message if not aborted
                    self.signals.program_output_progress_set_text.emit(
                        "Export Completed!"
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
                self._pool.close() # Close the pool to prevent new tasks from being submitted
                self._pool.join() # Wait for all worker processes to exit (if not terminated)
            self.signals.finished.emit() # Always emit finished, even on abort or error


# Convenience function for creating threaded operations
def create_csv_exporter(folder_path_containing_xml_files:str, xpath_expressions_list:list, output_save_path_for_csv_export:str, csv_headers_list:list, max_proccesses:int) -> CSVExportThread:
    """Create a CSV export thread for extracting data from multiple XML files

    Args:
        folder_path_containing_xml_files (str): Folder path that contains the XML files, use self.ui.line_edit_xml_folder_path_input
        xpath_expressions_list (list): List of XPath expressions to use and search XML file, use self.ui.list_widget_xpath_expressions
        output_save_path_for_csv_export (str): Folder path where the search result should be exported to as a CSV file, use self.ui.line_edit_csv_output_path

    Returns:
        CSVExportThread: Worker thread for exporting XML XPath evaluation results to a CSV file.
    """
    return CSVExportThread("export", folder_path_containing_xml_files=folder_path_containing_xml_files, xpath_expressions_list=xpath_expressions_list, output_save_path_for_csv_export=output_save_path_for_csv_export, csv_headers_list=csv_headers_list, max_proccesses=max_proccesses)
