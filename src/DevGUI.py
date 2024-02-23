import xml.etree.ElementTree as ET
import csv
import PySimpleGUI as sg

def filter_xml(input_file, output_file, tag, attribute=None, attribute_value=None):
    tree = ET.parse(input_file)
    root = tree.getroot()

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Tag', 'Attribute', 'Value'])

        if attribute and attribute_value:
            for elem in root.findall('.//' + tag):
                if attribute in elem.attrib and elem.attrib[attribute] == attribute_value:
                    writer.writerow([elem.tag, attribute, elem.attrib[attribute]])
        else:
            for elem in root.findall('.//' + tag):
                writer.writerow([elem.tag, '', elem.text])

def main():
    layout = [
        [sg.Text('XML File:'), sg.InputText(key='-XML_FILE-'), sg.FileBrowse()],
        [sg.Text('Output CSV File:'), sg.InputText(key='-OUTPUT_CSV-'), sg.FileSaveAs()],
        [sg.Text('Tag to Filter:'), sg.InputText(key='-TAG-')],
        [sg.Text('Attribute (optional):'), sg.InputText(key='-ATTRIBUTE-')],
        [sg.Text('Attribute Value (optional):'), sg.InputText(key='-ATTRIBUTE_VALUE-')],
        [sg.Button('Filter XML'), sg.Button('Exit')]
    ]

    window = sg.Window('XML Filter', layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        elif event == 'Filter XML':
            xml_file = values['-XML_FILE-']
            output_csv = values['-OUTPUT_CSV-']
            tag = values['-TAG-']
            attribute = values['-ATTRIBUTE-']
            attribute_value = values['-ATTRIBUTE_VALUE-']
            filter_xml(xml_file, output_csv, tag, attribute, attribute_value)
            sg.popup('XML Filtered Successfully!', title='Success')

    window.close()

if __name__ == '__main__':
    main()
