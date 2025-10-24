# services/csv_export_service.py
"""
CSVExportService - Pure business logic for CSV export.
No UI dependencies.
"""
from typing import Dict, Any
from modules.xpath_search_and_csv_export import create_xpath_searcher_and_csv_exporter


class CSVExportService:
    """Service for CSV export operations - pure business logic, no UI."""
    
    def __init__(self):
        pass
    
    def create_export_worker(self, config: Dict[str, Any]):
        """Create a worker thread for CSV export.
        
        Args:
            config: Configuration dictionary with export settings
            
        Returns:
            Worker thread for CSV export
        """
        return create_xpath_searcher_and_csv_exporter(
            xml_folder_path=config.get('xml_folder_path'),
            csv_file_path=config.get('csv_file_path'),
            xpath_filters=config.get('xpath_filters', []),
            csv_headers=config.get('csv_headers', []),
            group_matches=config.get('group_matches', False)
        )
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """Validate CSV export configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not config.get('xml_folder_path'):
            return False, "XML folder path is required"
        if not config.get('csv_file_path'):
            return False, "CSV output path is required"
        if not config.get('xpath_filters'):
            return False, "At least one XPath filter is required"
        return True, ""
