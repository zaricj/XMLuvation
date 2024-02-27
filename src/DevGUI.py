import PySimpleGUI as sg
from lxml import etree as ET
import csv
import os
import re

xml_32px = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAA8pJREFUWIXtVl1oHFUYPefOJpNkQ9omJps11mIZKkiTaQmEarMtguKDL4ot9adCQUVU0pBSRRBEpSiJUKlYxPTnrVUEhT5UCaKYbkqlVM0mNBTZaoNtuhuX/Ehbd5LZ+/mw2dnZNWm6NIhgztOd+X7OuWcu9xtgGcv4v4NL0eRcK8qaKu2dBNYpxWjDqcGv/lUByYj9KsgeABCRTIXo+pUDw5O3UquWQgCInfklRm+VfEkEJLY0NwNsyYuR46XU374Dwme8pYhkkClJQGCxhFSbVeOWBzug8ApEv9QYHT7hEQIcB5/KPZP4WURVJiN2UoscV4bbHeofSdys/4KHcHKrvdIRdkKkk+SqLKEcaTwVez6XM9a+fquhAt97gjJ6rxCzSqkD2RfylwZ6DTjdDdELV+fj+ccnmGpvXpVst99xNC4ReCtHDgDQ+M2fazDgtz9jiPGpoVQ8vz1WKrJTYF5MROwDfzxw750LOjC16b5apyywR8AOkjUFWSITEBy8YUy9e0//aBoAfrEssyYcvOoJFPk2FI09JIAxHmnpEuEeKoYL20haAYfSs+i++4fYFU/AxP0b18wE9E8kawsL9BUl2C+G2xvqH7nmjyU224/T4JeeORn9XPj00FGv1rLMVDi4KwPsJWkVbSgNyGOh6FBfAADcgPswadTm4+JQpCs14R5ZPzIyU2zbnHd++9Nm+toXBeF43EEcnwhwKLHZ3qYMfASwPhtkhRZ5BECfAgABfy8oJk1QvVFfV9aZarMKPweAida1K0g8mt8RTtb++Ot0cd7ngJGItGynwuseeY5DMAXMHcKG6NA3FP0mIPkbjGgC2eOa1aPJSMu+sXbLa+BUVW8DWeETcMzfXCzLTETsF7dE7AuK6jOSG/NBcbToXk64+7M0PlxsXbsiWFW9G2BXwenPklwH9BOh6FBfItLyHakenAtMTo9dD6+Lxx0ASG2ymzLlOANwdUG5iAPgaBnc9+qi5z3H570HUm1WjTaDuwXogv9giv5gxpH95aa6BNIAAK3lcHgg9kIuJdm+4WUoHPQRp5XIYWdGulefHb5czDXvTXjH2fifAPal2qwPdUWwQwRdIOsgiuUmngRheA2K7adMEwREbmiRXoMzPQ0D819CCzownyOzZtV2pdyT1OVfC7FhbneXP47G1rwN6FzuudbWsrsq3V2SkRPhM0Pji/Uu6X8gO/mMGOfqROP9xoHB10rpUYzSpqFWT9MnmjJ77GbpSy8AaMstRDAYOn0+drsCFh3HfhhaPSvQO7SirhKUNPeXsYz/LP4Gk8OElv5Vn3MAAAAASUVORK5CYII='

def XML(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        xml_string = ET.tostring(root).decode("UTF-8") # Converts the read xml file to a string
        window["-OUTPUT_WINDOW-"].update(xml_string) # Prints the xml file in the ouput window
        
        # Get tags in XML File:
        tags_xml = [element.tag for element in root.iter()]
        tags_to_set = set(tags_xml)
        tags_to_list = list(tags_to_set)
        # Add Elements to ComboBox List
        window["-XML_TAG_NAME-"].update(values=tags_to_list)
    except Exception as e:
        print(e)

def get_tag_values(xml_file, tag):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    tag_value = []
    for element in root.iter(tag): # Add Parameter in Function later for root.iter(parameter)
        tag_value.append(element.text)
    print(type(tag_value))
    return tag_value

def get_attributes(xml_file, tag):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    attributes = []
    for element in root.iter(tag):
        attributes.extend(element.attrib.keys())
    print(type(attributes))
    return list(set(attributes))

def get_attribute_values(xml_file, tag, attribute):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    attribute_value_list = []
    for element in root.iter(tag):
        attribute_value = element.attrib.get(attribute)
        if attribute_value is not None:
            attribute_value_list.append(attribute_value)
    print(type(attribute_value_list))
    return list(set(attribute_value_list))

def xpath_search(xml_file, xpath_expression):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        results = root.findall(xpath_expression)
        return results
    except ET.ParseError as e:
        return f"XML Parse Error: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

def parse_xml(xml_file, filters):
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

        for key, value in filters.items():
            if key == "tag_name":
                if root.tag not in value:
                    return False
            elif key == "tag_value":
                if root.text != value:
                    return False
            elif key == "attribute_name":
                if value not in root.attrib:
                    return False
            elif key == "attribute_value":
                if root.attrib.get(value) is None:
                    return False
        return True
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")
        return False

def build_query(filters, additional_data):
    """
    Builds a dictionary containing the filtering criteria and additional data.

    Args:
        filters (list): List containing dictionaries representing filtering criteria.
        additional_data (list): List of strings representing additional data to log.

    Returns:
        dict: Dictionary containing combined filtering criteria and additional data.
    """
    query = {}
    query["filters"] = filters
    query["additional_data"] = additional_data
    return query

def log_matching_files(folder_path, query, output_filename):
    """
    Logs information about matching XML files and additional data to a CSV file.

    Args:
        folder_path (str): Path to the folder containing XML files.
        query (dict): Dictionary containing filtering criteria and additional data.
        output_filename (str): Path to the output CSV file.
    """
    csv_exists = os.path.isfile(output_filename)
    with open(output_filename, 'a' if csv_exists else 'w', newline='') as csvfile:
        headers = ['File', 'Tag Name', 'Tag Value', 'Attributes', 'Attribute Value'] + list(query["additional_data"])
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if not csv_exists:
            writer.writeheader()

        for filename in os.listdir(folder_path):
            if filename.endswith('.xml'):
                xml_file = os.path.join(folder_path, filename)
                if parse_xml(xml_file, query["filters"]):
                    try:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        data = {
                            'File': filename,
                            'Tag Name': root.tag,
                            'Tag Value': root.text,
                            'Attributes': root.attrib,
                            'Attribute Value': None
                        }
                        for attr_name, attr_value in root.attrib.items():
                            if attr_name in query["filters"] and query["filters"][attr_name] == attr_value:
                                data['Attribute Value'] = attr_value
                                break  # Only need to report the first matching attribute
                        data.update({key: value for key, value in zip(query["additional_data"], query["additional_data"])})  # Add additional data
                        writer.writerow(data)
                    except Exception as e:
                        print(f"Error processing {xml_file}: {e}")

my_new_theme = {'BACKGROUND': '#2d3039', 
        'TEXT': 'white', 
        'INPUT': '#535360', 
        'TEXT_INPUT': 'white', 
        'SCROLL': '#333', 
        'BUTTON': ('#35b79a', '#626271'), 
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
filters = [] 
filters_log = []
additional_data = []

layout_xml_eval = [[sg.Text("Multi-XML Files Iteration in a Folder:", pad=5)],
                    [sg.Input(size=(36,2), font="Arial 10", expand_x=True, key="-FOLDER_EVALUATION_INPUT-"),sg.FolderBrowse(button_text="Browse Folder",target="-FOLDER_EVALUATION_INPUT-"),sg.Button("Read XML",key="-READ_XML-")],
                    [sg.Text("Filtering Options for XML Evaluation:", pad=5)],
                    [sg.Text("Tag name:"),sg.Combo(tag_name, size=(14,1), disabled=True, auto_size_text=False, enable_events=True, enable_per_char_events=True, expand_x=True, key="-XML_TAG_NAME-"),sg.Text("Tag Value:"),sg.Combo(tag_value, size=(14,1), disabled=True, enable_events=True, enable_per_char_events=True, auto_size_text=False, expand_x=True, key="-XML_TAG_VALUE-")],
                    [sg.Text("Att name:  "),sg.Combo(attribute_name, size=(14,1), disabled=True, auto_size_text=False, enable_events=True, expand_x=True, key="-XML_ATTRIBUTE_NAME-"),sg.Text("Att Value:  "),sg.Combo(attribute_value, size=(14,1), disabled=True, enable_events=True, auto_size_text=False, expand_x=True, key="-XML_ATTRIBUTE_VALUE-", pad=10)],
                    [sg.Text("Build XPath Expression:"),sg.Input(size=(14,1), expand_x=True, key="-XPATH_EXPRESSION-"),sg.Button("Build XPath",key="-XPATH_BUILD-")],
                    [sg.Text("Add selection for filtering/matching:", pad=10),sg.Button("Add to Filter", key="-FILTER-")],
                    [sg.Listbox(values=filters, size=(60,5), enable_events=True, right_click_menu=MENU_RIGHT_CLICK_DELETE, expand_x=True, key="-FILTER_LIST-")],
                    [sg.Text("Export Evaluation as CSV File:")],
                    [sg.Input(size=(36,2),font="Arial 10",key="-FOLDER_EVALUATION_OUTPUT-",expand_x=True),sg.SaveAs(button_text="Save as", file_types=(("Comma Seperated Values (.csv)",".csv"),), target="-FOLDER_EVALUATION_OUTPUT-"),sg.Button("Export", key="-EXPORT_AS_CSV-")]]


layout_output = [[sg.Multiline(size=(60,32),write_only=False,key="-OUTPUT_WINDOW-")]]

layout_xpath_output = [[sg.Multiline(size=(60,6),key="-OUTPUT_WINDOW_XPATH-")]]

frame_xml_eval = sg.Frame("XML Evaluation and Filtering", layout_xml_eval, expand_x=True)
frame_output = sg.Frame("XML Output", layout_output, expand_x=True)
frame_xpath_output = sg.Frame("Program Output",layout_xpath_output)

layout = [
    [
        sg.Column([[frame_xml_eval],[frame_xpath_output]], expand_y=True),
        sg.Column([[frame_output]], expand_y=True)
    ]
]

window = sg.Window("XMLuvation - by Jovan", layout, font=font, finalize=True,icon=xml_32px)

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
    
    filter_list = values["-FILTER_LIST-"]

    # RegEx Matching
    file_path_regex = r'\.xml$'
    
    # Delete and Delete All functionality with right click per item in list (needs to be selected with left click first)
    if event in ("Delete", "Delete All"):
        try:
            selected_indices_eval = window["-FILTER_LIST-"].get_indexes()
            if event == "Delete":
                if selected_indices_eval:
                    for index in selected_indices_eval:  # iterate in reverse order
                        if len(filters) > index:
                            filters.pop(index)
                            window["-FILTER_LIST-"].update(values=filters)
                   
            elif event == "Delete All":
                if selected_indices_eval:
                    filters.clear()
                    window["-FILTER_LIST-"].update(values=filters)
               
        except UnboundLocalError:
            window["-OUTPUT_WINDOW-"].update("ERROR: To delete an item from Listbox, select it first.")
        
    elif event == "-READ_XML-":
        parsed_xml_file = sg.popup_get_file("Select an XML file", file_types=(("XML Files", "*.xml"),))
        if parsed_xml_file:
            window.perform_long_operation(lambda: XML(parsed_xml_file),"-OUTPUT_WINDOW-")
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
            xpath_tag_name = f".//{tag_name_combo}"
            xpath_tag_value = f"[text()='{tag_value_combo}']"
            xpath_attribute_name = f"[@{attribute_name_combo}"
            xpath_attribute_value = f"='{attribute_value_combo}']"
            
            xpath_expression = ""
            if tag_name_combo:
                xpath_expression += xpath_tag_name
            if attribute_name_combo:
                print(f"Appending attribute name: @{xpath_attribute_name}")
                xpath_expression += xpath_attribute_name
            if attribute_value_combo:
                print(f"Appending attribute value:'{xpath_attribute_value}'")
                xpath_expression += xpath_attribute_value
            if tag_value_combo:
                print(f"Appending tag value: '{xpath_tag_value}'")
                xpath_expression += xpath_tag_value

            print(f"Final XPath expression: {xpath_expression}")
            window["-XPATH_EXPRESSION-"].update(xpath_expression)

            #if xpath_expression:
            #    xml_file = parsed_xml_file
            #    if xml_file:
            #        results = xpath_search(xml_file, xpath_expression)
            #        window["-OUTPUT_WINDOW_XPATH-"].update("Search Results:")
            #        for result in results:
            #            window["-OUTPUT_WINDOW_XPATH-"].update(ET.tostring(result, encoding="unicode"))
            #        if results:
            #            window["-OUTPUT_WINDOW_XPATH-"].print(f"Tag Name: {xpath_tag_name} Found", text_color="green")
            #        else:
            #            window["-OUTPUT_WINDOW_XPATH-"].print(f"Tag Name: {xpath_tag_name} Not Found", text_color="red")
            #else:
            #    window["-OUTPUT_WINDOW_XPATH-"].update("Please provide at least one search criteria.")
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
            
        # Filtering Functionality
    elif event == "-FILTER-":
        # Get current selections from comboboxes
        selected_tag_name = values.get("-XML_TAG_NAME-")
        selected_tag_value = values.get("-XML_TAG_VALUE-")
        selected_attribute_name = values.get("-XML_ATTRIBUTE_NAME-")
        selected_attribute_value = values.get("-XML_ATTRIBUTE_VALUE-")

        # Check if any value is selected from comboboxes
        if selected_tag_name or selected_tag_value or selected_attribute_name or selected_attribute_value:
            filter_dict = {}
            if selected_tag_name:
                filter_dict["tag_name"] = selected_tag_name
            if selected_tag_value:
                filter_dict["tag_value"] = selected_tag_value
            if selected_attribute_name:
                filter_dict["attribute_name"] = selected_attribute_name
            if selected_attribute_value:
                filter_dict["attribute_value"] = selected_attribute_value

            filters.append(filter_dict)
            window["-FILTER_LIST-"].update(values=filters)

    # Export as CSV
    elif event == "-EXPORT_AS_CSV-":
        if eval_input_folder and eval_output_folder:
            if os.path.exists(eval_input_folder) and os.path.splitext(eval_output_folder)[1].lower() == ".csv": # and os.path.isdir(eval_output_folder)?
                query = build_query(filters,filters_log)
                log_matching_files(eval_input_folder, query, eval_output_folder)
                sg.popup(f"Matching XML files information exported to {eval_output_folder}")
            else:
                if not os.path.exists(eval_input_folder):
                    message = "Invalid 'XML Evaluation Input' folder path."
                elif not os.path.splitext(eval_output_folder)[1].lower() == ".csv":
                    message = "Invalid 'Export Evaluation as CSV File' path. File must end with '.csv'."
                else:
                    message = "Unexpected error. Please check folder paths and try again."
                sg.popup(message)

window.close() # Kill program