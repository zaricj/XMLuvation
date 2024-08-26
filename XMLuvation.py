from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QRadioButton,
    QListWidget,
    QTextEdit,
    QProgressBar,
    QStatusBar,
    QCheckBox,
    QMenu,
    QFileDialog,
    QMessageBox,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QTableView,
    QHeaderView,
    QInputDialog,
    QButtonGroup,
)
from PySide6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QCloseEvent
from PySide6.QtCore import Qt, QThread, Signal, Slot, QSortFilterProxyModel
from datetime import datetime
from lxml import etree as ET
from qt_material import apply_stylesheet
import sys
import csv
import os
import re
import webbrowser
import pandas as pd
import json


class ConfigHandler:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(script_dir, "_internal", "configs")
        self.config_file = os.path.join(self.config_dir, "config.json")

        os.makedirs(self.config_dir, exist_ok=True)

        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(
                    f"Warning: {self.config_file} is empty or contains invalid JSON. Using default configuration."
                )
        return self.get_default_config()

    def get_default_config(self):
        return {"custom_paths": {}}

    def save_config(self):
        with open(self.config_file, "w") as f:
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


class XMLParserThread(QThread):
    finished = Signal(object) 
    error = Signal(str)

    def __init__(self, xml_file):
        super().__init__()
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
                "xml_string": xml_string,
                "tags": sorted(tags),
                "tag_values": sorted(tag_values),
                "attributes": sorted(attributes),
                "attribute_values": sorted(attribute_values),
            }
            self.finished.emit(result)
        except Exception as ex:
            self.error.emit(str(ex))


class MainWindow(QMainWindow):
    progress_updated = Signal(int)
    update_input_file_signal = Signal(str)
    update_output_file_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.config_handler = ConfigHandler()
        self.initUI()
        # Theme by qt_material
        self.current_theme = (
            "_internal/theme/dark_amber.xml"  # Sets the global main theme from the file
        )
        apply_stylesheet(self, self.current_theme)

    def initUI(self):
        self.setWindowTitle("XMLuvation v1.2.4")
        self.setWindowIcon(
            QIcon("_internal/icon/xml_32px.ico")
        )  # Replace with actual path
        self.setGeometry(500, 250, 1300, 840)
        self.saveGeometry()

        self.eval_input_file = None
        self.xpath_filters = []
        self.xpath_listbox = QListWidget(self)

        # Signals and Slots
        self.progress_updated.connect(self.update_progress)
        self.update_input_file_signal.connect(self.update_input_file)
        self.update_output_file_signal.connect(self.update_output_file)

        # Connect the custom context menu for Listbox
        self.xpath_listbox.setContextMenuPolicy(Qt.CustomContextMenu)
        self.xpath_listbox.customContextMenuRequested.connect(self.show_context_menu)

        # Create the menu bar
        self.create_menu_bar()

        # Create the main layout
        main_layout = QVBoxLayout()

        # Create the tab widget
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_xml_evaluation_tab(), "XML Evaluation")
        tab_widget.addTab(
            self.create_csv_conversion_tab(), "CSV Conversion and Display"
        )

        main_layout.addWidget(tab_widget)

        # Create a central widget to hold the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self,
            "Exit Program",
            "Are you sure you want to exit the program?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

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
        open_csv_conversion_input_action = QAction(
            "Open CSV Conversion Input Folder", self
        )
        open_csv_conversion_input_action.setStatusTip(
            "Open CSV Conversion Input Folder"
        )
        open_csv_conversion_input_action.triggered.connect(self.open_conversion_input)
        open_menu.addAction(open_csv_conversion_input_action)
        open_csv_conversion_output_action = QAction(
            "Open CSV Conversion Output Folder", self
        )
        open_csv_conversion_output_action.setStatusTip(
            "Open CSV Conversion Output Folder"
        )
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
        # help_menu.addAction(xpath_cheatsheet_action)

        # Theme Menu
        theme_menu = menu_bar.addMenu("&Personalize")
        personalize_action = QAction("Switch Dark/Light Theme", self)
        personalize_action.setStatusTip("Change theme to dark")
        personalize_action.triggered.connect(self.change_theme)
        theme_menu.addAction(personalize_action)

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
        name, ok = QInputDialog.getText(
            self, "Add Custom Path", "Enter a name for the path:"
        )
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
        program_info = "Name: XMluvation\nVersion: 1.2.4\nCredit: Jovan"
        about_message = """XMLuvation is a Python application designed to parse and evaluate XML files and use XPath to search for matches which matching results will be saved in a csv file. Use radio buttons to either write the values or the total found matches accordingly."""
        about_box = QMessageBox()
        about_box.setText("About this program...")
        about_box.setInformativeText(about_message)
        about_box.setDetailedText(program_info)
        about_box.exec()
        # self.program_output.setText(about_message)

    def change_theme(self):
        if self.current_theme == "_internal/theme/dark_amber.xml":
            self.current_theme = "_internal/theme/light_amber.xml"
        else:
            self.current_theme = "_internal/theme/dark_amber.xml"

        apply_stylesheet(self, self.current_theme)

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
                QMessageBox.critical(self, "Error", message)
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Path does not exist or is not a valid path:\n{directory_path}",
            )

    # Open CSV output folder function
    def open_output_folder(self):
        directory_path = self.folder_csv_input.text()

        if os.path.exists(directory_path):
            try:
                os.startfile(directory_path)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "Error", message)
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Path does not exist or is not a valid path:\n{directory_path}",
            )

    def open_conversion_input(self):
        directory_path = self.input_csv_file_conversion.text()
        dirname = os.path.dirname(directory_path)
        if os.path.exists(directory_path):
            try:
                os.startfile(dirname)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "Error", message)
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Path does not exist or is not a valid path:\n{directory_path}",
            )

    def open_conversion_output(self):
        directory_path = self.output_csv_file_conversion.text()

        if os.path.exists(directory_path):
            try:
                os.startfile(directory_path)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "Error", message)
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Path does not exist or is not a valid path:\n{directory_path}",
            )

    def open_path(self, path):
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
        group = QGroupBox("XML folder selection and XPath builder")
        layout = QVBoxLayout()
        self.horizontal_spacer = QSpacerItem(
            40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        xml_input_folder_and_statusbar_layout = QHBoxLayout()

        # Elements
        self.total_xml_files_statusbar = QStatusBar()
        self.setStatusBar(self.total_xml_files_statusbar)
        self.total_xml_files_statusbar.setSizeGripEnabled(False)
        self.total_xml_files_statusbar.setStyleSheet(
            "font-size: 20;font-weight: bold; color: #0cd36c"
        )

        xml_input_folder_and_statusbar_layout.addWidget(self.total_xml_files_statusbar)

        layout.addLayout(xml_input_folder_and_statusbar_layout)

        # Elements
        self.folder_xml_input = QLineEdit()
        self.folder_xml_input.setPlaceholderText(
            "Choose a folder that contains XML files..."
        )
        self.folder_xml_input.textChanged.connect(self.update_xml_file_count)
        self.browse_xml_folder_button = QPushButton("Browse")
        self.browse_xml_folder_button.clicked.connect(self.browse_folder)
        self.read_xml_button = QPushButton("Read XML")
        self.read_xml_button.setToolTip(
            "Parses XML content into the output and fills out the Comboboxes based on the XMLs content."
        )
        self.read_xml_button.clicked.connect(self.read_xml)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_xml_input)
        folder_layout.addWidget(self.browse_xml_folder_button)
        folder_layout.addWidget(self.read_xml_button)
        layout.addLayout(folder_layout)

        layout.addWidget(
            QLabel("Get XML Tag and Attribute Names/Values for XPath generation:")
        )
        layout.addSpacerItem(self.horizontal_spacer)

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
        self.attribute_name_combobox.currentTextChanged.connect(
            self.on_attribute_name_changed
        )
        self.attribute_value_label = QLabel("Attr value:")
        self.attribute_value_combobox = QComboBox()
        self.attribute_value_combobox.setEditable(True)
        
        # Set expanding size policy for comboboxes
        self.attribute_name_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.attribute_value_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


        att_layout.addWidget(self.attribute_name_label)
        att_layout.addWidget(self.attribute_name_combobox)
        att_layout.addWidget(self.attribute_value_label)
        att_layout.addWidget(self.attribute_value_combobox)
        layout.addLayout(att_layout)
        layout.addSpacerItem(self.horizontal_spacer)

        # Layout
        function_layout = QHBoxLayout()

        # Button Group (optional but recommended for grouping radio buttons)
        button_group = QButtonGroup()

        # Radio Buttons
        self.radio_button_writing = QRadioButton("Write Values")
        self.radio_button_writing.setChecked(True)
        self.radio_button_writing.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.radio_button_matching = QRadioButton("Match Values")
        self.radio_button_matching.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add buttons to group
        button_group.addButton(self.radio_button_writing)
        button_group.addButton(self.radio_button_matching)

        # Adding widgets to layout
        function_layout.addWidget(QLabel("Functions:"))
        function_layout.addWidget(self.radio_button_writing)
        function_layout.addWidget(self.radio_button_matching)

        function_layout.addStretch()

        layout.addLayout(function_layout)

        build_xpath_layout = QHBoxLayout()

        self.xpath_expression_input = QLineEdit()
        self.xpath_expression_input.setPlaceholderText(
            "Enter XPath expression or press Build Xpath"
        )
        self.build_xpath_button = QPushButton("Build Xpath")
        self.build_xpath_button.setToolTip(
            "Builds Xpath expression based on the selected Comboboxes for Tag Name/Value and Attribute Name/Value"
        )
        self.build_xpath_button.clicked.connect(self.build_xpath)
        build_xpath_layout.addWidget(self.xpath_expression_input)
        build_xpath_layout.addWidget(self.build_xpath_button)
        layout.addLayout(build_xpath_layout)

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
            if not values_xml or all(
                value.strip() == "" for value in values_xml if value is not None
            ):
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
            QMessageBox.critical(self, "Exception in Program", message)

    def on_attribute_name_changed(self, selected_attribute):
        try:
            selected_tag = self.tag_name_combobox.currentText()
            attribute_values = self.get_attribute_values(
                self.eval_input_file, selected_tag, selected_attribute
            )
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
            QMessageBox.critical(self, "Exception in Program", message)

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
            QMessageBox.critical(self, "Error getting attributes", message)
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
            QMessageBox.critical(self, "Error getting tag values", message)
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
            self.xml_parser_thread = XMLParserThread(xml_file)
            self.xml_parser_thread.finished.connect(self.on_xml_parsed)
            self.xml_parser_thread.error.connect(self.on_xml_parse_error)
            self.xml_parser_thread.start()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", message)

    def on_xml_parsed(self, result):
        self.xml_output.setText(result["xml_string"])

        self.tag_name_combobox.clear()
        self.tag_value_combobox.clear()
        self.attribute_name_combobox.clear()
        self.attribute_value_combobox.clear()

        self.tag_name_combobox.addItems(result["tags"])
        self.tag_value_combobox.addItems(result["tag_values"])
        self.attribute_name_combobox.addItems(result["attributes"])
        self.attribute_value_combobox.addItems(result["attribute_values"])

        # Sets the comboboxes to be empty, because on XML Read, for some reason the comboboxes always get filled with a random value
        self.tag_name_combobox.setEditText("")
        self.tag_value_combobox.setEditText("")
        self.attribute_name_combobox.setEditText("")
        self.attribute_value_combobox.setEditText("")

        self.eval_input_file = self.xml_parser_thread.xml_file
        self.program_output.setText("XML file loaded successfully.")

    def on_xml_parse_error(self, error_message):
        QMessageBox.critical(self, "Error Parsing XML", error_message)

    def read_xml(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Select XML File", "", "XML Files (*.xml)"
            )
            if file_name:
                self.parse_xml(file_name)
                directory_path = os.path.dirname(file_name)
                self.folder_xml_input.setText(directory_path)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", message)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_xml_input.setText(folder)
            self.update_xml_file_count(folder)

    # Statusbar update function
    def update_xml_file_count(self, folder):
        try:
            xml_files = list(Path(folder).glob("*.xml"))
            file_count = len(xml_files)
            self.total_xml_files_statusbar.showMessage(f"Found {file_count} XML Files")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.total_xml_files_statusbar.setStyleSheet("color: #ed2828")
            self.total_xml_files_statusbar.showMessage(
                f"Error counting XML files: {message}"
            )

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
                elif attribute_name and not tag_value:
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
                        criteria.append(
                            self.build_tag_criterion(selected_operation, tag_value)
                        )
                    if attribute_name and attribute_value:
                        criteria.append(
                            self.build_attribute_criterion(
                                selected_operation, attribute_name, attribute_value
                            )
                        )

                    if criteria:
                        xpath_expression = f"//{tag_name}[{' and '.join(criteria)}]"

            # Update XPath expression input
            self.xpath_expression_input.setText(xpath_expression)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error building XPath: {message}")

    def get_selected_operation(self):
        if self.radio_button_writing.isChecked():
            return "equals"
        elif self.radio_button_matching.isChecked():
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
        group = QGroupBox("List of filters to match in XML files")

        layout = QVBoxLayout()

        spacer = QFrame()
        spacer.setFrameShape(QFrame.HLine)
        spacer.setFrameShadow(QFrame.Sunken)

        # Elements
        self.add_xpath_to_list_button = QPushButton("Add Xpath to List")
        self.add_xpath_to_list_button.setToolTip(
            "Adds currently entered Xpath expression to the ListBox"
        )
        self.add_xpath_to_list_button.clicked.connect(
            self.add_xpath_expression_to_listbox
        )
        self.add_xpath_to_list_button.clicked.connect(
            self.update_statusbar_xpath_listbox_count
        )
        self.xpath_listbox.setMinimumHeight(100)
        self.statusbar_xpath_listbox_count = QStatusBar()
        self.statusbar_xpath_listbox_count.setSizeGripEnabled(False)
        self.statusbar_xpath_listbox_count.setStyleSheet(
            "font-weight: bold; color: #ffd740"
        )

        header_layout = QHBoxLayout()
        header_layout.addWidget(
            QLabel("Add XPath expressions to the list to search for in XML files:")
        )
        header_layout.addWidget(self.add_xpath_to_list_button)
        layout.addLayout(header_layout)
        layout.addWidget(spacer)
        layout.addWidget(self.xpath_listbox)
        layout.addWidget(self.statusbar_xpath_listbox_count)

        group.setLayout(layout)
        return group

    # ======= Start FUNCTIONS FOR create_matching_filter_group ======= #

    def update_statusbar_xpath_listbox_count(self):
        self.counter = self.xpath_listbox.count()
        if self.counter != 0:
            self.statusbar_xpath_listbox_count.showMessage(
                f"Total number of items in List: {self.counter}", 5000
            )

    def remove_selected_items(self):
        try:
            for item in self.xpath_listbox.selectedItems():
                self.xpath_listbox.takeItem(self.xpath_listbox.row(item))
            for index, item in enumerate(self.xpath_filters, 0):
                self.xpath_filters.pop(index)
                print(f"variable xpath_filters length: {len(self.xpath_filters) + 1}")
                self.update_statusbar_xpath_listbox_count()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(
                f"Error removing selected item from list: {message}"
            )

    def remove_all_items(self):
        try:
            self.xpath_listbox.clear()
            self.xpath_filters.clear()
            print(len(self.xpath_filters))
            self.update_statusbar_xpath_listbox_count()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(
                f"Error removing all items from list: {message}"
            )

    def show_context_menu(self, position):
        context_menu = QMenu(self)
        delete_action = QAction("Delete", self)
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
            r"^//[\w]+:[\w]+\[@[\w]+='[^']*'\]/@[\w]+$",  # //xml_tag:name[@attribute_name='value']/@attribute_name
        ]

        # Check if expression matches any pattern
        return any(re.match(pattern, xpath_expression) for pattern in valid_patterns)

    def add_xpath_expression_to_listbox(self):
        xpath_expression = self.xpath_expression_input.text()
        try:
            if not xpath_expression:
                self.program_output.setText("No Xpath expression entered.")
            elif xpath_expression and not self.is_duplicate(xpath_expression):
                # validate = self.validate_xpath_expression(xpath_expression)
                # if validate:
                self.xpath_filters.append(xpath_expression)
                self.xpath_listbox.addItem(xpath_expression)
                # else:
                #    self.program_output.setText("Not a valid Xpath expression!")
                #    QMessageBox.warning(self, "Exception adding filter", f"The entered Xpath expression '{xpath_expression}' is not valid, please try again.")
            else:
                self.program_output.setText(
                    f"Cannot add duplicate XPath expression: {xpath_expression}"
                )
                QMessageBox.warning(
                    self,
                    "Error adding filter",
                    f"Cannot add duplicate XPath expression:\n{xpath_expression}",
                )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error adding filter: {message}")
            QMessageBox.critical(self, "Exception adding filter", message)

    # ======= End FUNCTIONS FOR create_matching_filter_group ======= #

    def create_export_evaluation_group(self):
        group = QGroupBox("Export evaluation result as a CSV File")

        layout = QVBoxLayout()

        # Elements
        self.folder_csv_input = QLineEdit()
        self.folder_csv_input.setPlaceholderText(
            "Choose a folder where you want to save the evaluation..."
        )
        self.csv_save_as_button = QPushButton("Browse")
        self.csv_save_as_button.clicked.connect(self.choose_save_folder)
        self.csv_convert_button = QPushButton("Convert")
        self.csv_convert_button.setToolTip(
            "Starts reading the XML file and writes the matches to a CSV file"
        )
        self.csv_convert_button.clicked.connect(self.write_to_csv)

        export_layout = QHBoxLayout()
        export_layout.addWidget(self.folder_csv_input)
        export_layout.addWidget(self.csv_save_as_button)
        export_layout.addWidget(self.csv_convert_button)
        layout.addLayout(export_layout)

        group.setLayout(layout)
        return group

    # ======= Start FUNCTIONS FOR create_export_evaluation_group ======= #

    def choose_save_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.folder_csv_input.setText(folder)
            

    def parse_xml_with_xpath(self, xpath_expressions):
        folder_containing_xml_files = self.folder_xml_input.text()
        xml_files = [f for f in os.listdir(folder_containing_xml_files) if f.endswith(".xml")]
        total_files = len(xml_files)
        total_sum_matches = 0
        total_matching_files = 0

        for index, filename in enumerate(xml_files):
            file_path = os.path.join(folder_containing_xml_files, filename)
            self.program_output.setText(f"Processing {filename}")
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
            except ET.XMLSyntaxError:
                self.program_output(
                    "Error reading XML: XML file is empty, skipping file..."
                )
                continue
                
            column_values = {}
            file_total_matches = 0

            for xpath in xpath_expressions:
                column_name = self.get_header_from_xpath(xpath)
                column_values[column_name] = []
                matches = root.xpath(xpath)
                
                for match in matches:
                    if isinstance(match, ET._Element):
                        value = match.text.strip() if match.text else ''
                    elif isinstance(match, str):
                        value = match
                    elif isinstance(match, ET._ElementUnicodeResult):
                        value = str(match)
                    else:
                        value = ''
                    column_values[column_name].append(value)

            if file_total_matches > 0:
                total_sum_matches += file_total_matches
                total_matching_files += 1
                
            # Update progress
            progress = int((index + 1) / total_files * 100)
            self.progress_updated.emit(progress)

            return column_values, total_sum_matches, total_matching_files


    def get_header_from_xpath(self, xpath):
        
        if xpath.endswith("/text()") and self.radio_button_writing.isChecked():
            match = re.search(r"([^/]+)/text\(\)$", xpath)
            return f"{match.group(1)} Value" if match else xpath
        
        elif "[text()" in xpath and self.radio_button_matching.isChecked():
            match = re.search(r"//([^/]+)\[text\(\)='([^']*)'\]")
            return f"{match.group(1)} Matches" if match else xpath
        
        elif "/@" in xpath and self.radio_button_writing.isChecked():
            # For attributes, use the attribute name
            return f"{xpath.split("@")[-1]} Value"
        
        elif "[@" in xpath and self.radio_button_matching.isChecked():
            match = re.search(r"@([^=]+)='([^']*)'", xpath)
            return f"{match.group(0)} Matches" if match else xpath
        
        else:
            return xpath.split('/')[-1]

    def write_to_csv(self):
        # Date and Time
        today_date = datetime.now()
        formatted_today_date = today_date.strftime("%d.%m.%y-%H-%M-%S")

        folder_containing_xml_files = self.folder_xml_input.text()
        folder_for_csv_output = self.folder_csv_input.text()

        csv_output_path = os.path.join(
            folder_for_csv_output,
            f"Evaluation_Results_{formatted_today_date}.csv",
        )

        # Check if the XML input folder exists before proceeding
        if not os.path.exists(folder_containing_xml_files):
            QMessageBox.warning(
                self,
                "Path Error",
                "Cannot start evaluation because XML input folder is not set!",
            )
            return  # Exit the function if the folder doesn't exist

        # Check if any XPath filters have been added
        matching_filters = self.xpath_filters
        
        if len(matching_filters) == 0:
            QMessageBox.warning(
                self,
                "ListBox Error",
                "Cannot start evaluation because no XPath filters have been added to the list!",
            )
            return  # Exit the function if no filters are present

        # Check if the CSV output folder exists
        if not os.path.exists(folder_for_csv_output):
            QMessageBox.warning(
                self,
                "Path Error",
                "Cannot start evaluation because CSV output folder is not set!",
            )
            return  # Exit the function if the folder doesn't exist

        xml_files = [f for f in os.listdir(folder_containing_xml_files) if f.endswith(".xml")]

        try:
            self.browse_xml_folder_button.setDisabled(True)
            self.read_xml_button.setDisabled(True)
            self.build_xpath_button.setDisabled(True)
            self.add_xpath_to_list_button.setDisabled(True)
            self.browse_csv_button.setDisabled(True)
            self.csv_save_as_button.setDisabled(True)
            self.csv_convert_button.setDisabled(True)

            self.program_output.setText("Saving results as CSV, please wait...")

            all_column_values = []
            xml_filenames = []

            for xml_file in xml_files:
                column_values, total_matching_files, total_matches_found = self.parse_xml_with_xpath(matching_filters)
                all_column_values.append(column_values)
                xml_filenames.append(os.path.splitext(os.path.basename(xml_file))[0])

            # Prepare the header
            header = ['Filename'] + [self.get_header_from_xpath(xpath) for xpath in matching_filters]

            # Prepare the rows
            rows = []
            for filename, column_values in zip(xml_filenames, all_column_values):
                max_length = max(len(values) for values in column_values.values())
                for i in range(max_length):
                    row = [filename]
                    for column in header[1:]:
                        if i < len(column_values[column]):
                            row.append(column_values[column][i])
                        else:
                            row.append('')
                    rows.append(row)

            # Write to CSV
            with open(csv_output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(header)
                writer.writerows(rows)

            QMessageBox.information(
                self, "Export Successful", f"Matches saved to:\n{csv_output_path}"
            )
            self.program_output.setText(
                f"Found {total_matching_files} files that have a total sum of {total_matches_found} matches."
            )
            self.browse_xml_folder_button.setDisabled(False)
            self.read_xml_button.setDisabled(False)
            self.build_xpath_button.setDisabled(False)
            self.add_xpath_to_list_button.setDisabled(False)
            self.browse_csv_button.setDisabled(False)
            self.csv_save_as_button.setDisabled(False)
            self.csv_convert_button.setDisabled(False)
            self.progressbar.reset()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception in Program", f"Error exporting CSV: {message}"
            )
            self.browse_xml_folder_button.setDisabled(False)
            self.read_xml_button.setDisabled(False)
            self.build_xpath_button.setDisabled(False)
            self.add_xpath_to_list_button.setDisabled(False)
            self.browse_csv_button.setDisabled(False)
            self.csv_save_as_button.setDisabled(False)
            self.csv_convert_button.setDisabled(False)

    def update_progress(self, value):
        self.progressbar.setValue(value)

    # ======= End FUNCTIONS FOR create_export_evaluation_group ======= #

    def create_program_output_group(self):
        group = QGroupBox("Program Output")

        layout = QVBoxLayout()

        self.program_output = QTextEdit()
        self.program_output.setReadOnly(True)

        layout.addWidget(self.program_output)

        group.setLayout(layout)
        return group

    def create_xml_output_group(self):
        group = QGroupBox("XML Output")

        layout = QVBoxLayout()

        # Elements
        self.xml_output = QTextEdit()  # XML Output
        self.xml_output.setReadOnly(True)
        self.progressbar = QProgressBar()
        self.progressbar.setFormat("%p%")

        layout.addWidget(self.xml_output)
        layout.addSpacerItem(self.horizontal_spacer)
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
        group = QGroupBox("CSV Conversion")

        layout = QVBoxLayout()

        # Title
        title_label = QLabel("CSV Converter")
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #FFC857;")
        layout.addWidget(title_label)

        # Description
        self.desc_label = QLabel(
            "Convert CSV File to a different file type with the Pandas module.\nSupported output file types: Excel, Markdown, HTML and JSON"
        )

        # Elements
        self.input_csv_file_conversion = QLineEdit()
        self.input_csv_file_conversion.setPlaceholderText(
            "Choose a CSV file for conversion..."
        )
        self.browse_csv_button = QPushButton("Browse")
        self.browse_csv_button.clicked.connect(self.browse_csv_file)

        input_layout = QHBoxLayout()

        input_layout.addWidget(self.input_csv_file_conversion)
        input_layout.addWidget(self.browse_csv_button)

        layout.addWidget(self.desc_label)
        layout.addSpacerItem(self.horizontal_spacer)
        layout.addLayout(input_layout)

        # Elements
        self.output_csv_file_conversion = QLineEdit()
        self.output_csv_file_conversion.setPlaceholderText(
            "Choose where to save the converted CSV file..."
        )
        self.browse_csv_output_button = QPushButton("Browse")
        self.browse_csv_output_button.clicked.connect(self.csv_save_as)
        self.convert_csv_button = QPushButton("Convert")
        self.convert_csv_button.clicked.connect(self.pandas_convert_csv_file)
        self.checkbox_write_index_column = QCheckBox("Write Index Column?")
        self.checkbox_write_index_column.setChecked(False)
        self.checkbox_write_index_column.clicked.connect(self.wrinco_checkbox_info)

        output_layout = QHBoxLayout()

        output_layout.addWidget(self.output_csv_file_conversion)
        output_layout.addWidget(self.browse_csv_output_button)

        layout.addLayout(output_layout)

        layout.addSpacerItem(self.horizontal_spacer)
        layout.addWidget(self.convert_csv_button)
        layout.addWidget(self.checkbox_write_index_column)

        # Add logo
        # logo_label = QLabel() # "Hans Geis GmbH & Co.KG"
        ##logoqt_label = QLabel()
        # pixmap = QPixmap("_internal/images/logo.png")  # Replace with actual path
        ##pixmapqt = QPixmap("_internal/images/QT6.png")
        # logo_label.setPixmap(pixmap)
        ##logoqt_label.setPixmap(pixmapqt)
        # layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        ##layout.addWidget(logoqt_label, alignment=Qt.AlignCenter)

        layout.addStretch()  # This will push everything up and fill the empty space at the bottom

        group.setLayout(layout)
        return group

    def create_csv_conversion_output_group(self):
        group = QGroupBox("CSV Conversion Output")
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
            QMessageBox.critical(
                self, "Exception in Program", f"An error occurred: {message}"
            )

    def browse_csv_file(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Select CSV File", "", "CSV Files (*.csv)"
            )
            if file_name:
                self.input_csv_file_conversion.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception in reading CSV", f"Error reading CSV:\n{message}"
            )

    def csv_save_as(self):
        try:
            options = QFileDialog.Options()
            file_types = "Excel File (*.xlsx);;JSON File (*.json);;HTML File (*.html);;Markdown File (*.md)"
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save As", "", file_types, options=options
            )
            if file_name:
                self.output_csv_file_conversion.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception exporting CSV", f"Error exporting CSV: {message}"
            )

    @Slot(str)
    def update_output_file(self, file_name):
        if hasattr(self, "output_csv_file_conversion"):
            self.output_csv_file_conversion.setText(file_name)
            self.output_csv_file_conversion.repaint()  # Force a repaint

    @Slot(str)
    def update_input_file(self, file_name):
        if hasattr(self, "input_csv_file_conversion"):
            self.input_csv_file_conversion.setText(file_name)
            self.input_csv_file_conversion.repaint()  # Force a repaint

    def pandas_convert_csv_file(self):
        csv_input_file = self.input_csv_file_conversion.text()
        csv_output_file = self.output_csv_file_conversion.text()
        checkbox = self.checkbox_write_index_column.isChecked()
        try:
            self.csv_conversion_output.setText("Starting conversion, please wait...")
            with open(csv_input_file, encoding="utf-8") as file:
                sample = file.read(4096)
                sniffer = csv.Sniffer()
                get_delimiter = sniffer.sniff(sample).delimiter
            if not checkbox:
                csv_df = pd.read_csv(
                    csv_input_file,
                    delimiter=get_delimiter,
                    encoding="utf-8",
                    index_col=0,
                )
            else:
                csv_df = pd.read_csv(
                    csv_input_file, delimiter=get_delimiter, encoding="utf-8"
                )

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
                (input_ext, output_ext), (None, None)
            )

            if read_func is None or write_func is None:
                QMessageBox.warning(
                    self,
                    "Unsupported Conversion",
                    "Error converting file, unsupported conversion...",
                )
                return

            csv_df = read_func
            write_func(csv_df, csv_output_file)
            self.csv_conversion_output.setText(
                f"Successfully converted {Path(csv_input_file).stem} {input_ext.upper()} to {Path(csv_output_file).stem} {output_ext.upper()}"
            )

        except Exception as ex:
            self.csv_conversion_output.clear()
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception exporting CSV", f"Error exporting CSV: {message}"
            )

    # ======= End FUNCTIONS FOR create_csv_conversion_group ======= #

    def create_csv_to_table_group(self):
        group = QGroupBox("Display CSV into Table")

        layout = QVBoxLayout()

        # File selection
        file_layout = QHBoxLayout()
        self.csv_file_input = QLineEdit()
        self.csv_file_input.setPlaceholderText("Select CSV file...")
        file_button = QPushButton("Browse")
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
        load_button = QPushButton("Load CSV")
        load_button.clicked.connect(self.load_csv_data)
        layout.addWidget(load_button)

        group.setLayout(layout)
        return group

    def select_csv_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)"
        )
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
        filter_column = (
            self.filter_column.currentIndex() - 1
        )  # -1 because "All Columns" is at index 0

        if filter_column == -1:  # "All Columns" selected
            self.proxy_model.setFilterKeyColumn(-1)
        else:
            self.proxy_model.setFilterKeyColumn(filter_column)

        self.proxy_model.setFilterFixedString(filter_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

#//TODO How can I expand the code to write the CSV File completly differently, if I use the expressions that match these patterns: match = re.search(r"//([^/]+)\[text\(\)='([^']*)'\]") match = re.search(r"@([^=]+)='([^']*)'", xpath) I want to write the total number of matches found, here is how the CSV File should look like if I add the filter //filter[@id='187']: "Filename","@id='187' Matches" "TestXML","2" 
