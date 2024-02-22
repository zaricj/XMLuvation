import PySimpleGUI as sg
import xml.etree.ElementTree as ET
import csv

def XML(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tag_name = root.tag
        tag_attribute = root.attrib
        
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

def get_tag_values(xml_file,tag):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    tag_value = []
    for element in root.iter(tag): # Add Parameter in Function later for root.iter(parameter)
        tag_value.append(element.text)
    return list(set(tag_value))

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
    return attribute_value_list

# Function to filter XML data based on specified criteria ######FIRST APPROACH######
#def filter_xml(xml_file, tag_name=None, tag_value=None, attribute_name=None, attribute_value=None):
#    try:
#        filtered_data = []
#        tree = ET.parse(xml_file)
#        root = tree.getroot()
#
#        for element in root.iter(tag_name):
#            if tag_value and element.text != tag_value:
#                continue
#            if attribute_name and attribute_value:
#                if element.attrib.get(attribute_name) != attribute_value:
#                    continue
#            filtered_data.append(element)
#    except FileNotFoundError:
#        pass
#
#    return filtered_data

# Function to parse XML file and extract relevant information ######SECOND APPROACH#######
def parse_xml(xml_file, tag_name=None, tag_value=None, attribute_name=None, attribute_value=None):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        for element in root.iter(tag_name):
            if tag_value and element.text != tag_value:
                continue
            if attribute_name and attribute_value:
                if element.attrib.get(attribute_name) != attribute_value:
                    continue
            
            yield {
                'Tag Name': element.tag,
                'Tag Value': element.text,
                'Attributes': element.attrib,
                'Attribute Value': element.attrib.get(attribute_name)
            }
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")

# Function to write filtered data to a CSV file #######FIRST APPROACH#######
#def write_to_csv(data, filename):
#    with open(filename, 'w', newline='') as csvfile:
#        fieldnames = ['Tag', 'Value', 'Attributes']
#        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#        writer.writeheader()
#
#        for element in data:
#            writer.writerow({'Tag': element.tag, 'Value': element.text, 'Attributes': element.attrib})

# Function to log the extracted information to a CSV file ######SECOND APPROACH######
def log_to_csv(data, csv_filename):
    fieldnames = ['Tag Name', 'Tag Value', 'Attributes', 'Attribute Value']
    with open(csv_filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for item in data:
            writer.writerow(item)

sg.theme("SystemDefault")
font = ("Arial", 10)

FILE_TYPE_XML = (('XML (Extensible Markup Language)', '.xml'),)
tag_name = []
tag_value = []
attribute_name = []
attribute_value = []

layout_xml_eval = [[sg.Text("Multi-XML Files Iteration in a Folder:")],
                    [sg.Input(size=(35,2),font="Arial 8",key="-FOLDER_EVALUATION_INPUT-"),sg.FileBrowse(button_text="Browse File",file_types=FILE_TYPE_XML,target="-FOLDER_EVALUATION_INPUT-"),sg.Button("Read",key="-READ-")],
                    [sg.Text("Filtering Options for XML Evaluation:")],
                    [sg.Text("Tag name:"),sg.Combo(tag_name, size=(14,1), auto_size_text=False, enable_events=True, key="-XML_TAG_NAME-"),sg.Text("Tag Value:"),sg.Combo(tag_value, size=(14,1), enable_events=True, auto_size_text=False, key="-XML_TAG_VALUE-")],
                    [sg.Text("Att name: "),sg.Combo(attribute_name, size=(14,1), auto_size_text=False, enable_events=True, key="-XML_ATTRIBUTE_NAME-"),sg.Text("Att Value: "),sg.Combo(attribute_value, size=(14,1), enable_events=True, auto_size_text=False, key="-XML_ATTRIBUTE_VALUE-")],
                    [sg.Text("Filter:"),sg.Button("Filter",key="-FILTER-")],
                    [sg.Text("Export Evaluation as CSV File:")],
                    [sg.Input(size=(35,2),font="Arial 8",key="-FOLDER_EVALUATION_OUTPUT-"),sg.SaveAs(button_text="Save as CSV", file_types=(("Comma Seperated Values (.csv)",".csv"),) ,target="-FOLDER_EVALUATION_OUTPUT-"),sg.Button("Export",key="-EXPORT_AS_CSV-")]]

layout_statusbars = [[sg.Text("Names and Values:")],
                     [sg.Text("Tag Name:"),sg.StatusBar("", size=(20,1), auto_size_text=False, key="-STATUSBAR_TAG_NAME-")],
                     [sg.Text("Tag Value:"),sg.StatusBar("", size=(20,1), auto_size_text=False, key="-STATUSBAR_TAG_VALUE-")],
                     [sg.Text("Att Name:"),sg.StatusBar("", size=(20,1), auto_size_text=False, key="-STATUSBAR_ATTRIBUTE_NAME-")],
                     [sg.Text("Att Value:"),sg.StatusBar("" , size=(20,1), auto_size_text=False, key="-STATUSBAR_ATTRIBUTE_VALUE-")]]

layout_output = [[sg.Multiline(size=(60,21),write_only=False,key="-OUTPUT_WINDOW-")]]

frame_xml_eval = sg.Frame("XML Evaluation and Filtering", layout_xml_eval, expand_x=True)
frame_statusbars = sg.Frame("Status of XML Values/Attributes",layout_statusbars)
frame_output = sg.Frame("Program Output", layout_output, expand_x=True)

layout = [
    [
        sg.Column([[frame_xml_eval],[frame_statusbars]], expand_y=True),
        sg.Column([[frame_output]], expand_y=True)
    ]
]

window = sg.Window("XMLuvation - by Jovan",layout,font=font, finalize=True)

while True:
    event,values = window.read()
    
    if event == sg.WIN_CLOSED or event == "Exit":
        break

    # VARIABLES #
    eval_input_file = values["-FOLDER_EVALUATION_INPUT-"]
    eval_output_folder = values["-FOLDER_EVALUATION_OUTPUT-"]
    tag_name_combo = values["-XML_TAG_NAME-"]
    tag_value_combo = values["-XML_TAG_VALUE-"]
    attribute_name_combo = values["-XML_ATTRIBUTE_NAME-"]
    attribute_value_combo = values["-XML_ATTRIBUTE_VALUE-"]
    
    # StatusBar Element Variables
    statusbar_tag_name = "-STATUSBAR_TAG_NAME-"
    statusbar_tag_value = "-STATUSBAR_TAG_VALUE-"
    statusbar_attribute_name = "-STATUSBAR_ATTRIBUTE_NAME-"
    statusbar_attribute_value = "-STATUSBAR_ATTRIBUTE_VALUE-"
    
    if event == "-READ-":
        window.perform_long_operation(lambda: XML(eval_input_file),"-OUTPUT_WINDOW-")
        window["-XML_TAG_VALUE-"].update(values="")
        window["-XML_ATTRIBUTE_NAME-"].update(values="")
        window["-XML_ATTRIBUTE_VALUE-"].update(values="")
     
    if event == "-XML_TAG_NAME-":
        selected_tag = tag_name_combo
        attributes = get_attributes(eval_input_file, selected_tag)
        window["-XML_ATTRIBUTE_NAME-"].update(values=attributes)
        values_xml = get_tag_values(eval_input_file, selected_tag)
        window["-XML_TAG_VALUE-"].update(values=values_xml)
        
        # Disable tag value combo box if there are no values for the selected tag
        if not values_xml:
            window["-XML_TAG_VALUE-"].update(disabled=True, value="")
        else:
            window["-XML_TAG_VALUE-"].update(disabled=False)

        # Disable attribute name and value combo boxes if there are no attributes for the selected tag
        if not attributes:
            window["-XML_ATTRIBUTE_NAME-"].update(disabled=True, value="")
            window["-XML_ATTRIBUTE_VALUE-"].update(disabled=True, values=[])
        else:
            window["-XML_ATTRIBUTE_NAME-"].update(disabled=False)

        # Disable tag value combo box if the selected tag has no values
        if not values_xml:
            window["-XML_TAG_VALUE-"].update(disabled=True, value="")

    if event == "-XML_ATTRIBUTE_NAME-":
        selected_tag = tag_name_combo
        selected_attribute = attribute_name_combo
        attribute_values = get_attribute_values(eval_input_file, selected_tag, selected_attribute)
        window["-XML_ATTRIBUTE_VALUE-"].update(values=attribute_values)

        # Disable attribute value combo box if there are no attribute values
        if not attribute_values:
            window["-XML_ATTRIBUTE_VALUE-"].update(disabled=True, value="")
        else:
            window["-XML_ATTRIBUTE_VALUE-"].update(disabled=False)

        # Disable attribute name and value combo boxes if the selected tag has no attributes
        if not attributes:
            window["-XML_ATTRIBUTE_NAME-"].update(disabled=True, value="")
            window["-XML_ATTRIBUTE_VALUE-"].update(disabled=True, values=[])

        # Disable tag value combo box if the selected tag has no values
        if not values_xml:
            window["-XML_TAG_VALUE-"].update(disabled=True, value="")
    
    # Event handling...
    if event == "-FILTER-":
        filtered_data = parse_xml(eval_input_file, tag_name_combo, tag_value_combo, attribute_name_combo, attribute_value_combo)
        # Print filtered data for demonstration
        for element in filtered_data:
            window[statusbar_tag_name].update(value=tag_name_combo)
            window[statusbar_tag_value].update(value=tag_value_combo)
            window[statusbar_attribute_name].update(value=attribute_name_combo)
            window[statusbar_attribute_value].update(value=attribute_value_combo)
            print("Tag:", tag_name_combo)
            print("Value:", tag_value_combo)
            print("Attributes:", attribute_name_combo)
            print("Attribute Value:", attribute_value_combo)
            print("----------------------")
            
    if event == "-EXPORT_AS_CSV-":
        filtered_data = parse_xml(eval_input_file, tag_name_combo, tag_value_combo, attribute_name_combo, attribute_value_combo)
        csv_filename = eval_output_folder
        if csv_filename:
            log_to_csv(filtered_data, csv_filename)
        
window.close() # Kill program