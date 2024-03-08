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
    print(child.tag, child.attrib)
    for sibling in child:
        print(sibling.tag, sibling.attrib)
        print(type(sibling.tag))
        print(type(sibling.attrib))