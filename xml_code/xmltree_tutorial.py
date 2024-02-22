import csv
import xml.etree.ElementTree as ET

datafile = "Data.xml"

tree = ET.parse(datafile)
root = tree.getroot()

def root_has_attributes():
    root_tag = root.tag
    print(f"Root Tag: {root_tag}")
    root_attribute = root.attrib
    
    if root_attribute:
        print(root_attribute)
    else:
        print("Root has no attributes")
    
#for child in root:
#    print(f"Child Tag: {child.tag} - Child Attribute: {child.attrib}")
#    for subchild in child:
#        print(f"Subchild Tag: {subchild.tag} - Subchild Attribute: {subchild.attrib}")
#        for sibling in subchild:
#            print(f"Sibling tag: {sibling.tag} - Sibling Attribute {sibling.attrib}")

for element in root.iter("rank"): # Add Parameter in Function later for root.iter(parameter)
    print(f"Tag: {element.tag}") # Add to Combo Element
    print(f"Attribute: {element.attrib}") # Add to Combo Element
    print(f"Value: {element.text}") # Add to Combo Element

for country in root.findall('country'):
    countryAtt = country.attrib
    print(countryAtt)
    print(country.get("name"))


# Printing in a Text File for easier reading...

#with open("text.txt", "w") as f:
#    f.write(f"Root {root_tag} - {root_attribute}\n\n")
#
#    for child in root:
#        f.write(f"CHILD {child.tag} - {child.attrib} - {child.text}\n")
#        for children in child:
#            f.write(f"\t CHILDREN {children.tag} - {children.attrib} - {children.text}\n")
#            for sibling in children:
#                f.write(f"\t\t SIBLING {sibling.tag} - {sibling.attrib} - {sibling.text}")
