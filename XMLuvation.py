import PySimpleGUI as sg
import xml.etree.ElementTree as ET
import csv
import os
import re

xml_32px = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAA8pJREFUWIXtVl1oHFUYPefOJpNkQ9omJps11mIZKkiTaQmEarMtguKDL4ot9adCQUVU0pBSRRBEpSiJUKlYxPTnrVUEhT5UCaKYbkqlVM0mNBTZaoNtuhuX/Ehbd5LZ+/mw2dnZNWm6NIhgztOd+X7OuWcu9xtgGcv4v4NL0eRcK8qaKu2dBNYpxWjDqcGv/lUByYj9KsgeABCRTIXo+pUDw5O3UquWQgCInfklRm+VfEkEJLY0NwNsyYuR46XU374Dwme8pYhkkClJQGCxhFSbVeOWBzug8ApEv9QYHT7hEQIcB5/KPZP4WURVJiN2UoscV4bbHeofSdys/4KHcHKrvdIRdkKkk+SqLKEcaTwVez6XM9a+fquhAt97gjJ6rxCzSqkD2RfylwZ6DTjdDdELV+fj+ccnmGpvXpVst99xNC4ReCtHDgDQ+M2fazDgtz9jiPGpoVQ8vz1WKrJTYF5MROwDfzxw750LOjC16b5apyywR8AOkjUFWSITEBy8YUy9e0//aBoAfrEssyYcvOoJFPk2FI09JIAxHmnpEuEeKoYL20haAYfSs+i++4fYFU/AxP0b18wE9E8kawsL9BUl2C+G2xvqH7nmjyU224/T4JeeORn9XPj00FGv1rLMVDi4KwPsJWkVbSgNyGOh6FBfAADcgPswadTm4+JQpCs14R5ZPzIyU2zbnHd++9Nm+toXBeF43EEcnwhwKLHZ3qYMfASwPhtkhRZ5BECfAgABfy8oJk1QvVFfV9aZarMKPweAida1K0g8mt8RTtb++Ot0cd7ngJGItGynwuseeY5DMAXMHcKG6NA3FP0mIPkbjGgC2eOa1aPJSMu+sXbLa+BUVW8DWeETcMzfXCzLTETsF7dE7AuK6jOSG/NBcbToXk64+7M0PlxsXbsiWFW9G2BXwenPklwH9BOh6FBfItLyHakenAtMTo9dD6+Lxx0ASG2ymzLlOANwdUG5iAPgaBnc9+qi5z3H570HUm1WjTaDuwXogv9giv5gxpH95aa6BNIAAK3lcHgg9kIuJdm+4WUoHPQRp5XIYWdGulefHb5czDXvTXjH2fifAPal2qwPdUWwQwRdIOsgiuUmngRheA2K7adMEwREbmiRXoMzPQ0D819CCzownyOzZtV2pdyT1OVfC7FhbneXP47G1rwN6FzuudbWsrsq3V2SkRPhM0Pji/Uu6X8gO/mMGOfqROP9xoHB10rpUYzSpqFWT9MnmjJ77GbpSy8AaMstRDAYOn0+drsCFh3HfhhaPSvQO7SirhKUNPeXsYz/LP4Gk8OElv5Vn3MAAAAASUVORK5CYII='


def parse_XML(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        xml_string = ET.tostring(root).decode("UTF-8")  # Converts the read xml file to a string
        window["-OUTPUT_XML_FILE-"].update(xml_string)  # Prints the xml file in the output window

        # Get tags in XML File:
        tags_xml = [element.tag for element in root.iter()]
        tags_to_set = set(tags_xml)
        tags_to_list = list(tags_to_set)
        # Add Elements to ComboBox List
        window["-XML_TAG_NAME-"].update(values=tags_to_list)
    except Exception as e:
        window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in program: {e}")


def get_tag_values(xml_file, tag):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tag_value = []
        for element in root.iter(tag):  # Add Parameter in Function later for root.iter(parameter)
            tag_value.append(element.text)
        return list(set(tag_value))
    except ValueError as e:
        window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in Program {e}")


def get_attributes(xml_file, tag):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        attributes = []
        for element in root.iter(tag):
            attributes.extend(element.attrib.keys())
        return list(set(attributes))
    except ValueError as e:
        window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in Program {e}")


def get_attribute_values(xml_file, tag, attribute):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        attribute_value_list = []
        for element in root.iter(tag):
            attribute_value = element.attrib.get(attribute)
            if attribute_value is not None:
                attribute_value_list.append(attribute_value)
        return list(set(attribute_value_list))
    except ValueError as e:
        window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in Program {e}")


def evaluate_xml_files_matching(folder_path, matching_filters):
    try:
        final_results = []
        total_files = sum(1 for filename in os.listdir(folder_path) if filename.endswith('.xml'))
        progress_increment = 100 / total_files
        current_progress = 0
        window['-PROGRESS_BAR-'].update(current_progress)
        total_sum_matches = 0
        total_matching_files = 0
        
        for filename in os.listdir(folder_path):
            if filename.endswith('.xml'):
                file_path = os.path.join(folder_path, filename)
                # Update progress bar after processing each file
                current_progress += progress_increment
                window['-PROGRESS_BAR-'].update(current_progress)
                try:
                    tree = ET.parse(file_path)
                    total_matches = 0  # Initialize total matches for the file

                    print(f"Evaluating file: {filename}")

                    for expression in matching_filters:
                        result = tree.findall(expression)
                        total_matches += len(result)
                    total_sum_matches += total_matches # Sum together all matches
                    if total_matches > 0:  # Only append if there are any matches
                        final_results.append({"Filename": filename, "Total Matches": total_matches})
                        total_matching_files += 1   
                except Exception as e:
                    window["-OUTPUT_WINDOW_MAIN-"].update(f"Error processing {filename}, Error: {e}")
        return final_results, total_sum_matches, total_matching_files
    except Exception as e:
        window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in Program {e}")
        

def export_evaluation_as_csv(csv_output_path, folder_path, matching_filters):
    try:
        matching_results, total_matches_found, total_matching_files = evaluate_xml_files_matching(folder_path, matching_filters)

        # Save matching results to CSV file
        if matching_results:  # Check if matching results exist and logging message doesn't     
               
            with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Filename", "Total Matches"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                # Write matching results
                for match in matching_results:
                   
                    writer.writerow(match)
            window["-OUTPUT_WINDOW_MAIN-"].update(f"Matches saved to {csv_output_path}\nFound {total_matching_files} files that have a total sum of {total_matches_found} matches.")
        else:
            window["-OUTPUT_WINDOW_MAIN-"].update("No matches found.")
            window["-PROGRESS_BAR-"].update(0)
    except Exception as e:
        window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in Program {e}")

my_custom_theme = {
    "BACKGROUND": "#2d3039",
    "TEXT": "white",
    "INPUT": "#535360",
    "TEXT_INPUT": "white",
    "SCROLL": "#333",
    "BUTTON": ("#FFC857", "#626271"),
    "PROGRESS": ("#FFC857", "#ABABAB"),
    "BORDER": 2,
    "SLIDER_DEPTH": 1,
    "PROGRESS_DEPTH": 1,
}

# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new("MyTheme", my_custom_theme)

sg.theme("MyTheme")

font = ("Calibri", 12)

FILE_TYPE_XML = (('XML (Extensible Markup Language)', '.xml'),)
MENU_RIGHT_CLICK_DELETE = ["&Right", ["&Delete", "&Delete All"]]
# Combobox Lists
tag_name = []
tag_value = []
attribute_name = []
attribute_value = []
# Listbox Lists
matching_filters_listbox = []

layout_listbox_matching_filter = [[sg.Listbox(values=matching_filters_listbox, size=(60, 5), enable_events=True,expand_x=True, key="-MATCHING_FILTER_LIST-")],
                                  [sg.Text("Add a XPath Filter for matching in the XML Files:", expand_x=True),sg.Button("Add to Matching", key="-ADD_TO_MATCHING-")]]

layout_xml_eval = [[sg.Text("Multi-XML File Iteration in a Folder:", pad=5)],
                   [sg.Input(size=(36, 2), font="Arial 10", expand_x=True, key="-FOLDER_EVALUATION_INPUT-"),sg.FolderBrowse(button_text="Browse Folder", target="-FOLDER_EVALUATION_INPUT-"),sg.Button("Read XML", key="-READ_XML-")],
                   [sg.Text("Filtering Options for XML Evaluation:", pad=5)],
                   [sg.Text("Tag name:"),sg.Combo(tag_name, size=(15, 1), disabled=True, auto_size_text=False, enable_events=True,enable_per_char_events=True, expand_x=True, key="-XML_TAG_NAME-"), sg.Text("Tag Value:"),sg.Combo(tag_value, size=(15, 1), disabled=True, enable_events=True, enable_per_char_events=True,auto_size_text=False, expand_x=True, key="-XML_TAG_VALUE-")],
                   [sg.Text("Att name:"),sg.Combo(attribute_name, size=(15, 1), disabled=True, auto_size_text=False, enable_events=True,expand_x=True, key="-XML_ATTRIBUTE_NAME-"), sg.Text("Att Value:"),sg.Combo(attribute_value, size=(15, 1), disabled=True, enable_events=True, auto_size_text=False,expand_x=True, key="-XML_ATTRIBUTE_VALUE-", pad=5)],
                   [sg.Text("XPath Expression:"), sg.Input(size=(14, 1), expand_x=True, key="-XPATH_EXPRESSION-"),sg.Button("Build XPath", key="-XPATH_BUILD_MATCHING-")]]

layout_export_evaluation = [[sg.Text("Select a Path where you want to save the XML Evaluation:")],
                            [sg.Input(expand_x=True, font="Arial 10", key="-FOLDER_EVALUATION_OUTPUT-"),sg.SaveAs(button_text="Save as", file_types=(("Comma Seperated Value (.csv)", ".csv"),),target="-FOLDER_EVALUATION_OUTPUT-"),sg.Button("Export", key="-EXPORT_AS_CSV-")]]

layout_xml_output = [
    [sg.Multiline(size=(62,29), write_only=False, horizontal_scroll=True, key="-OUTPUT_XML_FILE-", pad=5)],
    [sg.Text("Progress:"),sg.ProgressBar(max_value=100, size=(20, 15), orientation="h", expand_x=True,key='-PROGRESS_BAR-', pad=11)]]

layout_output_main = [[sg.Multiline(size=(62, 5), key="-OUTPUT_WINDOW_MAIN-", pad=5)]]

frame_xml_eval = sg.Frame("XML Filters for Evaluation", layout_xml_eval, title_color="#FFC857", expand_x=True)
frame_export_evaluation = sg.Frame("Export Evaluation result as a CSV File", layout_export_evaluation, title_color="#FFC857",expand_x=True)
frame_xml_output = sg.Frame("XML Output", layout_xml_output, title_color="#FFC857", expand_x=True)
frame_output_main = sg.Frame("Program Output", layout_output_main, title_color="#FFC857", expand_x=True)
frame_listbox_matching_filter = sg.Frame("Filters to match in XML files", layout_listbox_matching_filter,title_color="#FFC857", expand_x=True)

layout = [[sg.Column(layout=[[frame_xml_eval], [frame_listbox_matching_filter],[frame_export_evaluation],[frame_output_main]], expand_y=True),sg.Column([[frame_xml_output]], expand_y=True)]]

window = sg.Window("XMLuvation", layout, font=font, icon=xml_32px, finalize=True)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    # BrowseFolder Input and Save As Input Elements
    evaluation_input_folder = values["-FOLDER_EVALUATION_INPUT-"]
    evaluation_output_folder = values["-FOLDER_EVALUATION_OUTPUT-"]

    # XML Combobox Element Values
    tag_name_combobox = values["-XML_TAG_NAME-"]
    tag_value_combobox = values["-XML_TAG_VALUE-"]
    attribute_name_combobox = values["-XML_ATTRIBUTE_NAME-"]
    attribute_value_combobox = values["-XML_ATTRIBUTE_VALUE-"]

    # XPath for XML Matching 
    xpath_expression_input = values["-XPATH_EXPRESSION-"]
    xpath_expression = ""

    # RegEx Matching
    file_path_regex = r'\.xml$'

    if event == "-READ_XML-":
        eval_input_file = sg.popup_get_file("Select an XML file", file_types=(("XML Files", "*.xml"),))
        if eval_input_file:
            window.perform_long_operation(lambda: parse_XML(eval_input_file), "-OUTPUT_WINDOW_MAIN-")
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
            selected_tag = tag_name_combobox
            attributes = get_attributes(eval_input_file, selected_tag)
            window["-XML_ATTRIBUTE_NAME-"].update(values=attributes)
            values_xml = get_tag_values(eval_input_file, selected_tag)
            window["-XML_TAG_VALUE-"].update(values=values_xml)
            # Disable tag value combo box if there are no values for the selected tag
            if not values_xml or all(value.strip() == '' for value in values_xml if value is not None):
                window["-XML_TAG_VALUE-"].update(disabled=True, values="")
            else:
                window["-XML_TAG_VALUE-"].update(disabled=False)
            # print(f"XML VALUES: {values_xml}")
            # print(type(values_xml))
            # Disable attribute name and value combo boxes if there are no attributes for the selected tag
            if not attributes:
                window["-XML_ATTRIBUTE_NAME-"].update(disabled=True, values="")
                window["-XML_ATTRIBUTE_VALUE-"].update(disabled=True, values=[])
            else:
                window["-XML_ATTRIBUTE_NAME-"].update(disabled=False)
                # print(f"ATTRIBUTE: {attributes}")
                # print(type(attributes))
        except Exception as e:
            window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in Program {e}")

    elif event == "-XML_ATTRIBUTE_NAME-":
        try:
            selected_tag = tag_name_combobox
            selected_attribute = attribute_name_combobox
            attribute_values = get_attribute_values(eval_input_file, selected_tag, selected_attribute)
            window["-XML_ATTRIBUTE_VALUE-"].update(values=attribute_values)

            # Disable attribute value combo box if there are no attribute values
            if not attribute_values:
                window["-XML_ATTRIBUTE_VALUE-"].update(disabled=True, values=[])
                window["-XML_ATTRIBUTE_NAME-"].update(disabled=True, values=[])
            else:
                window["-XML_ATTRIBUTE_VALUE-"].update(disabled=False)
                # print(f"ATTRIBUTE VALUES: {attribute_values}")
                # print(type(values_xml))

            # Disable tag value combo box if the selected tag has no values
            if not values_xml:
                window["-XML_TAG_VALUE-"].update(disabled=True, values="")
        except Exception as e:
            window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in Program: {e}")

    elif event == "-XPATH_BUILD_MATCHING-":
        try:
            tree = ET.parse(eval_input_file)
            xpath_expression = ".//" + tag_name_combobox

            if tag_value_combobox:
                xpath_expression += f"[text()='{tag_value_combobox}']"

            if attribute_name_combobox:
                if attribute_value_combobox:
                    xpath_expression += f"[@{attribute_name_combobox}='{attribute_value_combobox}']"
                else:
                    xpath_expression += f"[@{attribute_name_combobox}]"

            window["-XPATH_EXPRESSION-"].update(xpath_expression)
            if xpath_expression != "":
                window["-OUTPUT_WINDOW_MAIN-"].print(f"Final XPath expression: {xpath_expression}")
        except NameError:
            window["-OUTPUT_WINDOW_MAIN-"].update("Name 'parsed_xml_file' is not defined")

    elif event == "-ADD_TO_MATCHING-":
        try:
            if not xpath_expression_input:
                window["-OUTPUT_WINDOW_MAIN-"].update("No XPath expression entered.")
            else:
                matching_filters_listbox.append(xpath_expression_input)
                window["-MATCHING_FILTER_LIST-"].update(values=matching_filters_listbox)
                window["-OUTPUT_WINDOW_MAIN-"].update(f"XPath expression added: {xpath_expression_input}")
        except Exception as e:
            window["-OUTPUT_WINDOW_MAIN-"].update(f"Error adding filter: {e}")

    elif event == "-EXPORT_AS_CSV-":
        try:
            window.perform_long_operation(lambda: export_evaluation_as_csv(evaluation_output_folder, evaluation_input_folder, matching_filters_listbox), "-OUTPUT_WINDOW_MAIN-")
        except Exception as e:
            window["-OUTPUT_WINDOW_MAIN-"].update(f"Error exporting CSV: {e}")

window.close()  # Kill Programm
