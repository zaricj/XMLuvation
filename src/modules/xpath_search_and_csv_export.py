from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from lxml import etree as ET
from typing import List, Tuple, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dataclasses import dataclass, field
import csv
import os
import traceback
import re
import threading
import logging
import time
from queue import Queue
from threading import Thread


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
    """Optimized XML processor handling generic, dynamic XPath expressions safely."""

    def __init__(self):
        self._compiled_regexes = {
            'text_xpath': re.compile(r'/text\(\)\s*$'),
            'attr_xpath': re.compile(r'/@[\w:-]+\s*$')
        }

    def is_string_value_xpath(self, xpath: str) -> bool:
        """Determines if XPath targets string values (attributes or text)."""
        xpath = xpath.strip()
        return (
            self._compiled_regexes['text_xpath'].search(xpath) is not None or
            self._compiled_regexes['attr_xpath'].search(xpath) is not None
        )

    def parse_xml_file(self, xml_file_path: str) -> Optional[ET._Element]:
        """Thread-safe XML parsing with per-thread parser instance."""
        try:
            parser = ET.XMLParser(recover=True, huge_tree=True)
            tree = ET.parse(xml_file_path, parser)
            return tree.getroot()
        except (ET.XMLSyntaxError, FileNotFoundError, PermissionError) as e:
            logging.warning(f"Error parsing {xml_file_path}: {e}")
            return None

    def execute_xpaths(self, root: ET._Element, xpaths: List[str]) -> Dict[str, List[Any]]:
        """Executes generic XPath expressions safely on the document tree."""
        results = {}
        for xpath in xpaths:
            try:
                # Thread-local compiled XPath call
                compiled_xpath = ET.XPath(xpath)
                results[xpath] = compiled_xpath(root)
            except ET.XPathEvalError as e:
                logging.warning(f"XPath '{xpath}' failed: {e}")
                results[xpath] = []
            except Exception as e:
                logging.error(f"Unexpected error executing XPath '{xpath}': {e}")
                results[xpath] = []
        return results

    def find_row_anchor(self, xpaths: List[str]):
        """Common leading path of all XPaths = one row per element.
        Returns (anchor_xpath, {xpath: relative_xpath}) or None."""
        if len(xpaths) < 2 or any('[' in x for x in xpaths):
            return None
        parts = [x.strip().split('/') for x in xpaths]
        common = []
        for segs in zip(*parts):
            if len(set(segs)) != 1:
                break
            common.append(segs[0])
        anchor = '/'.join(common)
        if not anchor.strip('/') or any(len(p) <= len(common) for p in parts):
            return None
        rel = {x: '/'.join(p[len(common):]) for x, p in zip(xpaths, parts)}
        if any(r.startswith('/') or not r for r in rel.values()):
            return None
        return anchor, rel

    def format_match_value(self, match: Any) -> str:
        """Standardizes extracted values into clean single-line text."""
        if isinstance(match, str):
            val = match.strip()
        elif isinstance(match, (int, float, bool)):
            val = str(match)
        elif hasattr(match, 'text') and match.text:
            val = match.text.strip()
        elif hasattr(match, 'tag'):
            val = f"<{match.tag}>"
        else:
            val = str(match) if match is not None else ""

        # Flatten linebreaks so CSV structures remain intact for Excel
        if "\n" in val or "\r" in val:
            val = val.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
        return val


def process_single_xml_optimized(
    xml_file: str,
    folder: Path,
    xpath_expressions: List[str],
    headers: List[str],
    group_matches_flag: bool,
    terminate_event: threading.Event,
    processor: OptimizedXMLProcessor
) -> Tuple[List[Dict[str, str]], int, int]:
    """Processes a single XML file dynamically against user-defined XPaths with safe row padding."""
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

    # 1. Execute all user-defined XPaths globally
    xpath_results = processor.execute_xpaths(root, xpath_expressions)

    all_column_values = {}
    max_rows = 1
    total_matches = 0

    # Row anchoring: evaluate column XPaths per unit element so missing nodes become ""
    row_elements, rel_map = [], {}
    if not group_matches_flag:
        string_xpaths = [x for x in xpath_expressions if processor.is_string_value_xpath(x)]
        anchor = processor.find_row_anchor(string_xpaths)
        if anchor:
            row_elements = ET.XPath(anchor[0])(root)
            rel_map = anchor[1]

    # 2. Extract and format values, tracking the maximum row count needed
    for xpath, header in zip(xpath_expressions, headers):
        if terminate_event.is_set():
            return [], 0, 0

        matches = xpath_results.get(xpath, [])
        values = []

        if processor.is_string_value_xpath(xpath):
            if row_elements and xpath in rel_map:
                # one value per unit element, "" where the node doesn't exist
                rel = ET.XPath(rel_map[xpath])
                for el in row_elements:
                    found = rel(el)
                    values.append(processor.format_match_value(found[0]) if found else "")
                match_total = sum(1 for v in values if v)
            else:
                for match in matches:
                    formatted_value = processor.format_match_value(match)
                    values.append(formatted_value if formatted_value else "")
                match_total = len(values)

            all_column_values[header] = values
            if values:
                total_matches += match_total
                max_rows = max(max_rows, len(values))
        else:
            # Handle match counts or element counts
            match_count = len(matches)
            count_header = f"{header} Match Count"
            values = [str(match_count)] if match_count > 0 else []
            all_column_values[count_header] = values
            if match_count > 0:
                total_matches += match_count
                max_rows = max(max_rows, 1)

    result_rows = []
    has_matches = total_matches > 0

    if has_matches:
        num_rows = 1 if group_matches_flag else max_rows

        # 3. Build rows strictly by index, padding shorter lists with ""
        for row_index in range(num_rows):
            row = {"Filename": xml_file_name}
            row_has_content = False

            for xpath, header in zip(xpath_expressions, headers):
                if processor.is_string_value_xpath(xpath):
                    values = all_column_values.get(header, [])
                    if group_matches_flag:
                        non_empty = [v for v in values if v and v != ""]
                        row[header] = "; ".join(non_empty) if non_empty else ""
                        if non_empty:
                            row_has_content = True
                    else:
                        # If this list has an item at this index, use it. Otherwise, pad with ""
                        if row_index < len(values):
                            val = values[row_index]
                            row[header] = val
                            if val:
                                row_has_content = True
                        else:
                            row[header] = ""
                else:
                    count_header = f"{header} Match Count"
                    values = all_column_values.get(count_header, [])
                    row[count_header] = values[0] if values and row_index == 0 else ""
                    if values and row_index == 0:
                        row_has_content = True

            if row_has_content or group_matches_flag:
                result_rows.append(row)

    return result_rows, total_matches, 1 if result_rows else 0


class CSVExportSignals(QObject):
    """Signals for Qt GUI progress and output updates."""
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
    """Multi-threaded QRunnable for dynamic XPath evaluation and CSV generation."""

    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.signals = CSVExportSignals()
        self.setAutoDelete(True)

        self._terminate_event = threading.Event()
        self._executor = None

        self.folder_path = Path(kwargs.get("folder_path_containing_xml_files", ""))
        self.xpath_expressions = kwargs.get("xpath_expressions_list", [])
        self.output_path = Path(kwargs.get("output_save_path_for_csv_export", ""))
        self.headers = kwargs.get("csv_headers_list", [])
        self.group_matches_flag = kwargs.get("group_matches_flag", True)
        self.max_threads = min(kwargs.get("max_threads", os.cpu_count() or 4), 32)

        self._processor = OptimizedXMLProcessor()
        self._stats = ProcessingStats()

    def stop(self):
        """Signal termination and release resources."""
        self.signals.program_output_progress_append.emit("Aborting CSV export...")
        self._terminate_event.set()
        if self._executor:
            self._executor.shutdown(wait=False, cancel_futures=True)

    @Slot()
    def run(self):
        """Main execution entry point."""
        try:
            if self.operation == "export":
                self._export_search_to_csv()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
        except Exception as e:
            error_details = traceback.format_exc()
            self.signals.error_occurred.emit(
                "Operation Error", f"{str(e)}\n\nDetails:\n{error_details}"
            )
        finally:
            self.signals.finished.emit()

    def _validate_inputs(self) -> bool:
        if not self.folder_path.exists() or not self.folder_path.is_dir():
            self.signals.warning_occurred.emit(
                "XML Folder not found",
                "Please set the path to the folder that contains XML files to process."
            )
            return False

        if len(str(self.output_path).strip()) <= 1 or self.output_path.suffix.lower() != ".csv":
            self.signals.warning_occurred.emit(
                "CSV Output Path is Invalid",
                "Please set a valid output folder path ending in .csv."
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
                "No headers or XPath expressions found. Please add expressions and headers."
            )
            return False

        return True

    def _get_xml_files(self) -> List[str]:
        return [f.name for f in self.folder_path.glob("*.xml") if f.is_file()]

    def _generate_csv_headers(self) -> List[str]:
        headers = ["Filename"]
        for xpath, header in zip(self.xpath_expressions, self.headers):
            if self._processor.is_string_value_xpath(xpath):
                if header not in headers:
                    headers.append(header)
            else:
                count_header = f"{header} Match Count"
                if count_header not in headers:
                    headers.append(count_header)
        return headers

    def _export_search_to_csv(self):
        if not self._validate_inputs():
            return

        self._stats.start_time = time.time()
        xml_files = self._get_xml_files()
        self._stats.total_files = len(xml_files)

        if not xml_files:
            self.signals.warning_occurred.emit(
                "No XML Files Found", "No XML files found in selected folder."
            )
            return

        self.signals.program_output_progress_append.emit(
            f"Starting search and CSV export of {len(xml_files)} files with {self.max_threads} threads..."
        )
        self.signals.visible_state_widget.emit(True)

        result_queue: Queue = Queue(maxsize=5000)
        writer_thread_stop = threading.Event()

        def writer_worker():
            try:
                self.output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.output_path, 'w', newline='', encoding='utf-8', buffering=1_048_576) as csvfile:
                    headers = self._generate_csv_headers()
                    writer = csv.DictWriter(
                        csvfile,
                        fieldnames=headers,
                        extrasaction='ignore',
                        delimiter=',',
                        quotechar='"',
                        quoting=csv.QUOTE_MINIMAL
                    )
                    writer.writeheader()
                    while not (writer_thread_stop.is_set() and result_queue.empty()):
                        try:
                            row = result_queue.get(timeout=0.2)
                            if row is None:
                                continue
                            writer.writerow(row)
                            result_queue.task_done()
                        except Exception:
                            continue
            except Exception as e:
                self.signals.error_occurred.emit("CSV Write Error", str(e))

        writer_thread = Thread(target=writer_worker, daemon=True, name="CSVWriterThread")
        writer_thread.start()

        try:
            self._executor = ThreadPoolExecutor(
                max_workers=self.max_threads,
                thread_name_prefix="XMLProcessor"
            )

            futures = [
                self._executor.submit(
                    process_single_xml_optimized,
                    xml_file,
                    self.folder_path,
                    self.xpath_expressions,
                    self.headers,
                    self.group_matches_flag,
                    self._terminate_event,
                    self._processor
                )
                for xml_file in xml_files
            ]

            for future in as_completed(futures):
                if self._terminate_event.is_set():
                    self.signals.program_output_progress_append.emit("Export aborted by user.")
                    break

                try:
                    result_rows, file_matches, has_matches = future.result(timeout=30)

                    if result_rows and has_matches:
                        for row in result_rows:
                            result_queue.put(row)
                        self._stats.files_written += len(result_rows)

                    self._stats.total_matches += file_matches
                    self._stats.files_with_matches += has_matches
                    self._stats.processed_files += 1

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

            result_queue.join()
            writer_thread_stop.set()
            writer_thread.join(timeout=5)

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


def create_xpath_searcher_and_csv_exporter(
    folder_path_containing_xml_files: str,
    xpath_expressions_list: List[str],
    output_save_path_for_csv_export: str,
    csv_headers_list: List[str],
    group_matches_flag: bool = True,
    max_threads: Optional[int] = None
) -> OptimizedCSVExportThread:
    """Helper factory function to create worker instance for GUI thread pool execution."""
    if max_threads is None:
        max_threads = min(os.cpu_count() or 4, 16)

    return OptimizedCSVExportThread(
        "export",
        folder_path_containing_xml_files=folder_path_containing_xml_files,
        xpath_expressions_list=xpath_expressions_list,
        output_save_path_for_csv_export=output_save_path_for_csv_export,
        csv_headers_list=csv_headers_list,
        group_matches_flag=group_matches_flag,
        max_threads=max_threads
    )