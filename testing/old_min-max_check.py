import xml.etree.ElementTree as ET
from logging.handlers import RotatingFileHandler
import logging
import os
import glob
import multiprocessing
import csv

"""_summary_

Returns:
    _type_: _description_
    """

# Create a rotating file handler
file_handler = RotatingFileHandler(filename="Alte_min-max_auswertung.log",
                                   maxBytes=50 * 1024 * 1024,  # Max File Size: 50 MB
                                   backupCount=2,  # Number of backup files to keep
                                   encoding="utf-8",  # Specify the encoding if needed
                                   delay=False)  # Set to True if you want to delay file opening

# Define the log format
formatter = logging.Formatter("%(name)s %(levelname)s %(message)s")
# Set the formatter for the file handler
file_handler.setFormatter(formatter)

# Create a logger and add the file handler
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)  # Set the desired log level

def process_xml_file(file_path, log_queue):
    tree = ET.parse(file_path)
    root = tree.getroot()

    dataproperties = root.find(".//dataproperties")
    old_checking = dataproperties.findall(".//old_checking")
    for value in old_checking:
        old_checking_value = value.text
        # print(f"<old_checking> Tag has Value: {old_checking_value}")

    matching_fields = []
    if old_checking_value == "true":
        matching_fields.append(old_checking_value)
        log_message = f"Profilename: {root.attrib['name']}"
        log_queue.put(log_message)

    return matching_fields

# Log als .log file - remove comments to activate but comment the process_batch function under it

#def process_batch(file_paths, log_queue):
#    all_matching_fields = []
#    for file_path in file_paths:
#        matching_fields = process_xml_file(file_path, log_queue)
#        all_matching_fields.extend(matching_fields)
#    return all_matching_fields

# CSV Logging
def process_batch(file_paths, log_queue):
    for file_path in file_paths:
        process_xml_file(file_path, log_queue)

if __name__ == "__main__":
    source_dir = "C:/Users/ZaricJ/Documents/00 Aufgaben/01 Februar 2024/Lobster Admin Auswertung/Profile Export as XML"
    xml_files = glob.glob(os.path.join(source_dir, "*.xml"))

    batch_size = 100  # Adjust as needed
    file_batches = [xml_files[i:i+batch_size] for i in range(0, len(xml_files), batch_size)]

    manager = multiprocessing.Manager()
    log_queue = manager.Queue()  # Create a managed queue for logging

    num_processes = multiprocessing.cpu_count()  # Use all available CPU cores
    pool = multiprocessing.Pool(processes=num_processes)
    results = pool.starmap(process_batch, [(batch, log_queue) for batch in file_batches])
    pool.close()
    pool.join()

    # Process log messages from the queue and write them to the log file
    
    # while not log_queue.empty():
    #     log_message = log_queue.get()
    #     logger.info(log_message)

    # Flatten the list of matching fields
    # all_matching_fields = [field for result in results for field in result]
    # print("Total matching fields found:", len(all_matching_fields))
    
    # Process log messages from the queue and write them to a CSV file
    csv_filename = "log_data.csv"
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['Profilename']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        while not log_queue.empty():
            log_message = log_queue.get()
            profilename = log_message.split(":")[1].strip()
            writer.writerow({'Profilename': profilename})

    print("Log data has been written to:", csv_filename)