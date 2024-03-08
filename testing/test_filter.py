import xml.etree.ElementTree as ET

# Function to parse XML file and extract relevant information
def parse_xml(xml_file, tag_name=None, tag_value=None, attribute_name=None, attribute_value=None):
    try:
        filtered_data = []
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        for element in root.iter(tag_name):
            if tag_value and element.text != tag_value:
                continue
            if attribute_name and attribute_value:
                if element.attrib.get(attribute_name) != attribute_value:
                    continue
            
            yield {
                'Tag Name': element.tag,
                'Tag Value': element.text,
                'Attributes': element.attrib,
                'Attribute Value': element.attrib.get(attribute_name)
            }
            
            # If all conditions are met, add the element to the filtered data
            filtered_data.append(element)
            
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")
        
    return filtered_data

# Function to process XML file with filtering
def process_xml_file(file_path, filter_criteria):
    try:
        matching_fields = []
        for criteria in filter_criteria:
            # Unpack criteria
            tag_name, tag_value, attribute_name, attribute_value = criteria
            
            # Parse XML file with filter criteria
            filtered_data = list(parse_xml(file_path, tag_name, tag_value, attribute_name, attribute_value))
            
            # Add filtered data to matching fields
            matching_fields.extend(filtered_data)
            
            # Log matching fields
            for field in filtered_data:
                print(f"Matching Field: {field}")
            
        return matching_fields
    
    except Exception as e:
        print(f"Error processing XML file: {e}")
        return []

# Example usage
file_path = "C:/Users/Natasa/Desktop/Github/XMLuvation/XML_Files/mailtest.xml"
log_queue = None  # Replace with your log queue implementation
filter_criteria = [
    ("apply_for_all_excel", "false", None, None)
]

matching_fields = process_xml_file(file_path, filter_criteria)
print(f"MATCHING FIELDS: {matching_fields}")
