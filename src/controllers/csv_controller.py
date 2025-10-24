# controllers/csv_controller.py
"""
CSVController - Handles CSV-related UI coordination.
Delegates business logic to CSVExportService.
"""
import datetime
from PySide6.QtWidgets import QFileDialog, QMessageBox
from typing import TYPE_CHECKING, Dict, Any

from services.csv_export_service import CSVExportService
from services.file_service import FileService

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class CSVController:
    """Controller for CSV-related operations - UI coordination only, no business logic."""
    
    def __init__(self, main_window: 'MainWindow', csv_service: CSVExportService = None, file_service: FileService = None):
        """Initialize CSVController with dependency injection.
        
        Args:
            main_window: Reference to the main window
            csv_service: CSV export service (injected dependency)
            file_service: File service (injected dependency)
        """
        self.main_window = main_window
        self.csv_service = csv_service or CSVExportService()
        self.file_service = file_service or FileService()
        self.current_exporter = None
    
    def browse_csv_output(self):
        """Handle CSV output file browsing - UI coordination."""
        filename = f"Evaluation_{datetime.datetime.now().strftime('%Y.%m.%d_%H%M')}.csv"
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save as",
            filename,
            "CSV File (*.csv)"
        )
        if file_path:
            # Ensure directory exists using service
            self.file_service.ensure_directory_exists(file_path)
            # Update UI
            self.main_window.ui.line_edit_csv_output_path.setText(file_path)
    
    def start_csv_export(self):
        """Start CSV export process - UI coordination."""
        # Get configuration from UI
        config = self._get_export_config()
        
        # Validate configuration using service
        is_valid, error_message = self.csv_service.validate_config(config)
        if not is_valid:
            QMessageBox.warning(self.main_window, "Invalid Configuration", error_message)
            return
        
        try:
            # Delegate to service for creating worker
            worker = self.csv_service.create_export_worker(config)
            # Connect signals for UI updates
            self._connect_worker_signals(worker)
            # Start worker thread
            self.main_window.thread_pool.start(worker)
            self.current_exporter = worker
            
            # Update UI state
            self._update_ui_for_export_start()
        except Exception as ex:
            QMessageBox.critical(
                self.main_window,
                "Export Error",
                f"Failed to start CSV export: {str(ex)}"
            )
    
    def stop_csv_export(self):
        """Stop running CSV export - UI coordination."""
        if self.current_exporter:
            self.current_exporter.stop()
            self.current_exporter = None
            # Update UI state
            self._update_ui_for_export_stop()
    
    def _get_export_config(self) -> Dict[str, Any]:
        """Get export configuration from UI widgets."""
        # Extract configuration from main window UI
        return {
            'xml_folder_path': self.main_window.ui.line_edit_xml_folder_path_input.text(),
            'csv_file_path': self.main_window.ui.line_edit_csv_output_path.text(),
            'xpath_filters': self.main_window._listwidget_to_list(
                self.main_window.ui.list_widget_main_xpath_expressions
            ),
            'csv_headers': [
                h.strip() for h in 
                self.main_window.ui.line_edit_csv_headers_input.text().split(',')
                if h.strip()
            ],
            'group_matches': self.main_window.ui.checkbox_group_matches.isChecked()
        }
    
    def _connect_worker_signals(self, worker):
        """Connect export worker signals to UI update methods."""
        if hasattr(worker, 'signals'):
            if hasattr(worker.signals, 'finished'):
                worker.signals.finished.connect(self._on_export_complete)
            if hasattr(worker.signals, 'error_occurred'):
                worker.signals.error_occurred.connect(self._on_export_error)
            if hasattr(worker.signals, 'progress'):
                worker.signals.progress.connect(self._on_export_progress)
            if hasattr(worker.signals, 'program_output'):
                worker.signals.program_output.connect(
                    self.main_window.ui.text_edit_program_output.append
                )
    
    def _update_ui_for_export_start(self):
        """Update UI elements when export starts."""
        self.main_window.ui.button_start_csv_export.setEnabled(False)
        self.main_window.ui.button_abort_csv_export.show()
        self.main_window.ui.progressbar_main.show()
        self.main_window.ui.label_file_processing.show()
    
    def _update_ui_for_export_stop(self):
        """Update UI elements when export stops."""
        self.main_window.ui.button_start_csv_export.setEnabled(True)
        self.main_window.ui.button_abort_csv_export.hide()
        self.main_window.ui.progressbar_main.hide()
        self.main_window.ui.label_file_processing.hide()
    
    def _on_export_complete(self, result: Any):
        """Handle export completion - UI update."""
        self._update_ui_for_export_stop()
        self.current_exporter = None
        QMessageBox.information(
            self.main_window,
            "Export Complete",
            "CSV export completed successfully!"
        )
    
    def _on_export_error(self, title: str, message: str):
        """Handle export error - UI update."""
        self._update_ui_for_export_stop()
        self.current_exporter = None
        QMessageBox.critical(self.main_window, title, message)
    
    def _on_export_progress(self, current: int, total: int, filename: str):
        """Handle export progress update - UI update."""
        if total > 0:
            progress = int((current / total) * 100)
            self.main_window.ui.progressbar_main.setValue(progress)
        self.main_window.ui.label_file_processing.setText(f"Processing: {filename}")
