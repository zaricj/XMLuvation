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
    def __init__(self):
        self.config_dir = "_internal\\configuration"
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.config = self.load_config()


    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {self.config_file} is empty or contains invalid JSON. Using default configuration.")
        return self.get_default_config()


    def get_default_config(self):
        return {"custom_paths": {}}


    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)


    def add_custom_path(self, name, path):
        self.config["custom_paths"][name] = path
        self.save_config()


    def get_custom_paths(self):
        return self.config["custom_paths"]


    def remove_custom_path(self, name):
        if name in self.config["custom_paths"]:
            del self.config["custom_paths"][name]
            self.save_config()


class XMLParserThread(QObject):
    finished = Signal(dict)
    show_error_message = Signal(str, str)

    def __init__(self, parent, xml_file):
        super().__init__()
        self.parent = parent
        self.xml_file = xml_file

    def run(self):
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            xml_string = ET.tostring(root, encoding="unicode", pretty_print=True)

            tags = set()
            tag_values = set()
            attributes = set()
            attribute_values = set()

            for elem in root.iter():
                tags.add(elem.tag)
                if elem.text and elem.text.strip():
                    tag_values.add(elem.text.strip())
                for attr, value in elem.attrib.items():
                    attributes.add(attr)
                    attribute_values.add(value)

            result = {
                'xml_string': xml_string,
                'tags': sorted(tags),
                'tag_values': sorted(tag_values),
                'attributes': sorted(attributes),
                'attribute_values': sorted(attribute_values)
            }
            
        except Exception as ex:
            self.show_error_message.emit("An exception occurred", str(ex))
        finally:
            self.finished.emit(result)

# Standalone processing functions that can be pickled
def process_single_xml(filename: str, folder_path: str, xpath_expressions: List[str]) -> Tuple[List[Dict], int, int]:
    """Process a single XML file and return its results."""
    final_results = []
    file_total_matches = 0
    file_path = os.path.join(folder_path, filename)
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.XMLSyntaxError:
        return [], 0, 0
    except Exception:
        return [], 0, 0

    for expression in xpath_expressions:
        result = root.xpath(expression)
        match_count = len(result)
        file_total_matches += match_count

        pattern_text_or_attribute_end = r'(.*?/text\(\)$|.*?/@[a-zA-Z_][a-zA-Z0-9_]*$)'
        match = re.match(pattern_text_or_attribute_end, expression)
        ends_with_text_or_attribute = bool(match)

        if result:
            if not ends_with_text_or_attribute:
                current_result = {"Filename": os.path.splitext(filename)[0]}
                current_result["Matches"] = match_count
                current_result["Expression"] = expression
                final_results.append(current_result)
            else:
                new_results = process_xpath_result(expression, result, os.path.splitext(filename)[0])
                final_results.extend(new_results)
            

    return final_results, file_total_matches, 1 if file_total_matches > 0 else 0

def process_xpath_result(expression: str, result: list, filename: str) -> List[Dict]:
    """Process xpath results for a single expression."""
    results = []
    
    if "/@" in expression:
        attribute_name = expression.split("@")[-1]
        key = f"Attribute {attribute_name} Value"
        
        # Create separate entry for each result
        for elem in result:
            if elem.strip():
                results.append({
                    "Filename": filename,
                    key: elem.strip()
                })
                
    elif "/text()" in expression:
        tag_name = expression.split("/")[-2]
        key = f"Tag {tag_name} Value"
        
        # Create separate entry for each result
        for elem in result:
            if elem.strip():
                results.append({
                    "Filename": filename,
                    key: elem.strip()
                })
                
    elif "[@" in expression:
        match = re.search(r"@([^=]+)", expression)
        if match:
            attribute_name = match.group(1).strip()
            key = f"Attribute {attribute_name} Value"
            
            # Create separate entry for each result
            for elem in result:
                value = elem.get(attribute_name)
                if value:
                    results.append({
                        "Filename": filename,
                        key: value
                    })
    
    return results

class CSVExportThread(QObject):
    # Signals
    finished = Signal()
    show_info_message = Signal(str, str)
    show_error_message = Signal(str, str)
    progress_updated = Signal(int)
    output_set_text = Signal(str)
    output_append = Signal(str)

    def __init__(self, folder_containing_xml_files, list_of_xpath_filters, csv_output_path):
        super().__init__()
        self.folder_containing_xml_files = folder_containing_xml_files
        self.list_of_xpath_filters = list_of_xpath_filters
        self.csv_output_path = csv_output_path
        self._is_running = True
        
    def stop(self):
        """Method to stop the running task"""
        self._is_running = False

    def run(self):
        try:
            self.search_and_export()
        except Exception as ex:
            self.show_error_message.emit("An exception occurred", str(ex))
        finally:
            self.finished.emit()
        
    def search_and_export(self):
        try:
            matching_results, total_matches_found, total_matching_files = self.evaluate_xml_files_matching(
                self.folder_containing_xml_files, self.list_of_xpath_filters)
            # Check if the thread is supposed to be running
            if not self._is_running:
                return 

        except Exception as ex:
            tb = traceback.extract_tb(ex.__traceback__)
            line_number = tb[-1].lineno
            message = f"An exception of type {type(ex).__name__} occurred on line {line_number}. Arguments: {ex.args!r}"
            self.show_error_message.emit("An exception occurred", message)
            return
            
        try:
            if not matching_results:
                self.show_info_message.emit("No matches found", "No matches found by searching with the added filters.")
                self.output_set_text.emit("")
                return
            
            # Define headers excluding Index
            headers = ["Filename"]
            # Add all other headers excluding Filename
            additional_headers = set()
            for dic in matching_results:
                additional_headers.update(key for key in dic.keys() if key != "Filename")
            headers.extend(sorted(additional_headers))

            with open(self.csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(
                    csvfile, 
                    fieldnames=headers, 
                    delimiter=",", 
                    extrasaction="ignore", 
                    quotechar='"', 
                    quoting=csv.QUOTE_ALL
                )
                writer.writeheader()

                # Group results by filename
                results_by_filename = {}
                for match in matching_results:
                    filename = match["Filename"]
                    if filename not in results_by_filename:
                        results_by_filename[filename] = []
                    results_by_filename[filename].append(match)
        
                # Process each file's results
                for filename, file_matches in results_by_filename.items():
                    # Align values for each filename
                    aligned_rows = {}
                    for match in file_matches:
                        for key, value in match.items():
                            if key != "Filename" and value:  # Ignore Filename and empty values
                                if key not in aligned_rows:
                                    aligned_rows[key] = []
                                aligned_rows[key].append(value)
        
                    # Get the maximum number of aligned rows
                    max_rows = max(len(values) for values in aligned_rows.values())
                    for i in range(max_rows):
                        row = {"Filename": filename}
                        for key, values in aligned_rows.items():
                            if i < len(values):
                                row[key] = values[i]
                        writer.writerow(row)

            # Emit completion signals
            self.show_info_message.emit("Export Successful", "CSV export completed.")
            self.output_set_text.emit(
                f"Found {total_matching_files} files that have a total sum of {total_matches_found} matches."
            )

        except Exception as ex:
            tb = traceback.extract_tb(ex.__traceback__)
            line_number = tb[-1].lineno
            message = f"An exception of type {type(ex).__name__} occurred on line {line_number}. Arguments: {ex.args!r}"
            self.show_error_message.emit("An exception occurred", message)

        finally:
            self.finished.emit()

    def evaluate_xml_files_matching(self, folder_containing_xml_files, list_of_xpath_expressions):
        """Evaluate XML files using multiprocessing."""
        xml_files = [f for f in os.listdir(folder_containing_xml_files) if f.endswith(".xml")]
        total_files = len(xml_files)
        
        if not xml_files:
            return [], 0, 0

        # Calculate the number of processes to use (leave one core free)
        num_processes = max(1, multiprocessing.cpu_count() - 1)
        
        # Initialize multiprocessing variables
        final_results = []
        total_sum_matches = 0
        total_matching_files = 0
        
        try:
            while self._is_running:
                # Create a pool of processes
                with multiprocessing.Pool(processes=num_processes) as pool:
                    # Create partial function with fixed arguments
                    process_func = partial(
                        process_single_xml,
                        folder_path=folder_containing_xml_files,
                        xpath_expressions=list_of_xpath_expressions,
                    )
                    
                    # Process files and collect results
                    for i, (file_results, file_matches, matching_file) in enumerate(
                        pool.imap_unordered(process_func, xml_files)
                    ):
                        if not self._is_running:
                            self.output_set_text.emit("Export task aborted successfully.")
                            pool.terminate()
                            return final_results, total_sum_matches, total_matching_files
                        
                        final_results.extend(file_results)
                        total_sum_matches += file_matches
                        total_matching_files += matching_file
                        
                        # Update progress
                        progress = int((i + 1) / total_files * 100)
                        self.progress_updated.emit(progress)
                        self.output_set_text.emit(f"Processing file {i + 1} of {total_files}")
                    
                    return final_results, total_sum_matches, total_matching_files
                    
        except Exception as ex:
            self.show_error_message.emit(
                "Multiprocessing Error",
                f"Error during multiprocessing: {str(ex)}"
            )
            return [], 0, 0

class MainWindow(QMainWindow):
    progress_updated = Signal(int)
    update_input_file_signal = Signal(str)
    update_output_file_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.current_theme =  "_internal\\theme\\dark_theme.qss" # Sets the global main theme from the file
        self.config_handler = ConfigHandler()
        self.eval_input_file = None
        self.xpath_filters = []
        self.xpath_listbox = QListWidget(self)
        self.program_output = QTextEdit()
        self.csv_export_thread = None
        self.csv_export_worker = None
        self.parse_xml_thread = None
        self.parse_xml_worker = None
        self.setWindowTitle("XMLuvation v1.3.1")
        self.setWindowIcon(QIcon("_internal\\icon\\xml_256px.ico"))  # Replace with actual path
        self.setGeometry(500, 250, 1300, 840)
        self.saveGeometry()
        
        # Signals and Slots
        self.progress_updated.connect(self.update_progress)
        self.update_input_file_signal.connect(self.update_input_file)
        self.update_output_file_signal.connect(self.update_output_file)
        
        # Connect the custom context menu for Listbox
        self.xpath_listbox.setContextMenuPolicy(Qt.CustomContextMenu)
        self.xpath_listbox.customContextMenuRequested.connect(self.show_context_menu)
        
        # Theme stuff
        self.light_mode = QIcon("_internal\\images\\light.png")
        self.dark_mode = QIcon("_internal\\images\\dark.png")
        
        self.initUI()
        
        # Create the menu bar
        self.create_menu_bar()
        
        try:
            with open("_internal\\theme\\theme_config.txt", "r") as f:
                    self.initialize_theme(f.read())
                    if f.read() == "_internal\\theme\\light_theme.qss":
                        self.toggle_theme_action.setIcon(self.dark_mode)
                    else:
                        self.toggle_theme_action.setIcon(self.light_mode)
        except FileNotFoundError:
            self.initialize_theme(self.current_theme)
        
    def initUI(self):
        # Create the main layout
        main_layout = QVBoxLayout()

        # Create the tab widget
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_xml_evaluation_tab(), "XML Evaluation")
        tab_widget.addTab(self.create_csv_conversion_tab(), "CSV Conversion and Display")

        main_layout.addWidget(tab_widget)

        # Create a central widget to hold the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    
    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self, 'Exit Program', 'Are you sure you want to exit the program?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
            with open("_internal\\theme\\theme_config.txt", "w") as f:
                f.write(self.current_theme)
        else:
            event.ignore()
    

    def initialize_theme(self, theme_file):
        try:
            file = QFile(theme_file)
            if file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.setStyleSheet(stylesheet)
            file.close()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Theme load error", message)
    
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        clear_action = QAction("Clear Output", self)
        clear_action.setStatusTip("Clear the output")
        clear_action.triggered.connect(self.clear_output)
        file_menu.addAction(clear_action)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Open Menu
        open_menu = menu_bar.addMenu("&Open")
        open_input_action = QAction("Open XML Input Folder", self)
        open_input_action.setStatusTip("Open the XML input folder")
        open_input_action.triggered.connect(self.open_input_folder)
        open_menu.addAction(open_input_action)
        open_output_action = QAction("Open CSV Output Folder", self)
        open_output_action.setStatusTip("Open the CSV output folder")
        open_output_action.triggered.connect(self.open_output_folder)
        open_menu.addAction(open_output_action)
        open_menu.addSeparator()
        open_csv_conversion_input_action = QAction("Open CSV Conversion Input Folder", self)
        open_csv_conversion_input_action.setStatusTip("Open CSV Conversion Input Folder")
        open_csv_conversion_input_action.triggered.connect(self.open_conversion_input)
        open_menu.addAction(open_csv_conversion_input_action)
        open_csv_conversion_output_action = QAction("Open CSV Conversion Output Folder", self)
        open_csv_conversion_output_action.setStatusTip("Open CSV Conversion Output Folder")
        open_csv_conversion_output_action.triggered.connect(self.open_conversion_output)
        open_menu.addAction(open_csv_conversion_output_action)

        # Path Menu
        self.paths_menu = menu_bar.addMenu("&Path")
        
        # Add custom paths
        self.load_custom_paths()

        # Add option to add new custom path
        add_custom_path_action = QAction("Add Custom Path", self)
        add_custom_path_action.triggered.connect(self.add_custom_path)
        self.paths_menu.addAction(add_custom_path_action)

        
        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        xpath_help_action = QAction("XPath Help", self)
        xpath_help_action.setStatusTip("Open XPath Syntax Help")
        xpath_help_action.triggered.connect(self.open_web_xpath_help)
        help_menu.addAction(xpath_help_action)
        about = QAction("About", self)
        about.setStatusTip("About this program")
        about.triggered.connect(self.about_message)
        help_menu.addAction(about)
        #help_menu.addAction(xpath_cheatsheet_action)
        
        # Theme Menu
        self.toggle_theme_action = menu_bar.addAction(self.light_mode, "Toggle Theme")
        self.toggle_theme_action.triggered.connect(self.change_theme)
        
    # ======= START FUNCTIONS create_menu_bar ======= #
    
    def update_paths_menu(self):
        # Clear existing path actions, except the last one (Add Custom Path)
        for action in self.paths_menu.actions()[:-1]:
            self.paths_menu.removeAction(action)

        # Add custom paths
        custom_paths = self.config_handler.get_custom_paths()
        for name, path in custom_paths.items():
            action = QAction(name, self)
            action.setStatusTip(f"Open {name}")
            action.triggered.connect(lambda checked, p=path: self.open_path(p))
            self.paths_menu.insertAction(self.paths_menu.actions()[0], action)
            

    def add_custom_path(self):
        name, ok = QInputDialog.getText(self, "Add Custom Path", "Enter a name for the path:")
        if ok and name:
            path, ok = QInputDialog.getText(self, "Add Custom Path", "Enter path:")
            if ok and path:
                self.config_handler.add_custom_path(name, path)
                self.update_paths_menu()
                
    
    def load_custom_paths(self):
        custom_paths = self.config_handler.get_custom_paths()
        for name, path in custom_paths.items():
            action = QAction(name, self)
            action.setStatusTip(f"Open {name}")
            action.triggered.connect(lambda checked, p=path: self.open_path(p))
            self.paths_menu.addAction(action)
            
    
    def about_message(self):
        # About Message
        program_info = "Name: XMLuvation\nVersion: 1.3.1\nCredit: Jovan\nFramework: PySide6"
        about_message = """XMLuvation is a Python application designed to parse and evaluate XML files and use XPath to search for matches which matching results will be saved in a csv file. Radio buttons are disabled for now, this feature will be implemented in a later version."""
        about_box = QMessageBox()
        about_box.setText("About this program...")
        about_box.setInformativeText(about_message)
        about_box.setDetailedText(program_info)
        about_box.exec()

    
    def change_theme(self):
        if self.current_theme == "_internal\\theme\\dark_theme.qss":
            self.current_theme = "_internal\\theme\\light_theme.qss"
            self.toggle_theme_action.setIcon(self.dark_mode)
        else:
            self.current_theme = "_internal\\theme\\dark_theme.qss"
            self.toggle_theme_action.setIcon(self.light_mode)
        self.initialize_theme(self.current_theme)
    
    def clear_output(self):
        self.program_output.clear()
        self.csv_conversion_output.clear()
    
    # Open XML input folder function
    def open_input_folder(self):
        directory_path = self.folder_xml_input.text()
        
        if os.path.exists(directory_path):
            try:
                os.startfile(directory_path)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "An exception occurred", message)
        else:
            QMessageBox.warning(self, "Error", f"Path does not exist or is not a valid path:\n{directory_path}")
    
    
    # Open CSV output folder function
    def open_output_folder(self):
        directory_path = self.folder_csv_output.text()
        
        if os.path.exists(directory_path):
            try:
                os.startfile(directory_path)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "An exception occurred", message)
        else:
            QMessageBox.warning(self, "Error", f"Path does not exist or is not a valid path:\n{directory_path}")
    
    
    def open_conversion_input(self):
        directory_path = self.input_csv_file_conversion.text()
        dirname = os.path.dirname(directory_path)
        if os.path.exists(directory_path):
            try:
                os.startfile(dirname)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "An exception occurred", message)
        else:
            QMessageBox.warning(self, "Error", f"Path does not exist or is not a valid path:\n{directory_path}")
            
            
    def open_conversion_output(self):
        directory_path = self.output_csv_file_conversion.text()
        
        if os.path.exists(directory_path):
            try:
                os.startfile(directory_path)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "An exception occurred", message)
        else:
            QMessageBox.warning(self, "Error", f"Path does not exist or is not a valid path:\n{directory_path}")
            
            
    def open_path(self,path):
        self.folder_xml_input.setText(path)
    
    
    def open_web_xpath_help(self):
        webbrowser.open("https://www.w3schools.com/xml/xpath_syntax.asp")
        
    # ======= END FUNCTIONS create_menu_bar ======= #
    
    def create_xml_evaluation_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()

        # Left column
        left_column = QVBoxLayout()
        left_column.addWidget(self.create_xml_eval_group())
        left_column.addWidget(self.create_matching_filter_group())
        left_column.addWidget(self.create_export_evaluation_group())
        left_column.addWidget(self.create_program_output_group())

        # Right column
        right_column = QVBoxLayout()
        right_column.addWidget(self.create_xml_output_group())

        layout.addLayout(left_column, 1)
        layout.addLayout(right_column, 1)
        tab.setLayout(layout)
        return tab


    def create_xml_eval_group(self):
        group = QGroupBox("XML FOLDER SELECTION AND XPATH BUILDER")
        layout = QVBoxLayout()
        
        
        xml_input_folder_and_statusbar_layout = QHBoxLayout()
        
        # Elements
        self.total_xml_files_statusbar = QStatusBar()
        self.setStatusBar(self.total_xml_files_statusbar)
        self.total_xml_files_statusbar.setSizeGripEnabled(False)
        self.total_xml_files_statusbar.setStyleSheet("font-size: 20;font-weight: bold; color: #0cd36c")
        
        xml_input_folder_and_statusbar_layout.addWidget(self.total_xml_files_statusbar)
        
        layout.addLayout(xml_input_folder_and_statusbar_layout)
        
        # Elements
        self.folder_xml_input = QLineEdit()
        self.folder_xml_input.setPlaceholderText("Choose a folder that contains XML files...")
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

        tag_layout = QHBoxLayout()
        
        # Elements
        self.tag_name_label = QLabel("Tag name:")
        self.tag_name_combobox = QComboBox()
        self.tag_name_combobox.setEditable(True)
        self.tag_name_combobox.currentTextChanged.connect(self.on_tag_name_changed)
        self.tag_value_label = QLabel("Tag value:")
        self.tag_value_combobox = QComboBox()
        self.tag_value_combobox.setEditable(True)
        
        # Set expanding size policy for comboboxes
        self.tag_name_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.tag_value_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        tag_layout.addWidget(self.tag_name_label)
        tag_layout.addWidget(self.tag_name_combobox)
        tag_layout.addWidget(self.tag_value_label)
        tag_layout.addWidget(self.tag_value_combobox)
        layout.addLayout(tag_layout)

        att_layout = QHBoxLayout()
        
        # Elements
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
        
        # Set expanding size policy for comboboxes
        self.attribute_name_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.attribute_value_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        function_layout = QHBoxLayout()
    
        # Elements
        self.radio_button_equals = QRadioButton("Equals")
        self.radio_button_equals.setChecked(True)
        # self.radio_button_equals.setChecked(True)
        self.radio_button_contains = QRadioButton("Contains")
        # self.radio_button_contains.setDisabled(True)
        self.radio_button_startswith = QRadioButton("Starts-with")
        # self.radio_button_startswith.setDisabled(True)
        self.radio_button_greater = QRadioButton("Greater")
        # self.radio_button_greater.setDisabled(True)
        self.radio_button_smaller = QRadioButton("Smaller")
        # self.radio_button_smaller.setDisabled(True)
        
        function_layout.addWidget(QLabel("Function:"))
        function_layout.addWidget(self.radio_button_equals)
        function_layout.addWidget(self.radio_button_contains)
        function_layout.addWidget(self.radio_button_startswith)
        function_layout.addWidget(self.radio_button_greater)
        function_layout.addWidget(self.radio_button_smaller)
        layout.addLayout(function_layout)
        
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

    def on_tag_name_changed(self, selected_tag):
        if not selected_tag:
            return []
        try:
            attributes = self.get_attributes(self.eval_input_file, selected_tag)
            self.attribute_name_combobox.clear()
            self.attribute_name_combobox.addItems(attributes)

            values_xml = self.get_tag_values(self.eval_input_file, selected_tag)
            self.tag_value_combobox.clear()
            self.tag_value_combobox.addItems(values_xml)

            # Disable tag value combo box if there are no values for the selected tag
            if not values_xml or all(value.strip() == "" for value in values_xml if value is not None):
                self.tag_value_combobox.setDisabled(True)
                self.tag_value_combobox.clear()
            else:
                self.tag_value_combobox.setDisabled(False)

            # Disable attribute name and value combo boxes if there are no attributes for the selected tag
            if not attributes:
                self.attribute_name_combobox.setDisabled(True)
                self.attribute_name_combobox.clear()
                self.attribute_value_combobox.setDisabled(True)
                self.attribute_value_combobox.clear()
            else:
                self.attribute_name_combobox.setDisabled(False)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred", message)


    def on_attribute_name_changed(self, selected_attribute):
        try:
            selected_tag = self.tag_name_combobox.currentText()
            attribute_values = self.get_attribute_values(self.eval_input_file, selected_tag, selected_attribute)
            self.attribute_value_combobox.clear()
            self.attribute_value_combobox.addItems(attribute_values)

            # Disable attribute value combo box if there are no attribute values
            if not attribute_values:
                self.attribute_value_combobox.setDisabled(True)
                self.attribute_value_combobox.clear()
            else:
                self.attribute_value_combobox.setDisabled(False)

            # Disable tag value combo box if the selected tag has no values
            values_xml = self.get_tag_values(self.eval_input_file, selected_tag)
            
            if not values_xml:
                self.tag_value_combobox.setDisabled(True)
                self.tag_value_combobox.clear()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self,"Exception in Program", message)


    def get_attributes(self, eval_input_file, selected_tag):
        if not eval_input_file or not selected_tag:
            return []
        try:
            root = ET.parse(eval_input_file).getroot()
            attributes = set()
            for elem in root.iter(selected_tag):
                attributes.update(elem.attrib.keys())
            return sorted(attributes)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self,"Error getting attributes", message)
            return []


    def get_tag_values(self, eval_input_file, selected_tag):
        if not eval_input_file or not selected_tag:
            return []
        try:
            root = ET.parse(eval_input_file).getroot()
            values = set()
            for elem in root.iter(selected_tag):
                if elem.text and elem.text.strip():
                    values.add(elem.text.strip())
            return sorted(values)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self,"Error getting tag values", message)
            return []


    def get_attribute_values(self, eval_input_file, selected_tag, selected_attribute):
        if not eval_input_file or not selected_tag or not selected_attribute:
            return []
        try:
            root = ET.parse(eval_input_file).getroot()
            values = set()
            for elem in root.iter(selected_tag):
                if selected_attribute in elem.attrib:
                    values.add(elem.attrib[selected_attribute])
            return sorted(values)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Error getting attribute values", message)
            return []


    def parse_xml(self, xml_file):
        try:
            self.parse_xml_thread = QThread()
            self.parse_xml_worker = XMLParserThread(None, xml_file)
            self.parse_xml_worker.moveToThread(self.parse_xml_thread)
            
            # Connect signals and slots
            self.parse_xml_worker.finished.connect(self.on_xml_parsed)
            self.parse_xml_worker.finished.connect(self.parse_xml_thread.quit)
            self.parse_xml_worker.show_error_message.connect(self.show_error_message)
            self.parse_xml_thread.started.connect(self.parse_xml_worker.run)

            # Start the thread
            self.parse_xml_thread.start()

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", message)


    def on_xml_parsed(self, result: dict):
        self.xml_output.setText(result['xml_string'])

        self.tag_name_combobox.clear()
        self.tag_value_combobox.clear()
        self.attribute_name_combobox.clear()
        self.attribute_value_combobox.clear()

        self.tag_name_combobox.addItems(result['tags'])
        self.tag_value_combobox.addItems(result['tag_values'])
        self.attribute_name_combobox.addItems(result['attributes'])
        self.attribute_value_combobox.addItems(result['attribute_values'])
        
        # Sets the comboboxes to be empty, because on XML Read, for some reason the comboboxes always get filled with a random value
        self.tag_name_combobox.setEditText("") 
        self.tag_value_combobox.setEditText("")
        self.attribute_name_combobox.setEditText("")
        self.attribute_value_combobox.setEditText("")

        self.eval_input_file = self.parse_xml_worker.xml_file
        self.program_output.setText("XML file loaded successfully.")


    def read_xml(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select XML File", "", "XML Files (*.xml)")
            if file_name:
                self.parse_xml(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", message)
            

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_xml_input.setText(folder)
            self.update_xml_file_count(folder)
            
            
    def build_xpath(self):
        try:
            # Get values from comboboxes
            tag_name = self.tag_name_combobox.currentText()
            tag_value = self.tag_value_combobox.currentText()
            attribute_name = self.attribute_name_combobox.currentText()
            attribute_value = self.attribute_value_combobox.currentText()

            # Initialize XPath expression
            xpath_expression = ""

            if tag_name:
                xpath_expression = f"//{tag_name}"

                if tag_value and not attribute_name:
                    # Case: Tag Name and Tag Value
                    xpath_expression += f"[text()='{tag_value}']"
                elif tag_name and attribute_name and not attribute_value:
                    # Case: Tag Name and Attribute Name without Attribute Value
                    xpath_expression += f"[@{attribute_name}]/@{attribute_name}"
                elif attribute_name and not tag_value and not attribute_value:
                    # Case: Tag Name and Attribute Name
                    xpath_expression += f"/@{attribute_name}"
                elif attribute_name and attribute_value:
                    # Case: Tag Name, Attribute Name, and Attribute Value
                    xpath_expression += f"[@{attribute_name}='{attribute_value}']"
                elif not tag_value and not attribute_name:
                    # Case: Only Tag Name
                    xpath_expression += "/text()"

                #  Criteria based on radio buttons
                if tag_value or attribute_value:
                    criteria = []
                    selected_operation = self.get_selected_operation()

                    if tag_value:
                        criteria.append(self.build_tag_criterion(selected_operation, tag_value))
                    if attribute_name and attribute_value:
                        criteria.append(self.build_attribute_criterion(selected_operation, attribute_name, attribute_value))

                    if criteria:
                        xpath_expression = f"//{tag_name}[{' and '.join(criteria)}]"

            # Update XPath expression input
            self.xpath_expression_input.setText(xpath_expression)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error building XPath: {message}")


    def get_selected_operation(self):
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


    def build_tag_criterion(self, operation, value):
        if operation == "equals":
            return f"text()='{value}'"
        elif operation == "contains":
            return f"contains(text(), '{value}')"
        elif operation == "startswith":
            return f"starts-with(text(), '{value}')"
        elif operation == "greater":
            return f"text() > {value}"
        elif operation == "smaller":
            return f"text() < {value}"


    def build_attribute_criterion(self, operation, name, value):
        if operation == "equals":
            return f"@{name}='{value}'"
        elif operation == "contains":
            return f"contains(@{name}, '{value}')"
        elif operation == "startswith":
            return f"starts-with(@{name}, '{value}')"
        elif operation == "greater":
            return f"@{name} > {value}"
        elif operation == "smaller":
            return f"@{name} < {value}"

    # ======= END FUNCTIONS FOR create_xml_eval_group ======= #
    
    def create_matching_filter_group(self):
        group = QGroupBox("LIST OF XPATH FILTERS TO SEARCH AND MATCH IN XML FILE(S)")
        
        layout = QVBoxLayout()
        
        spacer = QFrame()
        spacer.setFrameShape(QFrame.HLine)
        spacer.setFrameShadow(QFrame.Sunken)
        
        # Elements
        self.xpath_listbox.setMinimumHeight(100)
        self.statusbar_xpath_listbox_count = QStatusBar()
        self.statusbar_xpath_listbox_count.setSizeGripEnabled(False)
        self.statusbar_xpath_listbox_count.setStyleSheet("font-weight: bold; color: #ffd740")

        layout.addWidget(self.xpath_listbox)
        layout.addWidget(self.statusbar_xpath_listbox_count)

        group.setLayout(layout)
        return group
    
    # ======= Start FUNCTIONS FOR create_matching_filter_group ======= #
    
    def update_statusbar_xpath_listbox_count(self):
        self.counter = self.xpath_listbox.count()
        if self.counter != 0:
            self.statusbar_xpath_listbox_count.showMessage(f"Total number of items in List: {self.counter}", 5000)
        
    
    def remove_selected_items(self):
        try:
            current_selected_item = self.xpath_listbox.currentRow()
            if current_selected_item != -1:
                item_to_remove = self.xpath_listbox.takeItem(current_selected_item)
                self.xpath_filters.pop(current_selected_item)
                self.update_xml_file_count(self.folder_xml_input.text())
                self.program_output.append(f"Removed item: {item_to_remove.text()} at row {current_selected_item}")
            else:
                self.program_output.append("No item selected to delete.")
        
        except IndexError:
            self.program_output.append("Nothing to delete.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error removing selected item from list: {message}")


    def remove_all_items(self):
        try:
            if self.xpath_listbox.count() > 0:
                self.xpath_filters.clear()
                self.xpath_listbox.clear()
                self.program_output.setText("Deleted all items from the list.")
            else:
                self.program_output.setText("No items to delete.")
                
            self.update_xml_file_count(self.folder_xml_input.text())
            
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error removing selected all items from list: {message}")
            
    # Statusbar update function
    def update_xml_file_count(self, folder):
        try:
            if Path(folder).is_dir():
                xml_files = list(Path(folder).glob('*.xml'))
                file_count = len(xml_files)
                self.total_xml_files_statusbar.showMessage(f"Found {file_count} XML Files")
            else:
                pass
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.total_xml_files_statusbar.setStyleSheet("color: #ed2828")
            self.total_xml_files_statusbar.showMessage(f"Error counting XML files: {message}")


    def show_context_menu(self, position):
        context_menu = QMenu(self)
        delete_action = QAction("Delete Selected", self)
        delete_all_action = QAction("Delete All", self)

        context_menu.addAction(delete_action)
        context_menu.addAction(delete_all_action)

        delete_action.triggered.connect(self.remove_selected_items)
        delete_all_action.triggered.connect(self.remove_all_items)

        # Show the context menu at the cursor's current position
        context_menu.exec(self.xpath_listbox.mapToGlobal(position))
    
    
    def is_duplicate(self, xpath_expression):
        return xpath_expression in self.xpath_filters
    
    
    def validate_xpath_expression(self, xpath_expression):
        # Define valid patterns
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
        r"^//[\w]+\[number\(@[\w]+\) > [0-9]+\]$",  # //xml_element[number(@attribute) > 10]
        r"^//[\w]+\[number\(@[\w]+\) < [0-9]+\]$",  # //xml_element[number(@attribute) < 10]
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
    ]

        # Check if expression matches any pattern
        return any(re.match(pattern, xpath_expression) for pattern in valid_patterns)

    
    def add_xpath_expression_to_listbox(self):
        xpath_expression = self.xpath_expression_input.text()
        try:
            if not xpath_expression:
                self.program_output.setText("No Xpath expression entered.")
            elif xpath_expression and not self.is_duplicate(xpath_expression):
                #validate = self.validate_xpath_expression(xpath_expression) #TODO Re-enable validating
                #if validate:
                self.xpath_filters.append(xpath_expression)
                self.xpath_listbox.addItem(xpath_expression)
                #else:
                #    self.program_output.setText("Not a valid Xpath expression!")
                #    QMessageBox.warning(self, "Exception adding filter", f"The entered Xpath expression '{xpath_expression}' is not valid, please try again.")
            else:
                QMessageBox.warning(self, "Error adding filter", f"Cannot add duplicate XPath expression:\n{xpath_expression}")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error adding filter: {message}")
            QMessageBox.critical(self, "Exception adding filter", message)

    # ======= End FUNCTIONS FOR create_matching_filter_group ======= #

    def create_export_evaluation_group(self):
        group = QGroupBox("EXPORT SEARCH RESULT TO A CSV FILE")
        
        layout = QVBoxLayout()
        
        # Elements
        self.folder_csv_output = QLineEdit()
        self.folder_csv_output.setPlaceholderText("Choose a folder where to save the CSV evaluation...")
        self.csv_save_as_button = QPushButton("BROWSE")
        self.csv_save_as_button.clicked.connect(self.choose_save_folder)
        self.csv_convert_button = QPushButton("EXPORT")
        self.csv_convert_button.setToolTip("Starts processing each XML file and writes the found matches to a CSV file.")
        self.csv_convert_button.clicked.connect(self.write_to_csv)
        self.csv_abort_export_button = QPushButton("ABORT")
        self.csv_abort_export_button.setHidden(True)
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
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.folder_csv_output.setText(folder)
    
    
    def write_to_csv(self):
        folder_containing_xml_files = self.folder_xml_input.text()
        folder_for_csv_output = self.folder_csv_output.text()

        # Date and Time
        today_date = datetime.now()
        formatted_today_date = today_date.strftime("%d.%m.%y-%H-%M-%S")

        csv_output_path = os.path.join(self.folder_csv_output.text(), f"Evaluation_Results_{formatted_today_date}.csv")
        list_of_xpath_filters = self.xpath_filters

        if not os.path.exists(folder_containing_xml_files):
            QMessageBox.warning(self, "XML input path error", "Cannot start evaluation because XML input folder is not set!")
        elif len(list_of_xpath_filters) == 0:
            QMessageBox.warning(self, "No Xpath filters error", "Cannot start evaluation because no XPath filters have been added to the list!")
        elif not os.path.exists(folder_for_csv_output):
            QMessageBox.warning(self, "CSV output path error", "Cannot start evaluation because CSV output folder is not set!")
        else:
            try:
                # Store references to thread and worker
                self.csv_export_thread = QThread()
                self.csv_export_worker = CSVExportThread(folder_containing_xml_files, list_of_xpath_filters, csv_output_path)
                self.csv_export_worker.moveToThread(self.csv_export_thread)

                # Connect signals
                self.csv_export_thread.started.connect(self.csv_export_worker.run)
                self.csv_export_worker.output_set_text.connect(self.program_output.setText)
                self.csv_export_worker.output_append.connect(self.program_output.append)
                self.csv_export_worker.finished.connect(self.csv_export_thread.quit)
                self.csv_export_worker.finished.connect(self.on_csv_export_finished)

                # Connect application signals
                self.csv_export_worker.show_error_message.connect(self.show_error_message)
                self.csv_export_worker.show_info_message.connect(self.show_info_message)
                self.csv_export_worker.progress_updated.connect(self.update_progress)
                
                # Disable UI elements during processing
                self.set_ui_enabled(True)
                self.csv_abort_export_button.setHidden(False)

                # Start the thread
                self.csv_export_thread.start()
                
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "Exception in Program", f"Error exporting CSV: {message}")
                self.csv_convert_button.setDisabled(False)


    def stop_csv_export_thread(self):
        if hasattr(self, "csv_export_worker"):
            self.csv_export_worker.stop()
            self.program_output.setText("Export task aborted successfully.")
    
    
    def on_csv_export_finished(self):
        self.set_ui_enabled(False)
        self.progressbar.reset()
        self.csv_abort_export_button.setHidden(True)

        
    def set_ui_enabled(self, enabled):
        # Disable buttons while exporting
        self.browse_xml_folder_button.setDisabled(enabled)
        self.browse_csv_button.setDisabled(enabled)
        self.read_xml_button.setDisabled(enabled)
        self.build_xpath_button.setDisabled(enabled)
        self.add_xpath_to_list_button.setDisabled(enabled)
        self.csv_save_as_button.setDisabled(enabled)
        self.csv_convert_button.setDisabled(enabled)
        self.folder_xml_input.setReadOnly(enabled)
        self.folder_csv_output.setReadOnly(enabled)
    
    
    def show_info_message(self, title, message):
        QMessageBox.information(self, title, message) 
    
    
    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message) 

                
    def update_progress(self, value):
        self.progressbar.setValue(value)
        
    # ======= End FUNCTIONS FOR create_export_evaluation_group ======= #

    def create_program_output_group(self):
        group = QGroupBox("PROGRAM OUTPUT")
        
        layout = QVBoxLayout()

        self.program_output.setReadOnly(True)
        
        layout.addWidget(self.program_output)

        group.setLayout(layout)
        return group


    def create_xml_output_group(self):
        group = QGroupBox("XML OUTPUT")
        
        layout = QVBoxLayout()

        # Elements
        self.xml_output = QTextEdit() # XML Output
        self.xml_output.setReadOnly(True)
        self.progressbar = QProgressBar()
        self.progressbar.setFormat("%p%")  
        
        layout.addWidget(self.xml_output)
        layout.addSpacerItem(QSpacerItem(40,10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progressbar)
        layout.addLayout(progress_layout)

        group.setLayout(layout)
        return group
    
    
    def create_csv_conversion_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()

        # Left column
        left_column = QVBoxLayout()
        left_column.addWidget(self.create_csv_conversion_group())
        left_column.addWidget(self.create_csv_conversion_output_group())

        # Right column
        right_column = QVBoxLayout()
        right_column.addWidget(self.create_csv_to_table_group())

        layout.addLayout(left_column, 1)
        layout.addLayout(right_column, 1)
        tab.setLayout(layout)
        return tab


    def create_csv_conversion_group(self):
        group = QGroupBox("CSV CONVERSION")
        
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("CSV Converter")
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #FFC857;")
        layout.addWidget(title_label)

        # Description
        self.desc_label = QLabel("Convert CSV File to a different file type with the Pandas module.\nSupported output file types: Excel, Markdown, HTML and JSON")
        
        # Elements
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
        
        # Elements
        self.output_csv_file_conversion = QLineEdit()
        self.output_csv_file_conversion.setPlaceholderText("Choose where to save the converted CSV file...")
        self.browse_csv_output_button = QPushButton("BROWSE")
        self.browse_csv_output_button.clicked.connect(self.csv_save_as)
        self.convert_csv_button = QPushButton("CONVERT")
        self.convert_csv_button.clicked.connect(self.pandas_convert_csv_file)
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
        group = QGroupBox("CSV CONVERSION OUTPUT")
        layout = QVBoxLayout()
        
        # Elements
        self.csv_conversion_output = QTextEdit()
        
        layout.addWidget(self.csv_conversion_output)
        group.setLayout(layout)
        
        return group
    
    # ======= Start FUNCTIONS FOR create_csv_conversion_group ======= #
    
    def wrinco_checkbox_info(self):
        message_with_index = """
        Data will look like  this:
        
        | Index           | Header 1   | Header 2    |
        |-------------------|-------------------|-------------------|
        | 1                  | Data...         | Data...        |
        """
        message_without_index = """
        Data will look like  this:
        
        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Data...         |
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
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
            if file_name:
                self.input_csv_file_conversion.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in reading CSV", f"Error reading CSV:\n{message}")

    
    def csv_save_as(self):
        try:
            options = QFileDialog.Options()
            file_types = "Excel File (*.xlsx);;JSON File (*.json);;HTML File (*.html);;Markdown File (*.md)"
            file_name, _ = QFileDialog.getSaveFileName(self, "Save As", "", file_types, options=options)
            if file_name:
                self.output_csv_file_conversion.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception exporting CSV", f"Error exporting CSV: {message}")
            
            
    @Slot(str)
    def update_output_file(self, file_name):
        if hasattr(self, 'output_csv_file_conversion'):
            self.output_csv_file_conversion.setText(file_name)
            self.output_csv_file_conversion.repaint()  # Force a repaint

    
    @Slot(str)
    def update_input_file(self,file_name):
        if hasattr(self, "input_csv_file_conversion"):
            self.input_csv_file_conversion.setText(file_name)
            self.input_csv_file_conversion.repaint() # Force a repaint
            
    
    def pandas_convert_csv_file(self):
        csv_input_file = self.input_csv_file_conversion.text()
        csv_output_file = self.output_csv_file_conversion.text()
        checkbox = self.checkbox_write_index_column.isChecked()
        try:
            self.csv_conversion_output.setText("Conversion started, please wait...")
            with open(csv_input_file, encoding="utf-8") as file:
                sample = file.read(4096)
                sniffer = csv.Sniffer()
                get_delimiter = sniffer.sniff(sample).delimiter
            if not checkbox:
                csv_df = pd.read_csv(csv_input_file, delimiter=get_delimiter, encoding="utf-8", index_col=0)
            else:
                csv_df = pd.read_csv(csv_input_file, delimiter=get_delimiter, encoding="utf-8")
                
            CONVERSION_FUNCTIONS = {
                # CSV Conversion
                ("csv", "html"): (csv_df, pd.DataFrame.to_html),
                ("csv", "json"): (csv_df, pd.DataFrame.to_json),
                ("csv", "xlsx"): (csv_df, pd.DataFrame.to_excel),
                ("csv", "md"): (csv_df, pd.DataFrame.to_markdown),
            }
            
            input_ext = Path(csv_input_file).suffix.lower().strip(".")
            output_ext = Path(csv_output_file).suffix.lower().strip(".")
            
            read_func, write_func = CONVERSION_FUNCTIONS.get(
            (input_ext, output_ext), (None, None))
            
            if read_func is None or write_func is None:
                QMessageBox.warning(self, "Unsupported Conversion", "Error converting file, unsupported conversion...")
                return
            
            csv_df = read_func
            write_func(csv_df, csv_output_file)
            self.csv_conversion_output.setText(f"Successfully converted {Path(csv_input_file).stem} {input_ext.upper()} to {Path(csv_output_file).stem} {output_ext.upper()}")
            
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception exporting CSV", f"Error exporting CSV: {message}")
            
    # ======= End FUNCTIONS FOR create_csv_conversion_group ======= #

    def create_csv_to_table_group(self):
        group = QGroupBox("DISPLAY CSV INTO TABLE")
        
        layout = QVBoxLayout()

        # File selection
        file_layout = QHBoxLayout()
        self.csv_file_input = QLineEdit()
        self.csv_file_input.setPlaceholderText("Select CSV file...")
        file_button = QPushButton("BROWSE")
        file_button.clicked.connect(self.select_csv_file)
        file_layout.addWidget(self.csv_file_input)
        file_layout.addWidget(file_button)
        layout.addLayout(file_layout)

        # Filter controls
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter filter text...")
        self.filter_input.textChanged.connect(self.filter_table)
        self.filter_column = QComboBox()
        self.filter_column.setMinimumWidth(150)
        self.filter_column.currentIndexChanged.connect(self.filter_table)
        filter_layout.addWidget(self.filter_column)
        filter_layout.addWidget(self.filter_input)
        layout.addLayout(filter_layout)

        # Table view
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.table_view.setModel(self.proxy_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_view)

        # Load CSV button
        load_button = QPushButton("LOAD CSV")
        load_button.clicked.connect(self.load_csv_data)
        layout.addWidget(load_button)

        group.setLayout(layout)
        return group

    def select_csv_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.csv_file_input.setText(file_name)

    def load_csv_data(self):
        file_path = self.csv_file_input.text()
        if not file_path:
            QMessageBox.warning(self, "Error", "Please select a CSV file first.")
            return

        try:
            with open(file_path, "r") as f:
                sample = f.read(1024)
                f.seek(0)  # Rewind to the beginning of the file
                sniffer = csv.Sniffer()
                has_header = sniffer.has_header(sample)
                dialect = sniffer.sniff(sample)
                delimiter = dialect.delimiter

                reader = csv.reader(f, delimiter=delimiter)
                headers = (
                    next(reader)
                    if has_header
                    else [f"Column {i}" for i in range(len(next(reader)))]
                )

                self.table_model.clear()
                self.table_model.setHorizontalHeaderLabels(headers)

                for row in reader:
                    items = [QStandardItem(field) for field in row]
                    self.table_model.appendRow(items)

            self.filter_column.clear()
            self.filter_column.addItems(["All Columns"] + headers)

            QMessageBox.information(self, "Success", "CSV data loaded successfully.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Error", f"Failed to load CSV data:\n{message}")

    def filter_table(self):
        filter_text = self.filter_input.text()
        filter_column = self.filter_column.currentIndex() - 1  # -1 because "All Columns" is at index 0

        if filter_column == -1:  # "All Columns" selected
            self.proxy_model.setFilterKeyColumn(-1)
        else:
            self.proxy_model.setFilterKeyColumn(filter_column)

        self.proxy_model.setFilterFixedString(filter_text)

if __name__ == "__main__": 
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
