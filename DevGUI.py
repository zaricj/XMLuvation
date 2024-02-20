import PySimpleGUI as sg
import numpy as np
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET
from logging.handlers import RotatingFileHandler
import logging
import csv
import random

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
LightTheme = {
'BACKGROUND': '#081705', 
'TEXT': '#FFFFFF', 
'INPUT': '#00303a', 
'TEXT_INPUT': '#ffffff',
'SCROLL': '#689F38',
'BUTTON': ('#212121', '#006699'),
'PROGRESS': ('#4CAF50', '#81C784'),
'BORDER': 0,
'SLIDER_DEPTH': 1,
'PROGRESS_DEPTH': 0}

# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new("LightTheme", LightTheme)

# Switch your theme to use the newly added one. You can add spaces to make it more readable
sg.theme("SystemDefault")
font = ("Arial", 10)

# Graphical User Interface layout #
MENU_RIGHT_CLICK = ["",["Clear Output", "Version", "Exit"]]
FILE_TYPES = (("CSV (Comma Seperated Value)",".csv"), ("XLSX (Excel Sheet)",".xlsx"), ("JSON (JavaScript Object Notation)",".json"),("HTML (Hypertext Markup Language)",".html"))
FILE_TYPE_XML = (('XML (Extensible Markup Language)', '.xml'),)
tag_name = []
attribute_name = []

layout_title =  [[sg.Text("XMLuvation",font=("Arial 24 bold"),pad=10, justification="center")]]

layout_xml_export = [[sg.Text("Select XML File that you want to read:")],
                    [sg.Input(size=(41,2),font="Arial 8",key="-FILE_EXPORT_INPUT-"),sg.FileBrowse(button_text="Choose",file_types=FILE_TYPE_XML),sg.Button("Read",key="-READ_BUTTON_EXPORT-")],
                    [sg.Text("Export XML File to a different filetype:")],
                    [sg.Input(size=(41,2),font="Arial 8",key="-FILE_EXPORT_OUTPUT-"),sg.FileSaveAs(button_text="Save as",file_types=FILE_TYPES,target="-FILE_EXPORT_OUTPUT-",key="-SAVE_AS_BUTTON_EXPORT-"),sg.Button("Export",key="-EXPORT-")]]

layout_xml_eval = [[sg.Text("Multi-XML Files Iteration in a Folder:")],
                    [sg.Input(size=(35,2),font="Arial 8",key="-FOLDER_EVALUATION_INPUT-"),sg.FolderBrowse(button_text="Browse Folder",target="-FOLDER_EVALUATION_INPUT-"),sg.Button("Read",key="-READ_BUTTON_EVALUATION-")],
                    [sg.Text("Filtering Options for XML Evaluation:")],
                    [sg.Text("Tag name:"),sg.Combo(tag_name,size=(14,1),auto_size_text=False,key="-XML_TAG_NAME-"),sg.Text("Tag Value:"),sg.Input(size=(14,1),key="-XML_TAG_VALUE-")],
                    [sg.Text("Att name: "),sg.Combo(attribute_name,size=(14,1),auto_size_text=False,key="-XML_ATTRIBUTE_NAME-"),sg.Text("Att Value:  "),sg.Input(size=(14,1),key="-XML_ATTRIBUTE_VALUE-")],
                    [sg.Text("Export Evaluation as CSV File:")],
                    [sg.Input(size=(35,2),font="Arial 8",key="-FOLDER_EVALUATION_OUTPUT-"),sg.FolderBrowse(button_text="Browse Folder",target="-FOLDER_EVALUATION_OUTPUT-"),sg.Button("Export")]]

layout_output = [[sg.Multiline(size=(60,21),write_only=False,key="-OUTPUT_WINDOW-")]]

frame_xml_export = sg.Frame("XML Export as Specific Filetype", layout_xml_export, expand_x=True)
frame_xml_eval = sg.Frame("XML Evaluation and Filtering", layout_xml_eval, expand_x=True)
frame_output = sg.Frame("Program Output", layout_output, expand_x=True)

layout = [
    [
        sg.Column([[frame_xml_export], [frame_xml_eval]], expand_y=True),
        sg.Column([[frame_output]], expand_y=True)
    ]
]

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
    
    if event == "-XML_TAG_NAME-":
            selected_tag = values["-XML_TAG_NAME-"]
            attributes_xml = get_attributes(selected_tag)
            window["-ATTRIBUTES-"].update(values=attributes_xml)
            
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