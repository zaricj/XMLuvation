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
    error_occurred = Signal(str, str)
    program_output_progress = Signal(str)
    progressbar_update = Signal(int)


 I have this XMLParser class with QRunnable:


# utils/xml_parser.py

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from lxml import etree as ET

import json



class XMLParserSignals(QObject):

    """Signals class for XMLParserThread operations."""

    finished = Signal(dict)

    error_occurred = Signal(str, str)

    progress = Signal(str)

    validation_result = Signal(bool, str)

    transformation_complete = Signal(str)



class XMLUtils:

    """Utility class for XML operations that don't require threading."""

    

    @staticmethod

    def validate_xml_syntax(xml_content: str) -> tuple[bool, str]:

        """Validate XML syntax without parsing the full document.

        

        Args:

            xml_content: XML content as string

            

        Returns:

            Tuple of (is_valid, error_message)

        """

        try:

            ET.fromstring(xml_content)

            return True, "XML syntax is valid"

        except ET.XMLSyntaxError as e:

            return False, f"XML syntax error: {str(e)}"

        except Exception as e:

            return False, f"Validation error: {str(e)}"

    

    @staticmethod

    def get_xml_encoding(file_path: str) -> str:

        """Extract encoding from XML file declaration.

        

        Args:

            file_path: Path to XML file

            

        Returns:

            Encoding string (default: 'utf-8')

        """

        try:

            with open(file_path, 'rb') as f:

                first_line = f.readline().decode('utf-8', errors='ignore')

                if 'encoding=' in first_line:

                    start = first_line.find('encoding=') + 10

                    end = first_line.find('"', start)

                    if end == -1:

                        end = first_line.find("'", start)

                    return first_line[start:end] if end != -1 else 'utf-8'

        except Exception:

            pass

        return 'utf-8'

    

    @staticmethod

    def pretty_print_xml(xml_content: str) -> str:

        """Format XML content with proper indentation.

        

        Args:

            xml_content: Raw XML content

            

        Returns:

            Pretty-formatted XML string

        """

        try:

            root = ET.fromstring(xml_content)

            return ET.tostring(root, encoding="unicode", pretty_print=True)

        except Exception as e:

            raise ValueError(f"Failed to format XML: {str(e)}")



class XMLParserThread(QRunnable):

    """Worker thread for various XML operations."""

    

    def __init__(self, operation: str, **kwargs):

        super().__init__()

        self.operation = operation

        self.kwargs = kwargs

        self.signals = XMLParserSignals()

        self.setAutoDelete(True)

        

        # Operation parameters

        self.xml_file_path = kwargs.get('xml_file_path')

        self.xml_content = kwargs.get('xml_content')

        self.namespace_map = kwargs.get('namespace_map', {})

        

    @Slot()

    def run(self):

        """Main execution method that routes to specific operations."""

        try:

            if self.operation == 'parse':

                self._parse_xml()

            elif self.operation == 'analyze':

                self._analyze_structure()

            else:

                raise ValueError(f"Unknown operation: {self.operation}")

                

        except Exception as e:

            self.signals.error_occurred.emit("Operation Error", str(e))

    

    def _parse_xml(self):

        """Parse XML file and extract comprehensive information."""

        tree = ET.parse(self.xml_file_path)

        root = tree.getroot()


        xml_string = ET.tostring(root, encoding="unicode", pretty_print=True)


        # Structures for comprehensive and contextual XML info

        tags = set()

        tag_values = set()

        attributes = set()

        attribute_values = set()

        namespaces = set()


        tag_to_values = {}  # e.g., {"author": ["Gambardella, Matthew", "Ralls, Kim", ...]}

        tag_to_attributes = {}  # e.g., {"book": ["id"]}

        tag_attr_to_values = {}  # e.g., {("book", "id"): ["bk101", "bk102", ...]}


        for elem in root.iter():

            tag = elem.tag

            tags.add(tag)


            # Namespace extraction

            if '}' in tag:

                namespace = tag.split('}')[0][1:]

                namespaces.add(namespace)


            # Text content mapping

            if elem.text and elem.text.strip():

                value = elem.text.strip()

                tag_values.add(value)

                tag_to_values.setdefault(tag, set()).add(value)


            # Attributes

            for attr, val in elem.attrib.items():

                attributes.add(attr)

                attribute_values.add(val)

                tag_to_attributes.setdefault(tag, set()).add(attr)

                tag_attr_to_values.setdefault((tag, attr), set()).add(val)


        # Convert sets to sorted lists

        tag_to_values = {k: sorted(v) for k, v in tag_to_values.items()}

        tag_to_attributes = {k: sorted(v) for k, v in tag_to_attributes.items()}

        tag_attr_to_values = {k: sorted(v) for k, v in tag_attr_to_values.items()}


        result = {

            'xml_string': xml_string,

            'tags': sorted(tags),

            'tag_values': sorted(tag_values),

            'attributes': sorted(attributes),

            'attribute_values': sorted(attribute_values),

            'namespaces': sorted(namespaces),

            'file_path': self.xml_file_path,

            'root_tag': root.tag,

            'element_count': len(list(root.iter())),

            'encoding': XMLUtils.get_xml_encoding(self.xml_file_path),

            'tag_to_values': tag_to_values,

            'tag_to_attributes': tag_to_attributes,

            'tag_attr_to_values': tag_attr_to_values,

        }


        self.signals.progress.emit("XML parsing completed successfully!")

        self.signals.finished.emit(result)


    

    def _analyze_structure(self):

        """Analyze XML document structure and provide detailed statistics."""

        self.signals.progress.emit("Analyzing XML structure...")

        

        tree = ET.parse(self.xml_file_path)

        root = tree.getroot()

        

        # Comprehensive structure analysis

        element_stats = {}

        depth_levels = {}

        max_depth = 0

        

        def analyze_element(elem, depth=0):

            nonlocal max_depth

            max_depth = max(max_depth, depth)

            

            tag = elem.tag

            if tag not in element_stats:

                element_stats[tag] = {

                    'count': 0,

                    'has_text': 0,

                    'has_attributes': 0,

                    'has_children': 0,

                    'attributes': set(),

                    'depths': set()

                }

            

            stats = element_stats[tag]

            stats['count'] += 1

            stats['depths'].add(depth)

            

            if elem.text and elem.text.strip():

                stats['has_text'] += 1

            

            if elem.attrib:

                stats['has_attributes'] += 1

                stats['attributes'].update(elem.attrib.keys())

            

            if len(elem) > 0:

                stats['has_children'] += 1

            

            # Track depth distribution

            if depth not in depth_levels:

                depth_levels[depth] = 0

            depth_levels[depth] += 1

            

            # Recurse through children

            for child in elem:

                analyze_element(child, depth + 1)

        

        analyze_element(root)

        

        # Convert sets to lists for JSON serialization

        for tag_stats in element_stats.values():

            tag_stats['attributes'] = sorted(tag_stats['attributes'])

            tag_stats['depths'] = sorted(tag_stats['depths'])

        

        result = {

            'file_path': self.xml_file_path,

            'root_element': root.tag,

            'max_depth': max_depth,

            'total_elements': sum(stats['count'] for stats in element_stats.values()),

            'unique_elements': len(element_stats),

            'element_statistics': element_stats,

            'depth_distribution': depth_levels,

            'namespaces': self._extract_namespaces(root)

        }

        

        self.signals.finished.emit(result)

        self.signals.progress.emit("Structure analysis completed!")

    

    def _extract_namespaces(self, root):

        """Extract all namespaces used in the document."""

        namespaces = {}

        for elem in root.iter():

            if elem.nsmap:

                namespaces.update(elem.nsmap)

        return namespaces



# Convenience functions for creating threaded operations

def create_xml_parser(xml_file_path: str) -> XMLParserThread:

    """Create a parser thread for basic XML parsing."""

    return XMLParserThread('parse', xml_file_path=xml_file_path)


def create_structure_analyzer(xml_file_path: str) -> XMLParserThread:

    """Create a structure analyzer thread for detailed XML analysis."""

    return XMLParserThread('analyze', xml_file_path=xml_file_path)



I want to create a CSV Eport one similar, this is what I have now. Also I have a ABORT button in my GUI, for now i used the stop method with self._is_running, is there another way to implement this If I use in my main class:


        #  Initialize the QThreadPool for running threads

        self.thread_pool = QThreadPool()


CSVExportThread class:


from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from lxml import etree as ET

import csv

import os

import traceback

import multiprocessing

from functools import partial

import re

from typing import List, Tuple, Dict, Any


# Standalone processing functions that can be pickled

def process_single_xml(filename: str, folder_path: str, xpath_expressions: List[str]) -> Tuple[List[Dict[str, str]], int, int]:

    """Process a single XML file and return its results as a list of dictionaries,

    where each dictionary represents a single XPath match for a CSV row.

    """

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

                        # If the result is an element, try to get its text or specific attribute

                        if ends_with_text_or_attribute:

                            # If XPath explicitly asked for text() or @attr, result will be string

                            match_content = str(result)

                        else:

                            # If result is an element, get its text content, or tag if no text

                            match_content = result.text.strip() if result.text else result.tag

                    elif isinstance(result, str):

                        # If XPath directly returned a string (e.g., text() or @attribute)

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

                # If no matches, still add a row to indicate the XPath was evaluated

                # with empty content, if desired. For now, only add rows for matches.

                pass


        except Exception as e:

            # Log specific XPath expression errors, but don't stop processing other XPaths/files

            # print(f"Error processing XPath '{expression}' in file '{filename}': {e}")

            pass # Or emit a signal for logging error


    return file_rows, file_total_matches, file_matched_any_xpath



class CSVExportSignals():

    """Signals class for XMLParserThread operations."""

    finished = Signal(dict)

    error_occurred = Signal(str, str)

    progress = Signal(str)

    progressbar_update = Signal(int)



class CSVExportThread(QRunnable):

    """Worker thread for exporting XML XPath evaluation results to a CSV file."""

    output_set_text = Signal(str)

    finished = Signal()

    error_occurred = Signal(str, str)

    info_occurred = Signal(str, str)

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

            self.info_occurred.emit("Export Finished", "No XML files found to export.")

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

                        self.info_occurred.emit(

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

            self.error_occurred.emit(

                "CSV Export Error",

                f"An error occurred during CSV export:\n{str(ex)}\n\nDetails:\n{detailed_error}"

            )

            self.finished.emit()

            

    def _worker_init_check(self):

        """Dummy function for multiprocessing pool initializer."""

        pass # Can be used for logging or setting up global resources if needed per worker

It's great to see you're using QRunnable and QThreadPool for your XML processing and CSV export, as this is the correct way to handle long-running tasks in a PySide6 application without freezing the GUI.

Let's refine your CSVExportThread and address your question about implementing the abort functionality more robustly.
Refined CSVExportThread and Abort Mechanism

Your current abort mechanism using self._is_running is a common and acceptable approach for QRunnable based workers. However, when dealing with multiprocessing.Pool, directly setting a flag in the QRunnable might not immediately propagate to the child processes that multiprocessing spawns. Each child process will have its own memory space and thus its own _is_running flag that won't be updated by the main thread.

A more robust way to signal termination to processes within a multiprocessing.Pool is to use a multiprocessing.Event.

Here's how you can modify your CSVExportThread and the process_single_xml function to incorporate this:
Python

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
    """Signals class for CSVExportThread operations."""
    finished = Signal(dict)
    error_occurred = Signal(str, str) # QMessageBox.critical
    info_occurred = Signal(str, str) # QMessageBox.information
    warning_occured = Signal(str, str) # QMessageBox.warning
    program_output_progress = Signal(str) # Program Output aka self.ui.text_edit_program_output
    progressbar_update = Signal(int) # Progressbar aka self.ui.progressbar_main

class CSVExportThread(QRunnable):
    """Worker thread for exporting XML XPath evaluation results to a CSV file."""

    def __init__(self, folder_path: str, output_csv_path: str, xpath_expressions: List[str], **kwargs):
        super().__init__()
        self.folder_path = folder_path
        self.output_csv_path = output_csv_path
        self.xpath_expressions = xpath_expressions
        self.kwargs = kwargs
        self.signals = CSVExportSignals()
        self.setAutoDelete(True)

        # Create a multiprocessing Event for signaling termination
        self._terminate_event = multiprocessing.Event()
        self._pool = None # To store the multiprocessing pool instance

    def stop(self):
        """Signals the worker to stop its processing by setting the multiprocessing event."""
        self.signals.program_output_progress.emit("Aborting CSV export...")
        self._terminate_event.set() # Set the event to signal termination
        if self._pool:
            self._pool.terminate() # Forcefully terminate processes in the pool
            self._pool.join() # Wait for the pool to terminate

    @Slot()
    def run(self):
        self.signals.program_output_progress.emit("Starting CSV export...")
        xml_filenames = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.xml')]
        total_files = len(xml_filenames)

        if total_files == 0:
            self.signals.info_occurred.emit("Export Finished", "No XML files found to export.")
            self.signals.finished_signal.emit()
            return

        fieldnames = ['XML_FILE', 'XPath_Expression', 'Match_Content', 'Match_Index']
        
        try:
            with open(self.output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()

                pool_func = partial(
                    process_single_xml,
                    folder_path=self.folder_path,
                    xpath_expressions=self.xpath_expressions
                )

                # Initialize the pool with the worker_init function and the terminate event
                self._pool = multiprocessing.Pool(initializer=worker_init, initargs=(self._terminate_event,))
                
                total_sum_matches = 0
                total_matching_files = 0

                for i, (file_rows, file_matches, matching_file_flag) in enumerate(
                    self._pool.imap_unordered(pool_func, xml_filenames)
                ):
                    if self._terminate_event.is_set():
                        self.signals.program_output_progress.emit("Export task aborted successfully.")
                        break # Exit the loop immediately

                    if file_rows:
                        writer.writerows(file_rows)
                    
                    total_sum_matches += file_matches
                    total_matching_files += matching_file_flag
                    
                    progress = int(((i + 1) / total_files) * 100)
                    self.signals.progress_updated.emit(progress)
                    self.signals.program_output_progress.emit(f"Processed file {i + 1} of {total_files}")
                
                if not self._terminate_event.is_set(): # Only show completion message if not aborted
                    self.signals.info_occurred.emit(
                        "Export Completed",
                        f"CSV export finished.\nTotal XML files processed: {total_files}\n"
                        f"Total matches found: {total_sum_matches}\n"
                        f"Total files with matches: {total_matching_files}\n"
                        f"Output saved to: {self.output_csv_path}"
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
            self.signals.finished_signal.emit() # Always emit finished, even on abort or error


# Convenience function for creating threaded operations
def create_csv_export_thread() -> CSVExportThread:
    """Create a CSV export thread for extracting data from multiple XML files."""
    return CSVExportThread()
