import PySimpleGUI as sg
import xml.etree.ElementTree as ET

sg.theme("SystemDefault")
font = ("Arial", 10)

tag_name = []
attribute_name = []

layout_xml_eval = [[sg.Text("Multi-XML Files Iteration in a Folder:")],
                    [sg.Input(size=(35,2),font="Arial 8",key="-FOLDER_EVALUATION_INPUT-"),sg.FolderBrowse(button_text="Browse Folder",target="-FOLDER_EVALUATION_INPUT-"),sg.Button("Read",key="-READ_BUTTON_EVALUATION-")],
                    [sg.Text("Filtering Options for XML Evaluation:")],
                    [sg.Text("Tag name:"),sg.Combo(tag_name,size=(14,1),auto_size_text=False,key="-XML_TAG_NAME-"),sg.Text("Tag Value:"),sg.Input(size=(14,1),key="-XML_TAG_VALUE-")],
                    [sg.Text("Att name: "),sg.Combo(attribute_name,size=(14,1),auto_size_text=False,key="-XML_ATTRIBUTE_NAME-"),sg.Text("Att Value: "),sg.Input(size=(14,1),key="-XML_ATTRIBUTE_VALUE-")],
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
    input_path = values["-FILE_EXPORT_INPUT-"]
    output_path = values["-FILE_EXPORT_OUTPUT-"]
    
window.close() # Kill program