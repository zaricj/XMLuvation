import PySimpleGUI as sg
import xml.etree.ElementTree as ET
import csv
import os
import re

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
        fieldnames = ['File', 'Tag Name', 'Tag Value', 'Attributes', 'Attribute Value'] + query["additional_data"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
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
tag_name = []
tag_value = []
attribute_name = []
attribute_value = []
filters = [] 
filters_log = []
additional_data = []

layout_xml_eval = [[sg.Text("Multi-XML Files Iteration in a Folder:", pad=5)],
                    [sg.Input(size=(36,2),font="Arial 10",key="-FOLDER_EVALUATION_INPUT-"),sg.FolderBrowse(button_text="Browse Folder",target="-FOLDER_EVALUATION_INPUT-"),sg.Button("Read XML",key="-READ_XML-")],
                    [sg.Text("Filtering Options for XML Evaluation:", pad=5)],
                    [sg.Text("Tag name:"),sg.Combo(tag_name, size=(14,1), disabled=True, auto_size_text=False, enable_events=True, enable_per_char_events=True, expand_x=True, key="-XML_TAG_NAME-"),sg.Text("Tag Value:"),sg.Combo(tag_value, size=(14,1), disabled=True, enable_events=True, enable_per_char_events=True, auto_size_text=False, expand_x=True, key="-XML_TAG_VALUE-")],
                    [sg.Text("Att name:  "),sg.Combo(attribute_name, size=(14,1), disabled=True, auto_size_text=False, enable_events=True, expand_x=True, key="-XML_ATTRIBUTE_NAME-"),sg.Text("Att Value:  "),sg.Combo(attribute_value, size=(14,1), disabled=True, enable_events=True, auto_size_text=False, expand_x=True, key="-XML_ATTRIBUTE_VALUE-")],
                    [sg.Text("Add selection for filtering/matching:", pad=10),sg.Button("Add to Filter", key="-FILTER-", pad=10)],
                    [sg.Listbox(values=filters, size=(60,5), enable_events=True, key="-FILTER_LIST-")]]

layout_statusbars = [[sg.Text("Additional data for logging (not used for XML filtering/matching):"), sg.Button("Add to Log", key="-ADD_DATA-")],
                    [sg.Listbox(values=additional_data, size=(60,5), enable_events=True, key="-ADDITIONAL_DATA_LIST-")],
                    [sg.Text("Export Evaluation as CSV File:")],
                    [sg.Input(size=(36,2),font="Arial 10",key="-FOLDER_EVALUATION_OUTPUT-"),sg.SaveAs(button_text="Save as", file_types=(("Comma Seperated Values (.csv)",".csv"),), target="-FOLDER_EVALUATION_OUTPUT-"),sg.Button("Export", key="-EXPORT_AS_CSV-")]]

layout_output = [[sg.Multiline(size=(60,30),write_only=False,key="-OUTPUT_WINDOW-",pad=10)]]

frame_xml_eval = sg.Frame("XML Evaluation and Filtering", layout_xml_eval, expand_x=True)
frame_statusbars = sg.Frame("Status of XML Values/Attributes",layout_statusbars,expand_x=True)
frame_output = sg.Frame("Program Output", layout_output, expand_x=True)

layout = [
    [
        sg.Column([[frame_xml_eval],[frame_statusbars]], expand_y=True),
        sg.Column([[frame_output]], expand_y=True)
    ]
]

window = sg.Window("XMLuvation - by Jovan", layout, font=font, finalize=True)

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
    additional_data_list = values["-ADDITIONAL_DATA_LIST-"]
    
    # RegEx Matching
    file_path_regex = r'\.xml$'
        
    if event == "-READ_XML-":
        eval_input_file = sg.popup_get_file("Select an XML file", file_types=(("XML Files", "*.xml"),))
        if eval_input_file:
            window.perform_long_operation(lambda: XML(eval_input_file),"-OUTPUT_WINDOW-")
            window["-XML_TAG_VALUE-"].update(values="")
            window["-XML_ATTRIBUTE_NAME-"].update(values="")
            window["-XML_ATTRIBUTE_VALUE-"].update(values="")

            if re.search(file_path_regex, eval_input_file):
                window["-XML_TAG_NAME-"].update(disabled=False)
                window["-XML_TAG_VALUE-"].update(disabled=False)
                tag_name = values["-XML_TAG_NAME-"]
                window["-XML_TAG_NAME-"].update(values=tag_name)

                for tag in tag_name:
                    tag_value_list = get_tag_values(eval_input_file, tag)
                    window["-XML_TAG_VALUE-"].update(disabled=False, values=tag_value_list)
                    attribute_name_list = get_attributes(eval_input_file, tag)
                    window["-XML_ATTRIBUTE_NAME-"].update(values=attribute_name_list)
                    for attribute_name in attribute_name_list:
                        attribute_value_list = get_attribute_values(eval_input_file, tag, attribute_name)
                        window["-XML_ATTRIBUTE_VALUE-"].update(values=attribute_value_list)
                        break  # Only need to get attributes and values for the first tag
     
    elif event == "-XML_TAG_NAME-":
        try:
            selected_tag = tag_name_combo
            attributes = get_attributes(eval_input_file, selected_tag)
            window["-XML_ATTRIBUTE_NAME-"].update(values=attributes)
            values_xml = get_tag_values(eval_input_file, selected_tag)
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
            attribute_values = get_attribute_values(eval_input_file, selected_tag, selected_attribute)
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

    #if event == "-FILTER-":
    #    try:
    #        print("Tag:", tag_name_combo)
    #        print("Value:", tag_value_combo)
    #        print("Attributes:", attribute_name_combo )
    #        print("Attribute Value:", attribute_value_combo )
    #        print("----------------------\n")
    #        
    #        window["-STATUSBAR_TAG_NAME-"].update(tag_name_combo)
    #        window["-STATUSBAR_TAG_VALUE-"].update(tag_value_combo)
    #        window["-STATUSBAR_ATTRIBUTE_NAME-"].update(attribute_name_combo)
    #        window["-STATUSBAR_ATTRIBUTE_VALUE-"].update(attribute_value_combo)
    #        
    #        print(f"Type of StatusBarElement: {type(window["-STATUSBAR_TAG_NAME-"])}")
    #    except Exception as e:
    #        print(f"Fatal error! \n {e}")
            
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
                
    elif event == "-ADD_DATA-":
        # Get current selections from comboboxes
        selected_tag_name2 = values.get("-XML_TAG_NAME-")
        selected_tag_value2 = values.get("-XML_TAG_VALUE-")
        selected_attribute_name2 = values.get("-XML_ATTRIBUTE_NAME-")
        selected_attribute_value2 = values.get("-XML_ATTRIBUTE_VALUE-")

        # Check if any value is selected from comboboxes
        if selected_tag_name2 or selected_tag_value2 or selected_attribute_name2 or selected_attribute_value2:
            filter_dict_log = {}
            if selected_tag_name2:
                filter_dict_log["tag_name"] = selected_tag_name2
            if selected_tag_value2:
                filter_dict_log["tag_value"] = selected_tag_value2
            if selected_attribute_name2:
                filter_dict_log["attribute_name"] = selected_attribute_name2
            if selected_attribute_value2:
                filter_dict_log["attribute_value"] = selected_attribute_value2
                
            filters_log.append(filter_dict_log)
            window["-ADDITIONAL_DATA_LIST-"].update(values=filters_log)
            
    elif event == "-ADDITIONAL_DATA_LIST-":
        # Handle potential actions on the listbox, such as editing or removing data
        pass  # Implement actions based on your specific requirements

    # Export as CSV
    elif event == "-EXPORT_AS_CSV-":
        if eval_input_folder and eval_output_folder:
            if os.path.isdir(eval_input_folder): # and os.path.isdir(eval_output_folder)?
                query = build_query(filters,filters_log)
                log_matching_files(eval_input_folder, query, eval_output_folder)
                sg.popup(f"Matching XML files information exported to {eval_output_folder}")
            else:
                sg.popup("Invalid folder paths.\nPlease enter valid paths for both 'XML Evaluation Input' and 'Export Evaluation as CSV File' sections.")

window.close()