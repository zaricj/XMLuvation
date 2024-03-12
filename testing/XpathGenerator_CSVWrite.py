from lxml import etree as ET
import os
import csv

def evaluate_xml_files_matching(folder_path, matching_filters):
    try:
        final_results = []
        total_files = sum(1 for filename in os.listdir(folder_path) if filename.endswith('.xml'))
        progress_increment = 100 / total_files
        current_progress = 0
        print(current_progress)
        total_sum_matches = 0
        total_matching_files = 0
        try:
            for filename in os.listdir(folder_path):
                if filename.endswith('.xml'):
                  file_path = os.path.join(folder_path, filename)
                  # Update progress bar after processing each file
                  current_progress += progress_increment
                  print(round(current_progress,2))

                  tree = ET.parse(file_path)
                  total_matches = 0  # Initialize total matches for the file
                  print(f"Evaluating file: {filename}")
                  current_file_results = {"Filename": filename}  # Create a dictionary for the current file
                  for expression in matching_filters:
                    result = tree.xpath(expression) # List of found Element Objects
                    total_matches += len(result) # Accumulate total matches across filters
                  current_file_results["Total Matching Tags"] = total_matches
                  if total_matches > 0:  # Only append if there are any matches for the entire file
                    for idx, expression in enumerate(matching_filters):
                        current_file_results[f"Filter {idx+1}"] = expression  # Add filter expressions with index
                        final_results.append(current_file_results)
                  total_sum_matches += total_matches
                  total_matching_files += 1 if total_matches > 0 else 0  # Increment only if there are matches
                  
            return final_results, total_sum_matches, total_matching_files
        
        except Exception as e:
            print(f"Error processing {filename}, Error: {e}")
    except Exception as ex:
        print(f"Exception in Program {ex}")


def export_evaluation_as_csv(csv_output_path, folder_path, matching_filters):
    try:
        final_results, total_matches_found, total_matching_files = evaluate_xml_files_matching(folder_path, matching_filters)
        # Save matching results to CSV file
        if final_results:  # Check if matching results exist and logging message doesn't     
            print(f"Final Results in Export Function: {final_results}")
            #keys_of_list_dictionary = set().union(*(dic.keys() for dic in final_results))
            keys_of_dictlist = [key for key in {key:None for dic in final_results for key in dic}]
            with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = keys_of_dictlist
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                # Write matching results
                for match in final_results:
                    writer.writerow(match)
                csvfile.close()
            print(f"Matches saved to {csv_output_path}\nFound {total_matching_files} files that have a total sum of {total_matches_found} matches.")
        else:
            print("No matches found.")
    except Exception as e:
        print(f"Exception in Program {e}")
        
csv_output_path = "C:/Users/ZaricJ/Desktop/Programming/GitHub/XMLuvation/OutputCSV.csv"
folder_path = "C:/Users/ZaricJ/Desktop/Programming/GitHub/XMLuvation/TestPath"
matching_filters = ["//old_checking[text()='false']","//filter[@id='127']","//use_contrl[text()='false']"]

export_evaluation_as_csv(csv_output_path,folder_path,matching_filters)
