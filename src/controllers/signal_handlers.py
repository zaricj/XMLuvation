# File: modules/signal_handlers.py
import webbrowser
import datetime
import os
from PySide6.QtWidgets import (
    QMenu,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QLineEdit
    
)
from PySide6.QtGui import QAction, QShortcut, QKeySequence, QDesktopServices
from PySide6.QtCore import (
    Qt,
    Slot,
    QUrl,
    QFile,
    QIODevice,
    QTextStream

)

from typing import List, TYPE_CHECKING
from ui.main.XMLuvation_ui import Ui_MainWindow

if TYPE_CHECKING:
    from PySide6.QtCore import QSettings
    from controllers.state_controller import ComboboxStateHandler
    from modules.config_handler import ConfigHandler



class SignalHandlerMixin:
    """Mixin class to handle all signal connections and slot methods"""
    # Type hints for attributes accessed in this mixin
    ui: Ui_MainWindow
    xpath_filters: List[str]
    recent_xpath_expressions: List[str]
    settings: 'QSettings'
    cb_state_controller: 'ComboboxStateHandler'
    set_max_threads: int
    current_theme: str
    config_handler: "ConfigHandler"  # Replace with actual type
    
    def __init__(self):
        super().__init__()
        self._current_xml_parser = None
        self._current_csv_exporter = None
        self._current_xpath_builder = None

    # ============= SLOT METHODS =============
    
    # === Message Box Slots ===
    @Slot(str, str)
    def handle_critical_message(self, title: str, message: str):
        """Show critical message dialog."""
        QMessageBox.critical(self, title, message)

    @Slot(str, str)
    def handle_info_message(self, title: str, message: str):
        """Show information message dialog."""
        QMessageBox.information(self, title, message)

    @Slot(str, str)
    def handle_warning_message(self, title: str, message: str):
        """Show warning message dialog."""
        QMessageBox.warning(self, title, message)

    # === Progress and Output Slots ===
    @Slot(int)
    def handle_progress_bar_update(self, progress: int):
        """Handle progress bar updates."""
        self.ui.progressbar_main.setValue(progress)

    @Slot(str)
    def handle_program_output_append(self, message: str):
        """Handle QTextEdit progress updates with append."""
        self.ui.text_edit_program_output.append(message)

    @Slot(str)
    def handle_program_output_set_text(self, message: str):
        """Handle QTextEdit progress updates with setText."""
        self.ui.text_edit_program_output.setText(message)

    @Slot(str)
    def handle_csv_tab_output_append(self, message: str):
        """Handle CSV tab QTextEdit progress updates with append."""
        self.ui.text_edit_csv_conversion_tab_program_output.append(message)

    @Slot(str)
    def handle_csv_tab_output_set_text(self, message: str):
        """Handle CSV tab QTextEdit progress updates with setText."""
        self.ui.text_edit_csv_conversion_tab_program_output.setText(message)

    @Slot(str)
    def handle_file_processing_label(self, message: str):
        """Handle QLabel progress updates for file processing."""
        self.ui.label_file_processing.setText(message)

    # === Specific Feature Slots ===
    @Slot(int)
    def handle_csv_column_dropped(self, index: int):
        """Handle CSV column drop completion."""
        self.ui.combobox_csv_headers.removeItem(index)

    @Slot(dict)
    def handle_xml_parsing_finished(self, result: dict):
        """Handle XML parsing completion."""
        try:
            from modules.xml_parser import set_xml_content_to_widget

            xml_content = result.get("xml_string", "")
            # Add highlighter for XML files then add to QTextEdit
            set_xml_content_to_widget(self.ui.text_edit_xml_output, xml_content)
            self.ui.text_edit_xml_output.setPlainText(xml_content)

            # Fill the combo boxes with unique tags and attributes
            tags = result.get("tags", [])
            attributes = result.get("attributes", [])
            tag_values = result.get("tag_values", [])
            attribute_values = result.get("attribute_values", [])

            self.ui.combobox_tag_names.clear()
            self.ui.combobox_tag_names.addItems(tags)
            self.ui.combobox_attribute_names.clear()
            self.ui.combobox_attribute_names.addItems(attributes)

            self.ui.combobox_tag_values.clear()
            self.ui.combobox_tag_values.addItems(tag_values)
            self.ui.combobox_attribute_values.clear()
            self.ui.combobox_attribute_values.addItems(attribute_values)

            # Enable ComboBoxes
            self.ui.combobox_tag_names.setDisabled(False)
            self.ui.combobox_attribute_names.setDisabled(False)
            self.ui.combobox_tag_values.setDisabled(False)
            self.ui.combobox_attribute_values.setDisabled(False)

            # Display additional info
            info_message = f"File: {result.get('file_path', 'Unknown')}\n"
            info_message += f"Root element: {result.get('root_tag', 'Unknown')}\n"
            info_message += f"Total elements: {result.get('element_count', 0)}\n"
            info_message += f"Unique tags: {len(result.get('tags', []))}\n"
            info_message += f"Encoding: {result.get('encoding', 'Unknown')}"

            # Save XML file in initialized variable
            self.current_read_xml_file = result.get("file_path")
            self.ui.text_edit_program_output.append(info_message)

            self.parsed_xml_data = result
            # Pass the new result data to the ComboBoxStateController
            self.cb_state_controller.set_parsed_data(result)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Error processing parsing results", message)

    @Slot(bool)
    def handle_csv_export_started(self, state: bool):
        """Handle CSV export start state changes."""
        self.ui.button_abort_csv_export.setVisible(state)
        self.ui.label_file_processing.setVisible(state)
        self._set_ui_widgets_disabled(state)

    @Slot()
    def handle_csv_export_finished(self):
        """Handle CSV export completion."""
        self.ui.button_abort_csv_export.setVisible(False)
        self.ui.label_file_processing.setVisible(False)
        self._set_ui_widgets_disabled(False)
        self.ui.progressbar_main.reset()
        
        # Release worker reference
        if hasattr(self, '_current_csv_exporter'):
            self._current_csv_exporter = None

    # ============= CONNECTION METHODS =============

    def connect_xml_parsing_signals(self, worker):
        """Connect signals for XML parsing operations."""
        self._current_xml_parser = worker
        worker.signals.finished.connect(self.handle_xml_parsing_finished)
        worker.signals.error_occurred.connect(self.handle_critical_message)
        worker.signals.program_output_progress.connect(self.handle_program_output_append)

    def connect_xpath_builder_signals(self, worker):
        """Connect signals for XPath building operations."""
        self._current_xpath_builder = worker
        worker.signals.program_output_progress.connect(self.handle_program_output_append)
        worker.signals.error_occurred.connect(self.handle_critical_message)
        worker.signals.warning_occurred.connect(self.handle_warning_message)

    def connect_csv_export_signals(self, worker):
        """Connect signals for CSV export operations."""
        self._current_csv_exporter = worker
        worker.signals.finished.connect(self.handle_csv_export_finished)
        worker.signals.error_occurred.connect(self.handle_critical_message)
        worker.signals.info_occurred.connect(self.handle_info_message)
        worker.signals.warning_occurred.connect(self.handle_warning_message)
        worker.signals.program_output_progress_append.connect(self.handle_program_output_append)
        worker.signals.program_output_progress_set_text.connect(self.handle_program_output_set_text)
        worker.signals.file_processing_progress.connect(self.handle_file_processing_label)
        worker.signals.progressbar_update.connect(self.handle_progress_bar_update)
        worker.signals.visible_state_widget.connect(self.handle_csv_export_started)

    def connect_file_cleanup_signals(self, worker):
        """Connect signals for file cleanup operations."""
        worker.signals.error_occurred.connect(self.handle_critical_message)
        worker.signals.warning_occurred.connect(self.handle_warning_message)
        worker.signals.tab2_program_output_append.connect(self.handle_csv_tab_output_append)
        worker.signals.column_dropped_successfully.connect(self.handle_csv_column_dropped)

    def connect_csv_conversion_signals(self, worker):
        """Connect signals for CSV conversion operations."""
        worker.signals.error_occurred.connect(self.handle_critical_message)
        worker.signals.info_occurred.connect(self.handle_info_message)
        worker.signals.warning_occurred.connect(self.handle_warning_message)
        worker.signals.tab2_program_output_append.connect(self.handle_csv_tab_output_append)

    def connect_menu_bar_actions(self):
        """Connect all menu bar actions to their handlers."""
                # Add theme action to Menu Bar at the far right
        self.toggle_theme_action = self.ui.menu_bar.addAction(self.theme_icon, "Toggle Theme")
        self.ui.clear_recent_xpath_expressions_action.triggered.connect(self.on_clearRecentXpathExpressions)
        self.ui.clear_action.triggered.connect(self.on_clearOutput)
        self.ui.open_input_action.triggered.connect(self.on_openInputDirectory)
        self.ui.open_output_action.triggered.connect(self.on_openOutputDirectory)
        self.ui.open_csv_conversion_input_action.triggered.connect(self.on_openCSVConversionInputDirectory)
        self.ui.add_custom_path_action.triggered.connect(self.on_addCustomPath)
        self.ui.open_paths_manager.triggered.connect(self.on_openPathsManager)
        self.ui.open_pre_built_xpaths_manager_action.triggered.connect(self.on_openPrebuiltXPathsManager)
        self.ui.xpath_help_action.triggered.connect(self.on_xpathHelp)
        self.toggle_theme_action.triggered.connect(self.on_changeTheme)

        # Connect context menu signals
        self.ui.list_widget_xpath_expressions.customContextMenuRequested.connect(self.on_showXPathContextMenu)
        self.ui.text_edit_xml_output.customContextMenuRequested.connect(self.on_showXMLOutputContextMenu)

        # Connect recent xpath expressions menu
        for action in self.ui.recent_xpath_expressions_menu.actions():
            action.triggered.connect(
                lambda checked, exp=action.text(): self.on_setXPathExpressionInInput(exp)
            )

    def connect_ui_events(self):
        """Connect all UI element events to their handlers."""
        
        # Keyboard shortcuts
        self.shortcut_find = QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_F), self
        )
        self.shortcut_find.activated.connect(self.on_toggleXMLOutputSearchWidgets)

        # Line Edit events
        self.ui.line_edit_xml_folder_path_input.textChanged.connect(self.on_XMLFolderPathChanged)
        self.ui.line_edit_profile_cleanup_csv_file_path.textChanged.connect(self.on_CSVProfileCleanupInputChanged)

        # ComboBox events
        self.ui.combobox_tag_names.currentTextChanged.connect(self.cb_state_controller.on_tag_name_changed)
        self.ui.combobox_attribute_names.currentTextChanged.connect(self.cb_state_controller.on_attribute_name_changed)

        # Button events
        self.ui.button_pass_csv_to_converter.linkActivated.connect(self.on_passCSVFilePathToConverter)
        self.ui.button_browse_xml_folder.clicked.connect(self.on_browseXMLFolder)
        self.ui.button_read_xml.clicked.connect(self.on_readXMLFile)
        self.ui.button_browse_csv.clicked.connect(self.on_browseCSVOutput)
        self.ui.button_build_xpath.clicked.connect(self.on_buildXPathExpression)
        self.ui.button_add_xpath_to_list.clicked.connect(self.on_addXPathToList)
        self.ui.button_start_csv_export.clicked.connect(self.on_startCSVSearch)
        self.ui.button_abort_csv_export.clicked.connect(self.on_stopCSVSearch)
        self.ui.button_browse_csv_conversion_path_input.clicked.connect(self.on_browseCSVConversionInput)
        self.ui.button_csv_conversion_convert.clicked.connect(self.on_convertCSVFile)
        self.ui.button_profile_cleanup_browse_csv_file_path.clicked.connect(self.on_browseProfileCleanupCSV)
        self.ui.button_profile_cleanup_browse_folder_path.clicked.connect(self.on_browseProfileCleanupFolder)
        self.ui.button_profile_cleanup_cleanup_start.clicked.connect(self.on_startProfileCleanup)
        self.ui.button_drop_csv_header.clicked.connect(self.on_dropCurrentCSVHeader)
        self.ui.button_find_next.clicked.connect(self.on_XMLOutputSearchNext)
        self.ui.button_find_previous.clicked.connect(self.on_XMLOutputSearchPrevious)

        # CheckBox events
        self.ui.checkbox_write_index_column.toggled.connect(self.on_writeIndexCheckBoxToggled)
        self.ui.checkbox_group_matches.toggled.connect(self.on_groupMatchesCheckBoxToggled)

    # ============= EVENT HANDLER METHODS =============

    # === Menu Bar Event Handlers ===
    @Slot()
    def on_clearRecentXpathExpressions(self):
        """Clear recent XPath expressions."""
        reply = QMessageBox.question(
            self,
            "Clear recent XPath expressions",
            "Are you sure you want to clear the list of recent XPath expressions?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.settings.remove("recent_xpath_expressions")
            self.recent_xpath_expressions = []
            self._update_recent_xpath_expressions_menu()

    @Slot()
    def on_clearOutput(self):
        """Clear output text areas."""
        self.ui.text_edit_program_output.clear()
        self.ui.text_edit_csv_conversion_tab_program_output.clear()

    @Slot()
    def on_openInputDirectory(self):
        """Open input XML folder in file explorer."""
        directory = self.ui.line_edit_xml_folder_path_input.text()
        self._open_folder_in_file_explorer(directory)

    @Slot()
    def on_openOutputDirectory(self):
        """Open output CSV folder in file explorer."""
        directory = os.path.dirname(self.ui.line_edit_csv_output_path.text()) if self.ui.line_edit_csv_output_path.text() else ""
        self._open_folder_in_file_explorer(directory)

    @Slot()
    def on_openCSVConversionInputDirectory(self):
        """Open CSV conversion input folder in file explorer."""
        directory = os.path.dirname(self.ui.line_edit_csv_conversion_path_input.text()) if self.ui.line_edit_csv_conversion_path_input.text() else ""
        self._open_folder_in_file_explorer(directory)

    @Slot()
    def on_addCustomPath(self):
        """Add custom path dialog."""
        name, ok = QInputDialog.getText(
            self, "Add Custom Path", "Enter a name for the path:"
        )
        if ok and name:
            existing_paths = self.config_handler.get("custom_paths", {})
            if name in existing_paths:
                QMessageBox.warning(
                    self,
                    "Duplicate Name",
                    f"A path with the name '{name}' already exists."
                )
                return

            path, ok = QInputDialog.getText(self, "Add Custom Path", "Enter path:")
            if ok and path:
                self.config_handler.set(f"custom_paths.{name}", path)
                self._update_paths_menu()
                
    @Slot() # Opens Pre-built XPaths Manager QWidget
    def on_openPrebuiltXPathsManager(self):
        from ui.widgets.pre_built_xpaths_manager import PreBuiltXPathsManager
        self.w = PreBuiltXPathsManager()
        self.w.show()

    @Slot() # Opens Paths Manager QWidget
    def on_openPathsManager(self):
        """Open paths manager window."""
        from ui.widgets.path_manager import CustomPathsManager
        self.w = CustomPathsManager(main_window=self)
        self.w.show()

    @Slot()
    def on_xpathHelp(self):
        """Open XPath help webpage."""
        webbrowser.open("https://www.w3schools.com/xml/xpath_syntax.asp")

    @Slot()
    def on_changeTheme(self):
        """Toggle application theme."""
        if self.current_theme == "dark_theme.qss":
            self.toggle_theme_action.setIcon(self.dark_mode_icon)
            self._initialize_theme_file(self.light_theme_file)
            self.current_theme = "light_theme.qss"
        else:
            self.toggle_theme_action.setIcon(self.light_mode_icon)
            self._initialize_theme_file(self.dark_theme_file)
            self.current_theme = "dark_theme.qss"

    # === UI Event Handlers ===
    @Slot()
    def on_toggleXMLOutputSearchWidgets(self):
        """Toggle XML output search widgets visibility."""
        is_hidden = self.ui.line_edit_xml_output_find_text.isHidden()
        
        self.ui.line_edit_xml_output_find_text.setHidden(not is_hidden)
        self.ui.button_find_next.setHidden(not is_hidden)
        self.ui.button_find_previous.setHidden(not is_hidden)
        
        if not is_hidden:
            self.ui.line_edit_xml_output_find_text.clear()

    @Slot()
    def on_XMLFolderPathChanged(self):
        """Update XML file count when folder path changes."""
        try:
            folder = self.ui.line_edit_xml_folder_path_input.text()
            if os.path.isdir(folder):
                xml_files_count = sum(
                    1 for f in os.listdir(folder) if f.endswith(".xml")
                )
                if xml_files_count >= 1:
                    self.ui.statusbar_xml_files_count.setText(
                        f"Found {xml_files_count} XML Files"
                    )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.statusbar_xml_files_count.setText(
                f"Error counting XML files: {message}"
            )

    @Slot()
    def on_CSVProfileCleanupInputChanged(self):
        """Handle CSV profile cleanup input changes."""
        from controllers.state_controller import CSVColumnDropHandler
        
        csv_file_path = self.ui.line_edit_profile_cleanup_csv_file_path.text()
        column_to_drop = self.ui.combobox_csv_headers.currentText()
        column_to_drop_index = self.ui.combobox_csv_headers.currentIndex()
        csv_header_combobox = self.ui.combobox_csv_headers
        drop_header_button = self.ui.button_drop_csv_header

        handler = CSVColumnDropHandler(
            main_window=self,
            csv_file_path=csv_file_path,
            column_to_drop=column_to_drop,
            column_to_drop_index=column_to_drop_index,
            csv_header_combobox=csv_header_combobox,
            drop_header_button=drop_header_button,
        )
        handler.on_csv_input_file_path_changed()

    # === Button Event Handlers ===
    @Slot()
    def on_browseXMLFolder(self):
        """Browse for XML folder."""
        self._browse_folder_helper(
            dialog_message="Select directory that contains XML files",
            line_widget=self.ui.line_edit_xml_folder_path_input,
        )

    @Slot()
    def on_readXMLFile(self):
        """Read XML file dialog and parsing."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Select XML File", "", "XML File (*.xml)"
            )
            if file_name:
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
    def on_browseCSVOutput(self):
        """Browse for CSV output file."""
        self._browse_save_file_as_helper(
            dialog_message="Save as",
            line_widget=self.ui.line_edit_csv_output_path,
            file_extension_filter="CSV File (*.csv)",
            filename_placeholder=f"Evaluation_{datetime.datetime.now().strftime('%Y.%m.%d_%H%M')}.csv"
        )

    @Slot()
    def on_buildXPathExpression(self):
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
            QMessageBox.critical(self, "Exception on building xpath expression", message)

    @Slot()
    def on_addXPathToList(self):
        """Add XPath expression to list."""
        try:
            from controllers.state_controller import AddXPathExpressionToListHandler, GenerateCSVHeaderHandler
            
            xpath_input = self.ui.line_edit_xpath_builder.text()
            xpath_filters = self.xpath_filters
            csv_headers_input = self.ui.line_edit_csv_headers_input
            list_widget_xpath_expressions = self.ui.list_widget_xpath_expressions

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
                self._update_statusbar_xpath_listbox_count()

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
            QMessageBox.critical(self, "Exception adding XPath Expression to list widget", message)

    @Slot()
    def on_startCSVSearch(self):
        """Start CSV search and export process."""
        try:
            from controllers.state_controller import SearchAndExportToCSVHandler
            
            xml_path = self.ui.line_edit_xml_folder_path_input.text()
            csv_output = self.ui.line_edit_csv_output_path.text()
            headers = self.ui.line_edit_csv_headers_input.text()
            group_matches_flag = self.ui.checkbox_group_matches.isChecked()
            max_threads = self.set_max_threads
            xpath_filters = self.xpath_filters

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
            QMessageBox.critical(self, "Exception on starting to search and export to csv", message)

    @Slot()
    def on_stopCSVSearch(self):
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
            QMessageBox.critical(self, "Exception on stopping CSV export", message)

    @Slot()
    def on_browseCSVConversionInput(self):
        """Browse for CSV conversion input file."""
        self._browse_file_helper(
            dialog_message="Select csv file for conversion",
            line_widget=self.ui.line_edit_csv_conversion_path_input,
            file_extension_filter="CSV File (*.csv)",
        )

    @Slot()
    def on_convertCSVFile(self):
        """Start CSV conversion process."""
        try:
            from controllers.state_controller import CSVConversionHandler
            
            csv_file_to_convert = self.ui.line_edit_csv_conversion_path_input.text()
            extension_type = self.ui.combobox_csv_conversion_output_type.currentText()
            write_index = self.ui.checkbox_write_index_column.isChecked()

            self.csv_conversion_controller = CSVConversionHandler(
                main_window=self,
                csv_file_to_convert=csv_file_to_convert,
                extension_type=extension_type,
                write_index=write_index,
            )
            self.csv_conversion_controller.start_csv_conversion()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception on starting csv convert to other filetype", message)

    @Slot()
    def on_browseProfileCleanupCSV(self):
        """Browse for profile cleanup CSV file."""
        self._browse_file_helper(
            dialog_message="Select csv file",
            line_widget=self.ui.line_edit_profile_cleanup_csv_file_path,
            file_extension_filter="CSV File (*.csv)",
        )

    @Slot()
    def on_browseProfileCleanupFolder(self):
        """Browse for profile cleanup folder."""
        self._browse_folder_helper(
            dialog_message="Select directory that contains XML files",
            line_widget=self.ui.line_edit_profile_cleanup_folder_path,
        )

    @Slot()
    def on_startProfileCleanup(self):
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
            QMessageBox.critical(self, "Exception on starting lobster profile xml files cleanup", message)

    @Slot()
    def on_dropCurrentCSVHeader(self):
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
    def on_XMLOutputSearchNext(self):
        """Search next in XML output."""
        self.xml_text_searcher.search_next()

    @Slot()
    def on_XMLOutputSearchPrevious(self):
        """Search previous in XML output."""
        self.xml_text_searcher.search_previous()

    @Slot()
    def on_passCSVFilePathToConverter(self):
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
            QMessageBox.critical(self, "Exception on starting csv convert to other filetype", message)

    # === Checkbox Event Handlers ===
    @Slot()
    def on_writeIndexCheckBoxToggled(self):
        """Handle write index checkbox toggle."""
        message_with_index = """
        Data will look like this:

        | Index           | Header 1   | Header 2    |
        |-------------------|-------------------|-------------------|
        | 1                  | Data...         | Data...        |
        """
        message_without_index = """
        Data will look like this:

        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Data...         |
        """
        try:
            if self.ui.checkbox_write_index_column.isChecked():
                self.ui.text_edit_csv_conversion_tab_program_output.setText(message_with_index)
            else:
                self.ui.text_edit_csv_conversion_tab_program_output.setText(message_without_index)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", f"An error occurred: {message}")
    
    @Slot()
    def on_groupMatchesCheckBoxToggled(self):
        """Handle group matches checkbox toggle."""
        example_on = """
        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Match 1; Match 2; Match 3 |"""
        
        example_off = """
        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Match 1         |
        | Data...       | Match 2         |
        | Data...       | Match 3         |"""
        
        try:
            if self.ui.checkbox_group_matches.isChecked():
                self.ui.text_edit_program_output.setText(
                    f"Group Matches is enabled. All matches for each XPath expression will be grouped together in the CSV output.\n{example_on}"
                )
            else:
                self.ui.text_edit_program_output.setText(
                    f"Group Matches is disabled. Each match will be listed separately in the CSV output.\n{example_off}"
                )
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception in Program", f"An error occurred: {message}")

    # === Context Menu Event Handlers ===
    @Slot()
    def on_showXPathContextMenu(self, position):
        """Show context menu for XPath expressions list."""
        context_menu = QMenu(self)
        remove_action = QAction("Remove Selected", self)
        remove_all_action = QAction("Remove All", self)

        context_menu.addAction(remove_action)
        context_menu.addAction(remove_all_action)

        remove_action.triggered.connect(self._remove_selected_xpath_item)
        remove_all_action.triggered.connect(self._remove_all_xpath_items)

        context_menu.exec(self.ui.list_widget_xpath_expressions.mapToGlobal(position))

    @Slot()
    def on_showXMLOutputContextMenu(self, position):
        """Show context menu for XML output."""
        menu = self.ui.text_edit_xml_output.createStandardContextMenu()
        find_action = QAction(
            "Find",
            self,
            shortcut=QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_F),
        )
        find_action.triggered.connect(self.on_toggleXMLOutputSearchWidgets)
        menu.addAction(find_action)

        menu.exec(self.ui.text_edit_xml_output.mapToGlobal(position))

    @Slot(str)
    def on_setXPathExpressionInInput(self, expression: str):
        """Set XPath expression in input field."""
        self.ui.line_edit_xpath_builder.clear()
        self.ui.line_edit_xpath_builder.setText(expression)

    # ============= HELPER METHODS =============

    def _browse_folder_helper(self, dialog_message: str, line_widget: QLineEdit):
        """Helper for folder browsing dialogs."""
        try:
            folder = QFileDialog.getExistingDirectory(self, dialog_message)
            if folder:
                line_widget.setText(folder)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred in browse folder method", message)

    def _browse_file_helper(self, dialog_message: str, line_widget: QLineEdit, file_extension_filter: str):
        """Helper for file browsing dialogs."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, caption=dialog_message, filter=file_extension_filter
            )
            if file_name:
                line_widget.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred in browse folder method", message)

    def _browse_save_file_as_helper(self, dialog_message: str, line_widget: QLineEdit, 
                                   file_extension_filter: str, filename_placeholder: str = ""):
        """Helper for save file dialogs."""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, caption=dialog_message, dir=filename_placeholder, filter=file_extension_filter
            )
            if file_name:
                line_widget.setText(file_name)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "An exception occurred in browse save file method", message)

    def _parse_xml_file(self, xml_file_path: str):
        """Parse XML file and display content."""
        try:
            from controllers.state_controller import ParseXMLFileHandler
            
            xml_parser = ParseXMLFileHandler(main_window=self, xml_file_path=xml_file_path)
            xml_parser.start_xml_parsing()
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Exception on starting to parse xml file", message)

    def _open_folder_in_file_explorer(self, folder_path: str):
        """Helper method to open folder in file explorer."""
        if folder_path and os.path.exists(folder_path):
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            except Exception as ex:
                message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
                QMessageBox.critical(self, "An exception occurred", message)
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Path does not exist or is not a valid path:\n{folder_path}"
            )

    def _set_ui_widgets_disabled(self, state: bool):
        """Helper to disable/enable UI widgets during operations."""
        self.ui.button_browse_xml_folder.setDisabled(state)
        self.ui.button_read_xml.setDisabled(state)
        self.ui.button_build_xpath.setDisabled(state)
        self.ui.button_add_xpath_to_list.setDisabled(state)
        self.ui.button_browse_csv.setDisabled(state)
        self.ui.button_browse_csv_conversion_path_input.setDisabled(state)
        self.ui.button_start_csv_export.setDisabled(state)
        self.ui.line_edit_xml_folder_path_input.setReadOnly(state)
        self.ui.line_edit_csv_output_path.setReadOnly(state)

    def _add_recent_xpath_expression(self, expression: str):
        """Add XPath expression to recent expressions."""
        MAX_RECENT = 10
        if expression not in self.recent_xpath_expressions:
            self.recent_xpath_expressions.insert(0, expression)
            self.recent_xpath_expressions = self.recent_xpath_expressions[:MAX_RECENT]
            self.settings.setValue("recent_xpath_expressions", self.recent_xpath_expressions)
            self._update_recent_xpath_expressions_menu()

    def _update_recent_xpath_expressions_menu(self):
        """Update recent XPath expressions menu."""
        self.ui.recent_xpath_expressions_menu.clear()
        for expression in self.recent_xpath_expressions:
            action = QAction(expression, self)
            action.triggered.connect(
                lambda checked, exp=expression: self.on_setXPathExpressionInInput(exp)
            )
            self.ui.recent_xpath_expressions_menu.addAction(action)

    def _update_statusbar_xpath_listbox_count(self):
        """Update statusbar with XPath expression count."""
        counter = self.ui.list_widget_xpath_expressions.count()
        if counter != 0:
            self.ui.statusbar_xpath_expressions.setText(
                f"XPath expressions in list: {counter}"
            )

    def _update_paths_menu(self):
        """Update the paths menu with custom paths."""
        self.ui.paths_menu.clear()
        
        custom_paths = self.config_handler.get("custom_paths", {})
        for name, path in custom_paths.items():
            action = QAction(name, self)
            action.setStatusTip(f"Open {name}")
            action.triggered.connect(lambda checked, p=path: self._set_path_in_input(p))
            self.ui.paths_menu.addAction(action)

        if custom_paths:
            self.ui.paths_menu.addSeparator()

        self.ui.paths_menu.addAction(self.ui.add_custom_path_action)

    def _set_path_in_input(self, path: str):
        """Set path in input field."""
        self.ui.line_edit_xml_folder_path_input.setText(path)

    def _initialize_theme_file(self, theme_file: str):
        """Initialize theme from file."""
        try:
            file = QFile(theme_file)
            if not file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
                return
            else:
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.setStyleSheet(stylesheet)
            file.close()
        except Exception as ex:
            QMessageBox.critical(self, "Theme load error", f"Failed to load theme: {str(ex)}")

    def _remove_selected_xpath_item(self):
        """Remove selected XPath item from list."""
        try:
            current_selected_item = self.ui.list_widget_xpath_expressions.currentRow()
            if current_selected_item != -1:
                item_to_remove = self.ui.list_widget_xpath_expressions.takeItem(current_selected_item)
                self.xpath_filters.pop(current_selected_item)
                self.ui.text_edit_program_output.append(
                    f"Removed item: {item_to_remove.text()} at row {current_selected_item}"
                )
                self._update_statusbar_xpath_listbox_count()
            else:
                self.ui.text_edit_program_output.append("No item selected to delete.")
        except IndexError:
            self.ui.text_edit_program_output.append("Nothing to delete.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.text_edit_program_output.setText(f"Error removing selected item from list: {message}")

    def _remove_all_xpath_items(self):
        """Remove all XPath items from list."""
        try:
            if self.ui.list_widget_xpath_expressions.count() > 0:
                self.xpath_filters.clear()
                self.ui.list_widget_xpath_expressions.clear()
                self.ui.text_edit_program_output.setText("Deleted all items from the list.")
                self._update_statusbar_xpath_listbox_count()
                # Clean CSV Header Input if it has any value in it
                if len(self.ui.line_edit_csv_headers_input.text()) > 1:
                    self.ui.line_edit_csv_headers_input.clear()
            else:
                self.ui.text_edit_program_output.setText("No items to delete in list.")
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            self.ui.text_edit_program_output.setText(f"Error removing all items from list: {message}")