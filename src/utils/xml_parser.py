from PySide6.QtCore import Signal, QObject
from lxml import etree as ET


class XMLParserThread(QObject):
    """Worker thread for parsing XML files.

    Args:
        QObject (QObject): Base class for all Qt objects, providing signals and slots.
    """
    finished = Signal(dict)
    show_error_message = Signal(str, str)

    def __init__(self, parent, xml_file):
        super().__init__()
        self.parent = parent
        self.xml_file = xml_file

    def run(self):
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            xml_string = ET.tostring(root, encoding="unicode", pretty_print=True)

            tags = set()
            tag_values = set()
            attributes = set()
            attribute_values = set()

            for elem in root.iter():
                tags.add(elem.tag)
                if elem.text and elem.text.strip():
                    tag_values.add(elem.text.strip())
                for attr, value in elem.attrib.items():
                    attributes.add(attr)
                    attribute_values.add(value)

            result = {
                'xml_string': xml_string,
                'tags': sorted(tags),
                'tag_values': sorted(tag_values),
                'attributes': sorted(attributes),
                'attribute_values': sorted(attribute_values)
            }
            
        except Exception as ex:
            self.show_error_message.emit("An exception occurred", str(ex))
        finally:
            self.finished.emit(result)