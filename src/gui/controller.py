import csv
import os
import pandas as pd
from PySide6.QtWidgets import QMessageBox
from utils.xpath_builder import create_xpath_validator
from utils.csv_export import create_csv_exporter

class ComboboxState:
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
    def __init__(self, main_window: object, parsed_xml_data: dict, cb_tag_name: object, cb_tag_value: object, cb_attr_name: object, cb_attr_value: object):
        """Constructor of ComboboxState class

        Args:
            main_window (object): Main window in main.py
            parsed_xml_data (dict): Dictionary of the parsed XML file, fills the Comboboxes
            cb_tag_name (object): QCombobox Widget self.ui.combobox_tag_names
            cb_tag_value (object): QCombobox Widget self.ui.combobox_tag_values
            cb_attr_name (object): QCombobox Widget self.ui.combobox_attribute_names
            cb_attr_value (object): QCombobox Widget self.ui.combobox_attribute_values
        """
        self.main_window = main_window
        self.ui = main_window.ui
        self.parsed_xml_data = parsed_xml_data
        self.tag_name = cb_tag_name
        self.tag_value = cb_tag_value
        self.attr_name = cb_attr_name
        self.attr_value = cb_attr_value
        
    def set_parsed_data(self, new_data: dict):
        self.parsed_xml_data = new_data
    
    def get_parsed_data(self):
        return self.parsed_xml_data
        
    def get_xml_file(self):
        return self.parsed_xml_data.get("file_path")
        
    # === Contains the Logic for the ComboBoxes textChanged signal === #
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
            QMessageBox.critical(self.main_window, "An exception occurred on tag name changed:", message)


    def on_attribute_name_changed(self, selected_attribute: str):
        """When the Combobox for the attribute name changes 

        Args:
            selected_attribute (str): Currently selected value from the self.ui.combobox_attribute_names
        """
        try:
            selected_tag = self.tag_name.currentText()
            attribute_values = self.get_attribute_values(selected_tag, selected_attribute)
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
            QMessageBox.critical(self.main_window,"An exception occurred on attribute name changed:", message)


    def get_attribute_values(self, selected_tag: str, selected_attribute: str):
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
            QMessageBox.critical(self.main_window, "An exception occurred on getting attribute values", message)
            return []


    def get_tag_values(self, selected_tag: str):
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
            QMessageBox.critical(self.main_window, "An exception occurred on get tag values:", message)
            return []


    def get_attributes(self, selected_tag: str):
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
            QMessageBox.critical(self.main_window, "An exception occurred on get attributes:", message)
            return []


class CSVConversion:
    """Handles methods and logic for csv_conversion_groupbox
    """
    def __init__(self, main_window: object, csv_file_to_convert: str, output_path_of_new_file: str, write_index: bool):
        self.main_window = main_window
        self.ui = main_window.ui
        self.csv_file_to_convert = csv_file_to_convert
        self.output_path_of_new_file = output_path_of_new_file
        self.write_index = write_index
            
    def start_csv_conversion(self) -> None:

        try:
            # Check if QLineEdit widgets aren't empty
            if not self.csv_file_to_convert:
                raise FileNotFoundError
            elif not self.output_path_of_new_file:
                raise FileNotFoundError
            
            # Detect delimiter
            with open(self.csv_file_to_convert, encoding="utf-8") as file:
                sample = file.read(1024)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

            # Load CSV
            df = pd.read_csv(self.csv_file_to_convert, delimiter=delimiter, encoding="utf-8", engine="pyarrow")

            # Get extensions
            _, input_ext = os.path.splitext(self.csv_file_to_convert)
            _, output_ext = os.path.splitext(self.output_path_of_new_file)
            input_ext = input_ext.lower().lstrip(".")
            output_ext = output_ext.lower().lstrip(".")

            # Define conversion functions
            def to_html(df, path): df.to_html(path, index=self.write_index)
            def to_json(df, path): df.to_json(path, orient="records", force_ascii=False)
            def to_md(df, path): df.to_markdown(path, index=self.write_index)
            def to_xlsx(df, path):
                with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=self.write_index)

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
            convert_func(df, self.output_path_of_new_file)

            QMessageBox.information(
                self.main_window,
                "Conversion Successful",
                f"Successfully converted:\n{os.path.basename(self.csv_file_to_convert)}\nto\n{os.path.basename(self.output_path_of_new_file)}"
            )
        
        except FileNotFoundError:
            QMessageBox.warning(self.main_window, "Path error", "Both the csv input and conversion output paths need to be declared!")

        except Exception as ex:
            msg = f"{type(ex).__name__}: {ex}"
            QMessageBox.critical(self.main_window, "Conversion Error", msg)


class AddXPathExpressionToList:
    """
    Handles methods and logic of the Button event for adding XPath Expression.
    """
    def __init__(self, main_window: object, xpath_expression: str, xpath_filters: list, list_widget_xpath_expressions: object):
        self.main_window = main_window
        self.ui = main_window.ui
        self.xpath_expression = xpath_expression
        self.xpath_filters = xpath_filters
        self.list_widget_xpath_expressions = list_widget_xpath_expressions
    
        # === QListWidget HANDLER ===
    def add_expression_to_list(self) -> bool:
        """Add the entered or built XPath expression from the QLineEdit to the QListWidget for later searching
        
        Has a built in XPath validator before adding the XPath to the QListWidget
        
        Returns:
            bool: If xpath expression has been successfully added to the list True, else False
        """
        try:
            # Check if the XPath input is not empty:
            if not self.xpath_expression: 
                QMessageBox.information(self.main_window, "Empty XPath", "Please enter a valid XPath expression before adding it to the list.")
                return False
            elif self.xpath_expression and not self._is_duplicate(self.xpath_expression, self.xpath_filters):
                validator = create_xpath_validator()
                self.main_window._connect_xpath_builder_signals(validator)
                # Validate the XPath expression
                validator.xpath_expression = self.xpath_expression
                is_valid = validator.validate_xpath_expression()
                if is_valid:
                    self.xpath_filters.append(self.xpath_expression)
                    self.list_widget_xpath_expressions.addItem(self.xpath_expression)
                    return True
            else:
                QMessageBox.warning(self.main_window, "Duplicate XPath Expression", f"Cannot add duplicate XPath expression:\n{self.xpath_expression}")
                return False
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception adding XPath Expression to List Widget", message)
            return False
        
    def _is_duplicate(self, xpath_expression:str, xpath_filters:list) -> bool:
        """Checks if the XPath expressions is a duplicate. Prevents of adding same XPath expressions to QListWidget

        Args:
            xpath_expression (str): XPath expression from the QLineEdit widget (line_edit_xpath_builder)

        Returns:
            bool: If XPath expression already exists in xpath_filters list, returns True if it exists, else False.
        """
        return xpath_expression in xpath_filters


class SearchAndExportToCSV:
    """
    Handles methods and logic of a button event that starts the search with XPath Expression and export of component.
    """
    def __init__(self, main_window: object, xml_folder_path: str, xpath_filters: list, csv_folder_output_path: str, csv_headers_input: str, set_max_threads: int):
        self.main_window = main_window
        self.ui = main_window.ui
        self.xml_folder_path = xml_folder_path
        self.xpath_filters = xpath_filters
        self.csv_folder_output_path = csv_folder_output_path
        self.csv_headers_input = csv_headers_input
        self.set_max_threads = set_max_threads
        
    # === CSV Exporting Process === #
    def start_csv_export(self) -> None:
        """Initializes and starts the CSV export in a new thread."""
        try:
            exporter = create_csv_exporter(self.xml_folder_path, self.xpath_filters, self.csv_folder_output_path, self._parse_csv_headers(self.csv_headers_input), self.set_max_threads)
            self.main_window._connect_csv_export_signals(exporter)
            self.main_window.thread_pool.start(exporter)

            # Optional: Keep track of the worker
            self.main_window.active_workers.append(exporter)
            
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception on starting to export results to csv file", message)
            
    def _parse_csv_headers(self, raw_headers: str) -> list:
        """Splits comma-separated string into a list of headers."""
        return [h.strip() for h in raw_headers.split(",") if h.strip()]


class GenerateCSVHeader:
    """
    Handles methods and logic of the csv generation based on the entered XPath Expression to the QListWidget.
    """
    def __init__(self, main_window: object):
        self.main_window = main_window
        self.ui = main_window.ui
        
    def generate_header(self, tag_name: str, tag_value: str, attr_name: str, attr_value: str) -> str:
        header = ""

        match (tag_name, tag_value, attr_name, attr_value):
            case (tag, "", "", ""):
                header = tag
            case (tag, value, "", ""):
                header = f"{tag} {value}"
            case (tag, "", attr, ""):
                header = f"{tag} @{attr}"
            case (tag, "", attr, val):
                header = f"{tag} {attr} {val}"
            case (tag, value, attr, ""):
                header = f"{tag} {value} {attr}"
            case (tag, value, attr, val):
                header = f"{tag} {value} {attr} {val}"
            case _:
                header = "Header"
        
        return header
