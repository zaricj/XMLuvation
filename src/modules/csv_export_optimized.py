from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from lxml import etree as ET
from typing import List, Tuple, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
from dataclasses import dataclass, field
from contextlib import contextmanager
import csv
import os
import traceback
import re
import threading
import logging
import time


@dataclass
class ProcessingStats:
    """Statistics for processing results."""
    total_files: int = 0
    processed_files: int = 0
    files_with_matches: int = 0
    total_matches: int = 0
    files_written: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    errors: List[str] = field(default_factory=list)


class OptimizedXMLProcessor:
    """Optimized XML processor with caching and better memory management."""
    
    def __init__(self):
        self._parser = ET.XMLParser()
        self._compiled_regexes = {
            'text_xpath': re.compile(r'/text\(\)\s*$'),
            'attr_xpath': re.compile(r'/@\w+\s*$')
        }
    
    @lru_cache(maxsize=256)
    def _is_string_value_xpath(self, xpath: str) -> bool:
        """Cached check if XPath targets string values."""
        xpath = xpath.strip()
        return (self._compiled_regexes['text_xpath'].search(xpath) is not None or 
                self._compiled_regexes['attr_xpath'].search(xpath) is not None)
    
    def parse_xml_file(self, xml_file_path: str) -> Optional[ET._Element]:
        """Parse XML file with optimized settings."""
        try:
            tree = ET.parse(xml_file_path, self._parser)
            return tree.getroot()
        except (ET.XMLSyntaxError, FileNotFoundError, PermissionError) as e:
            logging.warning(f"Error parsing {xml_file_path}: {e}")
            return None
    
    def execute_xpath_batch(self, root: ET._Element, xpaths: List[str]) -> Dict[str, List[Any]]:
        """Execute multiple XPath expressions efficiently."""
        results = {}
        for xpath in xpaths:
            try:
                results[xpath] = root.xpath(xpath)
            except ET.XPathEvalError as e:
                logging.warning(f"XPath '{xpath}' failed: {e}")
                results[xpath] = []
        return results
    
    def format_match_value(self, match: Any) -> str:
        """Optimized value formatting."""
        if isinstance(match, str):
            return match.strip()
        elif isinstance(match, (int, float, bool)):
            return str(match)
        elif hasattr(match, 'text') and match.text:
            return match.text.strip()
        elif hasattr(match, 'tag'):
            return f"<{match.tag}>"
        return str(match) if match is not None else ""


def process_single_xml_optimized(
    xml_file: str,
    folder: Path,
    xpath_expressions: List[str],
    headers: List[str],
    group_matches_flag: bool,
    terminate_event: threading.Event,
    processor: OptimizedXMLProcessor
) -> Tuple[List[Dict[str, str]], int, int]:
    """
    Optimized single XML file processing.
    
    Returns:
        Tuple of (result_rows, total_matches, file_had_matches_flag)
    """
    if terminate_event.is_set():
        return [], 0, 0
    
    xml_file_path = folder / xml_file
    xml_file_name = xml_file_path.stem
    
    try:
        root = processor.parse_xml_file(str(xml_file_path))
        if root is None:
            return [], 0, 0
    except Exception as e:
        logging.error(f"Error processing {xml_file_path}: {e}")
        return [], 0, 0
    
    # Batch execute all XPath expressions
    xpath_results = processor.execute_xpath_batch(root, xpath_expressions)
    
    # Process results efficiently
    all_results = {}
    max_matches = 0
    total_matches = 0
    has_matches = False
    
    for xpath, header in zip(xpath_expressions, headers):
        if terminate_event.is_set():
            return [], 0, 0
        
        matches = xpath_results.get(xpath, [])
        if not matches:
            all_results[header] = []
            continue
        
        if processor._is_string_value_xpath(xpath):
            # Process string values
            values = []
            for match in matches:
                formatted_value = processor.format_match_value(match)
                if formatted_value:  # Only non-empty values
                    values.append(formatted_value)
            
            all_results[header] = values
            if values:
                has_matches = True
                total_matches += len(values)
                max_matches = max(max_matches, len(values))
        else:
            # Count-based expressions
            match_count = len(matches)
            count_header = f"{header} Match Count"
            
            if match_count > 0:
                all_results[count_header] = [str(match_count)]
                has_matches = True
                total_matches += match_count
                max_matches = max(max_matches, 1)
            else:
                all_results[count_header] = []
    
    # Generate result rows only if there are matches
    result_rows = []
    if has_matches:
        num_rows = 1 if group_matches_flag else max_matches
        
        for row_index in range(num_rows):
            row = {"Filename": xml_file_name}
            
            for xpath, header in zip(xpath_expressions, headers):
                if processor._is_string_value_xpath(xpath):
                    values = all_results.get(header, [])
                    if group_matches_flag and values:
                        # Group all values with semicolon separator
                        row[header] = ";".join(values)
                    elif row_index < len(values):
                        row[header] = values[row_index]
                    else:
                        row[header] = ""
                else:
                    # Count headers
                    count_header = f"{header} Match Count"
                    values = all_results.get(count_header, [])
                    row[count_header] = values[0] if values and row_index == 0 else ""
            
            result_rows.append(row)
    
    return result_rows, total_matches, 1 if has_matches else 0


class CSVExportSignals(QObject):
    """Signals for CSV export operations."""
    finished = Signal()
    error_occurred = Signal(str, str)
    info_occurred = Signal(str, str)
    warning_occurred = Signal(str, str)
    program_output_progress_append = Signal(str)
    program_output_progress_set_text = Signal(str)
    file_processing_progress = Signal(str)
    progressbar_update = Signal(int)
    visible_state_widget = Signal(bool)


class OptimizedCSVExportThread(QRunnable):
    """Highly optimized CSV export thread with better resource management."""
    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.signals = CSVExportSignals()
        self.setAutoDelete(True)
        
        # Threading controls
        self._terminate_event = threading.Event()
        self._executor = None
        
        # Configuration
        self.folder_path = Path(kwargs.get("folder_path_containing_xml_files", ""))
        self.xpath_expressions = kwargs.get("xpath_expressions_list", [])
        self.output_path = Path(kwargs.get("output_save_path_for_csv_export", ""))
        self.headers = kwargs.get("csv_headers_list", [])
        self.group_matches_flag = kwargs.get("group_matches_flag", True)
        self.max_threads = min(kwargs.get("max_threads", os.cpu_count() or 4), 32)  # Cap at 32
        
        # Initialize processor
        self._processor = OptimizedXMLProcessor()
        
        # Statistics
        self._stats = ProcessingStats()
    
    def stop(self):
        """Signal termination and cleanup resources."""
        self.signals.program_output_progress_append.emit("Aborting CSV export...")
        self._terminate_event.set()
        
        if self._executor:
            # Graceful shutdown
            self._executor.shutdown(wait=False, cancel_futures=True)
    
    @Slot()
    def run(self):
        """Main execution method."""
        try:
            if self.operation == "export":
                self._export_search_to_csv()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
        except Exception as e:
            error_details = traceback.format_exc()
            self.signals.error_occurred.emit(
                "Operation Error", 
                f"{str(e)}\n\nDetails:\n{error_details}"
            )
        finally:
            self.signals.finished.emit()
    
    def _validate_inputs(self) -> bool:
        """Validate all inputs before processing."""
        if not self.folder_path.exists() or not self.folder_path.is_dir():
            self.signals.warning_occurred.emit(
                "XML Folder not found", 
                "Please set the path to the folder that contains XML files to process."
            )
            return False
        
        if not self.output_path:
            self.signals.warning_occurred.emit(
                "CSV Output Path is Empty", 
                "Please set an output folder path for the csv file."
            )
            return False
        
        if len(self.headers) != len(self.xpath_expressions):
            self.signals.warning_occurred.emit(
                "Header/XPath Length Mismatch",
                f"CSV headers length ({len(self.headers)}) doesn't match XPath expressions length ({len(self.xpath_expressions)})"
            )
            return False
        
        if not self.headers or not self.xpath_expressions:
            self.signals.warning_occurred.emit(
                "Empty Configuration", 
                "No headers or XPath expressions found\nPlease add xpath expressions and headers in order to start an evaluation."
            )
            return False
        
        return True
    
    def _get_xml_files(self) -> List[str]:
        """Get list of XML files efficiently."""
        return [f.name for f in self.folder_path.glob("*.xml") if f.is_file()]
    
    def _generate_csv_headers(self) -> List[str]:
        """Generate appropriate CSV headers."""
        headers = ["Filename"]
        
        for xpath, header in zip(self.xpath_expressions, self.headers):
            if self._processor._is_string_value_xpath(xpath):
                if header not in headers:
                    headers.append(header)
            else:
                count_header = f"{header} Match Count"
                if count_header not in headers:
                    headers.append(count_header)
        
        return headers
    
    @contextmanager
    def _csv_writer_context(self):
        """Context manager for CSV writing."""
        try:
            # Ensure output directory exists
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.output_path, 'w', newline='', encoding='utf-8') as csvfile:
                headers = self._generate_csv_headers()
                writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
                writer.writeheader()
                yield writer
        except Exception as e:
            raise IOError(f"Failed to create CSV writer: {e}")
    
    def _export_search_to_csv(self):
        """Optimized CSV export with better resource management."""
        # Validation
        if not self._validate_inputs():
            return
        
        # Start time tracking
        self._stats.start_time = time.time()
        
        # Get XML files
        xml_files = self._get_xml_files()
        self._stats.total_files = len(xml_files)
        
        if not xml_files:
            self.signals.warning_occurred.emit(
                "No XML Files Found", 
                "No XML files found in selected folder."
            )
            return
        
        self.signals.program_output_progress_append.emit(
            f"Starting search and CSV export of {len(xml_files)} files with {self.max_threads} threads..."
        )
        self.signals.visible_state_widget.emit(True)
        
        try:
            with self._csv_writer_context() as writer:
                # Create thread pool
                self._executor = ThreadPoolExecutor(
                    max_workers=self.max_threads,
                    thread_name_prefix="XMLProcessor"
                )
                
                # Submit all tasks
                futures = []
                for xml_file in xml_files:
                    future = self._executor.submit(
                        process_single_xml_optimized,
                        xml_file,
                        self.folder_path,
                        self.xpath_expressions,
                        self.headers,
                        self.group_matches_flag,
                        self._terminate_event,
                        self._processor
                    )
                    futures.append(future)
                
                # Process completed futures as they finish
                for future in as_completed(futures):
                    if self._terminate_event.is_set():
                        self.signals.program_output_progress_append.emit("Export aborted by user.")
                        break
                    
                    try:
                        result_rows, file_matches, has_matches = future.result(timeout=30)
                        
                        # Write results if any
                        if result_rows and has_matches:
                            for row in result_rows:
                                writer.writerow(row)
                            self._stats.files_written += 1
                        
                        # Update statistics
                        self._stats.total_matches += file_matches
                        self._stats.files_with_matches += has_matches
                        self._stats.processed_files += 1
                        
                        # Update UI
                        progress = int((self._stats.processed_files / self._stats.total_files) * 100)
                        self.signals.progressbar_update.emit(progress)
                        self.signals.file_processing_progress.emit(
                            f"Processed {self._stats.processed_files}/{self._stats.total_files}"
                        )
                        
                    except Exception as e:
                        error_msg = f"Error processing file: {str(e)}"
                        self._stats.errors.append(error_msg)
                        self._stats.processed_files += 1
                        logging.error(error_msg)
                
                # Final status
                if not self._terminate_event.is_set():
                    self._stats.end_time = time.time()
                    self._emit_completion_message()
                    
        except Exception as e:
            error_details = traceback.format_exc()
            self.signals.error_occurred.emit(
                "CSV Export Error",
                f"Export failed: {str(e)}\n\nDetails:\n{error_details}"
            )
        finally:
            if self._executor:
                self._executor.shutdown(wait=True)
    
    def _emit_completion_message(self):
        """Emit completion status message."""
        message_parts = [
            "CSV export completed successfully!",
            f"Files processed: {self._stats.processed_files}/{self._stats.total_files}",
            f"Files with matches: {self._stats.files_with_matches}",
            f"Total matches found: {self._stats.total_matches}",
            f"Rows written to CSV: {self._stats.files_written}",
            f"Output saved: {self.output_path}",
            f"Elapsed time: {self._stats.end_time - self._stats.start_time:.2f} seconds"
        ]
        
        if self._stats.errors:
            message_parts.append(f"Errors encountered: {len(self._stats.errors)}")
        
        self.signals.program_output_progress_set_text.emit("\n".join(message_parts))


def create_optimized_csv_exporter(
    folder_path_containing_xml_files: str,
    xpath_expressions_list: List[str],
    output_save_path_for_csv_export: str,
    csv_headers_list: List[str],
    group_matches_flag: bool = True,
    max_threads: int = None
) -> OptimizedCSVExportThread:
    """Create an optimized CSV export thread.
    
    Args:
        folder_path_containing_xml_files: Folder containing XML files
        xpath_expressions_list: XPath expressions to evaluate
        output_save_path_for_csv_export: Output CSV file path
        csv_headers_list: CSV headers for each XPath
        group_matches_flag: Whether to group matches in single row
        max_threads: Maximum threads to use (defaults to CPU count)
    
    Returns:
        Optimized CSV export thread
    """
    if max_threads is None:
        max_threads = min(os.cpu_count() or 4, 16)  # Reasonable default
    
    return OptimizedCSVExportThread(
        "export",
        folder_path_containing_xml_files=folder_path_containing_xml_files,
        xpath_expressions_list=xpath_expressions_list,
        output_save_path_for_csv_export=output_save_path_for_csv_export,
        csv_headers_list=csv_headers_list,
        group_matches_flag=group_matches_flag,
        max_threads=max_threads
    )
