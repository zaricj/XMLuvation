from lxml import etree

# Parse the XML file
xml_file = "lobster.xml"
tree = etree.parse(xml_file)

# XPath expression to get attribute value of "name" for "country" elements
attribute_name = tree.xpath("name(//datawizardprofile/@name)")
attribute_value = tree.xpath("string(//datawizardprofile/@name)") # ("//country/@name")[0] gets first value

text_content = tree.xpath("string(//filter/@description='send mail(a,b,c,d,e,f,g[,h,i,j,k,l])')")

anotha_xpath = tree.xpath("string(//id='6b61b635:18a6a69156c:7d89.642dc09126b690a0:6b61b635:18968469793:-8000' )")

test = tree.xpath("//fill_after_template[text()='false']")

print(test)

for elem in test:
    print(elem.tag)

print(f"Attribute Name: {attribute_name}")
print(f"Attribute Value: {attribute_value}")
print(f"Text Content: {text_content}")
print(f"anotha xpath: {anotha_xpath}")

datawiz = tree.xpath("//filter[@id='127']/@description")
value_from_list = datawiz[0]
print(f"Datawiz {value_from_list}")