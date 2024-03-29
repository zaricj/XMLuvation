import csv
import os
import re
import webbrowser
from pathlib import Path
import PySimpleGUI as sg
import pandas as pd
from lxml import etree as ET

xml_32px = b"iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAA8pJREFUWIXtVl1oHFUYPefOJpNkQ9omJps11mIZKkiTaQmEarMtguKDL4ot9adCQUVU0pBSRRBEpSiJUKlYxPTnrVUEhT5UCaKYbkqlVM0mNBTZaoNtuhuX/Ehbd5LZ+/mw2dnZNWm6NIhgztOd+X7OuWcu9xtgGcv4v4NL0eRcK8qaKu2dBNYpxWjDqcGv/lUByYj9KsgeABCRTIXo+pUDw5O3UquWQgCInfklRm+VfEkEJLY0NwNsyYuR46XU374Dwme8pYhkkClJQGCxhFSbVeOWBzug8ApEv9QYHT7hEQIcB5/KPZP4WURVJiN2UoscV4bbHeofSdys/4KHcHKrvdIRdkKkk+SqLKEcaTwVez6XM9a+fquhAt97gjJ6rxCzSqkD2RfylwZ6DTjdDdELV+fj+ccnmGpvXpVst99xNC4ReCtHDgDQ+M2fazDgtz9jiPGpoVQ8vz1WKrJTYF5MROwDfzxw750LOjC16b5apyywR8AOkjUFWSITEBy8YUy9e0//aBoAfrEssyYcvOoJFPk2FI09JIAxHmnpEuEeKoYL20haAYfSs+i++4fYFU/AxP0b18wE9E8kawsL9BUl2C+G2xvqH7nmjyU224/T4JeeORn9XPj00FGv1rLMVDi4KwPsJWkVbSgNyGOh6FBfAADcgPswadTm4+JQpCs14R5ZPzIyU2zbnHd++9Nm+toXBeF43EEcnwhwKLHZ3qYMfASwPhtkhRZ5BECfAgABfy8oJk1QvVFfV9aZarMKPweAida1K0g8mt8RTtb++Ot0cd7ngJGItGynwuseeY5DMAXMHcKG6NA3FP0mIPkbjGgC2eOa1aPJSMu+sXbLa+BUVW8DWeETcMzfXCzLTETsF7dE7AuK6jOSG/NBcbToXk64+7M0PlxsXbsiWFW9G2BXwenPklwH9BOh6FBfItLyHakenAtMTo9dD6+Lxx0ASG2ymzLlOANwdUG5iAPgaBnc9+qi5z3H570HUm1WjTaDuwXogv9giv5gxpH95aa6BNIAAK3lcHgg9kIuJdm+4WUoHPQRp5XIYWdGulefHb5czDXvTXjH2fifAPal2qwPdUWwQwRdIOsgiuUmngRheA2K7adMEwREbmiRXoMzPQ0D819CCzownyOzZtV2pdyT1OVfC7FhbneXP47G1rwN6FzuudbWsrsq3V2SkRPhM0Pji/Uu6X8gO/mMGOfqROP9xoHB10rpUYzSpqFWT9MnmjJ77GbpSy8AaMstRDAYOn0+drsCFh3HfhhaPSvQO7SirhKUNPeXsYz/LP4Gk8OElv5Vn3MAAAAASUVORK5CYII="
logo = "./images/logo.png"
pandas_font = "Calibri 13 bold"


# ========== FUNCTIONS ========== #
def convert_csv_file(input_file, output_file, input_ext, output_ext, ):
    """Converts the selected CSV File to the supported extension types with the Pandas module

    Args:
        input_file (str): Folder Path of CSV File
        output_file (str): Folder Path where the Converted CSV File should be saved
        input_ext (str): CSV Extension Suffix
        output_ext (str): To be converted to Extension Type Suffix
    """
    try:
        window["-CONVERT_CSV_FILE-"].update(disabled=True)

        with open(input_file) as file:  # Get Delimiter
            sample = file.read(4096)
            sniffer = csv.Sniffer()
            get_delimiter = sniffer.sniff(sample).delimiter
            print(f"Delimiter: {get_delimiter}")

        if not values["-CHECKBOX_WRITE_INDEX_COLUMN-"]:
            csv_df = pd.read_csv(input_file, delimiter=get_delimiter, encoding="utf-8", index_col=0)
        else:
            csv_df = pd.read_csv(input_file, delimiter=get_delimiter, encoding="utf-8")

        # Mapping of csv file to corresponding write functions
        CONVERSION_FUNCTIONS = {
            # CSV Conversion
            ("csv", "html"): (csv_df, pd.DataFrame.to_html),
            ("csv", "json"): (csv_df, pd.DataFrame.to_json),
            ("csv", "xlsx"): (csv_df, pd.DataFrame.to_excel),
            ("csv", "md"): (csv_df, pd.DataFrame.to_markdown),
        }

        read_func, write_func = CONVERSION_FUNCTIONS.get((input_ext, output_ext), (None, None))

        if read_func is None or write_func is None:
            window["-OUTPUT_WINDOW_CSV-"].update("Unsupported conversion!", text_color="#ff4545", font=pandas_font)
            return

        csv_df = read_func
        write_func(csv_df, output_file)
        window["-OUTPUT_WINDOW_CSV-"].update(
            f"Successfully converted {Path(input_file).stem} {input_ext.upper()} to {Path(output_file).stem} {output_ext.upper()}",
            text_color="#51e98b", font=pandas_font)
        window["-CONVERT_CSV_FILE-"].update(disabled=False)

    except FileNotFoundError:
        window["-OUTPUT_WINDOW_CSV-"].update(f"{input_ext.upper()} File not found!", text_color="#ff4545",
                                             font=pandas_font)
        window["-CONVERT_CSV_FILE-"].update(disabled=False)

    except Exception as e:
        window["-OUTPUT_WINDOW_CSV-"].update(f"ERROR: {e}", text_color="#ff4545", font=pandas_font)
        window["-CONVERT_CSV_FILE-"].update(disabled=False)


def read_csv_data(csv_file):
    """Reads CSV File and displays it's data as a DataFrame

    Args:
        csv_file (str): Path to CSV File
    Raises:
        ValueError: ValueError Exception gets risen if no input folder has been set

    Returns:
        dataframe: Returns CSV file as a Pandas DataFrame 
    """
    try:
        file_suffix_in_input = Path(csv_file).suffix.upper().strip(".")

        with open(csv_file) as file:  # Get Delimiter
            sample = file.read(4096)
            sniffer = csv.Sniffer()
            get_delimiter = sniffer.sniff(sample).delimiter

        if not values["-CHECKBOX_WRITE_INDEX_COLUMN-"]:
            csv_df = pd.read_csv(input_file, delimiter=get_delimiter, encoding="utf-8", index_col=0)
        else:
            csv_df = pd.read_csv(input_file, delimiter=get_delimiter, encoding="utf-8")

        if file_suffix_in_input == "":
            raise ValueError("Error: Input is empty. Cannot read nothing!")

        if csv_df is not None:
            window["-OUTPUT_WINDOW_CSV-"].update(csv_df, text_color="white")
            return csv_df
        else:
            return None, []

    except FileNotFoundError as e:
        window["-OUTPUT_WINDOW_CSV-"].update(f"ERROR: {e}", text_color="#ff4545", font=pandas_font)
        return None, []


def parse_xml(xml_file):
    """Reads XML file and adds elements to the tag name Combobox GUI element

    Args:
        xml_file (str): Single XML File
    """
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
        if not tag:
            pass
        return list(set(tag_value))
    except ValueError:
        pass


def get_attributes(xml_file, tag):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        attributes = []
        for element in root.iter(tag):
            attributes.extend(element.attrib.keys())
        return list(set(attributes))
    except ValueError:
        pass


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
    except ValueError:
        pass


def evaluate_xml_files_matching(folder_path, matching_filters):
    """Evaluates and searches for matches in XML files

    Args:
        folder_path (str): Folder path where one or more XML files are located
        matching_filters (list): Added XPath filters in the ListBox GUI element

    Returns:
        list: Returns list of added filter(s) to match to and evaluate one or more XML Files
    """
    final_results = []
    total_files = sum(1 for filename in os.listdir(folder_path) if filename.endswith('.xml'))
    progress_increment = 100 / total_files
    current_progress = 0
    window['-PROGRESS_BAR-'].update(current_progress)
    total_sum_matches = 0
    total_matching_files = 0

    try:
        for filename in os.listdir(folder_path):
            if filename.endswith('.xml'):
                file_path = os.path.join(folder_path, filename)
                # Update progress bar after processing each file
                current_progress += progress_increment
                window['-PROGRESS_BAR-'].update(round(current_progress, 2))
                window["-OUTPUT_WINDOW_MAIN-"].update(f"Processing {filename}")

                try:
                    tree = ET.parse(file_path)
                except ET.XMLSyntaxError as e:
                    if "Document is empty" in str(e):
                        window["-OUTPUT_WINDOW_MAIN-"].update(
                            f"Error processing {filename}\nXML File is empty, skipping file...")
                        continue  # Skip processing this file
                    else:
                        window["-OUTPUT_WINDOW_MAIN-"].update(f"XMLSyntaxError occurred: {e}")
                        continue

                total_matches = 0  # Initialize total matches for the file
                current_file_results = {"Filename": os.path.splitext(filename)[0]}
                # print(f"LENGTH OF MATCHING FILTERS LIST: {len(matching_filters)}")

                if len(matching_filters) == 1:

                    for expression in matching_filters:
                        result = tree.xpath(expression)
                        total_matches += len(result)

                        if result:

                            if "@" in expression:
                                # Code for handling attribute expressions
                                match = re.search(r"@([^=]+)=", expression)
                                if match:
                                    attribute_name_string = match.group(
                                        1).strip()  # Id, Description, Name etc (Attribute Name of Selected Tag)
                                    for element in result:
                                        attr_value = element.get(attribute_name_string)
                                        #print(f"Attribute Value in @ - = {attr_value}") # Uselful print if a filename has multiple filter in it for match
                                        if attr_value and attr_value.strip():  # Check if not None or empty
                                            current_file_results[f"Filter {attribute_name_string}"] = attr_value
                                else:
                                    match = re.search(r"@([^=]+),", expression)
                                    if match:
                                        attribute_name_string = match.group(1).strip()
                                        for element in result:
                                            attr_value = element.get(attribute_name_string)
                                            #print(f"Attribute Value in @ - , {attr_value}") # Uselful print if a filename has multiple filter in it for match
                                            if attr_value and attr_value.strip():  # Check if not None or empty
                                                current_file_results[f"Filter {attribute_name_string}"] = attr_value

                            if "text()=" in expression:
                                # Code for handling text() expressions
                                match = re.search(r"//(.*?)\[", expression)
                                if match:
                                    tag_name_string = match.group(1).strip()
                                    print(f"Tag_name_string: {tag_name_string}")
                                    for element in result:
                                        tag_value = element.text
                                        print(f"Tag value: {tag_value}")
                                        if tag_value and tag_value.strip():  # Check if not None or empty
                                            current_file_results[f"Filter {tag_name_string}"] = tag_value

                        current_file_results["Total Matching Tags"] = total_matches

                if len(matching_filters) > 1:

                    attribute_matches_dic = {}
                    tag_matches_dic = {}

                    for expression in matching_filters:
                        result = tree.xpath(expression)
                        matches_count = len(result)
                        total_matches += len(result)

                        if result:

                            if "@" in expression:  # Code for handling attribute expressions
                                match = re.search(r"@([^=]+)=", expression)
                                if match:
                                    attribute_name_string = match.group(1).strip()
                                    for element in result:
                                        attr_value = element.get(attribute_name_string)
                                        if attr_value and attr_value.strip():  # Check if not None or empty
                                            attribute_matches_dic[
                                                f"{attribute_name_string}={attr_value}"] = matches_count

                                else:
                                    match = re.search(r"@([^=]+),", expression)
                                    if match:
                                        attribute_name_string = match.group(1).strip()
                                        for element in result:
                                            attr_value = element.get(attribute_name_string)
                                            if attr_value and attr_value.strip():  # Check if not None or empty
                                                attribute_matches_dic[
                                                    f"{attribute_name_string}={attr_value}"] = matches_count

                                for attribute, attr_count in attribute_matches_dic.items():
                                    current_file_results[f"Filter {attribute} Matches"] = attr_count

                            elif "text()=" in expression:
                                # Code for handling text() expressions
                                match = re.search(r"//(.*?)\[", expression)
                                if match:
                                    tag_name_string = match.group(1).strip()
                                    for element in result:
                                        tag_value = element.text
                                        if tag_value and tag_value.strip():  # Check if not None or empty
                                            tag_matches_dic[f"{tag_name_string} {tag_value}"] = matches_count

                                for tag, tag_count in tag_matches_dic.items():
                                    current_file_results[f"Filter {tag} Matches"] = tag_count

                if total_matches > 0:
                    final_results.append(current_file_results)

                total_sum_matches += total_matches
                total_matching_files += 1 if total_matches > 0 else 0

        return final_results, total_sum_matches, total_matching_files

    except ZeroDivisionError:
        pass


def replace_empty_with_zero(value):
    """_summary_

    Args:
        value (str): Values of matches which will be written in the appropriate column name

    Returns:
        str: Returns 0 as value for CSV rows, which are empty
    """
    return value if value != '' else '0'


def export_evaluation_as_csv(csv_output_path, folder_path, matching_filters):
    """Export found XML files and it's matches in a single CSV file

    Args:
        csv_output_path (str): Folder Path where the evaluation should be exported to
        folder_path (str): Folder Path where one or more XML files are located
        matching_filters (list): Added XPath filters in the ListBox GUI element
    """
    try:
        window["-EXPORT_AS_CSV-"].update(disabled=True)
        matching_results, total_matches_found, total_matching_files = evaluate_xml_files_matching(folder_path,
                                                                                                  matching_filters)

        # Save matching results to CSV file
        if matching_results is not None:  # Check if matching results exist
            headers = [key for key in {key: None for dic in matching_results for key in dic}]
            #print("Headers:", headers)

            with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = headers
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()

                # Write matching results
                for match in matching_results:
                    if match is not None:  # If None, skip
                        matches = {header: replace_empty_with_zero(match.get(header, '')) for header in
                                             headers}
                        #print("Matches:", matches)
                        writer.writerow(matches)
                csvfile.close()

            window["-OUTPUT_WINDOW_MAIN-"].update(
                f"Matches saved to {csv_output_path}\nFound {total_matching_files} "
                f"files that have a total sum of {total_matches_found} matches.")
            window["-EXPORT_AS_CSV-"].update(disabled=False)
            window['-PROGRESS_BAR-'].update(0)
        else:
            window["-OUTPUT_WINDOW_MAIN-"].update("No matches found.")
            window["-PROGRESS_BAR-"].update(0)
            window["-EXPORT_AS_CSV-"].update(disabled=False)
            window['-PROGRESS_BAR-'].update(0)

    except TypeError as e:
        window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in program: {e}")
        window["-EXPORT_AS_CSV-"].update(disabled=False)
        window['-PROGRESS_BAR-'].update(0)


def is_duplicate(xpath_expression):
    return xpath_expression in matching_filters_listbox


my_custom_darker_theme = {
    "BACKGROUND": "#191e26",
    "TEXT": "white",
    "INPUT": "#36373d",
    "TEXT_INPUT": "white",
    "SCROLL": "#36373d",
    "BUTTON": ("#FFC857", "#36373d"),
    "PROGRESS": ("#FFC857", "#ABABAB"),
    "BORDER": 2,
    "SLIDER_DEPTH": 1,
    "PROGRESS_DEPTH": 1,
}

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
sg.theme_add_new("MyTheme", my_custom_darker_theme)
sg.theme("MyTheme")
font = ("Calibri", 13)

# Constants
FILE_TYPE_XML = (("XML (Extensible Markup Language)", ".xml"),)
MENU_RIGHT_CLICK_DELETE = ["&Right", ["&Delete", "&Delete All"]]
MENU_DEFINITION = [["&File", ["&Open Output Folder::OpenOutputFolder", "---", "E&xit"]],
                   ["&Help", ["&XPath Help::XPathSyntaxURL", "XPath Cheat Sheet::XPathCheatSheet"]]]
# Constants for Pandas Conversion
FILE_TYPES_INPUT = (("CSV (Comma Separated Value)", ".csv"),)
FILE_TYPES_OUTPUT = (
    ("XLSX (Excel Sheet)", ".xlsx"), ("MD (Markdown README)", ".md"), ("HTML (Hypertext Markup Language)", ".html"),
    ("JSON (JavaScript Object Notation)", ".json"))

# Combobox Lists
tag_name = []
tag_value = []
attribute_name = []
attribute_value = []
# Listbox List
matching_filters_listbox = []

# ========== START Layout for Pandas Conversion START ========== #
layout_pandas_conversion = [[sg.Text("CSV Converter", font="Calibri 36 bold underline", text_color="#578fff", pad=10,
                                     justification="center", grab=True)],
                            [sg.Text(
                                "Convert CSV File to a different file type with the Pandas module\nSupported output file types: Excel, Markdown. HTML and JSON",
                                justification="center")],
                            [sg.HSep(pad=10)],
                            [sg.Text("Choose a CSV file for conversion:")],
                            [sg.Input(size=(44, 1), key="-FILE_INPUT-"),
                             sg.FileBrowse(file_types=FILE_TYPES_INPUT, size=(8, 1)),
                             sg.Button("Read CSV", size=(7, 1), key="-READ_FILE-")],
                            [sg.Text("Choose where to save output of CSV file:")],
                            [sg.Input(size=(44, 1), key="-FILE_OUTPUT-"),
                             sg.FileSaveAs(button_text="Save as", size=(7, 1), file_types=FILE_TYPES_OUTPUT,
                                           target="-FILE_OUTPUT-", key="-SAVE_AS_BUTTON-"),
                             sg.Button("Convert", key="-CONVERT_CSV_FILE-", expand_x=True)],
                            [sg.Checkbox("Write Index Column?", default=False, key="-CHECKBOX_WRITE_INDEX_COLUMN-")],
                            [sg.Image(source=logo, expand_x=True, expand_y=True, key="-IMAGE-")]]

layout_pandas_output = [
    [sg.Multiline(size=(59, 32), key="-OUTPUT_WINDOW_CSV-", disabled=True, horizontal_scroll=True)]]

frame_pandas = sg.Frame("CSV Conversion to different file type", layout_pandas_conversion, expand_x=True, expand_y=True,
                        title_color="#FFC857", font="Calibri 13 bold")
frame_pandas_output = sg.Frame("CSV Conversion Output", layout_pandas_output, expand_x=True, expand_y=True,
                               title_color="#FFC857", font="Calibri 13 bold")
# ========== END Layout for Pandas Conversion END ========== #

# ========== START Layout for XML Evaluation START ========== #
layout_xml_evaluation = [[sg.Menu(MENU_DEFINITION)],
                         [sg.Text("Choose a Folder that contains XML Files:", pad=5)],
                         [sg.Input(size=(36, 2), font="Arial 10", expand_x=True, key="-FOLDER_EVALUATION_INPUT-"),
                          sg.FolderBrowse(button_text="Browse Folder", target="-FOLDER_EVALUATION_INPUT-"),
                          sg.Button("Read XML", key="-READ_XML-")],
                         [sg.Text("Get XML Tag and Attribute Names/Values for XPath generation:", pad=5)],
                         [sg.Text("Tag name:"),
                          sg.Combo(tag_name, size=(15, 1), disabled=True, auto_size_text=False, enable_events=True,
                                   enable_per_char_events=True, expand_x=True, key="-XML_TAG_NAME-"),
                          sg.Text("Tag Value:"),
                          sg.Combo(tag_value, size=(15, 1), disabled=True, enable_events=True,
                                   enable_per_char_events=True,
                                   auto_size_text=False, expand_x=True, key="-XML_TAG_VALUE-")],
                         [sg.Text("Att name:"),
                          sg.Combo(attribute_name, size=(15, 1), disabled=True, auto_size_text=False,
                                   enable_events=True,
                                   expand_x=True, key="-XML_ATTRIBUTE_NAME-"), sg.Text("Att Value:"),
                          sg.Combo(attribute_value, size=(15, 1), disabled=True, enable_events=True,
                                   auto_size_text=False,
                                   expand_x=True, key="-XML_ATTRIBUTE_VALUE-", pad=5)],
                         [sg.Text("Function:"),
                          sg.Radio("Equals", group_id=1, default=True, key="-RADIO_DEFAULT-"),
                          sg.Radio("Contains", group_id=1, key="-RADIO_CONTAINS-"),
                          sg.Radio("Starts-with", group_id=1, key="-RADIO_STARTSWITH-"),
                          sg.Radio("Greater", group_id=1, key="-RADIO_GREATER-"),
                          sg.Radio("Smaller", group_id=1, key="-RADIO_SMALLER-")],
                         [sg.Text("XPath Expression:"), sg.Input(size=(14, 1), expand_x=True, key="-XPATH_EXPRESSION-"),
                          sg.Button("Build XPath", key="-BUILD_XPATH-")],
                         [sg.Text("Add XPath Expressions to look for and match in XML Files:", expand_x=True),
                          sg.Button("Add XPath Filter", key="-ADD_TO_MATCHING-")]]

layout_listbox_matching_filter = [[sg.Listbox(values=matching_filters_listbox, size=(60, 4), enable_events=True,
                                              expand_x=True, right_click_menu=MENU_RIGHT_CLICK_DELETE,
                                              key="-MATCHING_FILTER_LIST-")]]

layout_export_evaluation = [[sg.Text("Choose a folder where you want to save the XML Evaluation:")],
                            [sg.Input(expand_x=True, font="Arial 10", key="-FOLDER_EVALUATION_OUTPUT-"),
                             sg.SaveAs(button_text="Save as", file_types=(("Comma Separated Value (.csv)", ".csv"),),
                                       target="-FOLDER_EVALUATION_OUTPUT-"),
                             sg.Button("Export", key="-EXPORT_AS_CSV-")]]

layout_program_output = [[sg.Multiline(size=(62, 5), key="-OUTPUT_WINDOW_MAIN-", pad=10, disabled=True)]]

layout_xml_output = [
    [sg.Multiline(size=(58, 30), write_only=False, horizontal_scroll=True, key="-OUTPUT_XML_FILE-", pad=5)],
    [sg.Text("Progress:"),
     sg.ProgressBar(max_value=100, size=(20, 18), orientation="h", expand_x=True, key='-PROGRESS_BAR-', pad=11)]]

frame_xml_eval = sg.Frame("XML folder selection and XPath builder", layout_xml_evaluation, title_color="#FFC857",
                          expand_x=True, font="Calibri 13 bold")
frame_export_evaluation = sg.Frame("Export Evaluation result as a CSV File", layout_export_evaluation,
                                   title_color="#FFC857", expand_x=True, font="Calibri 13 bold")
frame_xml_output = sg.Frame("XML Output", layout_xml_output, title_color="#FFC857", expand_x=True, font="Calibri 13 bold")
frame_output_main = sg.Frame("Program Output", layout_program_output, title_color="#FFC857", expand_x=True, font="Calibri 13 bold")
frame_listbox_matching_filter = sg.Frame("Filters to match in XML files", layout_listbox_matching_filter,
                                         title_color="#FFC857", expand_x=True, font="Calibri 13 bold")
# ========== END Layout for XML Evaluation END ========== #

# layout = [[sg.Column(layout=[[frame_xml_eval], [frame_listbox_matching_filter],[frame_export_evaluation],[frame_output_main]], expand_y=True),sg.Column([[frame_xml_output]], expand_y=True)]] # DEPRACTED

# Build GUI Layout
layout = [
    [
        sg.TabGroup([
            [
                sg.Tab('XML Evaluation', [
                    [
                        sg.Column(
                            layout=[
                                [frame_xml_eval],
                                [frame_listbox_matching_filter],
                                [frame_export_evaluation],
                                [frame_output_main]
                            ],
                            expand_y=True
                        ),
                        sg.Column(
                            layout=[[frame_xml_output]],
                            expand_y=True
                        )
                    ]
                ]),
                sg.Tab('CSV Conversion', [
                    [
                        sg.Column(
                            layout=[
                                [frame_pandas]
                            ],
                            expand_y=True
                        ),
                        sg.Column(
                            layout=[
                                [frame_pandas_output]
                            ],
                            expand_y=True
                        )
                    ]
                ])
            ]
        ], selected_background_color="#FFC857", selected_title_color="#000000")
    ]
]

window = sg.Window("XMLuvation", layout, font=font, icon=xml_32px, finalize=True)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break

    # Pandas related variables
    input_file = values["-FILE_INPUT-"]
    output_file = values["-FILE_OUTPUT-"]
    input_ext = Path(input_file).suffix.lower().strip(".")
    output_ext = Path(output_file).suffix.lower().strip(".")

    # Browse Folder and Save As input elements
    evaluation_input_folder = values["-FOLDER_EVALUATION_INPUT-"]  # Browse Folder
    evaluation_output_folder = values["-FOLDER_EVALUATION_OUTPUT-"]  # Save As

    # XML Combobox element values
    tag_name_combobox = values["-XML_TAG_NAME-"]
    tag_value_combobox = values["-XML_TAG_VALUE-"]
    attribute_name_combobox = values["-XML_ATTRIBUTE_NAME-"]
    attribute_value_combobox = values["-XML_ATTRIBUTE_VALUE-"]

    # XPath input element for XML matching 
    xpath_expression_input = values["-XPATH_EXPRESSION-"]
    xpath_expression = ""

    # Radio button elements
    radio_default = values["-RADIO_DEFAULT-"]
    radio_contains = values["-RADIO_CONTAINS-"]
    radio_startswith = values["-RADIO_STARTSWITH-"]
    radio_greater = values["-RADIO_GREATER-"]
    radio_smaller = values["-RADIO_SMALLER-"]

    # RegEx matching for only XML files
    file_path_regex = r'\.xml$'

    if event in ("Delete", "Delete All"):
        try:
            if event == "Delete":
                selected_indices = window["-MATCHING_FILTER_LIST-"].get_indexes()

                for index in selected_indices:
                    matching_filters_listbox.pop(index)
                    window["-MATCHING_FILTER_LIST-"].update(values=matching_filters_listbox)

            elif event == "Delete All":
                matching_filters_listbox.clear()
                window["-MATCHING_FILTER_LIST-"].update(values=matching_filters_listbox)

        except UnboundLocalError:
            window["-OUTPUT_WINDOW_MAIN-"].update("ERROR: To delete a filter from the Listbox, select it first.")

    elif event == "XPath Help::XPathSyntaxURL":
        webbrowser.open("https://www.w3schools.com/xml/xpath_syntax.asp")
    
    elif event == "XPath Cheat Sheet::XPathCheatSheet":
        excel_sheet = "./cheatsheet/XPath_Syntax.xlsx"
        read = pd.read_excel(excel_sheet).to_dict()
        
        table = pd.DataFrame(read)
        head = list(read)
        values = table.values.tolist()
        # Set column widths for empty record of table
        layout_table = [[sg.Table(values=values, headings=head, auto_size_columns=False,
        col_widths=list(map(lambda x:len(x)+1, head)), expand_x=True, expand_y=True, justification="left")]]
        
        window2 = sg.Window('Sample excel file',  layout_table, resizable=True, size=(1200,600), font="Calibri 13")
        event, value = window2.read()

    elif event == "Open Output Folder::OpenOutputFolder":
        output_folder = evaluation_output_folder
        if output_folder:
            directory_path = os.path.dirname(output_folder)
            windows_path = directory_path.replace("/", "\\")
            os.startfile(windows_path)
    
    elif event == "-IMAGE-":
    # update the animation in the window
        window['-IMAGE-'].update_animation(logo,  time_between_frames=100)

    elif event == "-READ_XML-":
        eval_input_file = sg.popup_get_file("Select a XML file to fill out the Name/Value boxes.",
                                            file_types=(("XML (Extensible Markup Language )", "*.xml"),))
        if eval_input_file:
            window.perform_long_operation(lambda: parse_xml(eval_input_file), "-OUTPUT_WINDOW_MAIN-")
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

    elif event == "-CONVERT_CSV_FILE-":
        window.perform_long_operation(lambda: convert_csv_file(input_file, output_file, input_ext, output_ext),
                                      "-OUTPUT_WINDOW_CSV-")

    elif event == "-READ_FILE-":
        window.perform_long_operation(lambda: read_csv_data(input_file), "-OUTPUT_WINDOW_CSV-")

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

            # Disable attribute name and value combo boxes if there are no attributes for the selected tag
            if not attributes:
                window["-XML_ATTRIBUTE_NAME-"].update(disabled=True, values="")
                window["-XML_ATTRIBUTE_VALUE-"].update(disabled=True, values=[])
            else:
                window["-XML_ATTRIBUTE_NAME-"].update(disabled=False)

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

            # Disable tag value combo box if the selected tag has no values
            if not values_xml:
                window["-XML_TAG_VALUE-"].update(disabled=True, values="")

        except Exception as e:
            window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in Program: {e}")

    elif event in ("-BUILD_XPATH-", "-RADIO_DEFAULT-", "-RADIO_CONTAINS-", "-RADIO_STARTSWITH-", "-RADIO_GREATER-", "-RADIO_SMALLER-"):
        try:
            # Initialize XPath expression
            xpath_expression = "//" + tag_name_combobox if tag_name_combobox else ""

            # Determine XPath criteria based on selected radio button
            if radio_default:
                xpath_criteria = []
                if tag_value_combobox:
                    xpath_criteria.append(f"text()='{tag_value_combobox}'")
                if attribute_name_combobox:
                    if attribute_value_combobox:
                        xpath_criteria.append(f"@{attribute_name_combobox}='{attribute_value_combobox}'")
                    else:
                        xpath_criteria.append(f"@{attribute_name_combobox}")

            elif radio_contains:
                xpath_criteria = []
                if tag_value_combobox:
                    xpath_criteria.append(f"contains(text(), '{tag_value_combobox}')")
                if attribute_name_combobox:
                    if attribute_value_combobox:
                        xpath_criteria.append(f"contains(@{attribute_name_combobox}, '{attribute_value_combobox}')")
                    else:
                        xpath_criteria.append(f"@{attribute_name_combobox}")

            elif radio_startswith:
                xpath_criteria = []
                if tag_value_combobox:
                    xpath_criteria.append(f"starts-with(text(), '{tag_value_combobox}')")
                if attribute_name_combobox:
                    if attribute_value_combobox:
                        xpath_criteria.append(f"starts-with(@{attribute_name_combobox}, '{attribute_value_combobox}')")
                    else:
                        xpath_criteria.append(f"@{attribute_name_combobox}")

            elif radio_greater:
                xpath_criteria = []
                if tag_value_combobox:
                    xpath_criteria.append(f"text() > {tag_value_combobox}")
                if attribute_name_combobox:
                    if attribute_value_combobox:
                        xpath_criteria.append(f"@{attribute_name_combobox} > {attribute_value_combobox}")
                    else:
                        xpath_criteria.append(f"@{attribute_name_combobox}")

            elif radio_smaller:
                xpath_criteria = []
                if tag_value_combobox:
                    xpath_criteria.append(f"text() < {tag_value_combobox}")
                if attribute_name_combobox:
                    if attribute_value_combobox:
                        xpath_criteria.append(f"@{attribute_name_combobox} < {attribute_value_combobox}")
                    else:
                        xpath_criteria.append(f"@{attribute_name_combobox}")

            # Append XPath criteria to expression
            if xpath_criteria:
                xpath_expression += "[" + " and ".join(xpath_criteria) + "]"

            # Update XPath expression and output window
            window["-XPATH_EXPRESSION-"].update(xpath_expression)
            if xpath_expression:
                window["-OUTPUT_WINDOW_MAIN-"].update(f"Final XPath expression: {xpath_expression}")

        except NameError:
            window["-OUTPUT_WINDOW_MAIN-"].update("Name 'parsed_xml_file' is not defined")


    elif event == "-ADD_TO_MATCHING-":
        try:
            if not xpath_expression_input:
                window["-OUTPUT_WINDOW_MAIN-"].update("No XPath expression entered.")


            elif xpath_expression_input and not is_duplicate(xpath_expression_input):
                matching_filters_listbox.append(xpath_expression_input)
                window["-MATCHING_FILTER_LIST-"].update(values=matching_filters_listbox)
                window["-OUTPUT_WINDOW_MAIN-"].update(f"XPath expression added: {xpath_expression_input}")
            elif is_duplicate(xpath_expression_input):
                window["-OUTPUT_WINDOW_MAIN-"].update(
                    f"Duplicate XPath expression {xpath_expression_input} is already in the list.")

        except Exception as e:
            window["-OUTPUT_WINDOW_MAIN-"].update(f"Error adding filter: {e}")

    elif event == "-EXPORT_AS_CSV-":
        try:
            if not os.path.exists(os.path.dirname(evaluation_input_folder)):
                window["-OUTPUT_WINDOW_MAIN-"].update(
                    "Folder Path that contains XML Files is either empty or not a valid path!")

            elif not len(matching_filters_listbox) > 0:
                window["-OUTPUT_WINDOW_MAIN-"].update("No filters for matching added, please add one as XPath!")

            elif not os.path.exists(os.path.dirname(evaluation_output_folder)):
                window["-OUTPUT_WINDOW_MAIN-"].update(
                    "Please select an Output Folder where the evaluation should be saved as a CSV file!")
            else:
                window.perform_long_operation(
                    lambda: export_evaluation_as_csv(evaluation_output_folder, evaluation_input_folder,
                                                     matching_filters_listbox), "-OUTPUT_WINDOW_MAIN-")
        except Exception as e:
            window["-OUTPUT_WINDOW_MAIN-"].update(f"Error exporting CSV: {e}")

window.close()  # Kill Program
