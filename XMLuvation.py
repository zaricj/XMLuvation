import PySimpleGUI as sg
import logging
import numpy as np
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET
from logging.handlers import RotatingFileHandler

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
        
def xml_parser(file):

    tree = ET.parse(file)
    root = tree.getroot()

    xml_string = ET.tostring(root).decode("UTF-8")
    window["-OUTPUT_WINDOW-"].update(xml_string)
    
    # Get elements in XML File:
    tags_xml = [elem.tag for elem in root.iter()]
    tags_to_set = set(tags_xml)
    tags_to_list = list(tags_to_set)
    
    # Add Elements to ComboBox List
    window["-ELEMENT_NAME_INPUT-"].update(values=tags_to_list)
    window["-DEL_ELEMENT_NAME_INPUT-"].update(values=tags_to_list)
    
def xml_add_attribute(file,element_name,attribute_name,attribute_value):
    
    tree = ET.parse(file)
    root = tree.getroot()

   # Add attribute to specified Element
    for element in tree.findall(element_name):
        element.set(attribute_name,attribute_value)
        
        if attribute_name == "id":
            window.refresh()
            window["-ATTRIBUTE_VALUE_INPUT-"].update(1)
            id = 1
            for element in tree.findall(element_name):
                element.set("id",str(id))
                id += 1
        else:
            pass
        
    tree.write(file)

def xml_delete_attribute(file,element_name,attribute_name):
    
    tree = ET.parse(file)
    root = tree.getroot()
    
    for element in tree.findall(element_name):
        del(element.attrib[attribute_name])
    
    tree.write(file)
    window["-DEL_ELEMENT_NAME_INPUT-"].update("")
    window["-DEL_ATTRIBUTE_NAME_INPUT-"]
    
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
element_name_in_xml = []

layout_add_attributes = [[sg.Text("Adding Attributes to XML:",text_color="#11b893")],
                         [sg.Text("Attribute:"),sg.Input(size=(15,1),key="-ATTRIBUTE_NAME_INPUT-"),sg.Text("to element:"),sg.Combo(element_name_in_xml,size=(15,1),key="-ELEMENT_NAME_INPUT-",readonly=True, auto_size_text=False),sg.Text("with value:"),sg.Input(size=(15,1),key="-ATTRIBUTE_VALUE_INPUT-"),sg.Button("Add",key="-ADD_ATTRIBUTE_BUTTON-")]]

layout_delete_attributes = [[sg.Text("Deleting Attributes from XML:",text_color="#11b893")],
                            [sg.Text("Attribute:"),sg.Input(size=(15,1),key="-DEL_ATTRIBUTE_NAME_INPUT-"),sg.Text("from element:"),sg.Combo(element_name_in_xml,size=(15,1),key="-DEL_ELEMENT_NAME_INPUT-", readonly=True, auto_size_text=False),sg.Button("Delete",key="-DELETE_ATTRIBUTE_BUTTON-")]]

main_tab_layout =  [[sg.Text("XML Data Parser",font=("Arial 24 bold underline"),text_color="#11b893", pad=10, justification="center")],
                    [sg.Text("Select a XML File:",text_color="#11b893")],
                    [sg.Input(size=(43,1),key="-FILE_INPUT_TAB1-"),sg.FileBrowse(button_text="Choose",file_types=FILE_TYPE_XML),sg.Button("Read",key="-READ_FILE-")],
                    [sg.Checkbox(text="Show Add Attributes",default=False,key="-CHECKBOX_ADD_ATTRIBUTES-",enable_events=True),sg.Checkbox(text="Show Delete Attributes",default=False,key="-CHECKBOX_DELETE_ATTRIBUTES-", enable_events=True)],
                    [sg.pin(sg.Column(layout_add_attributes,key="-ADD_ATTRIBUTES_COLUMN-",visible=False))],
                    [sg.pin(sg.Column(layout_delete_attributes,key="-DELETE_ATTRIBUTES_COLUMN-",visible=False))],
                    [sg.Text("Conversion", font=("Arial 18 bold"),text_color="#11b893", pad=10)],
                    [sg.Text("Convert XML file selected filetype:",text_color="#11b893")],
                    [sg.Input(size=(42,1),key="-FILE_OUTPUT_TAB1-"),sg.FileSaveAs(button_text="Save as",file_types=FILE_TYPES,target="-FILE_OUTPUT_TAB1-",key="-SAVE_AS_BUTTON-"),sg.Button("Convert",key="-CONVERT-")]]

other_tab_layout = [[sg.Text("XML Data Parser",font="Arial 24 bold underline",text_color="#11b893",pad=10)],
                    [sg.Text("Select a Folder for XML Batch Evaluation",text_color="#11b893")],
                    [sg.Input(size=(43,1),key="-FOLDER_INPUT-"),sg.FolderBrowse(target="-FOLDER_INPUT-")],
                    [sg.Text("Filtering", font=("Arial 18 bold"),text_color="#11b893",pad=10)],
                    [sg.Text("XML Filter Options for Evaluation:",text_color="#11b893")],
                    [sg.Text("Attribute:"),sg.Input(size=(15,1),key="-ATTRIBUTE-"),sg.Text("Element:"),sg.Combo(element_name_in_xml,size=(15,1),key="-ELEMENT-",readonly=True, auto_size_text=False)],
                    [sg.Text("Save Evaluation", font=("Arial 18 bold"),text_color="#11b893",pad=10)],
                    [sg.Text("Select a folder where to save the evaluation (Evaluations are saved as CSV Files):",text_color="#11b893")],
                    [sg.Input(size=(42,1),key="-FILE_OUTPUT_TAB2-"),sg.FolderBrowse(target="-FOLDER_INPUT_TAB2-"),sg.Button("Save",key="-SAVE_EVALUATION-")]]

layout_output = [[sg.Multiline(size=(82,18),key="-OUTPUT_WINDOW-")]]

layout = [[sg.TabGroup([[sg.Tab('Convert and Manipulate', main_tab_layout), sg.Tab('Batch Evaluation', other_tab_layout)]], selected_title_color="#11b893",expand_x=True)],    
          [sg.Frame("Program Output",layout_output)]]    

window = sg.Window("XMLuvation - by Jovan",layout,font=font, finalize=True,right_click_menu=MENU_RIGHT_CLICK)

# Main Window events and functionality #
while True:
    event,values = window.read()
    
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    
    # VARIABLES #
    input_path_tab1 = values["-FILE_INPUT_TAB1-"]
    output_path_tab1 = values["-FILE_OUTPUT_TAB1-"]
    input_file_extension = Path(input_path_tab1).stem
    output_file_extension = Path(output_path_tab1).stem
    output_path_tab2 = values["-FILE_OUTPUT_TAB2-"]
    element_name = values["-ELEMENT_NAME_INPUT-"]
    del_element_name = values["-DEL_ELEMENT_NAME_INPUT-"]
    del_attribute_name = values["-DEL_ATTRIBUTE_NAME_INPUT-"]
    attribute_name = values["-ATTRIBUTE_NAME_INPUT-"]
    attribute_value = values["-ATTRIBUTE_VALUE_INPUT-"]# 

# CheckBox Visiblity Option
    if event == "-CHECKBOX_ADD_ATTRIBUTES-":
        if values["-CHECKBOX_ADD_ATTRIBUTES-"]:
            window["-ADD_ATTRIBUTES_COLUMN-"].update(visible=True)
        else:
            window["-ADD_ATTRIBUTES_COLUMN-"].update(visible=False)
            
    if event == "-CHECKBOX_DELETE_ATTRIBUTES-":
        if values["-CHECKBOX_DELETE_ATTRIBUTES-"]:
            window["-DELETE_ATTRIBUTES_COLUMN-"].update(visible=True)
        else:
            window["-DELETE_ATTRIBUTES_COLUMN-"].update(visible=False)
            
    if event == "-CHECKBOX_FOLDER_INPUT-":
        if values["-CHECKBOX_FOLDER_INPUT-"]:
            window["-FOLDER_INPUT_COLUMN-"].update(visible=True)
        else:
            window["-FOLDER_INPUT_COLUMN-"].update(visible=False)

    if event == "-READ_FILE-":
        if len(input_path_tab1) == 0 or not input_path_tab1.endswith(".xml"):
            window["-OUTPUT_WINDOW-"].update("Error, no Input File selected or wrong filetype")
        else:
            window.perform_long_operation(lambda: xml_parser(input_path_tab1),"-OUTPUT_WINDOW-")
        
    if event == "-ADD_ATTRIBUTE_BUTTON-":
        if len(input_path_tab1) == 0 or not input_path_tab1.endswith(".xml"):
            window["-OUTPUT_WINDOW-"].update("Error, no Input File selected or wrong filetype")
        else:
            window.perform_long_operation(lambda: xml_add_attribute(input_path_tab1,element_name,attribute_name,attribute_value),"-OUTPUT_WINDOW-")
    if event =="-DELETE_ATTRIBUTE_BUTTON-":
        if len(input_path_tab1) == 0 or not input_path_tab1.endswith(".xml"):
            window["-OUTPUT_WINDOW-"].update("Empty Inputs, can't delete Attribute.")
        else:
            window.perform_long_operation(lambda: xml_delete_attribute(input_path_tab1,del_element_name,del_attribute_name),"-OUTPUT_WINDOW-")
            
    if event == "-CONVERT-":
        if len(values["-FILE_OUTPUT-"]) == 0:
            window["-OUTPUT_WINDOW-"].print("Path to save is empty")
        elif not values["-FILE_OUTPUT-"].endswith(".csv"):
            window["-OUTPUT_WINDOW-"].print("Wrong filetype to save as")
        else:
            window.perform_long_operation(lambda: convert_files(input_path_tab1, output_path_tab1, input_file_extension, output_file_extension),"-OUTPUT_WINDOW-")
        
    if event == "Clear Output":
        window["-OUTPUT_WINDOW-"].update("")
    if event == "Version":
            sg.popup_scrolled(sg.get_versions())
            
window.close() # Kill program