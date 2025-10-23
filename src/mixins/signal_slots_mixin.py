from pyclbr import Class
from pydoc import classname
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QMovie
from PySide6.QtCore import Slot
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

class SignalSlotsMixin:
    """Handles worker signals and slots"""
    
    def connect_worker_signals(self, worker: Class, worker_type: str):
        """Connect signals based on worker type"""
        
        if worker_type == "xml_parser":
            worker.signals.finished.connect(self.handle_xml_parsing_finished)
            worker.signals.error_occurred.connect(self.handle_critical_message)
            worker.signals.program_output_progress.connect(self.handle_program_output_append)
            
        elif worker_type == "xpath_builder":
            worker.signals.program_output_progress.connect(self.handle_program_output_append)
            worker.signals.error_occurred.connect(self.handle_critical_message)
            worker.signals.warning_occurred.connect(self.handle_warning_message)
            
        elif worker_type == "csv_export":
            worker.signals.finished.connect(self.handle_csv_export_finished)
            worker.signals.error_occurred.connect(self.handle_critical_message)
            worker.signals.info_occurred.connect(self.handle_info_message)
            worker.signals.warning_occurred.connect(self.handle_warning_message)
            worker.signals.program_output_progress_append.connect(self.handle_program_output_append)
            worker.signals.program_output_progress_set_text.connect(self.handle_program_output_set_text)
            worker.signals.file_processing_progress.connect(self.handle_file_processing_label)
            worker.signals.progressbar_update.connect(self.handle_progress_bar_update)
            worker.signals.visible_state_widget.connect(self.handle_csv_export_started)

        elif worker_type == "file_cleanup":
            worker.signals.error_occurred.connect(self.handle_critical_message)
            worker.signals.warning_occurred.connect(self.handle_warning_message)
            worker.signals.tab2_program_output_append.connect(self.handle_csv_tab_output_append)
            worker.signals.column_dropped_successfully.connect(self.handle_csv_column_dropped)

        elif worker_type == "csv_conversion":
            worker.signals.error_occurred.connect(self.handle_critical_message)
            worker.signals.info_occurred.connect(self.handle_info_message)
            worker.signals.warning_occurred.connect(self.handle_warning_message)
            worker.signals.tab2_program_output_append.connect(self.handle_csv_tab_output_append)
            worker.signals.set_file_open_path.connect(self.handler_set_converted_file_path)
            worker.signals.start_gif.connect(self.handle_start_loading_gif)
            worker.signals.stop_gif.connect(self.handle_stop_loading_gif)
            

    # ============= SLOT METHODS =============
    
    # === Message Box Slots ===
    @Slot(str, str)
    def handle_critical_message(self: "MainWindow", title: str, message: str):
        """Show critical message dialog."""
        QMessageBox.critical(self, title, message)

    @Slot(str, str)
    def handle_info_message(self: "MainWindow", title: str, message: str):
        """Show information message dialog."""
        QMessageBox.information(self, title, message)

    @Slot(str, str)
    def handle_warning_message(self: "MainWindow", title: str, message: str):
        """Show warning message dialog."""
        QMessageBox.warning(self, title, message)

    # === Progress and Output Slots ===
    @Slot(int)
    def handle_progress_bar_update(self: "MainWindow", progress: int):
        """Handle progress bar updates."""
        self.ui.progressbar_main.setValue(progress)

    @Slot(str)
    def handle_program_output_append(self: "MainWindow", message: str):
        """Handle QTextEdit progress updates with append."""
        self.ui.text_edit_program_output.append(message)

    @Slot(str)
    def handle_program_output_set_text(self: "MainWindow", message: str):
        """Handle QTextEdit progress updates with setText."""
        self.ui.text_edit_program_output.setText(message)

    @Slot(str)
    def handle_csv_tab_output_append(self: "MainWindow", message: str):
        """Handle CSV tab QTextEdit progress updates with append."""
        self.ui.text_edit_csv_output.append(message)

    @Slot(str)
    def handle_csv_tab_output_set_text(self: "MainWindow", message: str):
        """Handle CSV tab QTextEdit progress updates with setText."""
        self.ui.text_edit_csv_output.setText(message)
        
    @Slot(str)
    def handler_set_converted_file_path(self: "MainWindow", file_path: str):
        """Set the file path of the converted file in the "Open File" QLineEdit."""
        self.ui.line_edit_csv_conversion_open_file_path.setText(file_path)
        
    @Slot()
    def handle_start_loading_gif(self: "MainWindow"):
        """Handle starting the loading GIF - creates QMovie on main thread."""
        try:
            root = Path(__file__).parent.parent
            gif = root / "resources" / "gifs" / "loading_circle_small.gif"
            
            # Create QMovie on the MAIN thread
            movie = QMovie(str(gif))
            
            if not movie.isValid():
                QMessageBox.warning(self, "GIF Not Found", f"GIF file not found or invalid: {gif}")
                return
                
            self._main_thread_loading_movie_ref = movie
            self.ui.label_loading_gif.setMovie(movie)
            movie.start()
            self.ui.label_loading_gif.setVisible(True)
        except Exception as e:
            QMessageBox.critical(self, "GIF Error", f"Error loading GIF: {e}")
            
    @Slot()
    def handle_stop_loading_gif(self: "MainWindow"):
        """Handle stopping the loading GIF."""
        movie = self._main_thread_loading_movie_ref
        if movie:
            movie.stop()
            movie.deleteLater()  # Clean up the QMovie object
            self._main_thread_loading_movie_ref = None
        self.ui.label_loading_gif.clear()
        self.ui.label_loading_gif.setVisible(False)

    @Slot(str)
    def handle_file_processing_label(self: "MainWindow", message: str):
        """Handle QLabel progress updates for file processing."""
        self.ui.label_file_processing.setText(message)

    # === Specific Feature Slots ===
    @Slot(int)
    def handle_csv_column_dropped(self: "MainWindow", index: int):
        """Handle CSV column drop completion."""
        self.ui.combobox_csv_headers.removeItem(index)

    @Slot(dict)
    def handle_xml_parsing_finished(self: "MainWindow", result: dict):
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
    def handle_csv_export_started(self: "MainWindow", state: bool):
        """Handle CSV export start state changes."""
        self.ui.button_abort_csv_export.setVisible(state)
        self.ui.label_file_processing.setVisible(state)
        self.ui.progressbar_main.setVisible(state)
        self._set_ui_widgets_disabled(state)

    @Slot()
    def handle_csv_export_finished(self: "MainWindow"):
        """Handle CSV export completion."""
        self.ui.button_abort_csv_export.setVisible(False)
        self.ui.label_file_processing.setVisible(False)
        self.ui.progressbar_main.setVisible(False)
        self._set_ui_widgets_disabled(False)
        self.ui.progressbar_main.reset()
        
        # Release worker reference
        if hasattr(self, '_current_csv_exporter'):
            self._current_csv_exporter = None
            

    # Handle the enabled/disabled state of all the specified widgets that are in the search and export to csv GroupBox
    def _set_ui_widgets_disabled(self: "MainWindow", state: bool):
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
    
    # Handle the enabled/disabled state of all the specified widgets that affect the Table GroupBox
    def _set_ui_widgets_table_disabled(self: "MainWindow", state: bool):
        self.ui.button_clear_table.setDisabled(state)
        self.ui.line_edit_filter_table.setDisabled(state)