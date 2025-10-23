# File: modules/signal_handlers.py
import datetime
import os
import pandas as pd
from utils.ui_helpers import HelperMethods
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

class ButtonActionsMixin:
    """Handles button click events only"""

    def connect_button_actions(self: "MainWindow"):
        self.ui.button_pass_csv_to_converter.linkActivated.connect(
            self.on_passCSVFilePathToConverter)
        self.ui.button_browse_xml_folder.clicked.connect(
            self.on_browseXMLFolder)
        self.ui.button_read_xml.clicked.connect(self.on_readXMLFile)
        self.ui.button_browse_csv.clicked.connect(self.on_browseCSVOutput)
        self.ui.button_build_xpath.clicked.connect(
            self.on_buildXPathExpression)
        self.ui.button_add_xpath_to_list.clicked.connect(
            self.on_addXPathToList)
        self.ui.button_start_csv_export.clicked.connect(self.on_startCSVSearch)
        self.ui.button_abort_csv_export.clicked.connect(self.on_stopCSVSearch)
        self.ui.button_browse_csv_conversion_path_input.clicked.connect(
            self.on_browseCSVConversionInput)
        self.ui.button_csv_conversion_convert.clicked.connect(
            self.on_convertCSVFile)
        self.ui.button_profile_cleanup_browse_csv_file_path.clicked.connect(
            self.on_browseProfileCleanupCSV)
        self.ui.button_profile_cleanup_browse_folder_path.clicked.connect(
            self.on_browseProfileCleanupFolder)
        self.ui.button_profile_cleanup_cleanup_start.clicked.connect(
            self.on_startProfileCleanup)
        self.ui.button_drop_csv_header.clicked.connect(
            self.on_dropCurrentCSVHeader)
        self.ui.button_find_next.clicked.connect(self.on_XMLOutputSearchNext)
        self.ui.button_find_previous.clicked.connect(
            self.on_XMLOutputSearchPrevious)
        self.ui.button_csv_conversion_open_file.clicked.connect(
            self.on_OpenConvertedFile)
        self.ui.button_convert_hexadecimal_to_decimal.clicked.connect(
            self.on_ConvertHexToDecimal)
        self.ui.button_load_csv.clicked.connect(self.on_loadCSVFileForTable)
        self.ui.button_clear_table.clicked.connect(self.on_clearTable)

    @Slot()
    def on_passCSVFilePathToConverter(self: "MainWindow"):
        """Pass CSV output path to converter input."""
        try:
            if self.ui.line_edit_csv_output_path.text():
                if len(self.ui.line_edit_csv_conversion_path_input.text()) > 0:
                    self.ui.line_edit_csv_conversion_path_input.clear()

                self.ui.line_edit_csv_conversion_path_input.setText(
                    self.ui.line_edit_csv_output_path.text()
                )

                # Move to second tab
                if self.ui.tabWidget.currentIndex() == 0:
                    self.ui.tabWidget.setCurrentIndex(1)
            else:
                QMessageBox.information(
                    self,
                    "CSV output not set",
                    "No CSV output for exporting has been set.\nCannot copy path to CSV converter input field."
                )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception on starting csv convert to other filetype", message)

    @Slot()
    def on_browseXMLFolder(self: "MainWindow"):
        """Browse for XML folder."""
        HelperMethods.browse_folder_helper(
            dialog_message="Select directory that contains XML files",
            line_widget=self.ui.line_edit_xml_folder_path_input
        )

    @Slot()
    def on_readXMLFile(self: "MainWindow"):
        """Read XML file dialog and parsing."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Select XML File", "", "XML File (*.xml)"
            )
            if file_name:
                self.ui.text_edit_program_output.clear()
                self._parse_xml_file(file_name)
                # Add the read XML files path to the XML path input field if it's not already set
                if not self.ui.line_edit_xml_folder_path_input.text():
                    self.ui.line_edit_xml_folder_path_input.setText(
                        os.path.dirname(file_name)
                    )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception reading xml file", message)

    @Slot()
    def on_browseCSVOutput(self: "MainWindow"):
        """Browse for CSV output file."""
        HelperMethods.browse_save_file_as_helper(
            dialog_message="Save as",
            line_widget=self.ui.line_edit_csv_output_path,
            file_extension_filter="CSV File (*.csv)",
            filename_placeholder=f"Evaluation_{datetime.datetime.now().strftime('%Y.%m.%d_%H%M')}.csv"
        )

    @Slot()
    def on_buildXPathExpression(self: "MainWindow"):
        """Build XPath expression based on selected combobox values."""
        try:
            from controllers.state_controller import XPathBuildHandler

            builder = XPathBuildHandler(
                main_window=self,
                line_edit_xpath_builder=self.ui.line_edit_xpath_builder,
                tag_name_combo=self.ui.combobox_tag_names,
                tag_value_combo=self.ui.combobox_tag_values,
                attribute_name_combo=self.ui.combobox_attribute_names,
                attribute_value_combo=self.ui.combobox_attribute_values,
                radio_equals=self.ui.radio_button_equals,
                radio_contains=self.ui.radio_button_contains,
                radio_starts_with=self.ui.radio_button_starts_with,
                radio_greater=self.ui.radio_button_greater,
                radio_smaller=self.ui.radio_button_smaller,
            )
            builder.start_xpath_build()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception on building xpath expression", message)

    @Slot()
    def on_addXPathToList(self: "MainWindow"):
        """Add XPath expression to list."""
        try:
            from controllers.state_controller import AddXPathExpressionToListHandler, GenerateCSVHeaderHandler

            xpath_input = self.ui.line_edit_xpath_builder.text()
            xpath_filters = self._listwidget_to_list(
                self.ui.list_widget_main_xpath_expressions)
            csv_headers_input = self.ui.line_edit_csv_headers_input
            list_widget_xpath_expressions = self.ui.list_widget_main_xpath_expressions

            adder = AddXPathExpressionToListHandler(
                main_window=self,
                xpath_expression=xpath_input,
                xpath_filters=xpath_filters,
                list_widget_xpath_expressions=list_widget_xpath_expressions,
            )

            is_added = adder.add_expression_to_list()

            if is_added:
                current_text = csv_headers_input.text()
                self._add_recent_xpath_expression(xpath_input)

                generator = GenerateCSVHeaderHandler(
                    self,
                    tag_name_combo=self.ui.combobox_tag_names,
                    tag_value_combo=self.ui.combobox_tag_values,
                    attribute_name_combo=self.ui.combobox_attribute_names,
                    attribute_value_combo=self.ui.combobox_attribute_values,
                    xpath_input=self.ui.line_edit_xpath_builder,
                    csv_headers_input=self.ui.line_edit_csv_headers_input,
                )

                header = generator.generate_header()

                if current_text:
                    updated_text = f"{current_text}, {header}"
                else:
                    updated_text = header
                csv_headers_input.setText(updated_text)

                self.ui.line_edit_xpath_builder.clear()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception adding XPath Expression to list widget", message)

    @Slot()
    def on_startCSVSearch(self: "MainWindow"):
        """Start CSV search and export process."""
        try:
            from controllers.state_controller import SearchAndExportToCSVHandler

            xml_path = self.ui.line_edit_xml_folder_path_input.text()
            csv_output = self.ui.line_edit_csv_output_path.text()
            headers = self.ui.line_edit_csv_headers_input.text()
            group_matches_flag = self.ui.checkbox_group_matches.isChecked()
            max_threads = self.set_max_threads
            xpath_filters = self._listwidget_to_list(
                self.ui.list_widget_main_xpath_expressions)

            self.csv_exporter_handler = SearchAndExportToCSVHandler(
                main_window=self,
                xml_folder_path=xml_path,
                xpath_filters=xpath_filters,
                csv_folder_output_path=csv_output,
                csv_headers_input=headers,
                group_matches_flag=group_matches_flag,
                set_max_threads=max_threads,
            )
            self.csv_exporter_handler.start_csv_export()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception on starting to search and export to csv", message)

    @Slot()
    def on_stopCSVSearch(self: "MainWindow"):
        """Stop CSV search and export process."""
        try:
            if self.csv_exporter_handler:
                self.csv_exporter_handler.stop_csv_export()
                self.csv_exporter_handler = None
            else:
                QMessageBox.information(
                    self,
                    "No Active Export",
                    "There is no CSV export currently running to abort."
                )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception on stopping CSV export", message)

    @Slot()
    def on_browseCSVConversionInput(self: "MainWindow"):
        """Browse for CSV conversion input file."""
        self.helper._browse_file_helper(
            dialog_message="Select csv file for conversion",
            line_widget=self.ui.line_edit_csv_conversion_path_input,
            file_extension_filter="CSV File (*.csv)",
        )

    @Slot()
    def on_convertCSVFile(self: "MainWindow"):
        """Start CSV conversion process."""
        try:
            from controllers.state_controller import CSVConversionHandler

            csv_file_to_convert = self.ui.line_edit_csv_conversion_path_input.text()
            extension_type = self.ui.combobox_csv_conversion_output_type.currentText()
            write_index = self.ui.checkbox_write_index_column.isChecked()
            label_loading_gif = self.ui.label_loading_gif

            self.csv_conversion_controller = CSVConversionHandler(
                main_window=self,
                csv_file_to_convert=csv_file_to_convert,
                extension_type=extension_type,
                write_index=write_index,
                label_loading_gif=label_loading_gif
            )
            self.csv_conversion_controller.start_csv_conversion()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception on starting csv convert to other filetype", message)

    @Slot()
    def on_loadCSVFileForTable(self: "MainWindow"):
        """Browse for profile cleanup CSV file."""
        try:
            csv_path = self.helper._browse_file_helper_non_input(
                dialog_message="Select csv file",
                file_extension_filter="CSV File (*.csv)",
            )
            if csv_path:
                # Convert to a pandas dataframe
                results_df = pd.read_csv(csv_path)
                # Fill table widget
                self._populate_results_table(results_df)
                self._set_ui_widgets_table_disabled(False)
                self.ui.text_edit_csv_output.setText(
                    "CSV Data loaded successfully into the table!")

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception on loading csv file for table", message)

    @Slot()
    def on_clearTable(self: "MainWindow"):
        """Clears all data from the QTableView"""
        self.ui.table_csv_data.setModel(None)
        self.ui.text_edit_csv_output.setText("Cleared results table!")
        # Disable widgets again
        self._set_ui_widgets_table_disabled(True)

    @Slot()
    def on_startProfileCleanup(self: "MainWindow"):
        """Start profile cleanup process."""
        try:
            from controllers.state_controller import LobsterProfileExportCleanupHandler

            csv_file = self.ui.line_edit_profile_cleanup_csv_file_path.text()
            profiles_folder_path = self.ui.line_edit_profile_cleanup_folder_path.text()

            self.lobster_profile_cleaner = LobsterProfileExportCleanupHandler(
                main_window=self,
                csv_file_path=csv_file,
                profiles_folder_path=profiles_folder_path,
            )
            self.lobster_profile_cleaner.start_lobster_profile_cleanup()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self, "Exception on starting lobster profile xml files cleanup", message)

    @Slot()
    def on_dropCurrentCSVHeader(self: "MainWindow"):
        """Drop selected CSV header."""
        from controllers.state_controller import CSVColumnDropHandler

        csv_file_path = self.ui.line_edit_profile_cleanup_csv_file_path.text()
        column_to_drop = self.ui.combobox_csv_headers.currentText()
        column_to_drop_index = self.ui.combobox_csv_headers.currentIndex()

        drop_column = CSVColumnDropHandler(
            main_window=self,
            csv_file_path=csv_file_path,
            column_to_drop=column_to_drop,
            column_to_drop_index=column_to_drop_index,
        )
        drop_column.start_csv_column_drop()

    @Slot()
    def on_XMLOutputSearchNext(self: "MainWindow"):
        """Search next in XML output."""
        self.xml_text_searcher.search_next()

    @Slot()
    def on_XMLOutputSearchPrevious(self: "MainWindow"):
        """Search previous in XML output."""
        self.xml_text_searcher.search_previous()

    @Slot()
    def on_OpenConvertedFile(self: "MainWindow"):
        """Open the converted file in the default application."""
        file_path = self.ui.line_edit_csv_conversion_open_file_path.text()
        self.helper._open_file_directly(file_path)

    @Slot()
    def on_ConvertHexToDecimal(self: "MainWindow") -> None:
        """
        Converts the instance's hexadecimal string to its decimal equivalent.
        Returns:
            None
        """
        try:
            # Clean up hex string (removing the delimiter ':' from the string)
            hex_string = self.ui.line_edit_hexadecimal.text()
            if ":" in hex_string:
                hex_string = hex_string.replace(":", "")
            decimal_value = int(hex_string, 16)
            # Set decimal value to the second input field
            self.ui.line_edit_decimal.setText(str(decimal_value))
        except ValueError as ve:
            QMessageBox.critical(
                self,
                "Invalid Hexadecimal Input",
                f"The provided input is not a valid hexadecimal string.\nError details: {ve}"
            )

    @Slot()
    def on_browseProfileCleanupCSV(self: "MainWindow"):
        """Browse for profile cleanup CSV file."""
        self.helper._browse_file_helper(
            dialog_message="Select csv file",
            line_widget=self.ui.line_edit_profile_cleanup_csv_file_path,
            file_extension_filter="CSV File (*.csv)",
        )

    @Slot()
    def on_browseProfileCleanupFolder(self: "MainWindow"):
        """Browse for profile cleanup folder."""
        self.helper._browse_folder_helper(
            dialog_message="Select directory that contains XML files",
            line_widget=self.ui.line_edit_profile_cleanup_folder_path,
        )
