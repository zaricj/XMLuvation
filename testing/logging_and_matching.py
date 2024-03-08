import os
import xml.etree.ElementTree as ET
import re

def evaluate_xml_files_logging(folder_path, output_log_message, matching_filters=None):
    """Evaluates XML files in the given folder, performing both logging and matching operations.

    Args:
        folder_path (str): Path to the folder containing XML files.
        output_log_message (str): Comma-separated message for logging, with placeholders starting with '!'.
        matching_filters (list, optional): List of XPath expressions for matching. Defaults to None.

    Returns:
        tuple: A tuple containing two lists:
            - matches: A list of matches, where each match is a dictionary containing 'Filename' and 'Total Matches' keys.
            - log_results: A dictionary with log message parts and their corresponding values, or an empty dictionary if no logging message is provided.
    """

    matches = []
    log_results = {}

    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            file_path = os.path.join(folder_path, filename)
            try:
                tree = ET.parse(file_path)

                # Perform matching if filters are provided
                if matching_filters:
                    for expression in matching_filters:
                        result = tree.xpath(expression)
                        total_matches = len(result)
                        match = {"Filename": filename, "Total Matches": total_matches}
                        matches.append(match)

                # Perform logging if a message is provided
                if output_log_message:
                    parts = re.sub(r',\s*', ',', output_log_message).split(',')
                    log_values = []
                    field_names = []
                    for part in parts:
                        if part.startswith("!"):
                            xpath = part[1:]
                            result = tree.xpath(xpath)
                            log_values.append(result)
                        else:
                            field_names.append(part)

                    if log_values:
                        log_message = ' '.join([f"{field_name}: {log_part}" for field_name, log_part in zip(field_names, log_values)])
                        log_results = {field_name: log_part for field_name, log_part in zip(field_names, log_values)}

            except Exception as e:
                print(f"Error processing {filename}, Error: {e}")

    return matches, log_results
