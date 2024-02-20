import csv
import xml.etree.ElementTree as ET

xml_file = "Data.xml"

import requests

x = requests.get('https://w3schools.com/python/demopage.htm')

print(x.text)
