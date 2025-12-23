# File: controllers/xpath_handlers.py
from PySide6.QtWidgets import QMessageBox, QListWidget, QLineEdit, QComboBox, QRadioButton
from modules.xpath_builder import create_xpath_validator, create_xpath_builder
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow  # import only for type hints, not at runtime


class AddXPathExpressionToListHandler:
    """
    Handles methods and logic of the Button event for adding XPath Expression.
    """

    def __init__(self, main_window: "MainWindow", xpath_expression: str, xpath_filters: list | None, list_widget_xpath_expressions: QListWidget):
        self.main_window = main_window
        self.xpath_expression = xpath_expression
        self.xpath_filters = xpath_filters
        self.list_widget_xpath_expressions = list_widget_xpath_expressions

    def smart_split(self, s: str) -> list[str]:
        result = []
        current = []
        inside_single_quote = False
        inside_double_quote = False

        for char in s:
            if char == "'" and not inside_double_quote:
                inside_single_quote = not inside_single_quote
            elif char == '"' and not inside_single_quote:
                inside_double_quote = not inside_double_quote

            if char == ',' and not inside_single_quote and not inside_double_quote:
                result.append(''.join(current).strip())
                current = []
            else:
                current.append(char)

        # Add the last part
        if current:
            result.append(''.join(current).strip())

        return result

        # === QListWidget HANDLER ===
    def add_expression_to_list(self) -> bool | None:
        """Add the entered or built XPath expression from the QLineEdit to the QListWidget for later searching

        Has a built-in XPath validator before adding the XPath to the QListWidget

        Returns:
            bool: If xpath expression has been successfully added to the list True, else False
        """
        try:
            # Check if the XPath input is not empty:
            if not self.xpath_expression:
                QMessageBox.information(
                    self.main_window, "Empty XPath", "Please enter a XPath expression.")
                return False

            validator = create_xpath_validator()

            if "," in self.xpath_expression:
                try:
                    # Split by comma and validate each XPath expression
                    xpath_expressions = self.smart_split(self.xpath_expression)
                    for exp in xpath_expressions:
                        if exp and not self._is_duplicate(exp, self.xpath_filters):
                            validator.xpath_expression = exp
                            if not validator.validate_xpath_expression():
                                raise ValueError(f"Invalid XPath expression: {exp}")
                            else:
                                self.xpath_filters.append(exp)
                                self.list_widget_xpath_expressions.addItem(exp)
                        else:
                            QMessageBox.warning(self.main_window, "Duplicate XPath Expression", f"Cannot add duplicate XPath expression:\n{exp}")
                            return False
                except ValueError as e:
                    QMessageBox.warning(self.main_window, "XPathSyntaxError", f"Invalid XPath expression: {str(e)}")
            else:
                if self.xpath_expression and not self._is_duplicate(self.xpath_expression, self.xpath_filters):
                    self.main_window.connect_xpath_builder_signals(validator)
                    # Validate the XPath expression
                    validator.xpath_expression = self.xpath_expression
                    is_valid = validator.validate_xpath_expression()
                    if is_valid:
                        self.xpath_filters.append(self.xpath_expression)
                        self.list_widget_xpath_expressions.addItem(
                            self.xpath_expression)
                        return True
                else:
                    QMessageBox.information(self.main_window, "Duplicate XPath Expression",
                                        f"Cannot add duplicate XPath expression:\n{self.xpath_expression}")
                    return False
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception adding XPath Expression to List Widget", message)
            return False

    @staticmethod
    def _is_duplicate(xpath_expression: str, xpath_filters: list) -> bool:
        """Checks if the XPath expressions is a duplicate. Prevents from adding same XPath expressions to QListWidget

        Args:
            xpath_expression (str): XPath expression from the QLineEdit widget (line_edit_xpath_builder)
            xpath_filters (list): A list that contains 

        Returns:
            bool: Returns True if XPath expression already exists in the xpath_filters list, returns True if it exists, else False.
        """
        return xpath_expression in xpath_filters


class XPathBuildHandler:
    """Handles methods and logic of the XPath Build event based on the combobox values"""

    def __init__(self, main_window: "MainWindow",
                 line_edit_xpath_builder: QLineEdit,
                 tag_name_combo: QComboBox,
                 tag_value_combo: QComboBox,
                 attribute_name_combo: QComboBox,
                 attribute_value_combo: QComboBox,
                 radio_equals: QRadioButton,
                 radio_contains: QRadioButton,
                 radio_starts_with: QRadioButton,
                 radio_greater: QRadioButton,
                 radio_smaller: QRadioButton
                 ):

        self.main_window = main_window
        self.line_edit_xpath_builder = line_edit_xpath_builder
        self.tag_name_combo = tag_name_combo
        self.tag_value_combo = tag_value_combo
        self.attribute_name_combo = attribute_name_combo
        self.attribute_value_combo = attribute_value_combo
        self.radio_equals = radio_equals
        self.radio_contains = radio_contains
        self.radio_starts_with = radio_starts_with
        self.radio_greater = radio_greater
        self.radio_smaller = radio_smaller

    def start_xpath_build(self) -> None:
        """Triggers the XPath building process and updates the UI."""
        try:
            # Now build the expression using the already connected builder
            builder = create_xpath_builder(
                self.tag_name_combo,
                self.tag_value_combo,
                self.attribute_name_combo,
                self.attribute_value_combo,
                self.radio_equals,
                self.radio_contains,
                self.radio_starts_with,
                self.radio_greater,
                self.radio_smaller
            )

            self.main_window.connect_xpath_builder_signals(builder)

            xpath_expression = builder.build_xpath_expression()

            # Add built XPath Expression to the QLineEdit Widget for the XPath
            self.line_edit_xpath_builder.setText(xpath_expression)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception on building xpath expression", message)


class GenerateCSVHeaderHandler:
    """Handles methods and logic of the csv generation based on the entered XPath Expression to the QListWidget."""

    def __init__(self, main_window: "MainWindow",
                 tag_name_combo: QComboBox,
                 tag_value_combo: QComboBox,
                 attribute_name_combo: QComboBox,
                 attribute_value_combo: QComboBox,
                 xpath_input: QLineEdit,
                 csv_headers_input: QLineEdit
                 ):

        self.main_window = main_window
        self.tag_name_combo = tag_name_combo
        self.tag_value_combo = tag_value_combo
        self.attribute_name_combo = attribute_name_combo
        self.attribute_value_combo = attribute_value_combo
        self.xpath_input = xpath_input
        self.csv_headers_input = csv_headers_input

    def generate_header(self) -> str:
        header = ""

        tag_name = self.tag_name_combo.currentText()
        tag_value = self.tag_value_combo.currentText()
        attr_name = self.attribute_name_combo.currentText()
        attr_value = self.attribute_value_combo.currentText()
        headers_list: list[str] = self.csv_headers_input.text().split(",")

        if tag_name != "" and tag_value != "" and attr_name != "" and attr_value != "":
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

        else:
            try:
                # If no tag, value, attribute or attribute value is selected, use the XPath input as header
                xpath_expression: str = self.xpath_input.text().strip()
                split_xpath: list[str] = xpath_expression.split("/")

                part1 = split_xpath[-2]
                part2 = split_xpath[-1]

                header = f"{part1} {part2}"
            except IndexError:
                header = "Header"

        if not self._is_duplicate(header, headers_list):
            return header

    def _is_duplicate(self, header: str, headers_list: list) -> bool:
        """Checks if the header is a duplicate. Prevents from adding the same header to the QLineEdit input for headers.

        Args:
            header (str): Headers input
            header_list (list): A list that contains already added headers

        Returns:
            bool: Returns True if the header already exists in the headers list else False
        """

        return header in headers_list
