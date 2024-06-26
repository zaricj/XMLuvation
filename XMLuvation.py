import csv
import os
import re
import webbrowser
import pywinstyles
import FreeSimpleGUI as sg
import pandas as pd
from lxml import etree as ET
from pathlib import Path

PROGRAM_ICON = "_internal/icon/xml_32px.ico"
LOGO = "_internal/images/logo.png"
PANDAS_FONT = "Calibri 13 bold"


# ========== FUNCTIONS ========== #
def convert_csv_file(
    input_file,
    output_file,
    input_ext,
    output_ext,
):
    """Converts the selected CSV File to the supported extension types with the Pandas module

    Args:
        input_file (str): Folder Path of CSV File
        output_file (str): Folder Path where the Converted CSV File should be saved
        input_ext (str): CSV Extension Suffix
        output_ext (str): To be converted to Extension Type Suffix
    """
    try:
        window["-CONVERT_CSV_FILE-"].update(disabled=True)

        with open(input_file, encoding="utf-8") as file:  # Get Delimiter
            sample = file.read(4096)
            sniffer = csv.Sniffer()
            get_delimiter = sniffer.sniff(sample).delimiter
            # window["-OUTPUT_WINDOW_MAIN-"].update(f"Delimiter: {get_delimiter}")

        if not values["-CHECKBOX_WRITE_INDEX_COLUMN-"]:
            csv_df = pd.read_csv(
                input_file, delimiter=get_delimiter, encoding="utf-8", index_col=0
            )
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

        read_func, write_func = CONVERSION_FUNCTIONS.get(
            (input_ext, output_ext), (None, None)
        )

        if read_func is None or write_func is None:
            window["-OUTPUT_WINDOW_CSV-"].update(
                "Unsupported conversion!", text_color="#ff4545", font=PANDAS_FONT
            )
            return

        csv_df = read_func
        write_func(csv_df, output_file)
        window["-OUTPUT_WINDOW_CSV-"].update(
            f"Successfully converted {Path(input_file).stem} {input_ext.upper()} to {Path(output_file).stem} {output_ext.upper()}",
            text_color="#51e98b",
            font=PANDAS_FONT,
        )
        window["-CONVERT_CSV_FILE-"].update(disabled=False)

    except FileNotFoundError:
        window["-OUTPUT_WINDOW_CSV-"].update(
            f"{input_ext.upper()} File not found.",
            text_color="#ff4545",
            font=PANDAS_FONT,
        )
        window["-CONVERT_CSV_FILE-"].update(disabled=False)

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments: {1!r}"
        message = template.format(type(ex).__name__, ex.args)
        window["-OUTPUT_WINDOW_CSV-"].update(
            f"ERROR: {message}", text_color="#ff4545", font=PANDAS_FONT
        )
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

        try:
            if not values["-CHECKBOX_WRITE_INDEX_COLUMN-"]:
                csv_df = pd.read_csv(
                    input_file_pandas,
                    delimiter=get_delimiter,
                    encoding="utf-8",
                    index_col=0,
                )
            else:
                csv_df = pd.read_csv(
                    input_file_pandas, delimiter=get_delimiter, encoding="utf-8"
                )

        except UnicodeDecodeError:
            if not values["-CHECKBOX_WRITE_INDEX_COLUMN-"]:
                csv_df = pd.read_csv(
                    input_file_pandas,
                    delimiter=get_delimiter,
                    encoding="ansi",
                    index_col=0,
                )
            else:
                csv_df = pd.read_csv(
                    input_file_pandas, delimiter=get_delimiter, encoding="ansi"
                )

        if file_suffix_in_input == "":
            raise ValueError("Error: Input is empty. Cannot read nothing.")

        if csv_df is not None:
            window["-OUTPUT_WINDOW_CSV-"].update(csv_df, text_color="white")
            return csv_df
        else:
            return None, []

    except FileNotFoundError as e:
        window["-OUTPUT_WINDOW_CSV-"].update(
            f"ERROR: {e}", text_color="#ff4545", font=PANDAS_FONT
        )
        return None, []

    except pd.errors.ParserError:
        window["-OUTPUT_WINDOW_MAIN-"].update(
            "ERROR: Cannot Parse such CSV file which has a list of values in row"
        )


def parse_xml(xml_file):
    """Reads XML file and adds elements to the tag name Combobox GUI element

    Args:
        xml_file (str): Single XML File
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        xml_string = ET.tostring(root).decode(
            "UTF-8"
        )  # Converts the read xml file to a string
        window["-OUTPUT_XML_FILE-"].update(
            xml_string
        )  # Prints the xml file in the output window
        # Get tags in XML File:
        tags_xml = [element.tag for element in root.iter()]
        tags_to_set = set(tags_xml)
        tags_to_list = list(tags_to_set)
        # Add Elements to ComboBox List
        window["-XML_TAG_NAME-"].update(values=tags_to_list)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments: {1!r}"
        message = template.format(type(ex).__name__, ex.args)
        window["-OUTPUT_WINDOW_MAIN-"].update(f"Exception in program: {message}")


def get_tag_values(xml_file, tag_name):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tag_value = []
        for element in root.iter(
            tag_name
        ):  # Add Parameter in Function later for root.iter(parameter)
            tag_value.append(element.text)
        if not tag_name:
            pass
        return list(set(tag_value))
    except ValueError:
        pass


def get_attributes(xml_file, tag_name):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        attributes = []
        for element in root.iter(tag_name):
            attributes.extend(element.attrib.keys())
        return list(set(attributes))
    except ValueError:
        pass


def get_attribute_values(xml_file, tag_name, attribute):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        attribute_value_list = []
        for element in root.iter(tag_name):
            attribute_value = element.attrib.get(attribute)
            if attribute_value is not None:
                attribute_value_list.append(attribute_value)
        return list(set(attribute_value_list))
    except ValueError:
        pass


def is_valid_xpath(expression):
    # Define valid patterns
    valid_patterns = [
        r"^/[\w]+$",  # /xml_element
        r"^//[\w]+$",  # //xml_element
        r"^//[\w]+\[@[\w]+\]$",  # //xml_element[@attribute]
        r"^//[\w]+\[@[\w]+='[^']*'\]$",  # //xml_element[@attribute='value']
        r"^//[\w]+\[@[\w]+!='[^']*'\]$",  # //xml_element[@attribute!='value']
        r"^//[\w]+\[@[\w]+='[^']*' and @[\w]+='[^']*'\]$",  # //xml_element[@attribute1='value1' and @attribute2='value2']
        r"^//[\w]+\[contains\(@[\w]+, '[^']*'\)\]$",  # //xml_element[contains(@attribute, 'substring')]
        r"^//[\w]+\[starts-with\(@[\w]+, '[^']*'\)\]$",  # //xml_element[starts-with(@attribute, 'substring')]
        r"^//[\w]+\[text\(\)='[^']*'\]$",  # //xml_element[text()='value']
        r"^//[\w]+\[contains\(text\(\), '[^']*'\)\]$",  # //xml_element[contains(text(), 'substring')]
        r"^//[\w]+\[starts-with\(text\(\), '[^']*'\)\]$",  # //xml_element[starts-with(text(), 'substring')]
        r"^//[\w]+\[number\(@[\w]+\) > [0-9]+\]$",  # //xml_element[number(@attribute) > 10]
        r"^//[\w]+\[number\(@[\w]+\) < [0-9]+\]$",  # //xml_element[number(@attribute) < 10]
        r"^//[\w]+/[\w]+/text\(\)$",  # //xml_element/xml_element/text()
        r"^//[\w]+/[\w]+\[@[\w]+\]/text\(\)$",  # //xml_element/xml_element[@attribute]/text()
        r"^//[\w]+/[\w]+\[@[\w]+='[^']*'\]/text\(\)$",  # //xml_element/xml_element[@attribute='value']/text()
        r"^//[\w]+/[\w]+$",  # //xml_element/xml_element
        r"^//[\w]+/[\w]+/[\w]+$",  # //xml_element/xml_element/xml_element
        r"^//[\w]+/text\(\)$",  # //xml_element/text()
        r"^//[\w]+/@[\w]+$",  # //xml_element/@attribute
        r"^//[\w]+/[\w]+\[text\(\)='[^']*'\]$",  # //xml_tag_name/another_xml_tag_name[text()='some_value']
    ]

    # Check if expression matches any pattern
    return any(re.match(pattern, expression) for pattern in valid_patterns)


def evaluate_xml_files_matching(folder_containing_xml_files, matching_filters):
    final_results = []
    total_files = sum(
        1
        for filename in os.listdir(folder_containing_xml_files)
        if filename.endswith(".xml")
    )
    progress_increment = 100 / total_files
    current_progress = 0
    total_sum_matches = 0
    total_matching_files = 0
    window["-PROGRESS_BAR-"].update(current_progress)

    try:
        for filename in os.listdir(folder_containing_xml_files):
            if filename.endswith(".xml"):
                file_path = os.path.join(folder_containing_xml_files, filename)
                current_progress += progress_increment
                window["-PROGRESS_BAR-"].update(round(current_progress, 2))
                window["-OUTPUT_WINDOW_MAIN-"].update(f"Processing {filename}")

                try:
                    tree = ET.parse(file_path)
                except ET.XMLSyntaxError as e:
                    if "Document is empty" in str(e):
                        window["-OUTPUT_WINDOW_MAIN-"].update(
                            f"Error processing {filename}\nXML File is empty, skipping file..."
                        )
                        continue
                    else:
                        window["-OUTPUT_WINDOW_MAIN-"].update(
                            f"XMLSyntaxError occurred: {e}"
                        )
                        continue
                
                try:
                    total_matches = 0
                    current_file_results = {"Filename": os.path.splitext(filename)[0]}
                    special_case_results = []

                    for expression in matching_filters:
                        result = tree.xpath(expression)
                        match_count = len(result)
                        total_matches += match_count
            
                        if match_count:
                            if "[@" in expression or "[text()=" in expression:
                                special_case_results.append({
                                    "Filename": os.path.splitext(filename)[0],
                                    "Expression": expression,
                                    "Matches": match_count
                                })
                            else:
                                if "[@" in expression:
                                    match = re.search(r"@([^=]+)=", expression)
                                    if match:
                                        attribute_name_string = match.group(1).strip()
                                        for element in result:
                                            attr_value = element.get(attribute_name_string)
                                            if attr_value and attr_value.strip():
                                                if f"Attribute {attribute_name_string} Value" not in current_file_results:
                                                    current_file_results[f"Attribute {attribute_name_string} Value"] = []
                                                current_file_results[f"Attribute {attribute_name_string} Value"].append(attr_value)
                                
                                    else:
                                        match = re.search(r"@([^=]+),", expression)
                                        if match:
                                            attribute_name_string = match.group(1).strip()
                                            for element in result:
                                                attr_value = element.get(attribute_name_string)
                                                if attr_value and attr_value.strip():
                                                    if f"Attribute {attribute_name_string} Value" not in current_file_results:
                                                        current_file_results[f"Attribute {attribute_name_string} Value"] = []
                                                    current_file_results[f"Attribute {attribute_name_string} Value"].append(attr_value)
                                                    
                                elif "/@" in expression:
                                    attribute_name_string = f"Attribute {expression.split('@')[-1]} Value"
                                    if attribute_name_string not in current_file_results:
                                        current_file_results[attribute_name_string] = []
                                    for element in result:
                                        current_file_results[attribute_name_string].append(element.strip())

                                elif "[text()=" in expression:
                                    match = re.search(r"//(.*?)\[", expression)
                                    if match:
                                        tag_name_string = match.group(1).strip()
                                        for element in result:
                                            tag_value = element.text
                                            if tag_value and tag_value.strip():
                                                if f"Tag {tag_name_string} Value" not in current_file_results:
                                                    current_file_results[f"Tag {tag_name_string} Value"] = []
                                                current_file_results[f"Tag {tag_name_string} Value"].append(tag_value)

                                elif "/text()" in expression:
                                    tag_name_string = f"Tag {expression.split('/')[-2]} Value"
                                    if tag_name_string not in current_file_results:
                                        current_file_results[tag_name_string] = []
                                    for element in result:
                                        current_file_results[tag_name_string].append(element.strip())
                    
                    if total_matches > 0:
                        total_sum_matches += total_matches
                        total_matching_files += 1
                        if special_case_results:
                            final_results.extend(special_case_results)
                        if current_file_results:
                            final_results.append(current_file_results)

                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments: {1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    window["-OUTPUT_WINDOW_MAIN-"].update(f"ERROR: {message}")
                    break

        return final_results, total_sum_matches, total_matching_files

    except ZeroDivisionError:
        pass
    

def export_evaluation_as_csv(csv_output_path, folder_containing_xml_files, matching_filters):
    try:
        matching_results, total_matches_found, total_matching_files = (
            evaluate_xml_files_matching(folder_containing_xml_files, matching_filters)
        )

        # Save matching results to CSV file
        if matching_results:
            headers = [
                key for key in {key: None for dic in matching_results for key in dic}
            ]
            with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = headers
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()

                # Write matching results
                for match in matching_results:
                    if 'Expression' in match:
                        writer.writerow(match)
                    else:
                        filename = match["Filename"]
                        results = {key: match[key] for key in match if key != "Filename"}
                        if results:
                            max_len = max(len(v) if isinstance(v, list) else 1 for v in results.values())
                            for i in range(max_len):
                                row = {"Filename": filename}
                                for key in results:
                                    value = results[key]
                                    if isinstance(value, list):
                                        row[key] = value[i] if i < len(value) else ""
                                    else:
                                        row[key] = value
                                writer.writerow(row)

            window["-OUTPUT_WINDOW_MAIN-"].update(
                f"Matches saved to {csv_output_path}\nFound {total_matching_files} "
                f"files that have a total sum of {total_matches_found} matches."
            )
            window["-EXPORT_AS_CSV-"].update(disabled=False)
            window["-INPUT_FOLDER_BROWSE-"].update(disabled=False)
            window["-PROGRESS_BAR-"].update(0)
        else:
            window["-OUTPUT_WINDOW_MAIN-"].update("No matches found.")
            window["-EXPORT_AS_CSV-"].update(disabled=False)
            window["-INPUT_FOLDER_BROWSE-"].update(disabled=False)
            window["-PROGRESS_BAR-"].update(0)

    except TypeError as e:
        window["-OUTPUT_WINDOW_MAIN-"].update(f"TypeError Exception in program: {e}")
        window["-EXPORT_AS_CSV-"].update(disabled=False)
        window["-INPUT_FOLDER_BROWSE-"].update(disabled=False)
        window["-PROGRESS_BAR-"].update(0)


def is_duplicate(xpath_expression):
    """_summary_

    Args:
        xpath_expression (str): XML XPath expression in ListBox Element of the GUI
    Returns:
        str: Checks if
    """
    return xpath_expression in matching_filters_listbox


def statusbar_update_total_xml_files(filepath):
    try:
        if os.path.isfile(filepath):
            files = [filepath]
        elif os.path.isdir(filepath):
            files = [
                os.path.join(filepath, f)
                for f in os.listdir(filepath)
                if f.endswith(".xml")
            ]
            window["-STATUSBAR-"].update(value=f"Total XML files found: {len(files)}")
            window.refresh()
        else:
            window["-STATUSBAR-"].update(value="")
            pass
    except TypeError:
        pass
    except FileNotFoundError:
        pass


custom_theme_yellow = {
    "BACKGROUND": "#31353d",
    "TEXT": "#FFFFFF",
    "INPUT": "#4d5157",
    "TEXT_INPUT": "#FFFFFF",
    "SCROLL": "#e2e3e3",
    "BUTTON": ("#FFC857", "#4d5157"),
    "PROGRESS": ("#FFC857", "#abacac"),
    "BORDER": 2,
    "SLIDER_DEPTH": 1,
    "PROGRESS_DEPTH": 1,
}

# PySimpleGUI custom theme
sg.theme_add_new("MyTheme", custom_theme_yellow)
sg.theme("MyTheme")

# Constants for Font and Frame Title Color
FRAME_TITLE_COLOR = "#FFC857"
FONT = ("Calibri", 13)
FONT_FOR_TEXTINPUT = ("Calibri", 12)

# Constants
FILE_TYPE_XML = (("XML (Extensible Markup Language)", ".xml"),)
MENU_RIGHT_CLICK_DELETE = ["&Right", ["&Delete", "&Delete All"]]
MENU_DEFINITION = [
    [
        "&File",
        [
            "Clear Output::ClearOutput",
            "---",
            "E&xit",
        ],
    ],
    [
        "&Open",
        [
            "&Open XML Input Folder::OpenInputFolder",
            "&Open CSV Output Folder::OpenOutputFolder",
        ],
    ],
    [
        "&Paths",
        ["&Lobster Test System::LobsterTest", "&Lobster Prod System::LobsterProd"],
    ],
    ["&Help", ["&XPath Help::XPathSyntaxURL", "XPath Cheat Sheet::XPathCheatSheet"]],
]

# Constants for Pandas Conversion
FILE_TYPES_INPUT = (("CSV (Comma Separated Value)", ".csv"),)
FILE_TYPES_OUTPUT = (
    ("XLSX (Excel Sheet)", ".xlsx"),
    ("MD (Markdown README)", ".md"),
    ("HTML (Hypertext Markup Language)", ".html"),
    ("JSON (JavaScript Object Notation)", ".json"),
)

# Combobox Lists
tag_name_list = []
tag_value_list = []
attribute_name_list = []
attribute_value_list = []

# Listbox List
matching_filters_listbox = []

# ========== START Layout for Pandas Conversion START ========== #
layout_pandas_conversion = [
    [
        sg.Text(
            "CSV Converter",
            font="Calibri 36 bold underline",
            text_color="#FFC857",
            pad=10,
            justification="center",
            grab=True,
        )
    ],
    [
        sg.Text(
            "Convert CSV File to a different file type with the Pandas module.\nSupported output file types: Excel, Markdown, HTML and JSON",
            justification="center",
        )
    ],
    [sg.HSep(pad=10)],
    [sg.Text("Choose a CSV file for conversion:")],
    [
        sg.Input(size=(44, 1), key="-FILE_INPUT-"),
        sg.FileBrowse(file_types=FILE_TYPES_INPUT, size=(8, 1)),
        sg.Button("Read CSV", size=(7, 1), key="-READ_FILE-"),
    ],
    [sg.Text("Choose where to save output of CSV file")],
    [
        sg.Input(size=(44, 1), key="-FILE_OUTPUT-"),
        sg.FileSaveAs(
            button_text="Save as",
            size=(7, 1),
            file_types=FILE_TYPES_OUTPUT,
            target="-FILE_OUTPUT-",
            key="-SAVE_AS_BUTTON-",
        ),
        sg.Button("Convert", key="-CONVERT_CSV_FILE-", expand_x=True),
    ],
    [
        sg.Checkbox(
            "Write Index Column?", default=False, key="-CHECKBOX_WRITE_INDEX_COLUMN-"
        )
    ],
    [sg.Image(source=LOGO, expand_x=True, expand_y=True, key="-IMAGE-")],
]

layout_pandas_output = [
    [
        sg.Multiline(
            size=(59, 34),
            key="-OUTPUT_WINDOW_CSV-",
            disabled=True,
        )
    ]
]

frame_pandas = sg.Frame(
    "CSV Conversion to different file type",
    layout_pandas_conversion,
    expand_x=True,
    expand_y=True,
    title_color=FRAME_TITLE_COLOR,
    font="Calibri 13 bold",
)
frame_pandas_output = sg.Frame(
    "CSV Conversion Output",
    layout_pandas_output,
    expand_x=True,
    expand_y=True,
    title_color=FRAME_TITLE_COLOR,
    font="Calibri 13 bold",
)
# ========== END Layout for Pandas Conversion END ========== #

# ========== START Layout for XML Evaluation START ========== #
layout_xml_evaluation = [
    [sg.Menu(MENU_DEFINITION)],
    [
        sg.Text("Choose a Folder that contains XML Files", pad=5),
        sg.StatusBar(
            "",
            key="-STATUSBAR-",
            expand_x=True,
            auto_size_text=True,
            font="Calibri 14 bold",
            size=(10, 1),
        ),
    ],
    [
        sg.Input(
            size=(36, 2),
            font=FONT_FOR_TEXTINPUT,
            enable_events=True,
            expand_x=True,
            key="-FOLDER_EVALUATION_INPUT-",
        ),
        sg.FolderBrowse(
            button_text="Browse",
            target="-FOLDER_EVALUATION_INPUT-",
            key="-INPUT_FOLDER_BROWSE-",
        ),
        sg.Button("Read XML", key="-READ_XML-"),
    ],
    [sg.Text("Get XML Tag and Attribute Names/Values for XPath generation", pad=5)],
    [
        sg.Text("Tag name:"),
        sg.Combo(
            tag_name_list,
            size=(15, 1),
            disabled=True,
            auto_size_text=False,
            enable_events=True,
            enable_per_char_events=True,
            expand_x=True,
            key="-XML_TAG_NAME-",
        ),
        sg.Text("Tag Value:"),
        sg.Combo(
            tag_value_list,
            size=(15, 1),
            disabled=True,
            enable_events=True,
            enable_per_char_events=True,
            auto_size_text=False,
            expand_x=True,
            key="-XML_TAG_VALUE-",
        ),
    ],
    [
        sg.Text("Att name:"),
        sg.Combo(
            attribute_name_list,
            size=(15, 1),
            disabled=True,
            auto_size_text=False,
            enable_events=True,
            expand_x=True,
            key="-XML_ATTRIBUTE_NAME-",
        ),
        sg.Text("Att Value:"),
        sg.Combo(
            attribute_value_list,
            size=(15, 1),
            disabled=True,
            enable_events=True,
            auto_size_text=False,
            expand_x=True,
            key="-XML_ATTRIBUTE_VALUE-",
            pad=5,
        ),
    ],
    [
        sg.Text("Function:"),
        sg.Radio("Equals", group_id=1, default=True, key="-RADIO_DEFAULT-"),
        sg.Radio("Contains", group_id=1, key="-RADIO_CONTAINS-"),
        sg.Radio("Starts-with", group_id=1, key="-RADIO_STARTSWITH-"),
        sg.Radio("Greater", group_id=1, key="-RADIO_GREATER-"),
        sg.Radio("Smaller", group_id=1, key="-RADIO_SMALLER-"),
    ],
    [
        sg.Text("XPath Expression:"),
        sg.Input(
            size=(14, 1),
            font=FONT_FOR_TEXTINPUT,
            expand_x=True,
            key="-XPATH_EXPRESSION-",
        ),
        sg.Button("Build XPath", key="-BUILD_XPATH-"),
    ],
]

layout_listbox_matching_filter = [
    [
        sg.Text(
            "Add XPath Expressions to list to look for in XML Files:", expand_x=True
        ),
        sg.Button("Add XPath Filter", key="-ADD_TO_MATCHING-", expand_x=True),
    ],
    [
        sg.Listbox(
            values=matching_filters_listbox,
            size=(60, 4),
            enable_events=True,
            expand_x=True,
            right_click_menu=MENU_RIGHT_CLICK_DELETE,
            key="-MATCHING_FILTER_LIST-",
        )
    ],
]

layout_export_evaluation = [
    [sg.Text("Choose a folder where you want to save the XML Evaluation")],
    [
        sg.Input(
            expand_x=True, font=FONT_FOR_TEXTINPUT, key="-FOLDER_EVALUATION_OUTPUT-"
        ),
        sg.SaveAs(
            button_text="Save as",
            file_types=(("Comma Separated Value (.csv)", ".csv"),),
            target="-FOLDER_EVALUATION_OUTPUT-",
        ),
        sg.Button("Export", key="-EXPORT_AS_CSV-"),
    ],
]

layout_program_output = [
    [
        sg.Multiline(
            size=(62, 5),
            key="-OUTPUT_WINDOW_MAIN-",
            pad=10,
            horizontal_scroll=True,
            disabled=True,
        )
    ]
]

layout_xml_output = [
    [
        sg.Multiline(
            size=(58, 31),
            write_only=False,
            horizontal_scroll=True,
            key="-OUTPUT_XML_FILE-",
            pad=5,
        )
    ],
    [
        sg.Text("Progress:"),
        sg.ProgressBar(
            max_value=100,
            size=(20, 18),
            orientation="h",
            expand_x=True,
            key="-PROGRESS_BAR-",
            pad=10,
        ),
    ],
]

frame_xml_eval = sg.Frame(
    "XML folder selection and XPath builder",
    layout_xml_evaluation,
    title_color=FRAME_TITLE_COLOR,
    expand_x=True,
    font="Calibri 13 bold",
)
frame_export_evaluation = sg.Frame(
    "Export evaluation result as a CSV File",
    layout_export_evaluation,
    title_color=FRAME_TITLE_COLOR,
    expand_x=True,
    font="Calibri 13 bold",
)
frame_xml_output = sg.Frame(
    "XML Output",
    layout_xml_output,
    title_color=FRAME_TITLE_COLOR,
    expand_x=True,
    font="Calibri 13 bold",
)
frame_output_main = sg.Frame(
    "Program Output",
    layout_program_output,
    title_color=FRAME_TITLE_COLOR,
    expand_x=True,
    font="Calibri 13 bold",
)
frame_listbox_matching_filter = sg.Frame(
    "List of filters to match in XML files",
    layout_listbox_matching_filter,
    title_color=FRAME_TITLE_COLOR,
    expand_x=True,
    font="Calibri 13 bold",
)
# ========== END Layout for XML Evaluation END ========== #

# layout = [[sg.Column(layout=[[frame_xml_eval], [frame_listbox_matching_filter],[frame_export_evaluation],[frame_output_main]], expand_y=True),sg.Column([[frame_xml_output]], expand_y=True)]] # DEPRACTED

# Build GUI Layout
layout = [
    [
        sg.TabGroup(
            [
                [
                    sg.Tab(
                        "XML Evaluation",
                        [
                            [
                                sg.Column(
                                    layout=[
                                        [frame_xml_eval],
                                        [frame_listbox_matching_filter],
                                        [frame_export_evaluation],
                                        [frame_output_main],
                                    ],
                                    expand_y=True,
                                ),
                                sg.Column(layout=[[frame_xml_output]], expand_y=True),
                            ]
                        ],
                    ),
                    sg.Tab(
                        "CSV Conversion",
                        [
                            [
                                sg.Column(
                                    layout=[[frame_pandas]],
                                    expand_y=True,
                                ),
                                sg.Column(
                                    layout=[[frame_pandas_output]], expand_y=True
                                ),
                            ]
                        ],
                    ),
                ]
            ],
            selected_background_color="#FFC857",
            selected_title_color="#000000",
        )
    ]
]

window = sg.Window(
    "XMLuvation v0.9.4 © 2024 by Jovan Zaric",
    layout,
    font=FONT,
    icon=PROGRAM_ICON,
    finalize=True,
)
pywinstyles.change_header_color(window.TKroot, color="#4d5157")
input_checked = False

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    # Pandas related variables
    input_file_pandas = values["-FILE_INPUT-"]
    output_file_pandas = values["-FILE_OUTPUT-"]
    input_extension_pandas = Path(input_file_pandas).suffix.lower().strip(".")
    output_extension_pandas = Path(output_file_pandas).suffix.lower().strip(".")

    # Browse Folder and Save As input elements
    evaluation_input_folder = values["-FOLDER_EVALUATION_INPUT-"]  # Browse Folder
    evaluation_output_folder = values[
        "-FOLDER_EVALUATION_OUTPUT-"
    ]  # Save As CSV file output

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
    file_path_regex = r"\.xml$"

    if event in ("Delete", "Delete All"):
        try:
            if event == "Delete":
                selected_indices = window["-MATCHING_FILTER_LIST-"].get_indexes()

                for index in selected_indices:
                    matching_filters_listbox.pop(index)
                    window["-MATCHING_FILTER_LIST-"].update(
                        values=matching_filters_listbox
                    )

            elif event == "Delete All":
                matching_filters_listbox.clear()
                window["-MATCHING_FILTER_LIST-"].update(values=matching_filters_listbox)

        except UnboundLocalError:
            window["-OUTPUT_WINDOW_MAIN-"].update(
                "ERROR: To delete a filter from the Listbox, select it first."
            )

    elif event == "XPath Help::XPathSyntaxURL":
        webbrowser.open("https://www.w3schools.com/xml/xpath_syntax.asp")

    elif event == "XPath Cheat Sheet::XPathCheatSheet":
        excel_sheet = "_internal/cheatsheet/XPath_Syntax.xlsx"
        read = pd.read_excel(excel_sheet).to_dict()

        table = pd.DataFrame(read)
        head = list(read)
        values = table.values.tolist()
        # Set column widths for empty record of table
        layout_table = [
            [
                sg.Table(
                    values=values,
                    headings=head,
                    auto_size_columns=False,
                    col_widths=list(map(lambda x: len(x) + 1, head)),
                    expand_x=True,
                    expand_y=True,
                    justification="left",
                )
            ]
        ]

        window2 = sg.Window(
            "XPath Cheat Sheet",
            layout_table,
            resizable=True,
            size=(1200, 600),
            font="Calibri 16",
            grab_anywhere=True,
        )
        event, value = window2.read()

    elif event == "Open CSV Output Folder::OpenOutputFolder":
        output_folder = evaluation_output_folder
        if output_folder:
            directory_path = os.path.dirname(output_folder)
            windows_path = directory_path.replace("/", "\\")
            os.startfile(windows_path)
        elif not output_folder:
            window["-OUTPUT_WINDOW_MAIN-"].update(
                "No output folder set where the CSV export will be."
            )

    elif event == "Open XML Input Folder::OpenInputFolder":
        input_folder = evaluation_input_folder
        if input_folder:
            directory_path = os.path.dirname(input_folder)
            windows_path = directory_path.replace("/", "\\")
            os.startfile(windows_path)
        elif not input_folder:
            window["-OUTPUT_WINDOW_MAIN-"].update(
                "No input folder set where XML files are located."
            )

    elif event == "Clear Output::ClearOutput":
        window["-OUTPUT_WINDOW_MAIN-"].update("")

    elif event == "Lobster Test System::LobsterTest":
        window.write_event_value(
            key="-FOLDER_EVALUATION_INPUT-", value="//nesist02/ProfilileXMLExport"
        )
        window["-FOLDER_EVALUATION_INPUT-"].update("//nesist02/ProfilileXMLExport")

    elif event == "Lobster Prod System::LobsterProd":
        window.write_event_value(
            key="-FOLDER_EVALUATION_INPUT-", value="//nesis002/ProfilileXMLExport"
        )
        window["-FOLDER_EVALUATION_INPUT-"].update("//nesis002/ProfilileXMLExport")

    elif event == "-FOLDER_EVALUATION_INPUT-":
        if not input_checked and len(evaluation_input_folder) > 0:
            input_checked = True
            window.perform_long_operation(
                lambda: statusbar_update_total_xml_files(evaluation_input_folder),
                "-OUTPUT_WINDOW_MAIN-",
            )
            input_checked = False

    elif event == "-READ_XML-":
        eval_input_file = sg.popup_get_file(
            "Select a XML file to fill out the Name/Value boxes.",
            file_types=(("XML (Extensible Markup Language )", "*.xml"),),
        )
        if eval_input_file:
            window.perform_long_operation(
                lambda: parse_xml(eval_input_file), "-OUTPUT_WINDOW_MAIN-"
            )
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
                    window["-XML_TAG_VALUE-"].update(
                        disabled=False, values=tag_value_list
                    )
                    attribute_name_list = get_attributes(eval_input_file, tag)
                    window["-XML_ATTRIBUTE_NAME-"].update(values=attribute_name_list)

                    for attribute_name in attribute_name_list:
                        attribute_value_list = get_attribute_values(
                            eval_input_file, tag, attribute_name
                        )
                        window["-XML_ATTRIBUTE_VALUE-"].update(
                            values=attribute_value_list
                        )
                        break  # Only need to get attributes and values for the first tag

    elif event == "-CONVERT_CSV_FILE-":
        window.perform_long_operation(
            lambda: convert_csv_file(
                input_file_pandas,
                output_file_pandas,
                input_extension_pandas,
                output_extension_pandas,
            ),
            "-OUTPUT_WINDOW_CSV-",
        )

    elif event == "-READ_FILE-":
        window.perform_long_operation(
            lambda: read_csv_data(input_file_pandas), "-OUTPUT_WINDOW_CSV-"
        )

    elif event == "-XML_TAG_NAME-":
        try:
            selected_tag = tag_name_combobox
            attributes = get_attributes(eval_input_file, selected_tag)
            window["-XML_ATTRIBUTE_NAME-"].update(values=attributes)
            values_xml = get_tag_values(eval_input_file, selected_tag)
            window["-XML_TAG_VALUE-"].update(values=values_xml)

            # Disable tag value combo box if there are no values for the selected tag
            if not values_xml or all(
                value.strip() == "" for value in values_xml if value is not None
            ):
                window["-XML_TAG_VALUE-"].update(disabled=True, values="")
            else:
                window["-XML_TAG_VALUE-"].update(disabled=False)

            # Disable attribute name and value combo boxes if there are no attributes for the selected tag
            if not attributes:
                window["-XML_ATTRIBUTE_NAME-"].update(disabled=True, values="")
                window["-XML_ATTRIBUTE_VALUE-"].update(disabled=True, values=[])
            else:
                window["-XML_ATTRIBUTE_NAME-"].update(disabled=False)

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            window["-OUTPUT_WINDOW_MAIN-"].update(f"ERROR: {message}")

    elif event == "-XML_ATTRIBUTE_NAME-":
        try:
            selected_tag = tag_name_combobox
            selected_attribute = attribute_name_combobox
            attribute_values = get_attribute_values(
                eval_input_file, selected_tag, selected_attribute
            )
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

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            window["-OUTPUT_WINDOW_MAIN-"].update(f"ERROR: {message}")

    elif event in (
        "-BUILD_XPATH-",
        "-RADIO_DEFAULT-",
        "-RADIO_CONTAINS-",
        "-RADIO_STARTSWITH-",
        "-RADIO_GREATER-",
        "-RADIO_SMALLER-",
    ):
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
                        xpath_criteria.append(
                            f"@{attribute_name_combobox}='{attribute_value_combobox}'"
                        )
                    else:
                        xpath_criteria.append(f"@{attribute_name_combobox}")

            elif radio_contains:
                xpath_criteria = []
                if tag_value_combobox:
                    xpath_criteria.append(f"contains(text(), '{tag_value_combobox}')")
                if attribute_name_combobox:
                    if attribute_value_combobox:
                        xpath_criteria.append(
                            f"contains(@{attribute_name_combobox}, '{attribute_value_combobox}')"
                        )
                    else:
                        xpath_criteria.append(f"@{attribute_name_combobox}")

            elif radio_startswith:
                xpath_criteria = []
                if tag_value_combobox:
                    xpath_criteria.append(
                        f"starts-with(text(), '{tag_value_combobox}')"
                    )
                if attribute_name_combobox:
                    if attribute_value_combobox:
                        xpath_criteria.append(
                            f"starts-with(@{attribute_name_combobox}, '{attribute_value_combobox}')"
                        )
                    else:
                        xpath_criteria.append(f"@{attribute_name_combobox}")

            elif radio_greater:
                xpath_criteria = []
                if tag_value_combobox:
                    xpath_criteria.append(f"text() > {tag_value_combobox}")
                if attribute_name_combobox:
                    if attribute_value_combobox:
                        xpath_criteria.append(
                            f"@{attribute_name_combobox} > {attribute_value_combobox}"
                        )
                    else:
                        xpath_criteria.append(f"@{attribute_name_combobox}")

            elif radio_smaller:
                xpath_criteria = []
                if tag_value_combobox:
                    xpath_criteria.append(f"text() < {tag_value_combobox}")
                if attribute_name_combobox:
                    if attribute_value_combobox:
                        xpath_criteria.append(
                            f"@{attribute_name_combobox} < {attribute_value_combobox}"
                        )
                    else:
                        xpath_criteria.append(f"@{attribute_name_combobox}")

            # Append XPath criteria to expression
            if xpath_criteria:
                xpath_expression += "[" + "".join(xpath_criteria) + "]"

            # Update XPath expression and output window
            window["-XPATH_EXPRESSION-"].update(xpath_expression)

        except NameError:
            window["-OUTPUT_WINDOW_MAIN-"].update(
                "Name 'parsed_xml_file' is not defined"
            )

    elif event == "-ADD_TO_MATCHING-":
        try:
            if not xpath_expression_input:
                window["-OUTPUT_WINDOW_MAIN-"].update("No XPath expression entered.")

            elif xpath_expression_input and not is_duplicate(xpath_expression_input):
                validate = is_valid_xpath(xpath_expression_input)
                if validate:
                    matching_filters_listbox.append(xpath_expression_input)
                    window["-MATCHING_FILTER_LIST-"].update(
                        values=matching_filters_listbox
                    )
                    window["-OUTPUT_WINDOW_MAIN-"].update(
                        f"XPath expression added: {xpath_expression_input}"
                    )
                else:
                    window["-OUTPUT_WINDOW_MAIN-"].update(
                        "Not a valid XPath Expression."
                    )
                    continue
            elif is_duplicate(xpath_expression_input):
                window["-OUTPUT_WINDOW_MAIN-"].update(
                    f"Duplicate XPath expression {xpath_expression_input} is already in the list."
                )

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            window["-OUTPUT_WINDOW_MAIN-"].update(f"Error adding filter: {message}")

    elif event == "-EXPORT_AS_CSV-":
        try:
            if not os.path.exists(os.path.dirname(evaluation_input_folder)):
                window["-OUTPUT_WINDOW_MAIN-"].update(
                    "Input folder directory for XML files is either not set or is not a valid path."
                )

            elif not len(matching_filters_listbox) > 0:
                window["-OUTPUT_WINDOW_MAIN-"].update(
                    "No filters for matching added, please add one as XPath."
                )

            elif not os.path.exists(os.path.dirname(evaluation_output_folder)):
                window["-OUTPUT_WINDOW_MAIN-"].update(
                    "Please choose where you want to save the Evaluation as a CSV File."
                )
            else:
                window.perform_long_operation(
                    lambda: export_evaluation_as_csv(
                        evaluation_output_folder,
                        evaluation_input_folder,
                        matching_filters_listbox,
                    ),
                    "-OUTPUT_WINDOW_MAIN-",
                )
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            window["-OUTPUT_WINDOW_MAIN-"].update(f"Error exporting CSV: {message}")

window.close()  # Kill Program