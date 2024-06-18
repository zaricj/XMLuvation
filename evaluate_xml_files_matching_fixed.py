import csv
import os
import re
from pathlib import Path
import pandas as pd
from lxml import etree as ET

def extract_values_from_xml(tree, xpath_expressions):
    extracted_values = [tree.xpath(xpath) for xpath in xpath_expressions]
    return extracted_values

def evaluate_xml_files_matching(folder_containing_xml_files, matching_filters):
    final_results = []
    total_files = sum(1 for filename in os.listdir(folder_containing_xml_files) if filename.endswith(".xml"))
    progress_increment = 100 / total_files
    current_progress = 0
    total_sum_matches = 0
    total_matching_files = 0

    try:
        for filename in os.listdir(folder_containing_xml_files):
            if filename.endswith(".xml"):
                file_path = os.path.join(folder_containing_xml_files, filename)
                current_progress += progress_increment
                print(f"Progressbar: {round(current_progress, 2)}")
                print(f"Processing {filename}")

                try:
                    tree = ET.parse(file_path)
                except ET.XMLSyntaxError as e:
                    if "Document is empty" in str(e):
                        print(f"Error processing {filename}\nXML File is empty, skipping file...")
                        continue
                    else:
                        print(f"XMLSyntaxError occurred: {e}")
                        continue

                try:
                    total_matches = 0
                    current_file_results = {"Filename": os.path.splitext(filename)[0]}

                    extracted_values = extract_values_from_xml(tree, matching_filters)

                    if len(matching_filters) == 1:
                        expression = matching_filters[0]
                        result = tree.xpath(expression)
                        total_matches += len(result)

                        if result:
                            if "[@" in expression:
                                match = re.search(r"@([^=]+)=", expression)
                                if match:
                                    attribute_name_string = match.group(1).strip()
                                    for element in result:
                                        attr_value = element.get(attribute_name_string)
                                        if attr_value and attr_value.strip():
                                            current_file_results[f"Attribute {attribute_name_string} Value {attr_value} Matches"] = total_matches

                                else:
                                    match = re.search(r"@([^=]+),", expression)
                                    if match:
                                        attribute_name_string = match.group(1).strip()
                                        for element in result:
                                            attr_value = element.get(attribute_name_string)
                                            if attr_value and attr_value.strip():
                                                current_file_results[f"Attribute {attribute_name_string} Value {attr_value} Matches"] = total_matches

                            elif "/@" in expression:
                                attribute_name_string = f"Attribute {expression.split('/')[-2]} Value"
                                if attribute_name_string not in current_file_results:
                                    current_file_results[attribute_name_string] = []
                                    for element in result:
                                        current_file_results[attribute_name_string].append(element.strip())

                            elif "text()=" in expression:
                                match = re.search(r"//(.*?)\[", expression)
                                if match:
                                    tag_name_string = match.group(1).strip()
                                    for element in result:
                                        tag_value = element.text
                                        if tag_value and tag_value.strip():
                                            current_file_results[f"Tag {tag_name_string} Value {tag_value} Matches"] = total_matches

                            elif "/text()" in expression:
                                tag_name_string = f"Tag {expression.split('/')[-2]} Value"
                                if tag_name_string not in current_file_results:
                                    current_file_results[tag_name_string] = []
                                    for element in result:
                                        current_file_results[tag_name_string].append(element.strip())

                    elif len(matching_filters) > 1:
                        combined_data = list(zip(*extracted_values))

                        for row in combined_data:
                            result = {"Filename": os.path.splitext(filename)[0]}
                            for idx, value in enumerate(row):
                                expression = matching_filters[idx]
                                if isinstance(value, ET._Element):
                                    value = value.text if value.text else value.get(expression.split('@')[-1])

                                if "[@" in expression:
                                    match = re.search(r"@([^=]+)=", expression)
                                    if match:
                                        attribute_name_string = match.group(1).strip()
                                        if value and value.strip():
                                            result[f"Attribute {attribute_name_string}"] = value.strip()
                                    else:
                                        match = re.search(r"@([^=]+),", expression)
                                        if match:
                                            attribute_name_string = match.group(1).strip()
                                            if value and value.strip():
                                                result[f"Attribute {attribute_name_string}"] = value.strip()
                                elif "/@" in expression:
                                    attribute_name_string = f"Attribute {expression.split('/')[-2]}"
                                    if value and value.strip():
                                        result[attribute_name_string] = value.strip()
                                elif "text()=" in expression:
                                    match = re.search(r"//(.*?)\[", expression)
                                    if match:
                                        tag_name_string = match.group(1).strip()
                                        if value and value.strip():
                                            result[f"Tag {tag_name_string}"] = value.strip()
                                elif "/text()" in expression:
                                    tag_name_string = f"Tag {expression.split('/')[-2]}"
                                    if value and value.strip():
                                        result[tag_name_string] = value.strip()
                                else:
                                    if value and value.strip():
                                        result[f"Tag {idx + 1}"] = value.strip()

                            final_results.append(result)
                            total_matches += 1

                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments: {1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(f"ERROR: {message}")
                    break

                if total_matches > 0:
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
    return value if value != '' else 'NaN'


def export_evaluation_as_csv(csv_output_path, folder_containing_xml_files, matching_filters):
    """Export found XML files and it's matches in a single CSV file

    Args:
        csv_output_path (str): Folder Path where the evaluation should be exported to
        folder_containing_xml_files (str): Folder Path where one or more XML files are located
        matching_filters (list): Added XPath filters in the ListBox GUI element
    """
    try:
        # matching_results is a fucking list of dictionaries... *shrug*
        matching_results, total_matches_found, total_matching_files = evaluate_xml_files_matching(folder_containing_xml_files,
                                                                                                matching_filters)

        # Save matching results to CSV file
        if matching_results:  # Check if matching results exist
            headers = [key for key in {key: None for dic in matching_results for key in dic}]

            with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = headers
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()

                # Write matching results
                for match in matching_results:
                    if match is not None:  # If None, skip
                        matches = {header: replace_empty_with_zero(match.get(header, '')) for header in headers}
                        #print("Matches:", matches)
                        writer.writerow(matches)

            print(f"Matches saved to {csv_output_path}\nFound {total_matching_files} files that have a total sum of {total_matches_found} matches.")
        else:
            print("No matches found.")

    except TypeError as e:
        print(f"TypeError: {e}")
        

csv_result_file = "ResultFileNEWTEST.csv"
folder_with_xml_files = "C:/Users/ZaricJ/Documents/00 Aufgaben/01 Februar 2024/Lobster Admin Auswertung/SmallTest10"
xpath_filters = ["//unit_message/type/text()", "//unit_message/description/text()"] #//check_min_max[text()='false'] //check_min_max/text() //filter[@id='130']

export_evaluation_as_csv(csv_result_file, folder_with_xml_files, xpath_filters)