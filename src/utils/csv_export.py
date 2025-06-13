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

def process_single_xml(filename: str, folder_path: str, xpath_expressions: List[str]) -> Tuple[List[Dict[str, str]], int, int]:
    """Process a single XML file and return its results as a list of dictionaries,
    where each dictionary represents a single XPath match for a CSV row.
    """
    global _terminate_event
    if _terminate_event and _terminate_event.is_set():
        # Early exit if termination is requested
        return [], 0, 0

    file_path = os.path.join(folder_path, filename)
    file_rows: List[Dict[str, str]] = [] # Will store dictionaries for CSV rows
    file_total_matches = 0
    file_matched_any_xpath = 0 # 1 if any XPath matches in this file, 0 otherwise

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except (ET.XMLSyntaxError, Exception): # Catching general Exception for file read errors
        return [], 0, 0 # Return empty results if file cannot be parsed

    for expression in xpath_expressions:
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
            pattern_text_or_attribute_end = r'(.*?/text\(\)$|.*?/@[a-zA-Z_][a-zA-Z0-9_]*$)'
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
                    
                    row = {
                        'XML_FILE': filename,
                        'XPath_Expression': expression,
                        'Match_Content': match_content,
                        'Match_Index': str(i + 1) # 1-based index for matches
                    }
                    file_rows.append(row)
            else:
                pass

        except Exception as e:
            pass

    return file_rows, file_total_matches, file_matched_any_xpath


class CSVExportSignals(QObject):
    """Signals class for XMLParserThread operations."""
    finished = Signal(dict)
    error_occurred = Signal(str, str)
    progress = Signal(str)
    progressbar_update = Signal(int)


class CSVExportThread(QRunnable):
    """Worker thread for exporting XML XPath evaluation results to a CSV file."""
    output_set_text = Signal(str)
    finished = Signal()
    show_error_message = Signal(str, str)
    show_info_message = Signal(str, str)
    progress_updated = Signal(int)

    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self._is_running = True
        self.signals = CSVExportSignals()
        self.setAutoDelete(True)

    def stop(self):
        """Signals the worker to stop its processing."""
        self._is_running = False

    @Slot()
    def run(self):
        self.output_set_text.emit("Starting CSV export...")
        xml_filenames = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.xml')]
        total_files = len(xml_filenames)

        if total_files == 0:
            self.show_info_message.emit("Export Finished", "No XML files found to export.")
            self.finished.emit()
            return

        # Define fixed CSV headers
        fieldnames = ['XML_FILE', 'XPath_Expression', 'Match_Content', 'Match_Index']
        
        try:
            # Open CSV file in write mode ('w') and write header immediately
            with open(self.output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()

                pool_func = partial(
                    process_single_xml,
                    folder_path=self.folder_path,
                    xpath_expressions=self.xpath_expressions
                )

                # Using multiprocessing Pool to process XML files in parallel
                with multiprocessing.Pool(initializer=self._worker_init_check) as pool:
                    total_sum_matches = 0
                    total_matching_files = 0

                    for i, (file_rows, file_matches, matching_file_flag) in enumerate(
                        pool.imap_unordered(pool_func, xml_filenames)
                    ):
                        if not self._is_running:
                            self.output_set_text.emit("Export task aborted successfully.")
                            pool.terminate() # Terminate remaining processes in the pool
                            break # Exit the loop

                        # Write rows for the current file directly to CSV
                        if file_rows:
                            writer.writerows(file_rows)
                        
                        total_sum_matches += file_matches
                        total_matching_files += matching_file_flag
                        
                        # Update progress and status
                        progress = int(((i + 1) / total_files) * 100)
                        self.progress_updated.emit(progress)
                        self.output_set_text.emit(f"Processed file {i + 1} of {total_files}")
                    else: # This 'else' block executes if the loop completes without a 'break'
                        self.show_info_message.emit(
                            "Export Completed",
                            f"CSV export finished.\nTotal XML files processed: {total_files}\n"
                            f"Total matches found: {total_sum_matches}\n"
                            f"Total files with matches: {total_matching_files}\n"
                            f"Output saved to: {self.output_csv_path}"
                        )
                        self.finished.emit()
                    # If loop broke due to abort, also emit finished and terminate pool
                    if not self._is_running:
                        self.finished.emit()

        except Exception as ex:
            detailed_error = traceback.format_exc()
            self.show_error_message.emit(
                "CSV Export Error",
                f"An error occurred during CSV export:\n{str(ex)}\n\nDetails:\n{detailed_error}"
            )
            self.finished.emit()
            
    def _worker_init_check(self):
        """Dummy function for multiprocessing pool initializer."""
        pass # Can be used for logging or setting up global resources if needed per worker
