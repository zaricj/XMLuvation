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
    - 'encoding' --> XMLUtils.get_xml_encoding(self.get_xml_file_path)
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


class CSVConversionController:
    """Handles methods and logic for csv_conversion_groupbox
    """
    def __init__(self, main_window:object):
        self.main_window = main_window
        self.ui = main_window.ui
            
    def start_csv_conversion(self):
        csv_file_path = self.ui.line_edit_csv_conversion_path_input.text()
        output_converted_file_path = self.ui.line_edit_csv_conversion_path_output.text()
        write_index = self.ui.checkbox_write_index_column.isChecked()

        try:
            # Check if QLineEdit widgets aren't empty
            if not csv_file_path:
                raise FileNotFoundError
            elif not output_converted_file_path:
                raise FileNotFoundError
            
            # Detect delimiter
            with open(csv_file_path, encoding="utf-8") as file:
                sample = file.read(1024)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

            # Load CSV
            df = pd.read_csv(csv_file_path, delimiter=delimiter, encoding="utf-8", engine="pyarrow")

            # Get extensions
            _, input_ext = os.path.splitext(csv_file_path)
            _, output_ext = os.path.splitext(output_converted_file_path)
            input_ext = input_ext.lower().lstrip(".")
            output_ext = output_ext.lower().lstrip(".")

            # Define conversion functions
            def to_html(df, path): df.to_html(path, index=write_index)
            def to_json(df, path): df.to_json(path, orient="records", force_ascii=False)
            def to_md(df, path): df.to_markdown(path, index=write_index)
            def to_xlsx(df, path):
                with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=write_index)

            conversion_map = {
                ("csv", "html"): to_html,
                ("csv", "json"): to_json,
                ("csv", "md"): to_md,
                ("csv", "xlsx"): to_xlsx,
            }

            convert_func = conversion_map.get((input_ext, output_ext))

            if not convert_func:
                QMessageBox.warning(self.main_window, "Unsupported Conversion", f"Cannot convert from '{input_ext}' to '{output_ext}'.")
                return

            # Execute conversion
            convert_func(df, output_converted_file_path)

            QMessageBox.information(
                self.main_window,
                "Conversion Successful",
                f"Successfully converted:\n{os.path.basename(csv_file_path)}\nto\n{os.path.basename(output_converted_file_path)}"
            )
        
        except FileNotFoundError:
            QMessageBox.warning(self.main_window, "Path error", "Both the csv input and conversion output paths need to be declared!")

        except Exception as ex:
            msg = f"{type(ex).__name__}: {ex}"
            QMessageBox.critical(self.main_window, "Conversion Error", msg)
