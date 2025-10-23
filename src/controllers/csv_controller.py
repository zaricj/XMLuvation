from PySide6.QtWidgets import QFileDialog
from services.csv_export_service import CSVExportService
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from main import MainWindow

class CSVController:
    """Handles all CSV-related operations"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.csv_service = CSVExportService()
        self.current_exporter = None
    
    def browse_csv_output(self):
        """Handle CSV output file browsing"""
        filename = f"Evaluation_{datetime.datetime.now().strftime('%Y.%m.%d_%H%M')}.csv"
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save as",
            filename,
            "CSV File (*.csv)"
        )
        if file_path:
            self.main_window.ui.line_edit_csv_output_path.setText(file_path)
    
    def start_csv_export(self):
        """Start CSV export process"""
        config = self._get_export_config()
        worker = self.csv_service.create_export_worker(config)
        self.connect_worker_signals(worker)
        self.main_window.thread_pool.start(worker)
        self.current_exporter = worker
    
    def stop_csv_export(self):
        """Stop running CSV export"""
        if self.current_exporter:
            self.current_exporter.stop()
            self.current_exporter = None