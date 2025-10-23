from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

class ComboboxActionsMixin:
    """Handles menu bar actions only"""
    
    def connect_combobox_actions(self: "MainWindow"):
        self.ui.combobox_tag_names.currentTextChanged.connect(self.on_tag_name_changed)
        self.ui.combobox_attribute_names.currentTextChanged.connect(self.on_attribute_name_changed)
        
    @Slot()
    def on_tag_name_changed(self, selected_tag: str):
        """When the Combobox for the tag name changes

        Args:
            selected_tag (str): Currently selected value from the self.ui.combobox_tag_names
        """
        if not selected_tag:
            return []
        try:
            attributes = self.get_attributes(selected_tag)
            self.attr_name.clear()
            self.attr_name.addItems(attributes)

            values_xml = self.get_tag_values(selected_tag)
            self.tag_value.clear()
            self.tag_value.addItems(values_xml)

            # Disable tag value combo box if there are no values for the selected tag
            if not values_xml or all(value.strip() == "" for value in values_xml if value is not None):
                self.tag_value.setDisabled(True)
                self.tag_value.clear()
            else:
                self.tag_value.setDisabled(False)

            # Disable attribute name and value combo boxes if there are no attributes for the selected tag
            if not attributes:
                self.attr_name.setDisabled(True)
                self.attr_name.clear()
                self.attr_value.setDisabled(True)
                self.attr_value.clear()
            else:
                self.attr_name.setDisabled(False)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "An exception occurred on tag name changed:", message)

    @Slot()
    def on_attribute_name_changed(self: "MainWindow", selected_attribute: str):
        """When the Combobox for the attribute name changes

        Args:
            selected_attribute (str): Currently selected value from the self.ui.combobox_attribute_names
        """
        try:
            selected_tag = self.tag_name.currentText()
            attribute_values = self.get_attribute_values(
                selected_tag, selected_attribute)
            self.attr_value.clear()
            self.attr_value.addItems(attribute_values)

            # Disable attribute value combo box if there are no attribute values
            if not attribute_values:
                self.attr_value.setDisabled(True)
                self.attr_value.clear()
            else:
                self.attr_value.setDisabled(False)

            # Disable tag value combo box if the selected tag has no values
            values_xml = self.get_tag_values(selected_tag)

            if not values_xml:
                self.tag_value.setDisabled(True)
                self.tag_value.clear()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "An exception occurred on attribute name changed:", message)

    @Slot()
    def get_attribute_values(self: "MainWindow", selected_tag: str, selected_attribute: str):
        """Get the attribute values based on the selected combobox values in tag name and attribute name

        Args:
            selected_tag (str): Currently selected value from the self.ui.combobox_tag_names
            selected_attribute (str): Currently selected value from the self.ui.combobox_attribute_names
        """
        if not selected_tag or not selected_attribute:
            return []
        try:
            return self.parsed_xml_data.get('tag_attr_to_values', {}).get((selected_tag, selected_attribute), [])
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "An exception occurred on getting attribute values", message)
            return []

    @Slot()
    def get_tag_values(self: "MainWindow", selected_tag: str):
        """Get the tag values based on the selected combobox values in tag name

        Args:
            selected_tag (str): Currently selected value from the self.ui.combobox_tag_names
        """
        if not selected_tag:
            return []
        try:
            return self.parsed_xml_data.get('tag_to_values', {}).get(selected_tag, [])
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "An exception occurred on get tag values:", message)
            return []
        
    @Slot()
    def get_attributes(self: "MainWindow", selected_tag: str):
        """Get the attribute names based on the selected combobox values in tag name

        Args:
            selected_tag (str): Currently selected value from the self.ui.combobox_tag_names
        """
        if not selected_tag:
            return []
        try:
            return self.parsed_xml_data.get('tag_to_attributes', {}).get(selected_tag, [])
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "An exception occurred on get attributes:", message)
            return []