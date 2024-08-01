from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QGroupBox, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QRadioButton, 
                             QListWidget, QTextEdit, QProgressBar, QStatusBar,
                             QCheckBox,QMenu,QFileDialog, QMessageBox, QFrame, QSpacerItem, QSizePolicy)
from PySide6.QtGui import QIcon, QPalette, QColor, QPixmap, QAction
from PySide6.QtCore import Qt, QThread, Signal
import sys
import csv
import os
import re
import webbrowser
from  datetime import date
from lxml import etree as ET
from qt_material import apply_stylesheet

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
                'xml_string': xml_string,
                'tags': sorted(tags),
                'tag_values': sorted(tag_values),
                'attributes': sorted(attributes),
                'attribute_values': sorted(attribute_values)
            }
            self.finished.emit(result)
        except Exception as ex:
            self.error.emit(str(ex))

class MainWindow(QMainWindow):
    progress_updated = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
        
    def initUI(self):
        self.setWindowTitle("XMLuvation v1.0 © 2024 by Jovan Zaric")
        self.setWindowIcon(QIcon("_internal/icon/xml_32px.ico"))  # Replace with actual path
        self.setGeometry(100, 100, 1300, 840)
        self.eval_input_file = None
        self.xpath_filters = []
        self.xpath_listbox = QListWidget(self)
        self.progress_updated.connect(self.update_progress)
        
        # Connect the custom context menu for Listbox
        self.xpath_listbox.setContextMenuPolicy(Qt.CustomContextMenu)
        self.xpath_listbox.customContextMenuRequested.connect(self.show_context_menu)
        #self.set_dark_theme() # Remove comment to enable custom set DarkTheme Yellowish (Geis) Make sure to remove the qt_material apply_sytelsheet at the bottom under __init__

        # Set the font
        #font = QFont("Calibri", 12)
        #self.setFont(font)

        # Set the color scheme
        #self.set_dark_theme()

        # Create the menu bar
        self.create_menu_bar()

        # Create the main layout
        main_layout = QVBoxLayout()

        # Create the tab widget
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_xml_evaluation_tab(), "XML Evaluation")
        tab_widget.addTab(self.create_csv_conversion_tab(), "CSV Conversion")

        main_layout.addWidget(tab_widget)

        # Create a central widget to hold the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(49, 54, 59))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 47, 51))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 58, 63))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 58, 63))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(dark_palette)
    

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

        # Path Menu
        paths_menu = menu_bar.addMenu("&Path")
        lobster_test_action = QAction("Lobster Test System", self)
        lobster_test_action.setStatusTip("Open Lobster Test System")
        lobster_test_action.triggered.connect(lambda: self.open_path(r"\\nesist02\ProfilileXMLExport"))
        paths_menu.addAction(lobster_test_action)
        lobster_prod_action = QAction("Lobster Prod System", self)
        lobster_prod_action.setStatusTip("Open Lobster Prod System")
        lobster_prod_action.triggered.connect(lambda: self.open_path(r"\\nesis002\ProfilileXMLExport"))
        paths_menu.addAction(lobster_prod_action)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        xpath_help_action = QAction("XPath Help", self)
        xpath_help_action.setStatusTip("Open XPath Syntax Help")
        xpath_help_action.triggered.connect(self.open_web_xpath_help)
        help_menu.addAction(xpath_help_action)
        xpath_cheatsheet_action = QAction("XPath Cheat Sheet", self)
        xpath_cheatsheet_action.setStatusTip("Open XPath Cheat Sheet")
        #xpath_cheatsheet_action.triggered.connect(self.open_xpath_cheatsheet)
        #help_menu.addAction(xpath_cheatsheet_action)
        
    # ======= START FUNCTIONS create_menu_bar ======= #
    
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
            QMessageBox.critical(self, "Error", f"Path does not exist or is not a valid path:\n{directory_path}")
    
    
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
            QMessageBox.critical(self, "Error", f"Path does not exist or is not a valid path:\n{directory_path}")
            
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
        group = QGroupBox("XML folder selection and XPath builder")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()
        self.horizontal_spacer = QSpacerItem(40,10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        folder_with_xml_files_and_statusbar_layout = QHBoxLayout()
        
        # Elements
        self.total_xml_files_statusbar = QStatusBar()
        self.setStatusBar(self.total_xml_files_statusbar)
        self.total_xml_files_statusbar.setSizeGripEnabled(False)
        self.total_xml_files_statusbar.setStyleSheet("font-size: 20;font-weight: bold; color: #0cd36c")
        
        folder_with_xml_files_and_statusbar_layout.addWidget(QLabel("Choose a folder that contains XML files"))
        folder_with_xml_files_and_statusbar_layout.addWidget(self.total_xml_files_statusbar)
        
        layout.addLayout(folder_with_xml_files_and_statusbar_layout)
        
        # Elements
        self.folder_xml_input = QLineEdit()
        self.folder_xml_input.textChanged.connect(self.update_xml_file_count)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        self.read_xml_button = QPushButton("Read XML")
        self.read_xml_button.clicked.connect(self.read_xml)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_xml_input)
        folder_layout.addWidget(self.browse_button)
        folder_layout.addWidget(self.read_xml_button)
        layout.addLayout(folder_layout)

        layout.addWidget(QLabel("Get XML Tag and Attribute Names/Values for XPath generation"))

        tag_layout = QHBoxLayout()
        
        # Elements
        self.tag_name_label = QLabel("Tag name:")
        self.tag_name_combobox = QComboBox()
        self.tag_name_combobox.setEditable(True)
        self.tag_name_combobox.currentTextChanged.connect(self.on_tag_name_changed)
        self.tag_value_label = QLabel("Tag value:")
        self.tag_value_combobox = QComboBox()
        self.tag_value_combobox.setEditable(True)
        
        tag_layout.addWidget(self.tag_name_label)
        tag_layout.addWidget(self.tag_name_combobox)
        tag_layout.addWidget(self.tag_value_label)
        tag_layout.addWidget(self.tag_value_combobox)
        layout.addLayout(tag_layout)

        att_layout = QHBoxLayout()
        
        # Elements
        self.attribute_name_label = QLabel("Attribute name:")
        self.attribute_name_combobox = QComboBox()
        self.attribute_name_combobox.setEditable(True)
        self.attribute_name_combobox.currentTextChanged.connect(self.on_attribute_name_changed)
        self.attribute_value_label = QLabel("Attribute value:")
        self.attribute_value_combobox = QComboBox()
        self.attribute_value_combobox.setEditable(True)
        
        att_layout.addWidget(self.attribute_name_label)
        att_layout.addWidget(self.attribute_name_combobox)
        att_layout.addWidget(self.attribute_value_label)
        att_layout.addWidget(self.attribute_value_combobox)
        layout.addLayout(att_layout)
        layout.addSpacerItem(self.horizontal_spacer)
        
        function_layout = QHBoxLayout()
    
        # Elements
        self.radio_button_equals = QRadioButton("Equals")
        self.radio_button_equals.setChecked(True)
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
        
        build_xpath_layout = QHBoxLayout()
        
        build_xpath_layout.addWidget(QLabel("Xpath Expression:"))
        self.xpath_expression_input = QLineEdit()
        self.build_xpath_button = QPushButton("Build Xpath")
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
            QMessageBox.critical(self,"Exception in Program", message)


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
            self.xml_parser_thread = XMLParserThread(xml_file)
            self.xml_parser_thread.finished.connect(self.on_xml_parsed)
            self.xml_parser_thread.error.connect(self.on_xml_parse_error)
            self.xml_parser_thread.start()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", message)


    def on_xml_parsed(self, result):
        self.xml_output.setText(result['xml_string'])

        self.tag_name_combobox.clear()
        self.tag_value_combobox.clear()
        self.attribute_name_combobox.clear()
        self.attribute_value_combobox.clear()

        self.tag_name_combobox.addItems(result['tags'])
        self.tag_value_combobox.addItems(result['tag_values'])
        self.attribute_name_combobox.addItems(result['attributes'])
        self.attribute_value_combobox.addItems(result['attribute_values'])

        self.eval_input_file = self.xml_parser_thread.xml_file
        self.program_output.setText("XML file loaded successfully.")


    def on_xml_parse_error(self, error_message):
        QMessageBox.critical(self, "Error Parsing XML", error_message)
               
            
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


    # Statusbar update function
    def update_xml_file_count(self, folder):
        try:
            xml_files = list(Path(folder).glob('*.xml'))
            file_count = len(xml_files)
            self.total_xml_files_statusbar.showMessage(f"Found {file_count} XML Files")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.total_xml_files_statusbar.setStyleSheet("color: #ed2828")
            self.total_xml_files_statusbar.showMessage(f"Error counting XML files: {message}")
            
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

                # Apply additional criteria based on radio buttons
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
        group = QGroupBox("List of filters to match in XML files")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()
        
        spacer = QFrame()
        spacer.setFrameShape(QFrame.HLine)
        spacer.setFrameShadow(QFrame.Sunken)
        
        # Elements
        self.add_xpath_to_list_button = QPushButton("Add Xpath to List")
        self.add_xpath_to_list_button.setToolTip("Adds currently entered Xpath Expression to the ListBox")
        self.add_xpath_to_list_button.clicked.connect(self.add_xpath_expression_to_listbox)
        self.add_xpath_to_list_button.clicked.connect(self.update_statusbar_xpath_listbox_count)
        self.xpath_listbox.setMinimumHeight(100)
        self.statusbar_xpath_listbox_count = QStatusBar()
        self.statusbar_xpath_listbox_count.setSizeGripEnabled(False)
        self.statusbar_xpath_listbox_count.setStyleSheet("font-weight: bold; color: #ffd740")

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Add XPath Expressions to list to look for in XML files"))
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
        self.statusbar_xpath_listbox_count.showMessage(f"Total number of items in List: {self.counter}", 5000)
        
    
    def remove_selected_items(self):
        try:
            for item in self.xpath_listbox.selectedItems():
                self.xpath_listbox.takeItem(self.xpath_listbox.row(item))
            for index,item in enumerate(self.xpath_filters,0):
                self.xpath_filters.pop(index)
                print(f"variable xpath_filters length: {len(self.xpath_filters) + 1}")
                self.update_statusbar_xpath_listbox_count()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error removing selected item from list: {message}")


    def remove_all_items(self):
        try:
            self.xpath_listbox.clear()
            self.xpath_filters.clear()
            print(len(self.xpath_filters))
            self.update_statusbar_xpath_listbox_count()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error removing all items from list: {message}")


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
    
    
    def add_xpath_expression_to_listbox(self):
        xpath_expression = self.xpath_expression_input.text()
        try:
            if not xpath_expression:
                self.program_output.setText("No Xpath expression entered.")
            elif xpath_expression and not self.is_duplicate(xpath_expression):
                self.xpath_filters.append(xpath_expression)
                self.xpath_listbox.addItem(xpath_expression)
            else:
                self.program_output.setText(f"Cannot add duplicate XPath Expression: {xpath_expression}")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.program_output.setText(f"Error adding filter: {message}")
     
    # ======= End FUNCTIONS FOR create_matching_filter_group ======= #

    def create_export_evaluation_group(self):
        group = QGroupBox("Export evaluation result as a CSV File")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Choose a folder where you want to save the evaluation"))
        
        # Elements
        self.folder_csv_input = QLineEdit()
        self.csv_save_as_button = QPushButton("Browse")
        self.csv_save_as_button.clicked.connect(self.choose_save_folder)
        self.csv_covert_button = QPushButton("Convert")
        self.csv_covert_button.clicked.connect(self.convert_to_csv)
        
        export_layout = QHBoxLayout()
        export_layout.addWidget(self.folder_csv_input)
        export_layout.addWidget(self.csv_save_as_button)
        export_layout.addWidget(self.csv_covert_button)
        layout.addLayout(export_layout)

        group.setLayout(layout)
        return group
    
    # ======= Start FUNCTIONS FOR create_export_evaluation_group ======= #
    
    def choose_save_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.folder_csv_input.setText(folder)


    def evaluate_xml_files_matching(self, folder_containing_xml_files, matching_filters):
        final_results = []
        xml_files = [f for f in os.listdir(folder_containing_xml_files) if f.endswith(".xml")]
        total_files = len(xml_files)
        total_sum_matches = 0
        total_matching_files = 0

        for index, filename in enumerate(xml_files):
            file_path = os.path.join(folder_containing_xml_files, filename)

            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
            except ET.XMLSyntaxError as e:
                print(f"Error processing {filename}: {str(e)}")
                continue

            current_file_results = {"Filename": os.path.splitext(filename)[0]}
            file_total_matches = 0

            for expression in matching_filters:
                result = root.xpath(expression)
                match_count = len(result)
                file_total_matches += match_count

                if match_count:
                    if "[@" in expression or "[text()=" in expression:
                        final_results.append({
                            "Filename": os.path.splitext(filename)[0],
                            "Expression": expression,
                            "Matches": match_count,
                        })
                    else:
                        self.process_xpath_result(expression, result, current_file_results)

            if file_total_matches > 0:
                total_sum_matches += file_total_matches
                total_matching_files += 1
                if current_file_results:
                    final_results.append(current_file_results)

            # Update progress
            progress = int((index + 1) / total_files * 100)
            self.progress_updated.emit(progress)
            
        return final_results, total_sum_matches, total_matching_files
    
    
    def process_xpath_result(self, expression, result, current_file_results):
        if "/@" in expression:
            attribute_name = expression.split("@")[-1]
            key = f"Attribute {attribute_name} Value"
            current_file_results[key] = [elem.strip() for elem in result if elem.strip()]
        elif "/text()" in expression:
            tag_name = expression.split("/")[-2]
            key = f"Tag {tag_name} Value"
            current_file_results[key] = [elem.strip() for elem in result if elem.strip()]
        elif "[@" in expression:
            match = re.search(r"@([^=]+)", expression)
            if match:
                attribute_name = match.group(1).strip()
                key = f"Attribute {attribute_name} Value"
                current_file_results[key] = [
                    elem.get(attribute_name) for elem in result if elem.get(attribute_name)
                ]


    def convert_to_csv(self):
        folder_containing_xml_files = self.folder_xml_input.text()
        folder_for_csv_output = self.folder_csv_input.text()
        today_date = date.today()
        formatted_today_date = today_date.strftime("%d%m%y")
        csv_output_path = os.path.join(self.folder_csv_input.text(), f"Evaluation_Results_{formatted_today_date}.csv")
        matching_filters = self.xpath_filters

        if not os.path.exists(folder_containing_xml_files):
            QMessageBox.critical(self, "Path Error", "Cannot start evaluation because XML input folder is not set!")
        elif len(matching_filters) == 0:
            QMessageBox.critical(self, "ListBox Error", "Cannot start evaluation because no XPath filters have been added to the list!")
        elif not os.path.exists(folder_for_csv_output):
            QMessageBox.critical(self, "Path Error", "Cannot start evaluation because CSV output folder is not set!")
        else:
            try:
                matching_results, total_matches_found, total_matching_files = self.evaluate_xml_files_matching(
                    folder_containing_xml_files, matching_filters)

                #if self.folder_xml_input

                if not matching_results:
                    QMessageBox.information(self, "No Matches", "No matches found.")
                    return

                headers = ["Filename"] + [
                    header
                    for header in set(key for dic in matching_results for key in dic)
                    if header != "Filename"
                ]

                with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.DictWriter(
                        csvfile, fieldnames=headers, delimiter=";", extrasaction="ignore"
                    )
                    writer.writeheader()

                    for match in matching_results:
                        if "Expression" in match:
                            writer.writerow(match)
                        else:
                            filename = match["Filename"]
                            for key, value in match.items():
                                if key != "Filename":
                                    if isinstance(value, list):
                                        for item in value:
                                            writer.writerow({"Filename": filename, key: item})
                                    else:
                                        writer.writerow({"Filename": filename, key: value})

                QMessageBox.information(self, "Export Successful", f"Matches saved to {csv_output_path}\n")
                self.program_output.setText(f"Found {total_matching_files} files that have a total sum of {total_matches_found} matches.")
                self.progressbar.reset()
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "Error", f"Error exporting CSV: {message}")
        
                
    def update_progress(self, value):
        self.progressbar.setValue(value)
        
    # ======= End FUNCTIONS FOR create_export_evaluation_group ======= #

    def create_program_output_group(self):
        group = QGroupBox("Program Output")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        self.program_output = QTextEdit()
        self.program_output.setReadOnly(True)
        
        layout.addWidget(self.program_output)

        group.setLayout(layout)
        return group


    def create_xml_output_group(self):
        group = QGroupBox("XML Output")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        # Elements
        self.xml_output = QTextEdit() # XML Output
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

        # Right column
        right_column = QVBoxLayout()
        right_column.addWidget(self.create_csv_output_group())

        layout.addLayout(left_column, 1)
        layout.addLayout(right_column, 1)
        tab.setLayout(layout)
        return tab


    def create_csv_conversion_group(self):
        group = QGroupBox("CSV Conversion to different file type")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("CSV Converter")
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #FFC857;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel("Convert CSV File to a different file type with the Pandas module.\nSupported output file types: Excel, Markdown, HTML and JSON")
        layout.addWidget(desc_label)

        layout.addWidget(QLabel("Choose a CSV file for conversion:"))
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLineEdit())
        input_layout.addWidget(QPushButton("Browse"))
        input_layout.addWidget(QPushButton("Read CSV"))
        layout.addLayout(input_layout)

        layout.addWidget(QLabel("Choose where to save the converted CSV file"))
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLineEdit())
        output_layout.addWidget(QPushButton("Browse"))
        output_layout.addWidget(QPushButton("Convert"))
        layout.addLayout(output_layout)

        layout.addWidget(QCheckBox("Write Index Column?"))

        # Add logo
        logo_label = QLabel() # "Hans Geis GmbH & Co.KG"
        #logoqt_label = QLabel()
        pixmap = QPixmap("_internal/images/logo.png")  # Replace with actual path
        #pixmapqt = QPixmap("_internal/images/QT6.png")
        logo_label.setPixmap(pixmap)
        #logoqt_label.setPixmap(pixmapqt)
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        #layout.addWidget(logoqt_label, alignment=Qt.AlignCenter)

        layout.addStretch()  # This will push everything up and fill the empty space at the bottom

        group.setLayout(layout)
        return group


    def create_csv_output_group(self):
        group = QGroupBox("CSV Conversion Output")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        layout.addWidget(QTextEdit())

        group.setLayout(layout)
        return group
    
    
    def clear_output(self):
        self.program_output.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    apply_stylesheet(app, theme='dark_amber.xml') # my_theme.xml is my custom theme
    window.show()
    sys.exit(app.exec())
