import pandas as pd
import sys
import csv
import os
import re
import webbrowser
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QGroupBox, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QRadioButton, 
                             QListWidget, QTextEdit, QProgressBar, QStatusBar,
                             QMenuBar, QCheckBox,QMenu,QFileDialog, QMessageBox, QTableView)
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QAction
from PySide6.QtCore import Qt, QAbstractTableModel, QVariantAnimation, QThread, Signal
from lxml import etree as ET
from qt_material import apply_stylesheet
from pathlib import Path

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
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("XMLuvation v1.0 © 2024 by Jovan Zaric")
        self.setWindowIcon(QIcon("_internal/icon/xml_32px.ico"))  # Replace with actual path
        self.setGeometry(100, 100, 1280, 800)
        self.eval_input_file = None
        #self.set_dark_theme()

        # Set the font
        font = QFont("Calibri", 12)
        self.setFont(font)

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


    #def set_dark_theme(self):
    #    dark_palette = QPalette()
    #    dark_palette.setColor(QPalette.ColorRole.Window, QColor(49, 54, 59))
    #    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    #    dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 47, 51))
    #    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 58, 63))
    #    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    #    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    #    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    #    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 58, 63))
    #    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    #    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    #    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    #    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    #    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    #    self.setPalette(dark_palette)
    

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
        lobster_test_action.triggered.connect(lambda: self.open_path("//nesist02/ProfilileXMLExport"))
        paths_menu.addAction(lobster_test_action)
        lobster_prod_action = QAction("Lobster Prod System", self)
        lobster_prod_action.setStatusTip("Open Lobster Prod System")
        lobster_prod_action.triggered.connect(lambda: self.open_path("//nesis002/ProfilileXMLExport"))
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
                template = "An exception of type {0} occurred. Arguments: {1!r}"
                message = template.format(type(ex).__name__, ex.args)
                QMessageBox.setButtonText(self,"Okay")
                QMessageBox.critical(self,message)
        else:
            QMessageBox.critical(self, "Error", f"Path does not exist or is not a valid path:\n{directory_path}")
    
    
    # Open CSV output folder function
    def open_output_folder(self):
        directory_path = self.folder_csv_input.text()
        
        if os.path.exists(directory_path):
            try:
                os.startfile(directory_path)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments: {1!r}"
                message = template.format(type(ex).__name__, ex.args)
                QMessageBox.critical(self,message)
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
        
        folder_with_xml_files_and_statusbar_layout = QHBoxLayout()
        
        self.total_xml_files_statusbar = QStatusBar()
        self.setStatusBar(self.total_xml_files_statusbar)
        self.total_xml_files_statusbar.setSizeGripEnabled(False)
        self.total_xml_files_statusbar.setStyleSheet("font-weight: bold; color: #0cd36c")
        
        folder_with_xml_files_and_statusbar_layout.addWidget(QLabel("Choose a Folder that contains XML Files"))
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
        
        self.tag_name_label = QLabel("Tag name:")
        self.tag_name_combobox = QComboBox()
        self.tag_name_combobox.setEditable(True)
        self.tag_name_combobox.currentTextChanged.connect(self.on_tag_name_changed)
        self.tag_value_label = QLabel("Tag value:")
        self.tag_value_combobox = QComboBox()
        self.tag_value_combobox.setEditable(True)
        
        self.attribute_name_label = QLabel("Attribute name:")
        self.attribute_name_combobox = QComboBox()
        self.attribute_name_combobox.setEditable(True)
        self.attribute_name_combobox.currentTextChanged.connect(self.on_attribute_name_changed)
        self.attribute_value_label = QLabel("Attribute value:")
        self.attribute_value_combobox = QComboBox()
        self.attribute_value_combobox.setEditable(True)
        
        tag_layout.addWidget(self.tag_name_label)
        tag_layout.addWidget(self.tag_name_combobox)
        tag_layout.addWidget(self.tag_value_label)
        tag_layout.addWidget(self.tag_value_combobox)
        layout.addLayout(tag_layout)

        att_layout = QHBoxLayout()
        att_layout.addWidget(self.attribute_name_label)
        att_layout.addWidget(self.attribute_name_combobox)
        att_layout.addWidget(self.attribute_value_label)
        att_layout.addWidget(self.attribute_value_combobox)
        layout.addLayout(att_layout)

        group.setLayout(layout)
        return group

    # ======= START FUNCTIONS FOR create_xml_eval_group ======= #

    def on_tag_name_changed(self, selected_tag):
        if not selected_tag:
            return
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
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            self.program_output.setText(f"ERROR: {message}")


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
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            self.program_output.setText(f"ERROR: {message}")


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
            self.program_output.setText(f"Error getting attributes: {str(ex)}")
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
            self.program_output.setText(f"Error getting tag values: {str(ex)}")
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
            self.program_output.setText(f"Error getting attribute values: {str(ex)}")
            return []


    def parse_xml(self, xml_file):
        try:
            self.xml_parser_thread = XMLParserThread(xml_file)
            self.xml_parser_thread.finished.connect(self.on_xml_parsed)
            self.xml_parser_thread.error.connect(self.on_xml_parse_error)
            self.xml_parser_thread.start()
            self.program_output.setText("Loading XML file...")

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
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
        self.program_output.setText(f"Error loading XML file: {error_message}")
               
            
    def read_xml(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select XML File", "", "XML Files (*.xml)")
            if file_name:
                self.parse_xml(file_name)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
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
        except Exception as e:
            self.total_xml_files_statusbar.setStyleSheet("color: #ed2828")
            self.total_xml_files_statusbar.showMessage(f"Error counting XML files: {str(e)}")
            
    # ======= END FUNCTIONS FOR create_xml_eval_group ======= #
    
    def create_matching_filter_group(self):
        group = QGroupBox("List of filters to match in XML files")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Add XPath Expressions to list to look for in XML Files:"))
        header_layout.addWidget(QPushButton("Add XPath Filter"))
        layout.addLayout(header_layout)

        layout.addWidget(QListWidget())

        group.setLayout(layout)
        return group

    def create_export_evaluation_group(self):
        group = QGroupBox("Export evaluation result as a CSV File")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Choose a folder where you want to save the XML Evaluation"))
        
        # Elements
        self.folder_csv_input = QLineEdit()
        self.csv_save_as_button = QPushButton("Save as")
        self.csv_covert_button = QPushButton("Convert")
        
        export_layout = QHBoxLayout()
        export_layout.addWidget(self.folder_csv_input)
        export_layout.addWidget(self.csv_save_as_button)
        export_layout.addWidget(self.csv_covert_button)
        layout.addLayout(export_layout)

        group.setLayout(layout)
        return group

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
        self.progressbar.setTextVisible(True)
        
        layout.addWidget(self.xml_output)
        
        progress_layout = QHBoxLayout()
        #progress_layout.addWidget(QLabel("0%"))
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

        layout.addWidget(QLabel("Choose where to save output of CSV file"))
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLineEdit())
        output_layout.addWidget(QPushButton("Save as"))
        output_layout.addWidget(QPushButton("Convert"))
        layout.addLayout(output_layout)

        layout.addWidget(QCheckBox("Write Index Column?"))

        # Add logo (placeholder)
        logo_label = QLabel()
        pixmap = QPixmap("_internal/images/logo.png")  # Replace with actual path
        logo_label.setPixmap(pixmap)
        layout.addWidget(logo_label)

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
    apply_stylesheet(app, theme='dark_amber.xml')
    window.show()
    sys.exit(app.exec())
