import PySimpleGUI as sg
import numpy as np
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET
from logging.handlers import RotatingFileHandler
import logging
import csv

# Create a rotating file handler
# file_handler = RotatingFileHandler(filename="Log.log",
#                                    maxBytes=25 * 1024 * 1024,  # Max File Size: 25 MB
#                                    backupCount=2,  # Number of backup files to keep
#                                    encoding="utf-8",  # Specify the encoding if needed
#                                    delay=False)  # Set to True if you want to delay file opening
# Define the log format
# formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s",
#                               datefmt="Date: %d-%m-%Y Time: %H:%M:%S")
#  Set the formatter for the file handler
# file_handler.setFormatter(formatter)
# 
# # Create a logger and add the file handler
# logger = logging.getLogger()
# logger.addHandler(file_handler)
# logger.setLevel(logging.INFO)  # Set the desired log level

# Mapping file extensions to corresponding read and write functions

CONVERSION_FUNCTIONS = {
     # XML Conversion
    ("xml", "html"): (pd.read_xml, pd.DataFrame.to_html),
    ("xml", "csv"): (pd.read_xml, pd.DataFrame.to_csv),
    ("xml", "json"): (pd.read_xml, pd.DataFrame.to_json),
    ("xml", "xlsx"): (pd.read_xml, pd.DataFrame.to_excel),
    ("xml", "md"): (pd.read_xml, pd.DataFrame.to_markdown),
}

# Function declaration

# Generic conversion function
def convert_files(input_file, output_file, input_ext, output_ext):
    try:
        read_func, write_func = CONVERSION_FUNCTIONS.get((input_ext, output_ext), (None, None))
        
        if read_func is None or write_func is None:
            window["-OUTPUT_WINDOW-"].update("Unsupported conversion!", text_color="#ff4545")
            return
    
        df = read_func(input_file)
        write_func(df, output_file)
        window["-OUTPUT_WINDOW-"].update(f"Successfully converted {Path(input_file).stem} {input_ext.upper()} to {Path(output_file).stem} {output_ext.upper()}", text_color="#51e98b")

    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].update(f"{input_ext.upper()} File not found!", text_color="#ff4545")
    except Exception as e:
        window["-OUTPUT_WINDOW-"].update(f"ERROR: {e}", text_color="#ff4545")
        
def get_attributes(root, tag):
    attributes = []
    for elem in root.iter(tag):
        attributes.extend(elem.attrib.keys())
    return set(attributes)

def xml_parser(file):
    # Parse XML file
    tree = ET.parse(file)
    root = tree.getroot()

    xml_string = ET.tostring(root).decode("UTF-8")
    window["-OUTPUT_WINDOW-"].update(xml_string)
    
    # Get tags in XML File:
    tags_xml = [elem.tag for elem in root.iter()]
    tags_to_set = set(tags_xml)
    tags_to_list = list(tags_to_set)
    
    # Add Elements to ComboBox List
    window["-XML_TAG_NAME-"].update(values=tags_to_list)

# Graphical User Interface settings #

# Add your new theme colors and settings
my_new_theme = {"BACKGROUND": "#22333e",
                "TEXT": "#ffffff",
                "INPUT": "#1c1e23",
                "TEXT_INPUT": "#d2d2d3",
                "SCROLL": "#1c1e23",
                "BUTTON": ("#11b893", "#313641"),
                "PROGRESS": ("#11b893", "#4a6ab3"),
                "BORDER": 1,
                "SLIDER_DEPTH": 0,
                "PROGRESS_DEPTH": 0}
# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new("MyYellow", my_new_theme)

# Switch your theme to use the newly added one. You can add spaces to make it more readable
sg.theme("MyYellow")
font = ("Arial", 14)

# Graphical User Interface layout #
MENU_RIGHT_CLICK = ["",["Clear Output", "Version", "Exit"]]
FILE_TYPES = (("CSV (Comma Seperated Value)",".csv"), ("XLSX (Excel Sheet)",".xlsx"), ("JSON (JavaScript Object Notation)",".json"),("HTML (Hypertext Markup Language)",".html"))
FILE_TYPE_XML = (('XML (Extensible Markup Language)', '.xml'),)
tag_name = []
attribute_name = []

layout_xml_export = [[sg.Text("Select XML File that you want to read:",text_color="#11b893")],
                    [sg.Text("File:  "),sg.Input(size=(43,1),key="-FILE_EXPORT_INPUT-"),sg.FileBrowse(button_text="Choose",file_types=FILE_TYPE_XML),sg.Button("Read",key="-READ_BUTTON_EXPORT-")],
                    [sg.Text("Export XML File to a different filetype:",text_color="#11b893")],
                    [sg.Text("Output:"),sg.Input(size=(42,1),key="-FILE_EXPORT_OUTPUT-"),sg.FileSaveAs(button_text="Save as",file_types=FILE_TYPES,target="-FILE_EXPORT_OUTPUT-",key="-SAVE_AS_BUTTON_EXPORT-"),sg.Button("Export",key="-EXPORT-")]]

layout_xml_eval = [[sg.Text("Multi-XML Files Iteration in a Folder:",text_color="#11b893")],
                    [sg.Text("Path:"),sg.Input(size=(43,1),key="-FOLDER_EVALUATION_INPUT-"),sg.FolderBrowse(button_text="Browse Folder",target="-FOLDER_EVALUATION_INPUT-"),sg.Button("Read",key="-READ_BUTTON_EVALUATION-")],
                    [sg.Text("Filtering Options for XML Evaluation:",text_color="#11b893")],
                    [sg.Text("Tag:"),sg.Combo(tag_name,size=(10,1),key="-XML_TAG_NAME-", enable_events=True),sg.Text("Tag Value:"),sg.Input(size=(10,1),key="-XML_TAG_VALUE-")],
                    [sg.Text("Att:  "),sg.Combo(attribute_name,size=(10,1),key="-XML_ATTRIBUTE_NAME-"),sg.Text("Att Value:  "),sg.Input(size=(10,1),key="-XML_ATTRIBUTE_VALUE-")],
                    [sg.Text("Export Evaluation as CSV File:",text_color="#11b893")],
                    [sg.Text("Path:"),sg.Input(size=(43,1),key="-FOLDER_EVALUATION_OUTPUT-"),sg.FolderBrowse(button_text="Browse Folder",target="-FOLDER_EVALUATION_OUTPUT-"),sg.Button("Export")]]

layout_title =  [[sg.Text("XMLuvation",font=("Arial 24 bold"),text_color="#11b893",pad=10, justification="center")]]

layout_output = [[sg.Multiline(size=(80,18),key="-OUTPUT_WINDOW-")]]

layout = [[sg.Column(layout_title,justification="center")],
          [sg.Frame("XML Export as Specific Filetype", layout_xml_export,expand_x=True)],
          [sg.Frame("XML Evaluation and Filtering",layout_xml_eval,expand_x=True)],
          [sg.Frame("Program Output", layout_output,expand_x=True)]]

window = sg.Window("XMLuvation - by Jovan",layout,font=font, finalize=True,right_click_menu=MENU_RIGHT_CLICK)

# Main Window events and functionality #
while True:
    event,values = window.read()
    
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    
    # VARIABLES #
    input_path = values["-FILE_EXPORT_INPUT-"]
    output_path = values["-FILE_EXPORT_OUTPUT-"]
    input_file_extension = Path(input_path).stem
    output_file_extension = Path(output_path).stem

    if event == "-READ_BUTTON_EXPORT-":
        if len(input_path) == 0 or not input_path.endswith(".xml"):
            window["-OUTPUT_WINDOW-"].update("Error, no Input File selected or wrong filetype")
        else:
            window.perform_long_operation(lambda: xml_parser(input_path),"-OUTPUT_WINDOW-")
            
    if event == "-EXPORT-":
        if len(values["-FILE_EXPORT_OUTPUT-"]) == 0:
            window["-OUTPUT_WINDOW-"].print("Path to save is empty")
        elif not values["-FILE_EXPORT_OUTPUT-"].endswith(".csv"):
            window["-OUTPUT_WINDOW-"].print("Wrong filetype to save as")
        else:
            window.perform_long_operation(lambda: convert_files(input_path, output_path, input_file_extension, output_file_extension),"-OUTPUT_WINDOW-")
        
    if event == "Clear Output":
        window["-OUTPUT_WINDOW-"].update("")
    if event == "Version":
            sg.popup_scrolled(sg.get_versions())
            
window.close() # Kill program