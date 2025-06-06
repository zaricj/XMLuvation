from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QGroupBox, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QRadioButton, 
                             QListWidget, QTextEdit, QProgressBar, QStatusBar,
                             QCheckBox,QMenu,QFileDialog, QMessageBox, QFrame, 
                             QSpacerItem, QSizePolicy, QTableView, QHeaderView, QInputDialog)
from PySide6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QCloseEvent
from PySide6.QtCore import Qt, QThread, Signal, Slot, QSortFilterProxyModel, QObject, QFile, QTextStream
from pathlib import Path
from  datetime import datetime
from lxml import etree as ET
import pandas as pd
import sys
import csv
import os
import re
import webbrowser
import json
import traceback
import multiprocessing
from functools import partial
from typing import List, Tuple, Dict

class ConfigHandler:
    """Handles loading, saving, and managing application configuration,
    specifically custom paths.
    """
    def __init__(self):
        self.config_dir = "_internal\\configuration"
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Ensure the configuration directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.config = self.load_config()


    def load_config(self):
        """Loads configuration from the JSON file. If the file is missing or
        invalid, it returns a default configuration.
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {self.config_file} is empty or contains invalid JSON. Using default configuration.")
        return self.get_default_config()


    def get_default_config(self):
        """Returns the default application configuration."""
        return {"custom_paths": {}}


    def save_config(self):
        """Saves the current configuration to the JSON file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)


    def add_custom_path(self, name, path):
        """Adds a new custom path to the configuration and saves it."""
        self.config["custom_paths"][name] = path
        self.save_config()


    def get_custom_paths(self):
        """Returns all custom paths from the configuration."""
        return self.config["custom_paths"]


    def remove_custom_path(self, name):
        """Removes a custom path from the configuration and saves it."""
        if name in self.config["custom_paths"]:
            del self.config["custom_paths"][name]
            self.save_config()


class XMLParserThread(QObject):
    """Worker thread for parsing a single XML file and extracting its structure
    (tags, attributes, and their values). This prevents the UI from freezing.
    """
    finished = Signal(dict) # Emitted when parsing is complete, sends a dictionary of results
    show_error_message = Signal(str, str) # Emitted to show an error message in the UI

    def __init__(self, parent, xml_file):
        super().__init__()
        self.parent = parent
        self.xml_file = xml_file

    def run(self):
        """Parses the XML file and collects unique tags, tag values, attributes,
        and attribute values.
        """
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            # Convert XML tree to a pretty-printed string for display
            xml_string = ET.tostring(root, encoding="unicode", pretty_print=True)

            tags = set()
            tag_values = set()
            attributes = set()
            attribute_values = set()

            # Iterate over all elements to collect tags, attributes, and their values
            for elem in root.iter():
                tags.add(elem.tag) # Add tag name
                if elem.text and elem.text.strip():
                    tag_values.add(elem.text.strip()) # Add non-empty tag text
                for attr, value in elem.attrib.items():
                    attributes.add(attr) # Add attribute name
                    attribute_values.add(value) # Add attribute value

            # Prepare results dictionary
            result = {
                'xml_string': xml_string,
                'tags': sorted(tags),
                'tag_values': sorted(tag_values),
                'attributes': sorted(attributes),
                'attribute_values': sorted(attribute_values)
            }
            
        except Exception as ex:
            # Emit error message if parsing fails
            self.show_error_message.emit("An exception occurred during XML parsing", str(ex))
        finally:
            # Always emit finished signal, even if an error occurred
            self.finished.emit(result)

# Standalone processing functions that can be pickled for multiprocessing
def process_single_xml(filename: str, folder_path: str, xpath_expressions: List[str]) -> Tuple[List[Dict], int, int]:
    """
    Process a single XML file, apply a list of XPath expressions, and return
    a flattened list of matching results. Each result includes the filename,
    the XPath expression used, and the matched value.
    
    Args:
        filename (str): The name of the XML file to process.
        folder_path (str): The directory where the XML file is located.
        xpath_expressions (List[str]): A list of XPath expressions to apply.
        
    Returns:
        Tuple[List[Dict], int, int]: A tuple containing:
            - A list of dictionaries, where each dictionary represents a single match.
              Example: {"Filename": "doc1", "XPath Expression": "//tag", "Match Value": "value"}
            - The total number of matches found in the file.
            - 1 if any matches were found, 0 otherwise (used for counting matching files).
    """
    all_matches_for_file = []
    file_total_matches = 0
    file_path = os.path.join(folder_path, filename)

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.XMLSyntaxError:
        # Handle XML parsing errors gracefully, e.g., log them
        print(f"XML Syntax Error in {filename}. Skipping file.")
        return [], 0, 0
    except Exception as e:
        print(f"Error parsing {filename}: {e}. Skipping file.")
        return [], 0, 0

    for expression in xpath_expressions:
        try:
            result = root.xpath(expression)
            match_count = len(result)
            file_total_matches += match_count

            # Process each item found by the XPath expression
            for item in result:
                value = ""
                # Determine the value based on the type of item returned by XPath
                if isinstance(item, ET._Element):
                    # If the XPath returns an element, get its text content
                    value = item.text.strip() if item.text else ""
                elif isinstance(item, str):
                    # If the XPath returns a string (e.g., from /text() or /@attribute)
                    value = item.strip()
                else:
                    # For other types (e.g., numbers, booleans), convert to string
                    value = str(item).strip()

                # Add the flattened match to the list
                all_matches_for_file.append({
                    "Filename": os.path.splitext(filename)[0],
                    "XPath Expression": expression,
                    "Match Value": value
                })
        except Exception as e:
            # Log or handle XPath evaluation errors for a specific expression
            print(f"Error evaluating XPath '{expression}' in {filename}: {e}")
            continue # Continue to the next expression

    return all_matches_for_file, file_total_matches, 1 if file_total_matches > 0 else 0

class CSVExportThread(QObject):
    """Worker thread for exporting XML evaluation results to a CSV file.
    Uses multiprocessing for parallel XML file processing.
    """
    # Signals
    finished = Signal() # Emitted when the export task is complete
    show_info_message = Signal(str, str) # Emitted to show an informational message in the UI
    show_error_message = Signal(str, str) # Emitted to show an error message in the UI
    progress_updated = Signal(int) # Emitted to update the progress bar
    output_set_text = Signal(str) # Emitted to set text in the program output area
    output_append = Signal(str) # Emitted to append text to the program output area

    def __init__(self, folder_containing_xml_files, list_of_xpath_filters, csv_output_path):
        super().__init__()
        self.folder_containing_xml_files = folder_containing_xml_files
        self.list_of_xpath_filters = list_of_xpath_filters
        self.csv_output_path = csv_output_path
        self._is_running = True # Flag to control thread execution
        
    def stop(self):
        """Method to stop the running task by setting the internal flag."""
        self._is_running = False

    def run(self):
        """Entry point for the thread. Calls the search and export method and handles
        any exceptions.
        """
        try:
            self.search_and_export()
        except Exception as ex:
            self.show_error_message.emit("An unexpected exception occurred in CSV export thread", str(ex))
        finally:
            self.finished.emit()
        
    def search_and_export(self):
        """
        Coordinates the XML file evaluation using multiprocessing and exports the
        results to a CSV file.
        """
        try:
            # Evaluate XML files and get flattened results using multiprocessing
            matching_results, total_matches_found, total_matching_files = self.evaluate_xml_files_matching(
                self.folder_containing_xml_files, self.list_of_xpath_filters)
            
            # Check if the thread was stopped during the evaluation phase
            if not self._is_running:
                self.output_set_text.emit("Export task aborted successfully.")
                return 

        except Exception as ex:
            # Catch exceptions during the evaluation phase
            tb = traceback.extract_tb(ex.__traceback__)
            line_number = tb[-1].lineno
            message = f"An exception of type {type(ex).__name__} occurred on line {line_number}. Arguments: {ex.args!r}"
            self.show_error_message.emit("An exception occurred during XML evaluation", message)
            return
            
        try:
            if not matching_results:
                # If no matches found, inform the user and clear output
                self.show_info_message.emit("No matches found", "No matches found by searching with the added filters.")
                self.output_set_text.emit("")
                return
            
            # Define fixed headers for the flattened structure to be written to CSV
            headers = ["Filename", "XPath Expression", "Match Value"]

            with open(self.csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
                # Use csv.DictWriter to write dictionaries directly to CSV
                writer = csv.DictWriter(
                    csvfile, 
                    fieldnames=headers, 
                    delimiter=",", 
                    extrasaction="ignore", # Ignore any keys in dicts not in fieldnames
                    quotechar='"', 
                    quoting=csv.QUOTE_ALL
                )
                writer.writeheader() # Write the header row
                writer.writerows(matching_results) # Write all the collected matching results

            # Emit completion signals
            self.show_info_message.emit("Export Successful", "CSV export completed.")
            self.output_set_text.emit(
                f"Found {total_matching_files} files that have a total sum of {total_matches_found} matches."
            )

        except Exception as ex:
            # Catch exceptions during the CSV writing phase
            tb = traceback.extract_tb(ex.__traceback__)
            line_number = tb[-1].lineno
            message = f"An exception of type {type(ex).__name__} occurred on line {line_number}. Arguments: {ex.args!r}"
            self.show_error_message.emit("An exception occurred during CSV export", message)

        finally:
            self.finished.emit()

    def evaluate_xml_files_matching(self, folder_containing_xml_files, list_of_xpath_expressions):
        """
        Evaluates XML files in a given folder against a list of XPath expressions
        using multiprocessing for parallel processing.
        
        Args:
            folder_containing_xml_files (str): Path to the folder with XML files.
            list_of_xpath_expressions (List[str]): List of XPath expressions.
            
        Returns:
            Tuple[List[Dict], int, int]: A tuple containing:
                - A combined list of all flattened matching results from all files.
                - The total sum of all matches found across all files.
                - The total number of files that contained at least one match.
        """
        xml_files = [f for f in os.listdir(folder_containing_xml_files) if f.endswith(".xml")]
        total_files = len(xml_files)
        
        if not xml_files:
            return [], 0, 0

        # Calculate the number of processes to use (leave one core free to not block UI)
        num_processes = max(1, multiprocessing.cpu_count() - 1)
        
        # Initialize variables for results accumulation
        final_results = []
        total_sum_matches = 0
        total_matching_files = 0
        
        try:
            # Use a while loop to allow for early termination via _is_running flag
            while self._is_running:
                # Create a pool of processes
                with multiprocessing.Pool(processes=num_processes) as pool:
                    # Create a partial function with fixed arguments for the worker process
                    process_func = partial(
                        process_single_xml,
                        folder_path=folder_containing_xml_files,
                        xpath_expressions=list_of_xpath_expressions,
                    )
                    
                    # Process files asynchronously and collect results as they complete
                    # imap_unordered is used for better responsiveness as results come in any order
                    for i, (file_results, file_matches, matching_file) in enumerate(
                        pool.imap_unordered(process_func, xml_files)
                    ):
                        if not self._is_running:
                            # If stop signal received, terminate the pool and return
                            self.output_set_text.emit("Export task aborted successfully.")
                            pool.terminate()
                            # Return current partial results if aborted
                            return final_results, total_sum_matches, total_matching_files 
                        
                        # Extend the final results list with results from the current file
                        final_results.extend(file_results)
                        total_sum_matches += file_matches
                        total_matching_files += matching_file
                        
                        # Update progress for the UI
                        progress = int((i + 1) / total_files * 100)
                        self.progress_updated.emit(progress)
                        self.output_set_text.emit(f"Processing file {i + 1} of {total_files}")
                    
                    # If execution reaches here, all files have been processed
                    return final_results, total_sum_matches, total_matching_files
                    
        except Exception as ex:
            self.show_error_message.emit(
                "Multiprocessing Error",
                f"Error during multiprocessing: {str(ex)}"
            )
            return [], 0, 0

class MainWindow(QMainWindow):
    """Main application window for XMLuvation. Manages UI elements,
    user interactions, and orchestrates XML parsing and CSV export tasks.
    """
    progress_updated = Signal(int) # Signal to update the progress bar in the main window
    update_input_file_signal = Signal(str) # Signal to update the CSV conversion input file path
    update_output_file_signal = Signal(str) # Signal to update the CSV conversion output file path
    
    def __init__(self):
        super().__init__()
        # Ensure the widget is deleted when its window is closed
        self.setAttribute(Qt.WA_DeleteOnClose) 
        self.current_theme =  "_internal\\theme\\dark_theme.qss" # Default theme file path
        self.config_handler = ConfigHandler() # Initialize configuration handler
        self.eval_input_file = None # Stores the path of the XML file selected for individual evaluation
        self.xpath_filters = [] # List to store active XPath expressions for batch evaluation
        self.xpath_listbox = QListWidget(self) # UI element to display XPath filters
        self.program_output = QTextEdit() # UI element for general program messages
        # Thread and worker references for CSV export and XML parsing
        self.csv_export_thread = None
        self.csv_export_worker = None
        self.parse_xml_thread = None
        self.parse_xml_worker = None
        
        self.setWindowTitle("XMLuvation v1.3.1") # Set window title
        self.setWindowIcon(QIcon("_internal\\icon\\xml_256px.ico")) # Set window icon
        self.setGeometry(500, 250, 1300, 840) # Set initial window position and size
        self.saveGeometry() # Save geometry (e.g., for restoring window state)
        
        # Connect signals from worker threads to UI slots
        self.progress_updated.connect(self.update_progress)
        self.update_input_file_signal.connect(self.update_input_file)
        self.update_output_file_signal.connect(self.update_output_file)
        
        # Connect the custom context menu for the XPath Listbox
        self.xpath_listbox.setContextMenuPolicy(Qt.CustomContextMenu)
        self.xpath_listbox.customContextMenuRequested.connect(self.show_context_menu)
        
        # Theme icons
        self.light_mode = QIcon("_internal\\images\\light.png")
        self.dark_mode = QIcon("_internal\\images\\dark.png")
        
        self.initUI() # Initialize the main UI components
        
        # Create the menu bar after UI initialization
        self.create_menu_bar()
        
        # Attempt to load saved theme preference, otherwise apply default
        try:
            with open("_internal\\theme\\theme_config.txt", "r") as f:
                    saved_theme = f.read().strip()
                    self.initialize_theme(saved_theme)
                    # Update toggle theme icon based on loaded theme
                    if saved_theme == "_internal\\theme\\light_theme.qss":
                        self.toggle_theme_action.setIcon(self.dark_mode)
                    else:
                        self.toggle_theme_action.setIcon(self.light_mode)
        except FileNotFoundError:
            # If theme config file doesn't exist, apply current default theme
            self.initialize_theme(self.current_theme)
        
    def initUI(self):
        """Initializes the main user interface layout and tabs."""
        # Create the main vertical layout for the window
        main_layout = QVBoxLayout()

        # Create the tab widget to organize different functionalities
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_xml_evaluation_tab(), "XML Evaluation")
        tab_widget.addTab(self.create_csv_conversion_tab(), "CSV Conversion and Display")

        # Add the tab widget to the main layout
        main_layout.addWidget(tab_widget)

        # Create a central widget to hold the main layout and set it for the QMainWindow
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    
    def closeEvent(self, event: QCloseEvent):
        """Overrides the default close event to prompt the user before exiting
        and saves the current theme preference.
        """
        reply = QMessageBox.question(
            self, 'Exit Program', 'Are you sure you want to exit the program?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # If user confirms, accept the close event and save theme
            event.accept()
            with open("_internal\\theme\\theme_config.txt", "w") as f:
                f.write(self.current_theme)
        else:
            # If user cancels, ignore the close event
            event.ignore()
    

    def initialize_theme(self, theme_file):
        """Applies a QSS stylesheet from a given file to the application."""
        try:
            file = QFile(theme_file)
            if file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.setStyleSheet(stylesheet) # Apply the stylesheet
            file.close()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Theme load error", message)
    
    def create_menu_bar(self):
        """Creates the application's menu bar with various actions like File,
        Open, Path, and Help.
        """
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        clear_action = QAction("Clear Output", self)
        clear_action.setStatusTip("Clear the output text areas")
        clear_action.triggered.connect(self.clear_output)
        file_menu.addAction(clear_action)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Open Menu (for opening folders/files related to input/output)
        open_menu = menu_bar.addMenu("&Open")
        open_input_action = QAction("Open XML Input Folder", self)
        open_input_action.setStatusTip("Open the XML input folder")
        open_input_action.triggered.connect(self.open_input_folder)
        open_output_action = QAction("Open CSV Output Folder", self)
        open_output_action.setStatusTip("Open the CSV output folder")
        open_output_action.triggered.connect(self.open_output_folder)
        open_menu.addAction(open_output_action)
        open_menu.addSeparator()
        open_csv_conversion_input_action = QAction("Open CSV Conversion Input Folder", self)
        open_csv_conversion_input_action.setStatusTip("Open CSV Conversion Input Folder")
        open_csv_conversion_input_action.triggered.connect(self.open_conversion_input)
        open_csv_conversion_output_action = QAction("Open CSV Conversion Output Folder", self)
        open_csv_conversion_output_action.setStatusTip("Open CSV Conversion Output Folder")
        open_csv_conversion_output_action.triggered.connect(self.open_conversion_output)
        open_menu.addAction(open_csv_conversion_output_action)

        # Path Menu (for managing custom frequently used paths)
        self.paths_menu = menu_bar.addMenu("&Path")
        
        # Load custom paths from configuration and add them to the menu
        self.load_custom_paths()

        # Add option to add new custom path to the menu
        add_custom_path_action = QAction("Add Custom Path", self)
        add_custom_path_action.triggered.connect(self.add_custom_path)
        self.paths_menu.addAction(add_custom_path_action)

        
        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        xpath_help_action = QAction("XPath Help", self)
        xpath_help_action.setStatusTip("Open W3Schools XPath Syntax Help in browser")
        xpath_help_action.triggered.connect(self.open_web_xpath_help)
        help_menu.addAction(xpath_help_action)
        about = QAction("About", self)
        about.setStatusTip("About this program")
        about.triggered.connect(self.about_message)
        help_menu.addAction(about)
        
        # Theme Toggle Button in menu bar
        self.toggle_theme_action = menu_bar.addAction(self.light_mode, "Toggle Theme")
        self.toggle_theme_action.triggered.connect(self.change_theme)
        
    # ======= START FUNCTIONS FOR create_menu_bar ======= #
    
    def update_paths_menu(self):
        """Updates the 'Path' menu with current custom paths from config."""
        # Clear existing path actions, except the 'Add Custom Path' action (which is usually last)
        # Assuming 'Add Custom Path' is always the last action in the menu
        for action in self.paths_menu.actions()[:-1]:
            self.paths_menu.removeAction(action)

        # Add custom paths from the configuration handler
        custom_paths = self.config_handler.get_custom_paths()
        # Insert new actions at the beginning of the menu (before 'Add Custom Path')
        for name, path in custom_paths.items():
            action = QAction(name, self)
            action.setStatusTip(f"Open {name}")
            # Use functools.partial to pass path argument to open_path
            action.triggered.connect(partial(self.open_path, path))
            self.paths_menu.insertAction(self.paths_menu.actions()[0], action)
            

    def add_custom_path(self):
        """Prompts the user to add a new custom path (name and path) and saves it."""
        name, ok = QInputDialog.getText(self, "Add Custom Path", "Enter a name for the path:")
        if ok and name:
            path, ok = QInputDialog.getText(self, "Add Custom Path", "Enter path:")
            if ok and path:
                self.config_handler.add_custom_path(name, path)
                self.update_paths_menu() # Refresh the menu to show the new path
                
    
    def load_custom_paths(self):
        """Loads custom paths from config and adds them to the menu bar."""
        custom_paths = self.config_handler.get_custom_paths()
        for name, path in custom_paths.items():
            action = QAction(name, self)
            action.setStatusTip(f"Open {name}")
            action.triggered.connect(partial(self.open_path, path))
            self.paths_menu.addAction(action)
            
    
    def about_message(self):
        """Displays an 'About' message box with program information."""
        program_info = "Name: XMLuvation\nVersion: 1.3.1\nCredit: Jovan\nFramework: PySide6"
        about_message = """XMLuvation is a Python application designed to parse and evaluate XML files and use XPath to search for matches which matching results will be saved in a csv file. Radio buttons are disabled for now, this feature will be implemented in a later version."""
        
        about_box = QMessageBox()
        about_box.setText("About this program...")
        about_box.setInformativeText(about_message)
        about_box.setDetailedText(program_info)
        about_box.exec()

    
    def change_theme(self):
        """Toggles between dark and light themes."""
        if self.current_theme == "_internal\\theme\\dark_theme.qss":
            self.current_theme = "_internal\\theme\\light_theme.qss"
            self.toggle_theme_action.setIcon(self.dark_mode) # Set icon for next toggle
        else:
            self.current_theme = "_internal\\theme\\dark_theme.qss"
            self.toggle_theme_action.setIcon(self.light_mode) # Set icon for next toggle
        self.initialize_theme(self.current_theme) # Apply the new theme
    
    def clear_output(self):
        """Clears the text in the program output and CSV conversion output areas."""
        self.program_output.clear()
        self.csv_conversion_output.clear()
    
    def open_input_folder(self):
        """Opens the XML input folder in the system's file explorer."""
        directory_path = self.folder_xml_input.text()
        self._open_directory(directory_path, "XML input folder")
    
    
    def open_output_folder(self):
        """Opens the CSV output folder in the system's file explorer."""
        directory_path = self.folder_csv_output.text()
        self._open_directory(directory_path, "CSV output folder")
    
    
    def open_conversion_input(self):
        """Opens the directory of the CSV conversion input file in the system's file explorer."""
        file_path = self.input_csv_file_conversion.text()
        dirname = os.path.dirname(file_path) # Get directory from file path
        self._open_directory(dirname, "CSV Conversion input file directory")
            
            
    def open_conversion_output(self):
        """Opens the directory of the CSV conversion output file in the system's file explorer."""
        file_path = self.output_csv_file_conversion.text()
        dirname = os.path.dirname(file_path) # Get directory from file path
        self._open_directory(dirname, "CSV Conversion output file directory")
            
    def _open_directory(self, path: str, description: str):
        """Helper function to open a directory or its parent directory."""
        if os.path.exists(path) and os.path.isdir(path):
            try:
                os.startfile(path)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "Error opening directory", f"Failed to open {description}:\n{message}")
        elif os.path.exists(path) and os.path.isfile(path):
            try:
                os.startfile(os.path.dirname(path))
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "Error opening directory", f"Failed to open directory for {description}:\n{message}")
        else:
            QMessageBox.warning(self, "Path Error", f"Path does not exist or is not valid:\n{path}")
            
    
    def open_path(self, path: str):
        """Sets the XML input folder text to a selected custom path."""
        self.folder_xml_input.setText(path)
    
    
    def open_web_xpath_help(self):
        """Opens the W3Schools XPath syntax help page in the default web browser."""
        webbrowser.open("https://www.w3schools.com/xml/xpath_syntax.asp")
        
    # ======= END FUNCTIONS FOR create_menu_bar ======= #
    
    def create_xml_evaluation_tab(self):
        """Creates and returns the 'XML Evaluation' tab widget."""
        tab = QWidget()
        layout = QHBoxLayout()

        # Left column contains XML folder selection, XPath filters, export, and program output
        left_column = QVBoxLayout()
        left_column.addWidget(self.create_xml_eval_group())
        left_column.addWidget(self.create_matching_filter_group())
        left_column.addWidget(self.create_export_evaluation_group())
        left_column.addWidget(self.create_program_output_group())

        # Right column contains the XML output viewer
        right_column = QVBoxLayout()
        right_column.addWidget(self.create_xml_output_group())

        layout.addLayout(left_column, 1) # Set left column to take 1 unit of space
        layout.addLayout(right_column, 1) # Set right column to take 1 unit of space
        tab.setLayout(layout)
        return tab


    def create_xml_eval_group(self):
        """Creates the 'XML Folder Selection and XPath Builder' group box."""
        group = QGroupBox("XML FOLDER SELECTION AND XPATH BUILDER")
        layout = QVBoxLayout()
        
        xml_input_folder_and_statusbar_layout = QHBoxLayout()
        
        # Status bar for displaying total XML files found
        self.total_xml_files_statusbar = QStatusBar()
        self.setStatusBar(self.total_xml_files_statusbar)
        self.total_xml_files_statusbar.setSizeGripEnabled(False)
        self.total_xml_files_statusbar.setStyleSheet("font-size: 20;font-weight: bold; color: #0cd36c")
        
        xml_input_folder_and_statusbar_layout.addWidget(self.total_xml_files_statusbar)
        layout.addLayout(xml_input_folder_and_statusbar_layout)
        
        # Elements for XML input folder selection
        self.folder_xml_input = QLineEdit()
        self.folder_xml_input.setPlaceholderText("Choose a folder that contains XML files...")
        # Connect text change to update XML file count
        self.folder_xml_input.textChanged.connect(self.update_xml_file_count) 
        self.browse_xml_folder_button = QPushButton("BROWSE")
        self.browse_xml_folder_button.clicked.connect(self.browse_folder)
        self.read_xml_button = QPushButton("READ XML")
        self.read_xml_button.setToolTip("Writes the content of the selected XML file to the output and fills out the ComboBoxes based on the XMLs content.")
        self.read_xml_button.clicked.connect(self.read_xml)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_xml_input)
        folder_layout.addWidget(self.browse_xml_folder_button)
        folder_layout.addWidget(self.read_xml_button)
        layout.addLayout(folder_layout)

        layout.addSpacerItem(QSpacerItem(2,5, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(QLabel("Get XML Tag and Attribute Names/Values for XPath generation:"))
        layout.addSpacerItem(QSpacerItem(2,5, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Elements for Tag name and value selection
        tag_layout = QHBoxLayout()
        self.tag_name_label = QLabel("Tag name:")
        self.tag_name_combobox = QComboBox()
        self.tag_name_combobox.setEditable(True)
        self.tag_name_combobox.currentTextChanged.connect(self.on_tag_name_changed)
        self.tag_value_label = QLabel("Tag value:")
        self.tag_value_combobox = QComboBox()
        self.tag_value_combobox.setEditable(True)
        
        self.tag_name_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.tag_value_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        tag_layout.addWidget(self.tag_name_label)
        tag_layout.addWidget(self.tag_name_combobox)
        tag_layout.addWidget(self.tag_value_label)
        tag_layout.addWidget(self.tag_value_combobox)
        layout.addLayout(tag_layout)

        # Elements for Attribute name and value selection
        att_layout = QHBoxLayout()
        self.attribute_name_label = QLabel("Attr name:")
        self.attribute_name_combobox = QComboBox()
        self.attribute_name_combobox.setEditable(True)
        self.attribute_name_combobox.currentTextChanged.connect(self.on_attribute_name_changed)
        self.attribute_value_label = QLabel("Attr value:")
        self.attribute_value_combobox = QComboBox()
        self.attribute_value_combobox.setEditable(True)
        
        att_layout.addWidget(self.attribute_name_label)
        att_layout.addWidget(self.attribute_name_combobox)
        att_layout.addWidget(self.attribute_value_label)
        att_layout.addWidget(self.attribute_value_combobox)
        layout.addLayout(att_layout)
        layout.addSpacerItem(QSpacerItem(40,10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.attribute_name_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.attribute_value_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Radio buttons for XPath function selection (Equals, Contains, etc.)
        function_layout = QHBoxLayout()
        self.radio_button_equals = QRadioButton("Equals")
        self.radio_button_equals.setChecked(True) # Default selection
        self.radio_button_contains = QRadioButton("Contains")
        self.radio_button_startswith = QRadioButton("Starts-with")
        self.radio_button_greater = QRadioButton("Greater")
        self.radio_button_smaller = QRadioButton("Smaller")
        
        function_layout.addWidget(QLabel("Function:"))
        function_layout.addWidget(self.radio_button_equals)
        function_layout.addWidget(self.radio_button_contains)
        function_layout.addWidget(self.radio_button_startswith)
        function_layout.addWidget(self.radio_button_greater)
        function_layout.addWidget(self.radio_button_smaller)
        layout.addLayout(function_layout)
        
        # Elements for building and adding XPath expressions
        build_xpath_layout = QHBoxLayout()
        self.xpath_expression_input = QLineEdit()
        self.xpath_expression_input.setPlaceholderText("Enter a XPath expression or build one...")
        self.build_xpath_button = QPushButton("BUILD XPATH")
        self.build_xpath_button.setToolTip("Builds XPath expression based on the selected ComboBox values for Tag Name/Value and Attribute Name/Value")
        self.build_xpath_button.clicked.connect(self.build_xpath)
        self.add_xpath_to_list_button = QPushButton("ADD XPATH TO LIST")
        self.add_xpath_to_list_button.setToolTip("Adds currently entered XPath expression to the List below which is used to match for in the XML File(s).")
        self.add_xpath_to_list_button.clicked.connect(self.add_xpath_expression_to_listbox)
        self.add_xpath_to_list_button.clicked.connect(self.update_statusbar_xpath_listbox_count)
        build_xpath_layout.addWidget(self.xpath_expression_input)
        build_xpath_layout.addWidget(self.build_xpath_button)
        layout.addLayout(build_xpath_layout)
        layout.addWidget(self.add_xpath_to_list_button)

        group.setLayout(layout)
        return group
    
    # ======= START FUNCTIONS FOR create_xml_eval_group ======= #

    def on_tag_name_changed(self, selected_tag: str):
        """
        Slot connected to tag_name_combobox's currentTextChanged signal.
        Updates attribute and tag value comboboxes based on the selected tag.
        """
        if not selected_tag or not self.eval_input_file:
            # Clear and disable related comboboxes if no tag is selected or no XML file is loaded
            self.attribute_name_combobox.clear()
            self.attribute_name_combobox.setDisabled(True)
            self.attribute_value_combobox.clear()
            self.attribute_value_combobox.setDisabled(True)
            self.tag_value_combobox.clear()
            self.tag_value_combobox.setDisabled(True)
            return

        try:
            # Get attributes for the selected tag and populate attribute name combobox
            attributes = self.get_attributes(self.eval_input_file, selected_tag)
            self.attribute_name_combobox.clear()
            self.attribute_name_combobox.addItems(attributes)

            # Get tag values for the selected tag and populate tag value combobox
            values_xml = self.get_tag_values(self.eval_input_file, selected_tag)
            self.tag_value_combobox.clear()
            self.tag_value_combobox.addItems(values_xml)

            # Enable/disable tag value combobox based on availability of values
            if not values_xml or all(value.strip() == "" for value in values_xml if value is not None):
                self.tag_value_combobox.setDisabled(True)
                self.tag_value_combobox.clear()
            else:
                self.tag_value_combobox.setDisabled(False)

            # Enable/disable attribute comboboxes based on availability of attributes
            if not attributes:
                self.attribute_name_combobox.setDisabled(True)
                self.attribute_name_combobox.clear()
                self.attribute_value_combobox.setDisabled(True)
                self.attribute_value_combobox.clear()
            else:
                self.attribute_name_combobox.setDisabled(False)
                # If attributes exist, clear attribute value combo as its content depends on attribute name
                self.attribute_value_combobox.clear() 
                self.attribute_value_combobox.setDisabled(True) # Disable until an attribute name is chosen
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred", message)


    def on_attribute_name_changed(self, selected_attribute: str):
        """
        Slot connected to attribute_name_combobox's currentTextChanged signal.
        Updates the attribute value combobox based on the selected attribute name.
        """
        try:
            selected_tag = self.tag_name_combobox.currentText()
            if not selected_attribute or not selected_tag or not self.eval_input_file:
                self.attribute_value_combobox.clear()
                self.attribute_value_combobox.setDisabled(True)
                return

            # Get attribute values for the selected tag and attribute
            attribute_values = self.get_attribute_values(self.eval_input_file, selected_tag, selected_attribute)
            self.attribute_value_combobox.clear()
            self.attribute_value_combobox.addItems(attribute_values)

            # Enable/disable attribute value combobox based on availability of values
            if not attribute_values:
                self.attribute_value_combobox.setDisabled(True)
                self.attribute_value_combobox.clear()
            else:
                self.attribute_value_combobox.setDisabled(False)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self,"Exception in Program", message)


    def get_attributes(self, eval_input_file: str, selected_tag: str) -> List[str]:
        """Retrieves unique attribute names for a given tag from the XML file."""
        if not eval_input_file or not selected_tag:
            return []
        try:
            root = ET.parse(eval_input_file).getroot()
            attributes = set()
            # Iterate over elements with the selected tag and collect their attribute names
            for elem in root.iter(selected_tag):
                attributes.update(elem.attrib.keys())
            return sorted(attributes)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self,"Error getting attributes", message)
            return []


    def get_tag_values(self, eval_input_file: str, selected_tag: str) -> List[str]:
        """Retrieves unique text values for a given tag from the XML file."""
        if not eval_input_file or not selected_tag:
            return []
        try:
            root = ET.parse(eval_input_file).getroot()
            values = set()
            # Iterate over elements with the selected tag and collect their non-empty text values
            for elem in root.iter(selected_tag):
                if elem.text and elem.text.strip():
                    values.add(elem.text.strip())
            return sorted(values)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self,"Error getting tag values", message)
            return []


    def get_attribute_values(self, eval_input_file: str, selected_tag: str, selected_attribute: str) -> List[str]:
        """Retrieves unique values for a specific attribute within a given tag from the XML file."""
        if not eval_input_file or not selected_tag or not selected_attribute:
            return []
        try:
            root = ET.parse(eval_input_file).getroot()
            values = set()
            # Iterate over elements with the selected tag and collect values for the specified attribute
            for elem in root.iter(selected_tag):
                if selected_attribute in elem.attrib:
                    values.add(elem.attrib[selected_attribute])
            return sorted(values)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Error getting attribute values", message)
            return []


    def parse_xml(self, xml_file: str):
        """Initiates a new thread to parse the selected XML file.
        This prevents the UI from freezing during parsing.
        """
        try:
            self.parse_xml_thread = QThread() # Create a new QThread
            self.parse_xml_worker = XMLParserThread(None, xml_file) # Create a worker object
            self.parse_xml_worker.moveToThread(self.parse_xml_thread) # Move worker to the thread
            
            # Connect signals from worker to main thread slots
            self.parse_xml_worker.finished.connect(self.on_xml_parsed)
            self.parse_xml_worker.finished.connect(self.parse_xml_thread.quit) # Quit thread when worker finishes
            self.parse_xml_worker.show_error_message.connect(self.show_error_message)
            self.parse_xml_thread.started.connect(self.parse_xml_worker.run) # Start worker's run method when thread starts

            self.parse_xml_thread.start() # Start the QThread

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", message)


    def on_xml_parsed(self, result: dict):
        """
        Slot connected to XMLParserThread's finished signal.
        Updates the XML output area and populates comboboxes with parsed data.
        """
        # Display the pretty-printed XML string
        self.xml_output.setText(result['xml_string'])

        # Clear existing items in comboboxes
        self.tag_name_combobox.clear()
        self.tag_value_combobox.clear()
        self.attribute_name_combobox.clear()
        self.attribute_value_combobox.clear()

        # Populate comboboxes with sorted unique data
        self.tag_name_combobox.addItems(result['tags'])
        self.tag_value_combobox.addItems(result['tag_values'])
        self.attribute_name_combobox.addItems(result['attributes'])
        self.attribute_value_combobox.addItems(result['attribute_values'])
        
        # Clear selected text in comboboxes (important for fresh state after loading)
        self.tag_name_combobox.setEditText("") 
        self.tag_value_combobox.setEditText("")
        self.attribute_name_combobox.setEditText("")
        self.attribute_value_combobox.setEditText("")

        # Store the path of the currently evaluated XML file
        self.eval_input_file = self.parse_xml_worker.xml_file
        self.program_output.setText("XML file loaded successfully.")


    def read_xml(self):
        """Opens a file dialog to select an XML file for parsing."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select XML File", "", "XML Files (*.xml)")
            if file_name:
                self.parse_xml(file_name) # Initiate parsing if a file is selected
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", message)
            
    def browse_folder(self):
        """Opens a directory dialog to select a folder containing XML files."""
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_xml_input.setText(folder) # Set the selected folder path
            self.update_xml_file_count(folder) # Update the XML file count status


    def build_xpath(self):
        """
        Builds an XPath expression based on the currently selected tag, tag value,
        attribute name, and attribute value from the comboboxes, applying the
        chosen function (equals, contains, etc.).
        """
        try:
            # Get values from comboboxes
            tag_name = self.tag_name_combobox.currentText().strip()
            tag_value = self.tag_value_combobox.currentText().strip()
            attribute_name = self.attribute_name_combobox.currentText().strip()
            attribute_value = self.attribute_value_combobox.currentText().strip()

            xpath_expression = ""
            selected_operation = self.get_selected_operation() # Get the selected comparison function

            if not tag_name:
                self.xpath_expression_input.setText("") # Clear if no tag name
                self.program_output.setText("Please select a Tag name to build an XPath.")
                return

            # Start with the base tag path
            xpath_expression = f"//{tag_name}"
            
            # Build predicates based on selected criteria
            predicates = []

            # Handle tag value criteria
            if tag_value:
                # If only tag value is present, prioritize text() for simple matching
                if not attribute_name and not attribute_value:
                    xpath_expression += f"[{self.build_tag_criterion(selected_operation, tag_value)}]"
                else:
                    predicates.append(self.build_tag_criterion(selected_operation, tag_value))

            # Handle attribute criteria
            if attribute_name:
                if attribute_value:
                    predicates.append(self.build_attribute_criterion(selected_operation, attribute_name, attribute_value))
                else:
                    # If only attribute name is selected (no value), and no tag value,
                    # just add the attribute existence check
                    if not tag_value and not predicates:
                        xpath_expression += f"[@{attribute_name}]"
                        # If the goal is to get the attribute's value directly
                        if not tag_value and not attribute_value:
                            xpath_expression += f"/@{attribute_name}"
                    elif attribute_name:
                        # Otherwise, add attribute existence check to predicates
                        predicates.append(f"@{attribute_name}")
                        

            # If there are predicates, combine them
            if predicates:
                xpath_expression += f"[{' and '.join(predicates)}]"

            # Special case for getting text() or attribute values directly if only tag/attribute is chosen
            if not tag_value and not attribute_name and not attribute_value:
                xpath_expression += "/text()" # Default to text() if only tag name is present

            elif tag_name and attribute_name and not tag_value and not attribute_value:
                xpath_expression += f"/@{attribute_name}" # If only tag and attribute name are present
            
            self.xpath_expression_input.setText(xpath_expression) # Update XPath input field
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error building XPath: {message}")


    def get_selected_operation(self) -> str:
        """Determines the selected XPath comparison operation from radio buttons."""
        if self.radio_button_equals.isChecked():
            return "equals"
        elif self.radio_button_contains.isChecked():
            return "contains"
        elif self.radio_button_startswith.isChecked():
            return "startswith"
        elif self.radio_button_greater.isChecked():
            return "greater"
        elif self.radio_button_smaller.isChecked():
            return "smaller"
        else:
            return "equals"  # Default to equals if no radio button is checked


    def build_tag_criterion(self, operation: str, value: str) -> str:
        """Builds an XPath criterion for a tag's text content based on the operation."""
        if operation == "equals":
            return f"text()='{value}'"
        elif operation == "contains":
            return f"contains(text(), '{value}')"
        elif operation == "startswith":
            return f"starts-with(text(), '{value}')"
        elif operation == "greater":
            # For numerical comparison, ensure value is a number if applicable
            return f"number(text()) > {value}" if value.isdigit() else f"text() > '{value}'"
        elif operation == "smaller":
            return f"number(text()) < {value}" if value.isdigit() else f"text() < '{value}'"
        return ""


    def build_attribute_criterion(self, operation: str, name: str, value: str) -> str:
        """Builds an XPath criterion for an attribute's value based on the operation."""
        if operation == "equals":
            return f"@{name}='{value}'"
        elif operation == "contains":
            return f"contains(@{name}, '{value}')"
        elif operation == "startswith":
            return f"starts-with(@{name}, '{value}')"
        elif operation == "greater":
            return f"number(@{name}) > {value}" if value.isdigit() else f"@{name} > '{value}'"
        elif operation == "smaller":
            return f"number(@{name}) < {value}" if value.isdigit() else f"@{name} < '{value}'"
        return ""

    # ======= END FUNCTIONS FOR create_xml_eval_group ======= #
    
    def create_matching_filter_group(self):
        """Creates the 'List of XPath Filters' group box."""
        group = QGroupBox("LIST OF XPATH FILTERS TO SEARCH AND MATCH IN XML FILE(S)")
        layout = QVBoxLayout()
        
        # Horizontal line as a visual separator
        spacer = QFrame()
        spacer.setFrameShape(QFrame.HLine)
        spacer.setFrameShadow(QFrame.Sunken)
        
        # XPath listbox
        self.xpath_listbox.setMinimumHeight(100)
        # Status bar for displaying count of items in the listbox
        self.statusbar_xpath_listbox_count = QStatusBar()
        self.statusbar_xpath_listbox_count.setSizeGripEnabled(False)
        self.statusbar_xpath_listbox_count.setStyleSheet("font-weight: bold; color: #ffd740")

        layout.addWidget(self.xpath_listbox)
        layout.addWidget(self.statusbar_xpath_listbox_count)

        group.setLayout(layout)
        return group
    
    # ======= Start FUNCTIONS FOR create_matching_filter_group ======= #
    
    def update_statusbar_xpath_listbox_count(self):
        """Updates the status bar with the current number of XPath filters in the list."""
        self.counter = self.xpath_listbox.count()
        if self.counter != 0:
            self.statusbar_xpath_listbox_count.showMessage(f"Total number of items in List: {self.counter}", 5000)
        else:
            self.statusbar_xpath_listbox_count.clearMessage() # Clear message if list is empty
        
    
    def remove_selected_items(self):
        """Removes the currently selected XPath expression(s) from the listbox and internal list."""
        try:
            selected_items = self.xpath_listbox.selectedItems()
            if not selected_items:
                self.program_output.append("No item selected to delete.")
                return

            for item in selected_items:
                row = self.xpath_listbox.row(item)
                self.xpath_listbox.takeItem(row) # Remove from UI
                # Remove from internal list (adjust index if multiple items removed, or iterate carefully)
                # For simplicity, if multiple are selected, removing by text might be safer or recreate list
                # Here, we assume single selection for simplicity or items are distinct
                if item.text() in self.xpath_filters:
                    self.xpath_filters.remove(item.text()) 
                self.program_output.append(f"Removed item: {item.text()}")
            
            self.update_statusbar_xpath_listbox_count() # Update count after removal
        
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error removing selected item from list: {message}")


    def remove_all_items(self):
        """Removes all XPath expressions from the listbox and internal list."""
        try:
            if self.xpath_listbox.count() > 0:
                self.xpath_filters.clear() # Clear internal list
                self.xpath_listbox.clear() # Clear UI listbox
                self.program_output.setText("Deleted all items from the list.")
            else:
                self.program_output.setText("No items to delete.")
                
            self.update_statusbar_xpath_listbox_count() # Update count (should be 0)
            
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error removing all items from list: {message}")
            
    # Statusbar update function for XML files
    def update_xml_file_count(self, folder: str):
        """Updates the status bar to show the number of XML files in the specified folder."""
        try:
            if Path(folder).is_dir():
                xml_files = list(Path(folder).glob('*.xml')) # Find all .xml files
                file_count = len(xml_files)
                self.total_xml_files_statusbar.setStyleSheet("font-size: 20;font-weight: bold; color: #0cd36c")
                self.total_xml_files_statusbar.showMessage(f"Found {file_count} XML Files")
            else:
                # If path is not a directory or doesn't exist, clear message
                self.total_xml_files_statusbar.clearMessage() 
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.total_xml_files_statusbar.setStyleSheet("color: #ed2828") # Indicate error with red text
            self.total_xml_files_statusbar.showMessage(f"Error counting XML files: {message}")


    def show_context_menu(self, position):
        """Displays a context menu when the XPath listbox is right-clicked."""
        context_menu = QMenu(self)
        delete_action = QAction("Delete Selected", self)
        delete_all_action = QAction("Delete All", self)

        context_menu.addAction(delete_action)
        context_menu.addAction(delete_all_action)

        delete_action.triggered.connect(self.remove_selected_items)
        delete_all_action.triggered.connect(self.remove_all_items)

        # Show the context menu at the cursor's current position
        context_menu.exec(self.xpath_listbox.mapToGlobal(position))
    
    
    def is_duplicate(self, xpath_expression: str) -> bool:
        """Checks if an XPath expression already exists in the list."""
        return xpath_expression in self.xpath_filters
    
    
    def validate_xpath_expression(self, xpath_expression: str) -> bool:
        """
        Validates if an XPath expression matches any of the defined valid patterns.
        Note: This is a basic regex validation and might not cover all valid XPath syntax.
        """
        # Define valid patterns (example subset, extend as needed)
        valid_patterns = [
            r"^/[\w]+$",  # /xml_element
            r"^//[\w]+$",  # //xml_element
            r"^//[\w]+\[@[\w]+\]$",  # //xml_element[@attribute]
            r"^//[\w]+\[@[\w]+='[^']*'\]$",  # //xml_element[@attribute='value']
            r"^//[\w]+\[@[\w]+!='[^']*'\]$",  # //xml_element[@attribute!='value']
            r"^//[\w]+\[@[\w]+='[^']*' and @[\w]+='[^']*'\]$",  # //xml_element[@attribute1='value1' and @attribute2='value2']
            r"^//[\w]+\[contains\(@[\w]+, '[^']*'\)\]$",  # //xml_element[contains(@attribute, 'substring')]
            r"^//[\w]+\[starts-with\(@[\w]+, '[^']*'\)\]$",  # //xml_element[starts-with(@attribute, 'substring')]
            r"^//[\w]+\[text\(\)='[^']*'\]$",  # //xml_element[text()='value']
            r"^//[\w]+\[contains\(text\(\), '[^']*'\)\]$",  # //xml_element[contains(text(), 'substring')]
            r"^//[\w]+\[starts-with\(text\(\), '[^']*'\)\]$",  # //xml_element[starts-with(text(), 'substring')]
            r"^//[\w]+\[number\(@[\w]+\) > [0-9.]+\]$",  # //xml_element[number(@attribute) > 10]
            r"^//[\w]+\[number\(@[\w]+\) < [0-9.]+\]$",  # //xml_element[number(@attribute) < 10]
            r"^//[\w]+/[\w]+/text\(\)$",  # //xml_element/xml_element/text()
            r"^//[\w]+/[\w]+\[@[\w]+\]/text\(\)$",  # //xml_element/xml_element[@attribute]/text()
            r"^//[\w]+/[\w]+\[@[\w]+='[^']*'\]/text\(\)$",  # //xml_element/xml_element[@attribute='value']/text()
            r"^//[\w]+/[\w]+$",  # //xml_element/xml_element
            r"^//[\w]+/[\w]+/[\w]+$",  # //xml_element/xml_element/xml_element
            r"^//[\w]+/text\(\)$",  # //xml_element/text()
            r"^//[\w]+/@[\w]+$",  # //xml_element/@attribute
            r"^//[\w]+/[\w]+\[@[\w]+\]$",  # //xml_element/xml_element[@attribute]
            r"^//[\w]+/[\w]+\[text\(\)='[^']*'\]$",  # //xml_tag_name/another_xml_tag_name[text()='some_value']
            r"^//[\w]+/[\w]+/@[\w]+$",  # //xml_tag/xml_tag/@attribute
            r"^count\(//[\w]+\)$" # count(//tag)
        ]

        # Check if expression matches any pattern
        return any(re.match(pattern, xpath_expression) for pattern in valid_patterns)

    
    def add_xpath_expression_to_listbox(self):
        """Adds the XPath expression from the input field to the listbox if it's valid and not a duplicate."""
        xpath_expression = self.xpath_expression_input.text().strip()
        try:
            if not xpath_expression:
                self.program_output.setText("No XPath expression entered.")
            elif self.is_duplicate(xpath_expression):
                QMessageBox.warning(self, "Error adding filter", f"Cannot add duplicate XPath expression:\n{xpath_expression}")
            else:
                # Optional: Re-enable validation if desired, but be aware of its limitations
                # validate = self.validate_xpath_expression(xpath_expression) 
                # if validate:
                self.xpath_filters.append(xpath_expression) # Add to internal list
                self.xpath_listbox.addItem(xpath_expression) # Add to UI listbox
                self.xpath_expression_input.clear() # Clear input field after adding
                self.program_output.setText(f"Added XPath: '{xpath_expression}'")
                # else:
                #    self.program_output.setText("Not a valid XPath expression!")
                #    QMessageBox.warning(self, "Invalid XPath", f"The entered XPath expression '{xpath_expression}' is not valid, please try again.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error adding filter: {message}")
            QMessageBox.critical(self, "Exception adding filter", message)

    # ======= End FUNCTIONS FOR create_matching_filter_group ======= #

    def create_export_evaluation_group(self):
        """Creates the 'Export Search Result to a CSV File' group box."""
        group = QGroupBox("EXPORT SEARCH RESULT TO A CSV FILE")
        
        layout = QVBoxLayout()
        
        # Elements for CSV output folder selection
        self.folder_csv_output = QLineEdit()
        self.folder_csv_output.setPlaceholderText("Choose a folder where to save the CSV evaluation...")
        self.csv_save_as_button = QPushButton("BROWSE")
        self.csv_save_as_button.clicked.connect(self.choose_save_folder)
        
        # Buttons for export and aborting export
        self.csv_convert_button = QPushButton("EXPORT")
        self.csv_convert_button.setToolTip("Starts processing each XML file and writes the found matches to a CSV file.")
        self.csv_convert_button.clicked.connect(self.write_to_csv)
        self.csv_abort_export_button = QPushButton("ABORT")
        self.csv_abort_export_button.setHidden(True) # Hidden by default
        self.csv_abort_export_button.clicked.connect(self.stop_csv_export_thread)
        
        export_layout = QHBoxLayout()
        export_layout.addWidget(self.folder_csv_output)
        export_layout.addWidget(self.csv_save_as_button)
        export_layout.addWidget(self.csv_convert_button)
        export_layout.addWidget(self.csv_abort_export_button)
        layout.addLayout(export_layout)

        group.setLayout(layout)
        return group
    
    # ======= Start FUNCTIONS FOR create_export_evaluation_group ======= #
    
    def choose_save_folder(self):
        """Opens a directory dialog to select a folder for saving CSV output."""
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.folder_csv_output.setText(folder)
    
    
    def write_to_csv(self):
        """
        Initiates the CSV export process in a separate thread.
        Performs validation checks before starting the export.
        """
        folder_containing_xml_files = self.folder_xml_input.text()
        folder_for_csv_output = self.folder_csv_output.text()

        # Generate a timestamp for the output filename
        today_date = datetime.now()
        formatted_today_date = today_date.strftime("%Y-%m-%d_%H-%M-%S") # ISO-like format
        csv_output_path = os.path.join(folder_for_csv_output, f"Evaluation_Results_{formatted_today_date}.csv")
        list_of_xpath_filters = self.xpath_filters

        # Validation checks
        if not os.path.exists(folder_containing_xml_files) or not os.path.isdir(folder_containing_xml_files):
            QMessageBox.warning(self, "XML Input Folder Error", "XML input folder is not set or does not exist!")
            return
        if not list_of_xpath_filters: # Check if the list is empty
            QMessageBox.warning(self, "No XPath Filters Error", "No XPath filters have been added to the list!")
            return
        if not os.path.exists(folder_for_csv_output) or not os.path.isdir(folder_for_csv_output):
            QMessageBox.warning(self, "CSV Output Folder Error", "CSV output folder is not set or does not exist!")
            return

        try:
            # Initialize and start the CSV export worker thread
            self.csv_export_thread = QThread()
            self.csv_export_worker = CSVExportThread(
                folder_containing_xml_files, list_of_xpath_filters, csv_output_path
            )
            self.csv_export_worker.moveToThread(self.csv_export_thread)

            # Connect signals from worker to main thread slots
            self.csv_export_thread.started.connect(self.csv_export_worker.run)
            self.csv_export_worker.output_set_text.connect(self.program_output.setText)
            self.csv_export_worker.output_append.connect(self.program_output.append)
            self.csv_export_worker.finished.connect(self.csv_export_thread.quit)
            self.csv_export_worker.finished.connect(self.on_csv_export_finished)

            # Connect application-specific signals
            self.csv_export_worker.show_error_message.connect(self.show_error_message)
            self.csv_export_worker.show_info_message.connect(self.show_info_message)
            self.csv_export_worker.progress_updated.connect(self.update_progress)
            
            # Disable UI elements and show abort button during processing
            self.set_ui_enabled(False) # False to disable buttons
            self.csv_abort_export_button.setHidden(False)

            self.program_output.setText("Starting CSV export...")
            self.csv_export_thread.start() # Start the thread
            
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Error starting CSV export", f"Error exporting CSV: {message}")
            self.set_ui_enabled(True) # Re-enable UI if error occurs during setup


    def stop_csv_export_thread(self):
        """Requests the CSV export thread to stop."""
        if hasattr(self, "csv_export_worker") and self.csv_export_thread.isRunning():
            self.csv_export_worker.stop() # Call the worker's stop method
            self.program_output.setText("Export task abortion requested. Waiting for completion...")
            self.csv_abort_export_button.setDisabled(True) # Disable abort button after request


    def on_csv_export_finished(self):
        """Slot called when the CSV export thread finishes."""
        self.set_ui_enabled(True) # Re-enable UI elements
        self.progressbar.reset() # Reset progress bar
        self.csv_abort_export_button.setHidden(True) # Hide abort button
        self.csv_abort_export_button.setDisabled(False) # Re-enable for next use


    def set_ui_enabled(self, enabled: bool):
        """
        Enables or disables key UI elements during CSV export.
        Args:
            enabled (bool): If True, UI elements are enabled. If False, they are disabled.
        """
        # Invert 'enabled' for setDisabled which means True = disabled
        disabled_state = not enabled 
        
        self.browse_xml_folder_button.setDisabled(disabled_state)
        self.read_xml_button.setDisabled(disabled_state)
        self.build_xpath_button.setDisabled(disabled_state)
        self.add_xpath_to_list_button.setDisabled(disabled_state)
        self.csv_save_as_button.setDisabled(disabled_state)
        self.csv_convert_button.setDisabled(disabled_state)
        
        # Input fields for paths should be read-only while processing
        self.folder_xml_input.setReadOnly(disabled_state)
        self.folder_csv_output.setReadOnly(disabled_state)

        # For CSV conversion tab elements
        self.browse_csv_button.setDisabled(disabled_state)
        self.browse_csv_output_button.setDisabled(disabled_state)
        self.convert_csv_button.setDisabled(disabled_state)
        self.input_csv_file_conversion.setReadOnly(disabled_state)
        self.output_csv_file_conversion.setReadOnly(disabled_state)
        self.checkbox_write_index_column.setDisabled(disabled_state)
    
    
    def show_info_message(self, title: str, message: str):
        """Displays an informational message box."""
        QMessageBox.information(self, title, message) 
    
    
    def show_error_message(self, title: str, message: str):
        """Displays an error message box."""
        QMessageBox.critical(self, title, message) 

                
    def update_progress(self, value: int):
        """Updates the progress bar value."""
        self.progressbar.setValue(value)
        
    # ======= End FUNCTIONS FOR create_export_evaluation_group ======= #

    def create_program_output_group(self):
        """Creates the 'Program Output' group box."""
        group = QGroupBox("PROGRAM OUTPUT")
        layout = QVBoxLayout()

        self.program_output.setReadOnly(True) # Make output area read-only
        layout.addWidget(self.program_output)

        group.setLayout(layout)
        return group


    def create_xml_output_group(self):
        """Creates the 'XML Output' group box with a text editor and progress bar."""
        group = QGroupBox("XML OUTPUT")
        layout = QVBoxLayout()

        # XML content display area
        self.xml_output = QTextEdit() 
        self.xml_output.setReadOnly(True)
        
        # Progress bar for long running tasks
        self.progressbar = QProgressBar()
        self.progressbar.setFormat("%p%") # Display percentage
        
        layout.addWidget(self.xml_output)
        layout.addSpacerItem(QSpacerItem(40,10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progressbar)
        layout.addLayout(progress_layout)

        group.setLayout(layout)
        return group
    
    
    def create_csv_conversion_tab(self):
        """Creates and returns the 'CSV Conversion and Display' tab widget."""
        tab = QWidget()
        layout = QHBoxLayout()

        # Left column for CSV conversion controls and output
        left_column = QVBoxLayout()
        left_column.addWidget(self.create_csv_conversion_group())
        left_column.addWidget(self.create_csv_conversion_output_group())

        # Right column for displaying CSV data in a table
        right_column = QVBoxLayout()
        right_column.addWidget(self.create_csv_to_table_group())

        layout.addLayout(left_column, 1)
        layout.addLayout(right_column, 1)
        tab.setLayout(layout)
        return tab


    def create_csv_conversion_group(self):
        """Creates the 'CSV Conversion' group box."""
        group = QGroupBox("CSV CONVERSION")
        layout = QVBoxLayout()

        # Title and description for the CSV converter
        title_label = QLabel("CSV Converter")
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #FFC857;")
        layout.addWidget(title_label)

        self.desc_label = QLabel("Convert CSV File to a different file type with the Pandas module.\nSupported output file types: Excel, Markdown, HTML and JSON")
        
        # Elements for CSV input file selection
        self.input_csv_file_conversion = QLineEdit()
        self.input_csv_file_conversion.setPlaceholderText("Choose a CSV file for conversion...")
        self.browse_csv_button = QPushButton("BROWSE")
        self.browse_csv_button.clicked.connect(self.browse_csv_file)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_csv_file_conversion)
        input_layout.addWidget(self.browse_csv_button)
        
        layout.addWidget(self.desc_label)
        layout.addSpacerItem(QSpacerItem(40,10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addLayout(input_layout)
        
        # Elements for CSV output file selection and conversion
        self.output_csv_file_conversion = QLineEdit()
        self.output_csv_file_conversion.setPlaceholderText("Choose where to save the converted CSV file...")
        self.browse_csv_output_button = QPushButton("BROWSE")
        self.browse_csv_output_button.clicked.connect(self.csv_save_as_conversion) # Renamed to avoid conflict
        self.convert_csv_button = QPushButton("CONVERT")
        self.convert_csv_button.clicked.connect(self.pandas_convert_csv_file)
        
        # Checkbox for including index column in output
        self.checkbox_write_index_column = QCheckBox("Write Index Column?")
        self.checkbox_write_index_column.setChecked(False)
        self.checkbox_write_index_column.clicked.connect(self.wrinco_checkbox_info)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_csv_file_conversion)
        output_layout.addWidget(self.browse_csv_output_button)

        layout.addLayout(output_layout)
        
        layout.addSpacerItem(QSpacerItem(40,10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(self.convert_csv_button)
        layout.addWidget(self.checkbox_write_index_column)
        
        layout.addStretch()  # This will push everything up and fill the empty space at the bottom

        group.setLayout(layout)
        return group
    
    def create_csv_conversion_output_group(self):
        """Creates the 'CSV Conversion Output' group box."""
        group = QGroupBox("CSV CONVERSION OUTPUT")
        layout = QVBoxLayout()
        
        self.csv_conversion_output = QTextEdit() # Text area for conversion messages
        
        layout.addWidget(self.csv_conversion_output)
        group.setLayout(layout)
        
        return group
    
    # ======= Start FUNCTIONS FOR create_csv_conversion_group ======= #
    
    def wrinco_checkbox_info(self):
        """Displays information about the effect of the 'Write Index Column' checkbox."""
        message_with_index = """
        Data will look like this (with index):
        
        | Index | Header 1 | Header 2 |
        |-------|----------|----------|
        | 0     | Data A   | Data X   |
        | 1     | Data B   | Data Y   |
        """
        message_without_index = """
        Data will look like this (without index):
        
        | Header 1 | Header 2 |
        |----------|----------|
        | Data A   | Data X   |
        | Data B   | Data Y   |
        """
        try:
            if self.checkbox_write_index_column.isChecked():
                self.csv_conversion_output.setText(message_with_index)
            else:
                self.csv_conversion_output.setText(message_without_index)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", f"An error occurred: {message}")
                
    
    def browse_csv_file(self):
        """Opens a file dialog to select a CSV file for conversion."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
            if file_name:
                self.input_csv_file_conversion.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in reading CSV", f"Error reading CSV:\n{message}")

    
    def csv_save_as_conversion(self):
        """Opens a 'Save As' file dialog for the CSV conversion output, allowing
        selection of various output formats (Excel, JSON, HTML, Markdown).
        """
        try:
            options = QFileDialog.Options()
            file_types = (
                "Excel File (*.xlsx);;"
                "JSON File (*.json);;"
                "HTML File (*.html);;"
                "Markdown File (*.md)"
            )
            # Get save file name and selected filter
            file_name, selected_filter = QFileDialog.getSaveFileName(
                self, "Save Converted File As", "", file_types, options=options
            )
            if file_name:
                # Add default extension if not provided by user
                if not Path(file_name).suffix:
                    if "Excel File" in selected_filter:
                        file_name += ".xlsx"
                    elif "JSON File" in selected_filter:
                        file_name += ".json"
                    elif "HTML File" in selected_filter:
                        file_name += ".html"
                    elif "Markdown File" in selected_filter:
                        file_name += ".md"
                self.output_csv_file_conversion.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception saving converted file", f"Error saving file: {message}")
            
            
    @Slot(str)
    def update_output_file(self, file_name: str):
        """Slot to update the CSV conversion output file path (e.g., from menu actions)."""
        if hasattr(self, 'output_csv_file_conversion'):
            self.output_csv_file_conversion.setText(file_name)
            self.output_csv_file_conversion.repaint()  # Force a repaint to update immediately

    
    @Slot(str)
    def update_input_file(self, file_name: str):
        """Slot to update the CSV conversion input file path (e.g., from menu actions)."""
        if hasattr(self, "input_csv_file_conversion"):
            self.input_csv_file_conversion.setText(file_name)
            self.input_csv_file_conversion.repaint() # Force a repaint
            
    
    def pandas_convert_csv_file(self):
        """
        Converts the selected CSV input file to a different format (Excel, JSON, HTML, Markdown)
        using the Pandas library.
        """
        csv_input_file = self.input_csv_file_conversion.text()
        csv_output_file = self.output_csv_file_conversion.text()
        write_index = self.checkbox_write_index_column.isChecked()

        # Validate file paths
        if not csv_input_file or not os.path.exists(csv_input_file):
            QMessageBox.warning(self, "Input File Error", "Please select a valid CSV input file.")
            return
        if not csv_output_file:
            QMessageBox.warning(self, "Output File Error", "Please specify an output file path.")
            return

        try:
            self.csv_conversion_output.setText("Conversion started, please wait...")
            
            # Sniff the delimiter to read the CSV correctly
            with open(csv_input_file, "r", encoding="utf-8") as file:
                # Read a sample to sniff the delimiter
                sample = file.read(4096)
                sniffer = csv.Sniffer()
                get_delimiter = sniffer.sniff(sample).delimiter

            # Read the CSV into a Pandas DataFrame
            # index_col=False prevents pandas from using the first column as index if not explicitly desired
            csv_df = pd.read_csv(csv_input_file, delimiter=get_delimiter, encoding="utf-8", index_col=None)
            
            # Determine output format based on file extension
            output_ext = Path(csv_output_file).suffix.lower().strip(".")
            
            # Dictionary mapping output extensions to Pandas DataFrame methods
            CONVERSION_FUNCTIONS = {
                "xlsx": csv_df.to_excel,
                "json": csv_df.to_json,
                "html": csv_df.to_html,
                "md": csv_df.to_markdown,
            }
            
            write_func = CONVERSION_FUNCTIONS.get(output_ext)
            
            if write_func is None:
                QMessageBox.warning(self, "Unsupported Conversion", f"Unsupported output file type: .{output_ext}. Please select from .xlsx, .json, .html, .md.")
                return
            
            # Call the appropriate Pandas method with or without index
            if output_ext == "xlsx":
                write_func(csv_output_file, index=write_index)
            elif output_ext == "json":
                # For JSON, orient='records' or 'split' is common for human-readability
                # Depending on desired JSON structure, this might need adjustment
                write_func(csv_output_file, orient="records", indent=4) 
            else: # html, md
                write_func(csv_output_file, index=write_index)

            self.csv_conversion_output.setText(
                f"Successfully converted '{Path(csv_input_file).name}' to '{Path(csv_output_file).name}'"
            )
            
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception converting CSV", f"Error converting CSV: {message}")
            
    # ======= End FUNCTIONS FOR create_csv_conversion_group ======= #

    def create_csv_to_table_group(self):
        """Creates the 'Display CSV into Table' group box."""
        group = QGroupBox("DISPLAY CSV INTO TABLE")
        layout = QVBoxLayout()

        # File selection for CSV to display
        file_layout = QHBoxLayout()
        self.csv_file_input = QLineEdit()
        self.csv_file_input.setPlaceholderText("Select CSV file to display...")
        file_button = QPushButton("BROWSE")
        file_button.clicked.connect(self.select_csv_file)
        file_layout.addWidget(self.csv_file_input)
        file_layout.addWidget(file_button)
        layout.addLayout(file_layout)

        # Filter controls for the table view
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter filter text...")
        self.filter_input.textChanged.connect(self.filter_table) # Connect to filter function
        self.filter_column = QComboBox()
        self.filter_column.setMinimumWidth(150)
        self.filter_column.currentIndexChanged.connect(self.filter_table) # Connect to filter function
        filter_layout.addWidget(self.filter_column)
        filter_layout.addWidget(self.filter_input)
        layout.addLayout(filter_layout)

        # Table view to display CSV data
        self.table_view = QTableView()
        self.table_model = QStandardItemModel() # Data model
        self.proxy_model = QSortFilterProxyModel() # Proxy model for sorting and filtering
        self.proxy_model.setSourceModel(self.table_model)
        self.table_view.setModel(self.proxy_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        layout.addWidget(self.table_view)

        # Button to load CSV data into the table
        load_button = QPushButton("LOAD CSV")
        load_button.clicked.connect(self.load_csv_data)
        layout.addWidget(load_button)

        group.setLayout(layout)
        return group

    def select_csv_file(self):
        """Opens a file dialog to select a CSV file for table display."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.csv_file_input.setText(file_name)

    def load_csv_data(self):
        """Loads data from the selected CSV file into the QTableView."""
        file_path = self.csv_file_input.text()
        if not file_path:
            QMessageBox.warning(self, "Error", "Please select a CSV file first.")
            return

        try:
            # Open file and sniff delimiter/header
            with open(file_path, "r", encoding="utf-8") as f:
                sample = f.read(1024) # Read a sample to sniff
                f.seek(0)  # Rewind to the beginning of the file
                sniffer = csv.Sniffer()
                has_header = sniffer.has_header(sample)
                dialect = sniffer.sniff(sample)
                delimiter = dialect.delimiter

                reader = csv.reader(f, delimiter=delimiter)
                
                # Determine headers based on sniffing
                headers = (
                    next(reader) # Read first row as headers if 'has_header' is True
                    if has_header
                    # Otherwise, generate generic column names
                    else [f"Column {i+1}" for i in range(len(next(reader)))] 
                )

                self.table_model.clear() # Clear existing data in model
                self.table_model.setHorizontalHeaderLabels(headers) # Set headers

                # Populate the table model with rows from the CSV
                for row in reader:
                    items = [QStandardItem(field) for field in row]
                    self.table_model.appendRow(items)

            # Populate the filter column combobox with column headers
            self.filter_column.clear()
            self.filter_column.addItems(["All Columns"] + headers)

            QMessageBox.information(self, "Success", "CSV data loaded successfully.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Error", f"Failed to load CSV data:\n{message}")

    def filter_table(self):
        """Filters the QTableView based on text input and selected column."""
        filter_text = self.filter_input.text()
        # -1 because "All Columns" is at index 0 in the combobox
        filter_column = self.filter_column.currentIndex() - 1  

        if filter_column == -1:  # "All Columns" selected
            self.proxy_model.setFilterKeyColumn(-1) # Apply filter to all columns
        else:
            self.proxy_model.setFilterKeyColumn(filter_column) # Apply filter to a specific column

        # Set the filter string for the proxy model (case-insensitive by default)
        self.proxy_model.setFilterFixedString(filter_text)

if __name__ == "__main__": 
    multiprocessing.freeze_support() # Required for multiprocessing on Windows when frozen
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show() # Display the main window
    sys.exit(app.exec()) # Start the application event loop
