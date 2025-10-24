# controllers/xml_controller.py
"""
XMLController - Handles XML-related UI coordination.
Delegates business logic to XMLParserService.
"""
import os
from PySide6.QtWidgets import QFileDialog, QMessageBox
from typing import TYPE_CHECKING

from services.xml_parser_service import XMLParserService
from services.file_service import FileService

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class XMLController:
    """Controller for XML-related operations - UI coordination only, no business logic."""
    
    def __init__(self, main_window: 'MainWindow', xml_service: XMLParserService = None, file_service: FileService = None):
        """Initialize XMLController with dependency injection.
        
        Args:
            main_window: Reference to the main window
            xml_service: XML parser service (injected dependency)
            file_service: File service (injected dependency)
        """
        self.main_window = main_window
        self.xml_service = xml_service or XMLParserService()
        self.file_service = file_service or FileService()
        self.current_xml_file = None
        self.parsed_data = {}
    
    def browse_xml_folder(self):
        """Handle XML folder browsing - UI coordination."""
        folder = QFileDialog.getExistingDirectory(
            self.main_window, 
            "Select directory that contains XML files"
        )
        if folder:
            # Update UI
            self.main_window.ui.line_edit_xml_folder_path_input.setText(folder)
            # Delegate to service for business logic
            self._update_file_count(folder)
    
    def read_xml_file(self):
        """Handle XML file reading - UI coordination."""
        file_name, _ = QFileDialog.getOpenFileName(
            self.main_window, 
            "Select XML File", 
            "", 
            "XML File (*.xml)"
        )
        if file_name:
            # Validate using service
            is_valid, message = self.file_service.validate_xml_file(file_name)
            if not is_valid:
                QMessageBox.warning(self.main_window, "Invalid File", message)
                return
            
            # Clear UI output
            self.main_window.ui.text_edit_program_output.clear()
            # Parse file
            self.parse_xml_file(file_name)
            
            # Update XML path input if not already set
            if not self.main_window.ui.line_edit_xml_folder_path_input.text():
                self.main_window.ui.line_edit_xml_folder_path_input.setText(
                    os.path.dirname(file_name)
                )
    
    def parse_xml_file(self, file_path: str):
        """Parse XML file using worker thread - UI coordination."""
        try:
            # Delegate to service for creating worker
            worker = self.xml_service.create_parser_worker(file_path)
            # Connect signals for UI updates
            self._connect_parser_signals(worker)
            # Start worker thread
            self.main_window.thread_pool.start(worker)
            self.current_xml_file = file_path
        except Exception as ex:
            QMessageBox.critical(
                self.main_window,
                "Parse Error",
                f"Failed to parse XML file: {str(ex)}"
            )
    
    def _update_file_count(self, folder: str):
        """Update XML file count in status bar - UI update."""
        try:
            # Delegate to service for business logic
            count = self.xml_service.count_xml_files(folder)
            # Update UI
            self.main_window.ui.statusbar_xml_files_count.setText(
                f"Found {count} XML Files"
            )
        except Exception as e:
            self.main_window.ui.statusbar_xml_files_count.setText(
                f"Error counting XML files: {e}"
            )
    
    def _connect_parser_signals(self, worker):
        """Connect parser worker signals to UI update methods."""
        # This connects the worker's signals to MainWindow methods
        # The actual signal connections would depend on the worker's signal definitions
        if hasattr(worker, 'signals'):
            if hasattr(worker.signals, 'finished'):
                worker.signals.finished.connect(self._on_parse_complete)
            if hasattr(worker.signals, 'error_occurred'):
                worker.signals.error_occurred.connect(self._on_parse_error)
            if hasattr(worker.signals, 'program_output_progress'):
                worker.signals.program_output_progress.connect(
                    self.main_window.ui.text_edit_program_output.append
                )
    
    def _on_parse_complete(self, data: dict):
        """Handle parse completion - UI update."""
        self.parsed_data = data
        # Update the main window's parsed data reference
        self.main_window._parsed_xml_data_ref = data
        # Update combobox state controller
        self.main_window.cb_state_controller.set_parsed_data(data)
        # Display result in UI
        self.main_window.ui.text_edit_program_output.append(
            f"Successfully parsed XML file: {data.get('file_path', 'unknown')}"
        )
    
    def _on_parse_error(self, title: str, message: str):
        """Handle parse error - UI update."""
        QMessageBox.critical(self.main_window, title, message)
