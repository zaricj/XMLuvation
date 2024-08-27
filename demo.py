from lxml import etree as ET
import csv
import os
import re

def get_xml_data(xml_file: str):
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    list_of_tag_names = set()
    list_of_tag_values = set()
    list_of_attribute_names = set()
    list_of_attribute_values = set()
    
    for element in root.iter():
        list_of_tag_names.add(element.tag)
        if element.text:
            list_of_tag_values.add(element.text.strip())
            
        for attribute_name, attribute_value in element.attrib.items():
            list_of_attribute_names.add(attribute_name)
            list_of_attribute_values.add(attribute_value)
            
    
    grouped_data_dictionary = {
        "TagName": sorted(list_of_tag_names),
        "TagValue": sorted(list_of_tag_values),
        "AttributeName": sorted(list_of_attribute_names),
        "AttributeValue": sorted(list_of_attribute_values)
    }
    print(grouped_data_dictionary)
    print(type(grouped_data_dictionary))
    return grouped_data_dictionary

# Pattern for more complex XPath expressions
complex_xpath_pattern = r"""
    ^                           # Start of the string
    //                          # Double forward slash
    (\w+)                       # First tag (some_tag)
    \[@                         # Opening square bracket and @
    (\w+)                       # Attribute name (some_attribute)
    =                           # Equals sign
    '([^']*)'                   # Attribute value in single quotes
    \]                          # Closing square bracket
    (?:                         # Non-capturing group
        /(\w+)                  # Optional second tag (another_tag)
    )?                          # This group is optional
    /text\(\)                   # Ending with /text()
    $                           # End of the string
"""

# Pattern for simpler XPath expressions
simple_xpath_pattern = r"""
    ^                           # Start of the string
    //                          # Double forward slash
    (\w+)                       # Tag name (some_tag)
    /                           # Forward slash
    (?:                         # Non-capturing group for two alternatives
        text\(\)                # Either text()
        |                       # OR
        @(\w+)                  # @some_attribute
    )
    $                           # End of the string
"""

# Compile the patterns
complex_xpath_regex = re.compile(complex_xpath_pattern, re.VERBOSE)
simple_xpath_regex = re.compile(simple_xpath_pattern, re.VERBOSE)

# Test function
def test_xpath(xpath):
    complex_match = complex_xpath_regex.match(xpath)
    simple_match = simple_xpath_regex.match(xpath)
    
    if complex_match:
        print(f"Complex XPath matched: {xpath}")
        print(f"  Tag: {complex_match.group(1)}")
        print(f"  Attribute: {complex_match.group(2)}")
        print(f"  Value: {complex_match.group(3)}")
        print(f"  Second tag (if any): {complex_match.group(4)}")
    elif simple_match:
        print(f"Simple XPath matched: {xpath}")
        print(f"  Tag: {simple_match.group(1)}")
        if simple_match.group(2):
            print(f"  Attribute: {simple_match.group(2)}")
        else:
            print("  Ends with: text()")
    else:
        print(f"No match: {xpath}")



if __name__ == "__main__":
    
    xml_file = "TestXML.xml"
    get_xml_data(xml_file)
    
    # Test cases
    test_cases = [
        "//some_tag[@some_attribute='some_value']/another_tag/text()",
        "//some_tag[@some_attribute='some_value']/text()",
        "//some_tag/text()",
        "//filter/@id",
        "//invalid_xpath",
    ]

    for case in test_cases:
        test_xpath(case)
        print()