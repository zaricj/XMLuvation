import PySimpleGUI as sg
from lxml import etree as ET
from logging.handlers import RotatingFileHandler
import logging
import csv
import os
import re

# Create a rotating file handler
file_handler = RotatingFileHandler(filename="XML_Evaluation.log",
                                   maxBytes=50 * 1024 * 1024,  # Max File Size: 50 MB
                                   backupCount=2,  # Number of backup files to keep
                                   encoding="utf-8",  # Specify the encoding if needed
                                   delay=False)  # Set to True if you want to delay file opening

# Define the log format
formatter = logging.Formatter("%(name)s %(levelname)s %(message)s")
# Set the formatter for the file handler
file_handler.setFormatter(formatter)

# Create a logger and add the file handler
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)  # Set the desired log level

xml_32px = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAA8pJREFUWIXtVl1oHFUYPefOJpNkQ9omJps11mIZKkiTaQmEarMtguKDL4ot9adCQUVU0pBSRRBEpSiJUKlYxPTnrVUEhT5UCaKYbkqlVM0mNBTZaoNtuhuX/Ehbd5LZ+/mw2dnZNWm6NIhgztOd+X7OuWcu9xtgGcv4v4NL0eRcK8qaKu2dBNYpxWjDqcGv/lUByYj9KsgeABCRTIXo+pUDw5O3UquWQgCInfklRm+VfEkEJLY0NwNsyYuR46XU374Dwme8pYhkkClJQGCxhFSbVeOWBzug8ApEv9QYHT7hEQIcB5/KPZP4WURVJiN2UoscV4bbHeofSdys/4KHcHKrvdIRdkKkk+SqLKEcaTwVez6XM9a+fquhAt97gjJ6rxCzSqkD2RfylwZ6DTjdDdELV+fj+ccnmGpvXpVst99xNC4ReCtHDgDQ+M2fazDgtz9jiPGpoVQ8vz1WKrJTYF5MROwDfzxw750LOjC16b5apyywR8AOkjUFWSITEBy8YUy9e0//aBoAfrEssyYcvOoJFPk2FI09JIAxHmnpEuEeKoYL20haAYfSs+i++4fYFU/AxP0b18wE9E8kawsL9BUl2C+G2xvqH7nmjyU224/T4JeeORn9XPj00FGv1rLMVDi4KwPsJWkVbSgNyGOh6FBfAADcgPswadTm4+JQpCs14R5ZPzIyU2zbnHd++9Nm+toXBeF43EEcnwhwKLHZ3qYMfASwPhtkhRZ5BECfAgABfy8oJk1QvVFfV9aZarMKPweAida1K0g8mt8RTtb++Ot0cd7ngJGItGynwuseeY5DMAXMHcKG6NA3FP0mIPkbjGgC2eOa1aPJSMu+sXbLa+BUVW8DWeETcMzfXCzLTETsF7dE7AuK6jOSG/NBcbToXk64+7M0PlxsXbsiWFW9G2BXwenPklwH9BOh6FBfItLyHakenAtMTo9dD6+Lxx0ASG2ymzLlOANwdUG5iAPgaBnc9+qi5z3H570HUm1WjTaDuwXogv9giv5gxpH95aa6BNIAAK3lcHgg9kIuJdm+4WUoHPQRp5XIYWdGulefHb5czDXvTXjH2fifAPal2qwPdUWwQwRdIOsgiuUmngRheA2K7adMEwREbmiRXoMzPQ0D819CCzownyOzZtV2pdyT1OVfC7FhbneXP47G1rwN6FzuudbWsrsq3V2SkRPhM0Pji/Uu6X8gO/mMGOfqROP9xoHB10rpUYzSpqFWT9MnmjJ77GbpSy8AaMstRDAYOn0+drsCFh3HfhhaPSvQO7SirhKUNPeXsYz/LP4Gk8OElv5Vn3MAAAAASUVORK5CYII='

def parse_XML(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        xml_string = ET.tostring(root).decode("UTF-8") # Converts the read xml file to a string
        window["-OUTPUT_WINDOW-"].update(xml_string) # Prints the xml file in the ouput window
        # Get tags in XML File:
        tags_xml = [element.tag for element in root.iter()]
        # Add Elements to ComboBox List
        window["-XML_TAG_NAME-"].update(values=tags_xml)
    except Exception as e:
        print(e)

def get_tag_values(xml_file, tag):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    tag_value = []
    for element in root.iter(tag): # Add Parameter in Function later for root.iter(parameter)
        tag_value.append(element.text)
    return tag_value

def get_attributes(xml_file, tag):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    attributes = []
    for element in root.iter(tag):
        attributes.extend(element.attrib.keys())
    return list(set(attributes))

def get_attribute_values(xml_file, tag, attribute):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    attribute_value_list = []
    for element in root.iter(tag):
        attribute_value = element.attrib.get(attribute)
        if attribute_value is not None:
            attribute_value_list.append(attribute_value)
    return list(set(attribute_value_list))

def return_matching_expression(xml_file, xpath_expression):
    """
    Parses an XML file based on the provided filters.

    Args:
        xml_file (str): Path to the XML file.
        filters (dict): Dictionary containing the filtering criteria.

    Returns:
        bool: True if the file matches the filters, False otherwise.
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        matching_fields = root.findall(xpath_expression)

        return matching_fields
    except Exception as e:
        window["-OUTPUT_WINDOW_XPATH-"].update(f"Error: {e}")

def build_query(folder_path, xpath_expression, filter_values, log_file):
    """
    Iterates over all XML files in a folder, uses the given XPath expression
    to find matching elements, and exports information about them to a rotating log file.

    Args:
        folder_path (str): Path to the folder containing XML files.
        xpath_expression (str): XPath expression to find matching elements.
        filter_values (dict, optional): Dictionary containing additional filter values to log:
            - "TagName": XPATH for tag name (string or list of strings)
            - "TagValue": XPATH for tag value (string or list of strings)
            - "AttributeName": XPATH for attribute name (string or list of strings)
            - "AttributeValue": XPATH for attribute value (string or list of strings)
        log_file (str, optional): Path to the rotating log file.
    """

    # Configure logging setup (outside the function for efficiency)

    # Ensure log_file is provided
    if not log_file:
        raise ValueError("Error: Missing required argument 'log_file'")

    # Set up logging with rotating file handler
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Adjust logging level as needed

    handler = RotatingFileHandler(
        filename=log_file, maxBytes=50 * 1024 * 1024, backupCount=2, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    try:
        # Calculate the total number of files for progress calculation
        total_files = sum(1 for filename in os.listdir(folder_path) if filename.endswith('.xml'))
        progress_increment = 100 / total_files
        current_progress = 0

        # Update the progress bar (consider replacing with a custom solution if needed)
         # Calculate the total number of files for progress calculation
        total_files = sum(1 for filename in os.listdir(folder_path) if filename.endswith('.xml'))
        progress_increment = 100 / total_files
        current_progress = 0
        
        # Update the progress bar before starting the loop
        window['-PROGRESS_BAR-'].update(current_progress)

        # Ensure consistent data type for filter values
        filter_values = filter_values or {}
        for key, value in filter_values.items():
            if isinstance(value, (list, tuple)):
                filter_values[key] = list(value)
            else:
                filter_values[key] = [value]

        for filename in os.listdir(folder_path):
            if filename.endswith('.xml'):
                full_path = os.path.join(folder_path, filename)
                try:
                    matching_elements = return_matching_expression(full_path, xpath_expression)

                    if matching_elements:
                        for element in matching_elements:
                            log_message = f"File: {filename}\n"
                            log_message += f"Tag Name: {element.tag}\n"
                            log_message += f"Tag Value: {element.text}\n"
                            
                            # Log all attributes and their values
                            for attr_name, attr_value in element.attrib.items():
                                log_message += f"Attribute Name: {attr_name}, Attribute Value: {attr_value}\n"

                            # Add filter information if provided (not used for matching)
                            for key, value in filter_values.items():
                                log_message += f"{key}: {value}\n"  # No filtering, just logging

                            logger.info(log_message)
                            # Progress update
                            current_progress += progress_increment
                            window['-PROGRESS_BAR-'].update(current_progress)
                except Exception as e:
                    window["-OUTPUT_WINDOW_XPATH-"].update(f"Error: element.xpath = {e}")            
                    
            # Remove commented-out progress update lines if not needed
            window["-OUTPUT_WINDOW_XPATH-"].update(f"Information about matching elements logged to '{log_file}'")

    except FileNotFoundError as e:
        window["-OUTPUT_WINDOW_XPATH-"].update(f"Error: File not found: '{log_file}'")
    except PermissionError as e:
        window["-OUTPUT_WINDOW_XPATH-"].update(f"Error: Insufficient permissions to write to '{log_file}'")


my_new_theme = {'BACKGROUND': '#2d3039', 
        'TEXT': 'white', 
        'INPUT': '#535360', 
        'TEXT_INPUT': 'white', 
        'SCROLL': '#333', 
        'BUTTON': ('#f74d50', '#626271'), 
        'PROGRESS': ('#49cda6', '#144939'), 
        'BORDER': 2, 
        'SLIDER_DEPTH': 1, 
        'PROGRESS_DEPTH': 1, }

# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new("MyTheme", my_new_theme)

sg.theme("MyTheme")
font = ("Arial", 12)

FILE_TYPE_XML = (('XML (Extensible Markup Language)', '.xml'),)
MENU_RIGHT_CLICK_DELETE = ["&Right", ["&Delete", "&Delete All"]]
tag_name = []
tag_value = []
attribute_name = []
attribute_value = []
filters_log = []
additional_data = []

layout_xml_eval = [[sg.Text("Multi-XML Files Iteration in a Folder:", pad=5)],
                    [sg.Input(size=(36,2), font="Arial 10", expand_x=True, key="-FOLDER_EVALUATION_INPUT-"),sg.FolderBrowse(button_text="Browse Folder",target="-FOLDER_EVALUATION_INPUT-"),sg.Button("Read XML",key="-READ_XML-")],
                    [sg.Text("Filtering Options for XML Evaluation and XPath Expression:", pad=5)],
                    [sg.Text("Tag name:"),sg.Combo(tag_name, size=(14,1), disabled=True, auto_size_text=False, enable_events=True, enable_per_char_events=True, expand_x=True, key="-XML_TAG_NAME-"),sg.Text("Tag Value:"),sg.Combo(tag_value, size=(14,1), disabled=True, enable_events=True, enable_per_char_events=True, auto_size_text=False, expand_x=True, key="-XML_TAG_VALUE-")],
                    [sg.Text("Att name:  "),sg.Combo(attribute_name, size=(14,1), disabled=True, auto_size_text=False, enable_events=True, expand_x=True, key="-XML_ATTRIBUTE_NAME-"),sg.Text("Att Value:  "),sg.Combo(attribute_value, size=(14,1), disabled=True, enable_events=True, auto_size_text=False, expand_x=True, key="-XML_ATTRIBUTE_VALUE-", pad=10)],
                    [sg.Text("Build XPath Expression:"),sg.Input(size=(14,1), expand_x=True, key="-XPATH_EXPRESSION-"),sg.Button("Build XPath",key="-XPATH_BUILD-",pad=10)],
                    [sg.Text("Add Elements/Attributes to Log File as Xpath Expression (not used for matching):")],
                    [sg.Text("Tag name:"),sg.Input(size=(14,1), enable_events=True, expand_x=True, key="-XPATH_TAG_NAME-"),sg.Text("Tag Value:"),sg.Input( size=(14,1), enable_events=True, expand_x=True, key="-XPATH_TAG_VALUE-")],
                    [sg.Text("Att name:  "),sg.Input(size=(14,1), enable_events=True,expand_x=True, key="-XPATH_ATTRIBUTE_NAME-"),sg.Text("Att Value:  "),sg.Input(size=(14,1), enable_events=True, expand_x=True, key="-XPATH_ATTRIBUTE_VALUE-", pad=10)],
                    [sg.Text("Export Evaluation Log as a CSV File:")],
                    [sg.Input(size=(36,2),font="Arial 10",key="-FOLDER_EVALUATION_OUTPUT-",expand_x=True),sg.SaveAs(button_text="Save as", file_types=(("Logging File (.log)",".log"),), target="-FOLDER_EVALUATION_OUTPUT-"),sg.Button("Export", key="-EXPORT_AS_CSV-")]]

layout_output = [[sg.Multiline(size=(64,33), write_only=False, horizontal_scroll=True, key="-OUTPUT_WINDOW-")],
                 [sg.Text("Progress: "),sg.ProgressBar(100, orientation='h', size=(20, 20), key='-PROGRESS_BAR-',expand_x=True)]]

layout_xpath_output = [[sg.Multiline(size=(60,11),key="-OUTPUT_WINDOW_XPATH-")]]

frame_xml_eval = sg.Frame("XML Evaluation and Filtering", layout_xml_eval, expand_x=True)
frame_output = sg.Frame("XML Output", layout_output, expand_x=True)
frame_xpath_output = sg.Frame("Program Output",layout_xpath_output)

layout = [
    [
        sg.Column([[frame_xml_eval],[frame_xpath_output]], expand_y=True),
        sg.Column([[frame_output]], expand_y=True)
    ]
]

window = sg.Window("XMLuvation - by Jovan", layout, font=font, finalize=True, icon=xml_32px)

while True:
    event,values = window.read()
    
    if event == sg.WIN_CLOSED or event == "Exit":
        break

        # Values #
    eval_input_folder = values["-FOLDER_EVALUATION_INPUT-"]
    eval_output_folder = values["-FOLDER_EVALUATION_OUTPUT-"]
    tag_name_combo = values["-XML_TAG_NAME-"]
    tag_value_combo = values["-XML_TAG_VALUE-"]
    attribute_name_combo = values["-XML_ATTRIBUTE_NAME-"]
    attribute_value_combo = values["-XML_ATTRIBUTE_VALUE-"]
    
    xpath_expression_input = values["-XPATH_EXPRESSION-"]

    # RegEx Matching
    file_path_regex = r'\.xml$'
        
    if event == "-READ_XML-":
        parsed_xml_file = sg.popup_get_file("Select an XML file", file_types=(("XML Files", "*.xml"),))
        if parsed_xml_file:
            window.perform_long_operation(lambda: parse_XML(parsed_xml_file),"-OUTPUT_WINDOW-")
            window["-XML_TAG_VALUE-"].update(values="")
            window["-XML_ATTRIBUTE_NAME-"].update(values="")
            window["-XML_ATTRIBUTE_VALUE-"].update(values="")

            if re.search(file_path_regex, parsed_xml_file):
                window["-XML_TAG_NAME-"].update(disabled=False)
                window["-XML_TAG_VALUE-"].update(disabled=False)
                tag_name = values["-XML_TAG_NAME-"]
                window["-XML_TAG_NAME-"].update(values=tag_name)

                for tag in tag_name:
                    tag_value_list = get_tag_values(parsed_xml_file, tag)
                    window["-XML_TAG_VALUE-"].update(disabled=False, values=tag_value_list)
                    attribute_name_list = get_attributes(parsed_xml_file, tag)
                    window["-XML_ATTRIBUTE_NAME-"].update(values=attribute_name_list)
                    for attribute_name in attribute_name_list:
                        attribute_value_list = get_attribute_values(parsed_xml_file, tag, attribute_name)
                        window["-XML_ATTRIBUTE_VALUE-"].update(values=attribute_value_list)
                        break  # Only need to get attributes and values for the first tag
    
    elif event == "-XPATH_BUILD-":
        try:
            # Basic XPath expression based on the tag name
            xpath_expression = ""

            if not tag_name_combo:
                window["-OUTPUT_WINDOW_XPATH-"].update("No tag selected.")
            else:
                xpath_expression += f".//{tag_name_combo}"
                # Check if tag value is provided
                if tag_value_combo:
                    xpath_expression += f"[text()='{tag_value_combo}']"
                # Check if attribute name is provided
                if attribute_name_combo:
                    # Check if attribute value is provided
                    if attribute_value_combo:
                        xpath_expression += f"[@{attribute_name_combo}='{attribute_value_combo}']"
                    else:
                        window["-OUTPUT_WINDOW_XPATH-"].update("No attribute value selected")
                        xpath_expression += f"[@{attribute_name_combo}]"   
            window["-XPATH_EXPRESSION-"].update(xpath_expression)
            if xpath_expression != "":
                window["-OUTPUT_WINDOW_XPATH-"].update(f"Final XPath expression: {xpath_expression}")

        except NameError:
            window["-OUTPUT_WINDOW_XPATH-"].update("Name 'parsed_xml_file' is not defined")

    elif event == "-XML_TAG_NAME-":
        try:
            selected_tag = tag_name_combo
            attributes = get_attributes(parsed_xml_file, selected_tag)
            window["-XML_ATTRIBUTE_NAME-"].update(values=attributes)
            values_xml = get_tag_values(parsed_xml_file, selected_tag)
            window["-XML_TAG_VALUE-"].update(values=values_xml)

            # Disable tag value combo box if there are no values for the selected tag
            if not values_xml or all(value.strip() == '' for value in values_xml if value is not None):
                window["-XML_TAG_VALUE-"].update(disabled=True, values="")
            else:
                window["-XML_TAG_VALUE-"].update(disabled=False)
            print(f"XML VALUES: {values_xml}")
            print(type(values_xml))

            # Disable attribute name and value combo boxes if there are no attributes for the selected tag
            if not attributes:
                window["-XML_ATTRIBUTE_NAME-"].update(disabled=True, values="")
                window["-XML_ATTRIBUTE_VALUE-"].update(disabled=True, values=[])
            else:
                window["-XML_ATTRIBUTE_NAME-"].update(disabled=False)
                print(f"ATTRIBUTE: {attributes}")
                print(type(attributes))
        except Exception as e:
            print(f"Fatal error! \n {e}")

    elif event == "-XML_ATTRIBUTE_NAME-":
        try:
            selected_tag = tag_name_combo
            selected_attribute = attribute_name_combo
            attribute_values = get_attribute_values(parsed_xml_file, selected_tag, selected_attribute)
            window["-XML_ATTRIBUTE_VALUE-"].update(values=attribute_values)

            # Disable attribute value combo box if there are no attribute values
            if not attribute_values:
                window["-XML_ATTRIBUTE_VALUE-"].update(disabled=True, values=[])
                window["-XML_ATTRIBUTE_NAME-"].update(disabled=True, values=[])
            else:
                window["-XML_ATTRIBUTE_VALUE-"].update(disabled=False)
                print(f"ATTRIBUTE VALUES: {attribute_values}")
                print(type(values_xml))

            # Disable tag value combo box if the selected tag has no values
            if not values_xml:
                window["-XML_TAG_VALUE-"].update(disabled=True, values="")
        except Exception as e:
            print(f"Fatal error! \n {e}")
            
    # Export as CSV
    elif event == "-EXPORT_AS_CSV-":
        # Get log filter values from GUI elements
        log_filter_values = {
            "TagName": values.get("-XPATH_TAG_NAME-", []),
            "TagValue": values.get("-XPATH_TAG_VALUE-", []),
            "AttributeName": values.get("-XPATH_ATTRIBUTE_NAME-", []),
            "AttributeValue": values.get("-XPATH_ATTRIBUTE_VALUE-", []),
        }
        
        if eval_input_folder and eval_output_folder:
            if os.path.exists(eval_input_folder) and os.path.splitext(eval_output_folder)[1].lower() == ".log":
                try:
                    # Call build_query with the gathered information
                    window["-OUTPUT_WINDOW_XPATH-"].update("Exporting data...")
                    window.perform_long_operation(lambda: build_query(eval_input_folder, xpath_expression_input, log_filter_values, eval_output_folder),"-OUTPUT_WINDOW_XPATH-")
                    window["-OUTPUT_WINDOW_XPATH-"].update("Data exported successfully.")
                except (ValueError, Exception) as e:  # Catch both specific and general exceptions
                    sg.popup_error(f"Error exporting data: {e}")
            else:
                error_message = ""
                if not os.path.exists(eval_input_folder):
                    error_message = "Invalid 'XML Evaluation Input' folder path."
                elif not os.path.splitext(eval_output_folder)[1].lower() == ".csv":
                    error_message = "Invalid 'Export Evaluation as CSV File' path. File must end with '.csv'."
                else:
                    error_message = "Unexpected error. Please check folder paths and try again."
                sg.popup_error(error_message)

window.close() # Kill program