# services/xml_parser_service.py
"""
XMLParserService - Pure business logic for XML parsing.
No UI dependencies.
"""
from typing import Any, Dict
from modules.xml_parser import create_xml_parser


class XMLParserService:
    """Service for XML parsing operations - pure business logic, no UI."""
    
    def __init__(self):
        pass
    
    def create_parser_worker(self, file_path: str):
        """Create a worker thread for parsing XML.
        
        Args:
            file_path: Path to XML file to parse
            
        Returns:
            Worker thread for XML parsing
        """
        return create_xml_parser(file_path)
    
    def count_xml_files(self, folder_path: str) -> int:
        """Count XML files in a folder.
        
        Args:
            folder_path: Path to folder
            
        Returns:
            Number of XML files found
        """
        import os
        try:
            return sum(1 for f in os.listdir(folder_path) if f.endswith(".xml"))
        except Exception:
            return 0

