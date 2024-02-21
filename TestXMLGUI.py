import PySimpleGUI as sg
import xml.etree.ElementTree as ET

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

def get_attributes(xml_file, tag):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    attributes = []
    for elem in root.iter(tag):
        attributes.extend(elem.attrib.keys())
    return list(set(attributes))

sg.theme("SystemDefault")
font = ("Arial", 10)

FILE_TYPE_XML = (('XML (Extensible Markup Language)', '.xml'),)
tag_name = []
attribute_name = []

layout_xml_eval = [[sg.Text("Multi-XML Files Iteration in a Folder:")],
                    [sg.Input(size=(35,2),font="Arial 8",key="-FOLDER_EVALUATION_INPUT-"),sg.FileBrowse(button_text="Browse File",file_types=FILE_TYPE_XML,target="-FOLDER_EVALUATION_INPUT-"),sg.Button("Read",key="-READ-")],
                    [sg.Text("Filtering Options for XML Evaluation:")],
                    [sg.Text("Tag name:"),sg.Combo(tag_name,size=(14,1),auto_size_text=False,enable_events=True,key="-XML_TAG_NAME-"),sg.Text("Tag Value:"),sg.Input(size=(14,1),key="-XML_TAG_VALUE-")],
                    [sg.Text("Att name: "),sg.Combo(attribute_name,size=(14,1),auto_size_text=False,enable_events=True,key="-XML_ATTRIBUTE_NAME-"),sg.Text("Att Value: "),sg.Input(size=(14,1),key="-XML_ATTRIBUTE_VALUE-")],
                    [sg.Text("Export Evaluation as CSV File:")],
                    [sg.Input(size=(35,2),font="Arial 8",key="-FOLDER_EVALUATION_OUTPUT-"),sg.FolderBrowse(button_text="Browse Folder",target="-FOLDER_EVALUATION_OUTPUT-"),sg.Button("Export")]]

layout_output = [[sg.Multiline(size=(60,21),write_only=False,key="-OUTPUT_WINDOW-")]]

frame_xml_eval = sg.Frame("XML Evaluation and Filtering", layout_xml_eval, expand_x=True)
frame_output = sg.Frame("Program Output", layout_output, expand_x=True)

layout = [
    [
        sg.Column([[frame_xml_eval]], expand_y=True),
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
    tag_attribute_combo = values["-XML_ATTRIBUTE_NAME-"]
    
    if event == "-READ-":
        window.perform_long_operation(lambda: XML(eval_input_file),"-OUTPUT_WINDOW-")
     
    if event == "-XML_TAG_NAME-":
        selected_tag = tag_name_combo
        attributes_xml = get_attributes(eval_input_file,selected_tag)
        window["-XML_ATTRIBUTE_NAME-"].update(values=attributes_xml)
        
window.close() # Kill program