import csv
import xml.etree.ElementTree as ET

datafile = "Data.xml"

tree = ET.parse(datafile)
root = tree.getroot()

root_tag = root.tag
print(root_tag)
root_attribute = root.attrib
print(root_attribute)

for child in root:
    print(f"Child Tag: {child.tag} - Child Attribute: {child.attrib}")
    
for element in child:
    print(f"Element Tag: {element.tag} - Element Attribute: {element.attrib}")

#with open("text.txt", "w") as f:
#    f.write(f"Root Tag: {root_tag} - Root Attribute: {root_attribute}\n\n")
#
#    for child in root:
#        f.write(f"Child Tag: {child.tag} - Child Attribute: {child.attrib}\n")
#        for childs_child in child:
#            f.write(f"\tChilds_child Tag: {childs_child.tag} - Childs_child Attribute: {childs_child.attrib}\n")
#            for sibling in childs_child:
#                f.write(f"\t\tSibling Tag: {sibling.tag} - Sibling Attribute: {sibling.attrib}\n")
