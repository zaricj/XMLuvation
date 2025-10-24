# File: controllers/button_event_handler.py
"""Handler for button click events."""
import datetime
import os
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


class ButtonEventHandler:
    """Handles all button click events."""
    
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window
        
    def connect_signals(self):
        """Connect all button events to their handlers."""
        ui = self.main_window.ui
        
        # Browse buttons
        ui.button_browse_xml_folder.clicked.connect(self.on_browse_xml_folder)
        ui.button_browse_csv.clicked.connect(self.on_browse_csv_output)
        ui.button_browse_csv_conversion_path_input.clicked.connect(self.on_browse_csv_conversion_input)
        ui.button_profile_cleanup_browse_csv_file_path.clicked.connect(self.on_browse_profile_cleanup_csv)
        ui.button_profile_cleanup_browse_folder_path.clicked.connect(self.on_browse_profile_cleanup_folder)
        
        # XML operations
        ui.button_read_xml.clicked.connect(self.on_read_xml_file)
        
        # XPath operations
        ui.button_build_xpath.clicked.connect(self.on_build_xpath_expression)
        ui.button_add_xpath_to_list.clicked.connect(self.on_add_xpath_to_list)
        
        # CSV export operations
        ui.button_start_csv_export.clicked.connect(self.on_start_csv_search)
        ui.button_abort_csv_export.clicked.connect(self.on_stop_csv_search)
        
        # CSV conversion operations
        ui.button_csv_conversion_convert.clicked.connect(self.on_convert_csv_file)
        ui.button_csv_conversion_open_file.clicked.connect(self.on_open_converted_file)
        
        # Profile cleanup operations
        ui.button_profile_cleanup_cleanup_start.clicked.connect(self.on_start_profile_cleanup)
        ui.button_drop_csv_header.clicked.connect(self.on_drop_current_csv_header)
        
        # Search operations
        ui.button_find_next.clicked.connect(self.on_xml_output_search_next)
        ui.button_find_previous.clicked.connect(self.on_xml_output_search_previous)
        
        # Utility operations
        ui.button_convert_hexadecimal_to_decimal.clicked.connect(self.on_convert_hex_to_decimal)
        ui.button_load_csv.clicked.connect(self.on_load_csv_file_for_table)
        ui.button_clear_table.clicked.connect(self.on_clear_table)
        
        # Link button
        ui.button_pass_csv_to_converter.linkActivated.connect(self.on_pass_csv_file_path_to_converter)
    
    # === Button Event Handlers ===
    
    @Slot()
    def on_browse_xml_folder(self):
        """Browse for XML folder."""
        self.main_window.helper._browse_folder_helper(
            dialog_message="Select directory that contains XML files",
            line_widget=self.main_window.ui.line_edit_xml_folder_path_input,
        )
    
    @Slot()
    def on_read_xml_file(self):
        """Read XML file dialog and parsing."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self.main_window, "Select XML File", "", "XML File (*.xml)"
            )
            if file_name:
                self.main_window.ui.text_edit_program_output.clear()
                self.main_window._parse_xml_file(file_name)
                # Add the read XML files path to the XML path input field if it's not already set
                if not self.main_window.ui.line_edit_xml_folder_path_input.text():
                    self.main_window.ui.line_edit_xml_folder_path_input.setText(
                        os.path.dirname(file_name)
                    )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception reading xml file", message)
    
    @Slot()
    def on_browse_csv_output(self):
        """Browse for CSV output file."""
        self.main_window.helper._browse_save_file_as_helper(
            dialog_message="Save as",
            line_widget=self.main_window.ui.line_edit_csv_output_path,
            file_extension_filter="CSV File (*.csv)",
            filename_placeholder=f"Evaluation_{datetime.datetime.now().strftime('%Y.%m.%d_%H%M')}.csv"
        )
    
    @Slot()
    def on_build_xpath_expression(self):
        """Build XPath expression based on selected combobox values."""
        try:
            from controllers.state_controller import XPathBuildHandler
            
            builder = XPathBuildHandler(
                main_window=self.main_window,
                line_edit_xpath_builder=self.main_window.ui.line_edit_xpath_builder,
                tag_name_combo=self.main_window.ui.combobox_tag_names,
                tag_value_combo=self.main_window.ui.combobox_tag_values,
                attribute_name_combo=self.main_window.ui.combobox_attribute_names,
                attribute_value_combo=self.main_window.ui.combobox_attribute_values,
                radio_equals=self.main_window.ui.radio_button_equals,
                radio_contains=self.main_window.ui.radio_button_contains,
                radio_starts_with=self.main_window.ui.radio_button_starts_with,
                radio_greater=self.main_window.ui.radio_button_greater,
                radio_smaller=self.main_window.ui.radio_button_smaller,
            )
            builder.start_xpath_build()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception on building xpath expression", message)
    
    @Slot()
    def on_add_xpath_to_list(self):
        """Add XPath expression to list."""
        try:
            from controllers.state_controller import AddXPathExpressionToListHandler, GenerateCSVHeaderHandler
            
            xpath_input = self.main_window.ui.line_edit_xpath_builder.text()
            xpath_filters = self.main_window._listwidget_to_list(self.main_window.ui.list_widget_main_xpath_expressions)
            csv_headers_input = self.main_window.ui.line_edit_csv_headers_input
            list_widget_xpath_expressions = self.main_window.ui.list_widget_main_xpath_expressions

            adder = AddXPathExpressionToListHandler(
                main_window=self.main_window,
                xpath_expression=xpath_input,
                xpath_filters=xpath_filters,
                list_widget_xpath_expressions=list_widget_xpath_expressions,
            )

            is_added = adder.add_expression_to_list()

            if is_added:
                current_text = csv_headers_input.text()
                self.main_window._add_recent_xpath_expression(xpath_input)

                generator = GenerateCSVHeaderHandler(
                    self.main_window,
                    tag_name_combo=self.main_window.ui.combobox_tag_names,
                    tag_value_combo=self.main_window.ui.combobox_tag_values,
                    attribute_name_combo=self.main_window.ui.combobox_attribute_names,
                    attribute_value_combo=self.main_window.ui.combobox_attribute_values,
                    xpath_input=self.main_window.ui.line_edit_xpath_builder,
                    csv_headers_input=self.main_window.ui.line_edit_csv_headers_input,
                )

                header = generator.generate_header()

                if current_text:
                    updated_text = f"{current_text}, {header}"
                else:
                    updated_text = header
                csv_headers_input.setText(updated_text)

                self.main_window.ui.line_edit_xpath_builder.clear()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception adding XPath Expression to list widget", message)
    
    @Slot()
    def on_start_csv_search(self):
        """Start CSV search and export process."""
        try:
            from controllers.state_controller import SearchAndExportToCSVHandler
            
            xml_folder_path = self.main_window.ui.line_edit_xml_folder_path_input.text()
            csv_folder_output_path = self.main_window.ui.line_edit_csv_output_path.text()
            csv_headers_input = self.main_window.ui.line_edit_csv_headers_input.text()
            group_matches_flag = self.main_window.ui.checkbox_group_matches.isChecked()
            xpath_filters = self.main_window._listwidget_to_list(self.main_window.ui.list_widget_main_xpath_expressions)

            if not xml_folder_path or not os.path.isdir(xml_folder_path):
                QMessageBox.warning(
                    self.main_window, "Invalid XML Folder", "Please select a valid XML folder path."
                )
                return

            if not csv_folder_output_path:
                QMessageBox.warning(
                    self.main_window, "Invalid CSV Output", "Please select a CSV output path."
                )
                return

            if not xpath_filters:
                QMessageBox.warning(
                    self.main_window, "No XPath Expressions", "Please add at least one XPath expression."
                )
                return

            self.main_window._csv_exporter_handler_ref = SearchAndExportToCSVHandler(
                main_window=self.main_window,
                xml_folder_path=xml_folder_path,
                xpath_filters=xpath_filters,
                csv_folder_output_path=csv_folder_output_path,
                csv_headers_input=csv_headers_input,
                group_matches_flag=group_matches_flag,
                set_max_threads=self.main_window.set_max_threads,
            )
            self.main_window._csv_exporter_handler_ref.start_csv_export()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception on starting CSV search", message)
    
    @Slot()
    def on_stop_csv_search(self):
        """Stop CSV search and export process."""
        if self.main_window._csv_exporter_handler_ref:
            self.main_window._csv_exporter_handler_ref.stop_csv_export()
    
    @Slot()
    def on_browse_csv_conversion_input(self):
        """Browse for CSV conversion input file."""
        self.main_window.helper._browse_file_helper(
            dialog_message="Select csv file",
            line_widget=self.main_window.ui.line_edit_csv_conversion_path_input,
            file_extension_filter="CSV File (*.csv)",
        )
    
    @Slot()
    def on_convert_csv_file(self):
        """Convert CSV file."""
        try:
            from controllers.state_controller import CSVConversionHandler
            
            csv_path = self.main_window.ui.line_edit_csv_conversion_path_input.text()
            write_index = self.main_window.ui.checkbox_write_index_column.isChecked()

            if not csv_path or not os.path.exists(csv_path):
                QMessageBox.warning(
                    self.main_window, "Invalid CSV File", "Please select a valid CSV file."
                )
                return

            handler = CSVConversionHandler(
                main_window=self.main_window,
                csv_file_path=csv_path,
                write_index_flag=write_index,
            )
            handler.start_csv_conversion()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception on CSV conversion", message)
    
    @Slot()
    def on_open_converted_file(self):
        """Open converted file."""
        file_path = self.main_window.ui.line_edit_csv_conversion_open_file_path.text()
        self.main_window.helper._open_file_directly(file_path)
    
    @Slot()
    def on_browse_profile_cleanup_csv(self):
        """Browse for profile cleanup CSV file."""
        self.main_window.helper._browse_file_helper(
            dialog_message="Select csv file",
            line_widget=self.main_window.ui.line_edit_profile_cleanup_csv_file_path,
            file_extension_filter="CSV File (*.csv)",
        )
    
    @Slot()
    def on_browse_profile_cleanup_folder(self):
        """Browse for profile cleanup folder."""
        self.main_window.helper._browse_folder_helper(
            dialog_message="Select directory that contains XML files",
            line_widget=self.main_window.ui.line_edit_profile_cleanup_folder_path,
        )
    
    @Slot()
    def on_start_profile_cleanup(self):
        """Start profile cleanup process."""
        try:
            from controllers.state_controller import LobsterProfileExportCleanupHandler
            
            csv_file = self.main_window.ui.line_edit_profile_cleanup_csv_file_path.text()
            profiles_folder_path = self.main_window.ui.line_edit_profile_cleanup_folder_path.text()

            self.lobster_profile_cleaner = LobsterProfileExportCleanupHandler(
                main_window=self.main_window,
                csv_file_path=csv_file,
                profiles_folder_path=profiles_folder_path,
            )
            self.lobster_profile_cleaner.start_lobster_profile_cleanup()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception on starting lobster profile xml files cleanup", message)
    
    @Slot()
    def on_drop_current_csv_header(self):
        """Drop selected CSV header."""
        from controllers.state_controller import CSVColumnDropHandler
        
        csv_file_path = self.main_window.ui.line_edit_profile_cleanup_csv_file_path.text()
        column_to_drop = self.main_window.ui.combobox_csv_headers.currentText()
        column_to_drop_index = self.main_window.ui.combobox_csv_headers.currentIndex()

        drop_column = CSVColumnDropHandler(
            main_window=self.main_window,
            csv_file_path=csv_file_path,
            column_to_drop=column_to_drop,
            column_to_drop_index=column_to_drop_index,
        )
        drop_column.start_csv_column_drop()
    
    @Slot()
    def on_xml_output_search_next(self):
        """Search next in XML output."""
        self.main_window.xml_text_searcher.search_next()
    
    @Slot()
    def on_xml_output_search_previous(self):
        """Search previous in XML output."""
        self.main_window.xml_text_searcher.search_previous()
    
    @Slot()
    def on_pass_csv_file_path_to_converter(self):
        """Pass CSV output path to converter input."""
        try:
            if self.main_window.ui.line_edit_csv_output_path.text():
                if len(self.main_window.ui.line_edit_csv_conversion_path_input.text()) > 0:
                    self.main_window.ui.line_edit_csv_conversion_path_input.clear()
                
                self.main_window.ui.line_edit_csv_conversion_path_input.setText(
                    self.main_window.ui.line_edit_csv_output_path.text()
                )
                
                # Move to second tab
                if self.main_window.ui.tabWidget.currentIndex() == 0:
                    self.main_window.ui.tabWidget.setCurrentIndex(1) 
            else:
                QMessageBox.information(
                    self.main_window, 
                    "CSV output not set", 
                    "No CSV output for exporting has been set.\nCannot copy path to CSV converter input field."
                )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception passing CSV path", message)
    
    @Slot()
    def on_convert_hex_to_decimal(self):
        """Convert hexadecimal to decimal."""
        try:
            hex_value = self.main_window.ui.line_edit_hex_input.text()
            if hex_value:
                decimal_value = int(hex_value, 16)
                self.main_window.ui.line_edit_decimal_output.setText(str(decimal_value))
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Empty Input",
                    "Please enter a hexadecimal value."
                )
        except ValueError:
            QMessageBox.warning(
                self.main_window,
                "Invalid Hexadecimal",
                "Please enter a valid hexadecimal value."
            )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception converting hex to decimal", message)
    
    @Slot()
    def on_load_csv_file_for_table(self):
        """Load CSV file for table display."""
        try:
            import pandas as pd
            
            file_path = self.main_window.helper._browse_file_helper_non_input(
                dialog_message="Select CSV file to display",
                file_extension_filter="CSV File (*.csv)"
            )
            
            if file_path:
                df = pd.read_csv(file_path)
                self.main_window._populate_results_table(df)
                self.main_window._set_ui_widgets_table_disabled(False)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception loading CSV file", message)
    
    @Slot()
    def on_clear_table(self):
        """Clear table data."""
        self.main_window.ui.table_csv_data.setModel(None)
        self.main_window.ui.line_edit_filter_table.clear()
        self.main_window._set_ui_widgets_table_disabled(True)
