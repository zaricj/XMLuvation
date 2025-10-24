# File: controllers/signal_connector.py
"""Centralized signal connection management."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


class SignalConnector:
    """Manages signal connections for worker threads."""
    
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window
        self._current_xml_parser = None
        self._current_xpath_builder = None
        self._current_csv_exporter = None
    
    def connect_xml_parsing_signals(self, worker):
        """Connect signals for XML parsing operations."""
        self._current_xml_parser = worker
        worker.signals.finished.connect(self.main_window.handle_xml_parsing_finished)
        worker.signals.error_occurred.connect(self.main_window.handle_critical_message)
        worker.signals.program_output_progress.connect(self.main_window.handle_program_output_append)
    
    def connect_xpath_builder_signals(self, worker):
        """Connect signals for XPath building operations."""
        self._current_xpath_builder = worker
        worker.signals.program_output_progress.connect(self.main_window.handle_program_output_append)
        worker.signals.error_occurred.connect(self.main_window.handle_critical_message)
        worker.signals.warning_occurred.connect(self.main_window.handle_warning_message)
    
    def connect_csv_export_signals(self, worker):
        """Connect signals for CSV export operations."""
        self._current_csv_exporter = worker
        worker.signals.finished.connect(self.main_window.handle_csv_export_finished)
        worker.signals.error_occurred.connect(self.main_window.handle_critical_message)
        worker.signals.info_occurred.connect(self.main_window.handle_info_message)
        worker.signals.warning_occurred.connect(self.main_window.handle_warning_message)
        worker.signals.program_output_progress_append.connect(self.main_window.handle_program_output_append)
        worker.signals.program_output_progress_set_text.connect(self.main_window.handle_program_output_set_text)
        worker.signals.file_processing_progress.connect(self.main_window.handle_file_processing_label)
        worker.signals.progressbar_update.connect(self.main_window.handle_progress_bar_update)
        worker.signals.visible_state_widget.connect(self.main_window.handle_csv_export_started)
    
    def connect_file_cleanup_signals(self, worker):
        """Connect signals for file cleanup operations."""
        worker.signals.error_occurred.connect(self.main_window.handle_critical_message)
        worker.signals.warning_occurred.connect(self.main_window.handle_warning_message)
        worker.signals.tab2_program_output_append.connect(self.main_window.handle_csv_tab_output_append)
        worker.signals.column_dropped_successfully.connect(self.main_window.handle_csv_column_dropped)
    
    def connect_csv_conversion_signals(self, worker):
        """Connect signals for CSV conversion operations."""
        worker.signals.error_occurred.connect(self.main_window.handle_critical_message)
        worker.signals.info_occurred.connect(self.main_window.handle_info_message)
        worker.signals.warning_occurred.connect(self.main_window.handle_warning_message)
        worker.signals.tab2_program_output_append.connect(self.main_window.handle_csv_tab_output_append)
        worker.signals.set_file_open_path.connect(self.main_window.handler_set_converted_file_path)
        worker.signals.start_gif.connect(self.main_window.handle_start_loading_gif)
        worker.signals.stop_gif.connect(self.main_window.handle_stop_loading_gif)
