import csv
import xml.etree.ElementTree as ET

datafile = "movies.xml"

tree = ET.parse(datafile)
root = tree.getroot()

root_tag = root.tag
print(f"Root Tag: {root_tag}")
root_attribute = root.attrib

if root_attribute:
    print(root_attribute)
else:
    print("Root has no attributes")
    
for child in root:
    print(f"Child Tag: {child.tag} - Child Attribute: {child.attrib}")
    for children in child:
        print(f"Children Tag: {children.tag} - Children Attribute: {children.attrib}")
        for sibling in children:
            print(f"Sibling tag: {sibling.tag} - Sibling Attribute {sibling.attrib}")

#with open("text.txt", "w") as f:
#    f.write(f"Root {root_tag} - {root_attribute}\n\n")
#
#    for child in root:
#        f.write(f"CHILD {child.tag} - {child.attrib} - {child.text}\n")
#        for children in child:
#            f.write(f"\t CHILDREN {children.tag} - {children.attrib} - {children.text}\n")
#            for sibling in children:
#                f.write(f"\t\t SIBLING {sibling.tag} - {sibling.attrib} - {sibling.text}")
