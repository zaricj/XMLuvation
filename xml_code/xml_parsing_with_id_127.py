import xml.etree.ElementTree as ET
from logging.handlers import RotatingFileHandler
import logging
import os
import glob
import multiprocessing
import csv

"""_summary_

Skript welcher alle Lobster Profile als XML Dateinen durchgeht in einem bestimmten ordner und
Die Profile die den Filter ID = 127 haben (Funktion im Mapping Send Mail) werden in ein Log geschrieben

Returns:
    _type_: _description_
    """

# Create a rotating file handler
file_handler = RotatingFileHandler(filename="Profiles_Send_Mail_Mapping.log",
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

    outputtree = root.find(".//outputtree")
    fields = outputtree.findall(".//field")

    matching_fields = []
    for field in fields:
        field_name = field.attrib.get("name")
        filter_127 = field.find(".//filter[@id='127']")
        if filter_127 is not None:
            matching_fields.append(field_name)
            log_queue.put(f"Profilename: '{root.attrib['name']}' enthält Funktion: 'send mail(a,b,c,d,e,f,g[,h,i,j,k,l])' im Feld: '{field_name}'")

    return matching_fields

def process_batch(file_paths, log_queue):
    all_matching_fields = []
    for file_path in file_paths:
        matching_fields = process_xml_file(file_path, log_queue)
        all_matching_fields.extend(matching_fields)
    return all_matching_fields

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
    while not log_queue.empty():
        log_message = log_queue.get()
        logger.info(log_message)

    # Flatten the list of matching fields
    all_matching_fields = [field for result in results for field in result]

    print("Total matching fields found:", len(all_matching_fields))