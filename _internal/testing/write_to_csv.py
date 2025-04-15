from  datetime import datetime
from lxml import etree as ET
import pandas as pd
import sys
import csv
import os
import re
import webbrowser
import json
import traceback
import multiprocessing
from functools import partial
from typing import List, Tuple, Dict


# Standalone processing functions that can be pickled
def process_single_xml(filename: str, folder_path: str, xpath_expressions: List[str]) -> Tuple[List[Dict], int, int]:
    """Process a single XML file and return its results."""
    final_results = []
    file_total_matches = 0
    file_path = os.path.join(folder_path, filename)
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.XMLSyntaxError:
        return [], 0, 0
    except Exception:
        return [], 0, 0

    for expression in xpath_expressions:
        result = root.xpath(expression)
        match_count = len(result)
        file_total_matches += match_count

        pattern_text_or_attribute_end = r'(.*?/text\(\)$|.*?/@[a-zA-Z_][a-zA-Z0-9_]*$)'
        match = re.match(pattern_text_or_attribute_end, expression)
        ends_with_text_or_attribute = bool(match)

        if result:
            if not ends_with_text_or_attribute:
                current_result = {"Filename": os.path.splitext(filename)[0]}
                current_result["Matches"] = match_count
                current_result["Expression"] = expression
                final_results.append(current_result)
            else:
                new_results = process_xpath_result(expression, result, os.path.splitext(filename)[0])
                final_results.extend(new_results)
                print(f"Final results in process_single_xml: {final_results}")
            

    return final_results, file_total_matches, 1 if file_total_matches > 0 else 0


def evaluate_xml_files_matching(folder_containing_xml_files, list_of_xpath_expressions):
        """Evaluate XML files using multiprocessing."""
        xml_files = [f for f in os.listdir(folder_containing_xml_files) if f.endswith(".xml")]
        total_files = len(xml_files)
        
        if not xml_files:
            return [], 0, 0

        # Calculate the number of processes to use (leave one core free)
        num_processes = max(1, multiprocessing.cpu_count() - 1)
        
        # Initialize multiprocessing variables
        final_results = []
        total_sum_matches = 0
        total_matching_files = 0
        
        # Create a pool of processes
        with multiprocessing.Pool(processes=num_processes) as pool:
            # Create partial function with fixed arguments
            process_func = partial(process_single_xml,folder_path=folder_containing_xml_files,xpath_expressions=list_of_xpath_expressions)
            
            # Process files and collect results
            for i, (file_results, file_matches, matching_file) in enumerate(pool.imap_unordered(process_func, xml_files)):
                
                final_results.extend(file_results)
                total_sum_matches += file_matches
                total_matching_files += matching_file
                
                print(f"Processing file {i + 1} of {total_files}")
            
        return final_results, total_sum_matches, total_matching_files
                

def process_xpath_result(expression: str, result, filename: str) -> List[Dict]:
    """Process xpath results for a single expression."""
    results = []
    
    if "/@" in expression:
        attribute_name = expression.split("@")[-1]
        key = f"Attribute {attribute_name} Value"
        
        # Create separate entry for each result
        for elem in result:
            if elem.strip():
                results.append({
                    "Filename": filename,
                    key: elem.strip()
                })
                
    elif "/text()" in expression:
        tag_name = expression.split("/")[-2]
        key = f"Tag {tag_name} Value"
        
        # Create separate entry for each result
        for elem in result:
            if elem.strip():
                results.append({
                    "Filename": filename,
                    key: elem.strip()
                })
                
    elif "[@" in expression:
        match = re.search(r"@([^=]+)", expression)
        if match:
            attribute_name = match.group(1).strip()
            key = f"Attribute {attribute_name} Value"
            
            # Create separate entry for each result
            for elem in result:
                value = elem.get(attribute_name)
                if value:
                    results.append({
                        "Filename": filename,
                        key: value
                    })
    
    return results


def search_and_export(folder_containing_xml_files, list_of_xpath_filters):

    matching_results, total_matches_found, total_matching_files = evaluate_xml_files_matching(
        folder_containing_xml_files, list_of_xpath_filters)

    if not matching_results:
        print("No matches found", "No matches found by searching with the added filters.")
        return
    
    # Define headers excluding Index
    headers = ["Filename"]
    # Add all other headers excluding Filename
    additional_headers = set()
    for dic in matching_results:
        additional_headers.update(key for key in dic.keys() if key != "Filename")
    headers.extend(sorted(additional_headers))

    with open("export\\result.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile, 
            fieldnames=headers, 
            delimiter=",", 
            extrasaction="ignore", 
            quotechar='"', 
            quoting=csv.QUOTE_ALL
        )
        writer.writeheader()

    # Group results by filename
        results_by_filename = {}
        for match in matching_results:
            filename = match["Filename"]
            if filename not in results_by_filename:
                results_by_filename[filename] = []
            results_by_filename[filename].append(match)

        # Process each file's results
        for filename, file_matches in results_by_filename.items():
            # Align values for each filename
            aligned_rows = {}
            for match in file_matches:
                for key, value in match.items():
                    if key != "Filename" and value:  # Ignore Filename and empty values
                        if key not in aligned_rows:
                            aligned_rows[key] = []
                        aligned_rows[key].append(value)

            # Get the maximum number of aligned rows
            max_rows = max(len(values) for values in aligned_rows.values())
            for i in range(max_rows):
                row = {"Filename": filename}
                for key, values in aligned_rows.items():
                    if i < len(values):
                        row[key] = values[i]
                writer.writerow(row)

if __name__ == "__main__": 
    multiprocessing.freeze_support()
    # Usage
    folder_containing_xml_files = "XMLTest"
    xpath_xpressions_list = ["//filter/@description", "//filter/@id"]
    search_and_export(folder_containing_xml_files, xpath_xpressions_list)
