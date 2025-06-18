# utils/xpath_builder.py
from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from PySide6.QtWidgets import QComboBox, QRadioButton # Assuming these are the types
from lxml import etree as ET
from typing import Optional, Dict, List, Tuple

class XPathBuilderSignals(QObject):
    """Signals class for XPathBuilder operations."""
    error_occurred = Signal(str, str)  # Emitted when an error occurs
    program_output_progress = Signal(str)  # Emitted for progress updates


class XPathValidator(QRunnable):
    """Thread worker for validating XPath expressions."""
    
    def __init__(self, xpath_expression: Optional[str] = None, xml_file_path: Optional[str] = None):
        super().__init__()
        self.xpath_expression = xpath_expression
        self.xml_file_path = xml_file_path
        self.signals = XPathBuilderSignals()
        self.setAutoDelete(True)
    
    @Slot()
    def run(self):
        """Main execution method for XPath validation."""
        self.validate_xpath_expression()

    def validate_xpath_expression(self):
        """Validate XPath expression and optionally test against XML file.
        
        Returns: True if valid, False otherwise.
        """
        try:
            # First, validate syntax
            self.signals.program_output_progress.emit("Validating XPath syntax...")
            ET.XPath(self.xpath_expression)
            
            # If XML file provided, test the expression
            if self.xml_file_path:
                self.signals.program_output_progress.emit("Testing XPath against XML file...")
                tree = ET.parse(self.xml_file_path)
                root = tree.getroot()
                
                # Execute XPath query
                results = root.xpath(self.xpath_expression)
                result_count = len(results) if isinstance(results, list) else 1
                
                self.signals.program_output_progress.emit(f"XPath is valid and returned {result_count} result(s)")
            else:
                self.signals.program_output_progress.emit("XPath syntax is valid")
            
            return True
            
        except ET.XPathSyntaxError as e:
            error_msg = f"XPath syntax error: {str(e)}"
            self.signals.error_occurred.emit("XPathSyntaxError", error_msg)
            self.signals.program_output_progress.emit("XPath syntax is invalid")
            return False
        except ET.XPathEvalError as e:
            error_msg = f"XPath evaluation error: {str(e)}"
            self.signals.error_occurred.emit("XPathEvalError", error_msg)
            return False
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.signals.error_occurred.emit("Validation Error", error_msg)
            return False


class XPathBuilder(QObject):
    """Main XPathBuilder class for constructing XPath expressions."""
    
    # Operation types
    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    GREATER_THAN = "greater"
    SMALLER_THAN = "smaller"
    
    def __init__(self,
                 tag_name_combo: object,
                 tag_value_combo: object,
                 attribute_name_combo: object,
                 attribute_value_combo: object,
                 radio_equals: object,
                 radio_contains: object,
                 radio_starts_with: object,
                 radio_greater: object,
                 radio_smaller: object):
        super().__init__()
        self.signals = XPathBuilderSignals()
        self._current_xpath = ""
        
        # Store references to UI widgets
        self.tag_name_combo = tag_name_combo
        self.tag_value_combo = tag_value_combo
        self.attribute_name_combo = attribute_name_combo
        self.attribute_value_combo = attribute_value_combo

        self.radio_equals = radio_equals
        self.radio_contains = radio_contains
        self.radio_starts_with = radio_starts_with
        self.radio_greater = radio_greater
        self.radio_smaller = radio_smaller

    
    def _get_selected_operation(self) -> str:
        """Determine selected operation based on radio buttons."""
        if self.radio_equals and self.radio_equals.isChecked():
            return self.EQUALS
        elif self.radio_contains and self.radio_contains.isChecked():
            return self.CONTAINS
        elif self.radio_starts_with and self.radio_starts_with.isChecked():
            return self.STARTS_WITH
        elif self.radio_greater and self.radio_greater.isChecked():
            return self.GREATER_THAN
        elif self.radio_smaller and self.radio_smaller.isChecked():
            return self.SMALLER_THAN
        return self.EQUALS  # Default fallback

    
    def build_xpath_expression(self) -> str:
        """Build XPath expression based on currently selected combobox values.
        
        Available combobox values are:
        - tag name
        - tag value
        - attribute name
        - attribute value

        Returns:
            str: Built XPath expression string
        """
        try:
            # Get current values from UI
            tag_name = self._get_combo_text(self.tag_name_combo)
            tag_value = self._get_combo_text(self.tag_value_combo)
            attr_name = self._get_combo_text(self.attribute_name_combo)
            attr_value = self._get_combo_text(self.attribute_value_combo)
            
            # Get selected operation
            operation = self._get_selected_operation()
            
            # Build XPath expression
            xpath = self._construct_xpath(tag_name, tag_value, attr_name, attr_value, operation)
            
            self._current_xpath = xpath
            
            if xpath != "":
                self.signals.program_output_progress.emit(f"Built XPath: {xpath}")
            else:
                self.signals.program_output_progress.emit("No XPath expression built, select at least a tag name.")
            
            return xpath
            
        except Exception as e:
            error_msg = f"Error building XPath: {str(e)}"
            self.signals.error_occurred.emit("XPath Builder Error", error_msg)
            return ""
    
    def _get_combo_text(self, combo) -> str:
        """Safely get text from combobox."""
        if combo and combo.currentText():
            return combo.currentText().strip()
        return ""
    
    def _construct_xpath(self, tag_name: str, tag_value: str, 
                          attr_name: str, attr_value: str, operation: str) -> str:
        """Construct XPath expression based on provided parameters."""
        if not tag_name:
            return ""
        
        # Start with basic element selection
        xpath = f"//{tag_name}"
        
        # Build predicates
        predicates = []
        
        # Add text content predicate if tag_value is provided
        if tag_value:
            text_predicate = self._build_text_predicate(tag_value, operation)
            if text_predicate:
                predicates.append(text_predicate)
        
        # Add attribute predicate if attribute info is provided
        if attr_name:
            if attr_value:
                # Attribute with value
                attr_predicate = self._build_attribute_predicate(attr_name, attr_value, operation)
                if attr_predicate:
                    predicates.append(attr_predicate)
            else:
                # Just check for attribute existence
                predicates.append(f"@{attr_name}")
        
        # Combine predicates
        if predicates:
            xpath += f"[{' and '.join(predicates)}]"
        
        # Determine what to select
        if attr_name and not attr_value and not tag_value:
            # Select attribute value
            xpath += f"/@{attr_name}"
        elif not attr_name and not tag_value:
            # Select text content
            xpath += "/text()"
        # Otherwise, select the element itself
        
        return xpath
    
    def _build_text_predicate(self, value: str, operation: str) -> str:
        """Build predicate for text content."""
        if operation == self.EQUALS:
            return f"text()='{value}'"
        elif operation == self.CONTAINS:
            return f"contains(text(), '{value}')"
        elif operation == self.STARTS_WITH:
            return f"starts-with(text(), '{value}')"
        elif operation == self.GREATER_THAN:
            return f"text() > {value}"
        elif operation == self.SMALLER_THAN:
            return f"text() < {value}"
        return f"text()='{value}'"  # Default to equals
    
    def _build_attribute_predicate(self, attr_name: str, attr_value: str, operation: str) -> str:
        """Build predicate for attribute value."""
        if operation == self.EQUALS:
            return f"@{attr_name}='{attr_value}'"
        elif operation == self.CONTAINS:
            return f"contains(@{attr_name}, '{attr_value}')"
        elif operation == self.STARTS_WITH:
            return f"starts-with(@{attr_name}, '{attr_value}')"
        elif operation == self.GREATER_THAN:
            return f"@{attr_name} > {attr_value}" # Corrected from "<" to ">"
        elif operation == self.SMALLER_THAN:
            return f"@{attr_name} < {attr_value}"
        return f"@{attr_name}='{attr_value}'"  # Default to equals
    
    def _get_input_xpath(self) -> str:
        """
        Builds and returns an XPath expression based on the current values
        of the UI comboboxes and selected radio button, without emitting signals
        or updating the internal _current_xpath state.
        This method is intended to be used for validation or preview purposes
        where the XPath needs to be generated on-the-fly from input controls.
        """
        try:
            tag_name = self._get_combo_text(self.tag_name_combo)
            tag_value = self._get_combo_text(self.tag_value_combo)
            attr_name = self._get_combo_text(self.attribute_name_combo)
            attr_value = self._get_combo_text(self.attribute_value_combo)
            operation = self._get_selected_operation()
            
            xpath = self._construct_xpath(tag_name, tag_value, attr_name, attr_value, operation)
            return xpath
        except Exception:
            # If any error occurs during input retrieval or construction, return empty string
            return ""

    def validate_xpath_async(self, xpath_expression: str = None, xml_file_path: str = None) -> XPathValidator:
        """Create validator worker for async XPath validation."""
        expression = xpath_expression or self._current_xpath or self._get_input_xpath()
        validator = XPathValidator(expression, xml_file_path)
        return validator
    
    def validate_xpath_sync(self, xpath_expression: str = None) -> Tuple[bool, str]:
        """Synchronously validate XPath expression."""
        expression = xpath_expression or self._current_xpath or self._get_input_xpath()
        
        if not expression:
            return False, "No XPath expression to validate"
        
        try:
            ET.XPath(expression)
            return True, "XPath syntax is valid"
        except ET.XPathSyntaxError as e:
            return False, f"XPath syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"


# Convenience functions
def create_xpath_builder(tag_name_combo: QComboBox,
                         tag_value_combo: QComboBox,
                         attribute_name_combo: QComboBox,
                         attribute_value_combo: QComboBox,
                         radio_equals: QRadioButton,
                         radio_contains: QRadioButton,
                         radio_starts_with: QRadioButton,
                         radio_greater: QRadioButton,
                         radio_smaller: QRadioButton) -> XPathBuilder:
    """Create a new XPathBuilder instance."""
    return XPathBuilder(tag_name_combo, tag_value_combo, attribute_name_combo,
                        attribute_value_combo, radio_equals, radio_contains,
                        radio_starts_with, radio_greater, radio_smaller)


def create_xpath_validator(xpath_expression: Optional[str] = None, xml_file_path: Optional[str] = None) -> XPathValidator:
    """Create a new XPathValidator worker."""
    return XPathValidator(xpath_expression, xml_file_path)
