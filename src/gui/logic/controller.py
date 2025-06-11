from lxml import etree as ET
from PySide6.QtWidgets import QMessageBox

class ComboBoxStateController:
    """
    Controller the states of the ComboBoxes based on the selected values. Values need to be loaded from a XML file.
    
    parsed_xml_data is a dictionary and contains the following keys:
            'xml_string' --> xml_string,
            'tags' --> sorted(tags),
            'tag_values' --> sorted(tag_values),
            'attributes' --> sorted(attributes),
            'attribute_values' --> sorted(attribute_values),
            'namespaces' --> sorted(namespaces),
            'file_path' --> self.xml_file_path,
            'root_tag' --> root.tag,
            'element_count' --> len(list(root.iter())),
            'encoding' --> XMLUtils.get_xml_encoding(self.xml_file_path)
    """
    def __init__(self, main_window, parsed_xml_data):
        self.main_window = main_window
        self.ui = main_window.ui
        self.parsed_xml_data = parsed_xml_data
        
    def set_parsed_data(self, new_data: dict):
        self.parsed_xml_data = new_data
        
    # === Contains the Logic for the ComboBoxes textChanged signal === #
    def on_tag_name_changed(self, selected_tag):
            print(f"Tag name changed to: {selected_tag}")
            if not selected_tag:
                return []
            try:
                attributes = self.get_attributes(selected_tag)
                self.ui.combobox_attribute_names.clear()
                self.ui.combobox_attribute_names.addItems(attributes)
    
                values_xml = self.get_tag_values(selected_tag)
                self.ui.combobox_tag_values.clear()
                self.ui.combobox_tag_values.addItems(values_xml)
    
                # Disable tag value combo box if there are no values for the selected tag
                if not values_xml or all(value.strip() == "" for value in values_xml if value is not None):
                    self.ui.combobox_tag_values.setDisabled(True)
                    self.ui.combobox_tag_values.clear()
                else:
                    self.ui.combobox_tag_values.setDisabled(False)
    
                # Disable attribute name and value combo boxes if there are no attributes for the selected tag
                if not attributes:
                    self.ui.combobox_attribute_names.setDisabled(True)
                    self.ui.combobox_attribute_names.clear()
                    self.ui.combobox_attribute_values.setDisabled(True)
                    self.ui.combobox_attribute_values.clear()
                else:
                    self.ui.combobox_attribute_names.setDisabled(False)
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self.main_window, "An exception occurred on tag name changed:", message)


    def on_attribute_name_changed(self, selected_attribute):
        print(f"Attribute name changed to: {selected_attribute}")
        try:
            selected_tag = self.ui.combobox_tag_names.currentText()
            attribute_values = self.get_attribute_values(self.xml_file, selected_tag, selected_attribute)
            self.ui.combobox_attribute_values.clear()
            self.ui.combobox_attribute_values.addItems(attribute_values)

            # Disable attribute value combo box if there are no attribute values
            if not attribute_values:
                self.ui.combobox_attribute_values.setDisabled(True)
                self.ui.combobox_attribute_values.clear()
            else:
                self.ui.combobox_attribute_values.setDisabled(False)

            # Disable tag value combo box if the selected tag has no values
            values_xml = self.get_tag_values(self.xml_file, selected_tag)

            if not values_xml:
                self.ui.combobox_tag_values.setDisabled(True)
                self.ui.combobox_tag_values.clear()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window,"An exception occurred on attribute name changed:", message)


    def get_attribute_values(self, selected_tag, selected_attribute):
        if not selected_tag or not selected_attribute:
            return []
        try:
            elements = self.parsed_xml_data.get("attribute_values", {})
            values = set()
            for elem in elements.get(selected_tag, []):
                if selected_attribute in elem.attrib:
                    values.add(elem.attrib[selected_attribute])
            return sorted(values)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Error getting attribute values", message)
            return []


    def get_tag_values(self, selected_tag):
        if not selected_tag:
            return []
        try:
            elements = self.parsed_xml_data.get("tag_values", {})
            values = set()
            for elem in elements.get(selected_tag, []):
                values.update(elem.attrib.keys())
            return sorted(values)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window,"An exception occurred on get tag values:", message)
            return []


    def get_attributes(self, selected_tag):
        if not selected_tag:
            return []
        try:
            elements = self.parsed_xml_data.get("attributes", {})
            attributes = set()
            for elem in elements.get(selected_tag, []):
                attributes.update(elem.attrib.keys())
            return sorted(attributes)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window,"An exception occurred on get attributes:", message)
            return []