import csv
import os
import pandas as pd
from PySide6.QtWidgets import QMessageBox

class ComboBoxStateController:
    """
    Controller the states of the ComboBoxes based on the selected values. Values need to be loaded from a XML file.
    
    parsed_xml_data is a dictionary and contains the following keys:
    - 'xml_string' --> xml_string,
    - 'tags' --> sorted(tags),
    - 'tag_values' --> sorted(tag_values),
    - 'attributes' --> sorted(attributes),
    - 'attribute_values' --> sorted(attribute_values),
    - 'namespaces' --> sorted(namespaces),
    - 'file_path' --> self.get_xml_file()_path,
    - 'root_tag' --> root.tag,
    - 'element_count' --> len(list(root.iter())),
    - 'encoding' --> XMLUtils.get_xml_encoding(self.get_xml_file()_path)
    """
    def __init__(self, main_window:object, parsed_xml_data:dict):
        self.main_window = main_window
        self.ui = main_window.ui
        self.parsed_xml_data = parsed_xml_data
        
    def set_parsed_data(self, new_data: dict):
        self.parsed_xml_data = new_data
    
    def get_parsed_data(self):
        return self.parsed_xml_data
        
    def get_xml_file(self):
        return self.parsed_xml_data.get("file_path")
        
    # === Contains the Logic for the ComboBoxes textChanged signal === #
    def on_tag_name_changed(self, selected_tag:str):
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


    def on_attribute_name_changed(self, selected_attribute:str):
        print(f"Attribute name changed to: {selected_attribute}")
        try:
            selected_tag = self.ui.combobox_tag_names.currentText()
            attribute_values = self.get_attribute_values(selected_tag, selected_attribute)
            self.ui.combobox_attribute_values.clear()
            self.ui.combobox_attribute_values.addItems(attribute_values)

            # Disable attribute value combo box if there are no attribute values
            if not attribute_values:
                self.ui.combobox_attribute_values.setDisabled(True)
                self.ui.combobox_attribute_values.clear()
            else:
                self.ui.combobox_attribute_values.setDisabled(False)

            # Disable tag value combo box if the selected tag has no values
            values_xml = self.get_tag_values(selected_tag)

            if not values_xml:
                self.ui.combobox_tag_values.setDisabled(True)
                self.ui.combobox_tag_values.clear()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window,"An exception occurred on attribute name changed:", message)


    def get_attribute_values(self, selected_tag: str, selected_attribute: str):
        if not selected_tag or not selected_attribute:
            return []
        try:
            return self.parsed_xml_data.get('tag_attr_to_values', {}).get((selected_tag, selected_attribute), [])
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "An exception occurred on getting attribute values", message)
            return []


    def get_tag_values(self, selected_tag: str):
        if not selected_tag:
            return []
        try:
            return self.parsed_xml_data.get('tag_to_values', {}).get(selected_tag, [])
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "An exception occurred on get tag values:", message)
            return []


    def get_attributes(self, selected_tag: str):
        if not selected_tag:
            return []
        try:
            return self.parsed_xml_data.get('tag_to_attributes', {}).get(selected_tag, [])
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "An exception occurred on get attributes:", message)
            return []


class CSVExportController:
    def __init__(self, main_window:object):
        self.main_window = main_window
        self.ui = main_window.ui
            
    def start_csv_conversion(self):
        csv_input_file = self.ui.line_edit_csv_conversion_path_input.text()
        excel_output_file = self.ui.line_edit_csv_conversion_path_output.text()
        checkbox = self.ui.checkbox_write_index_column.isChecked()
        try:
            with open(csv_input_file, encoding="utf-8") as file:
                sample = file.read(4096)
                sniffer = csv.Sniffer()
                get_delimiter = sniffer.sniff(sample).delimiter
            if not checkbox:
                csv_df = pd.read_csv(csv_input_file, delimiter=get_delimiter, encoding="utf-8", index_col=0)
            else:
                csv_df = pd.read_csv(csv_input_file, delimiter=get_delimiter, encoding="utf-8")
                
            CONVERSION_FUNCTIONS = {
                # CSV Conversion
                ("csv", "html"): (csv_df, pd.DataFrame.to_html),
                ("csv", "json"): (csv_df, pd.DataFrame.to_json),
                ("csv", "xlsx"): (csv_df, pd.DataFrame.to_excel),
                ("csv", "md"): (csv_df, pd.DataFrame.to_markdown),
            }
            
            filename, input_extension  = os.path.splitext(csv_input_file)
            filename, output_extension  = os.path.splitext(excel_output_file)
            
            read_func, write_func = CONVERSION_FUNCTIONS.get(
            (input_extension, output_extension), (None, None))
            
            if read_func is None or write_func is None:
                QMessageBox.warning(self, "Unsupported Conversion", "Error converting file, unsupported conversion...")
                return
            
            csv_df = read_func
            write_func(csv_df, excel_output_file)
            QMessageBox.info(self.main_window, "Conversion Successful", f"Successfully converted\n{os.path.basename(csv_input_file)}\nto\n{os.path.basename(excel_output_file)}")
            
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception exporting CSV", f"Error exporting CSV: {message}")


    # ======= End FUNCTIONS FOR create_csv_conversion_group ======= #
