# File: controllers/xml_output_search_handler.py
from PySide6.QtWidgets import QMessageBox, QLineEdit, QTextEdit
from PySide6.QtGui import QTextDocument
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow  # import only for type hints, not at runtime


class SearchXMLOutputTextHandler:
    """Handles methods and logic of the search functionality of the XML Output Text in the QTextEdit"""

    def __init__(self,
                 main_window: "MainWindow",
                 line_edit_xml_output_find_text: QLineEdit,
                 text_edit_xml_output: QTextEdit
                 ):

        self.main_window = main_window
        self.line_edit_xml_output_find_text = line_edit_xml_output_find_text
        self.text_edit_xml_output = text_edit_xml_output

    def search_next(self):
        text = self.line_edit_xml_output_find_text.text()
        try:
            if text:
                self.text_edit_xml_output.find(text)
            else:
                QMessageBox.information(
                    self.main_window, "Find text input is empty", "No text has been entered for search criteria.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception on XML search next function", message)

    def search_previous(self):
        text = self.line_edit_xml_output_find_text.text()
        try:
            if text:
                self.text_edit_xml_output.find(
                    text, QTextDocument.FindFlag.FindBackward)
            else:
                QMessageBox.information(
                    self.main_window, "Find text input is empty", "No text has been entered for search criteria.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception on XML search previous function", message)
