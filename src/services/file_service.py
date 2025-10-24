# services/file_service.py
"""
FileService - Pure business logic for file operations.
No UI dependencies.
"""
import os
from pathlib import Path
from typing import Optional


class FileService:
    """Service for file operations - pure business logic, no UI."""
    
    def __init__(self):
        pass
    
    def validate_xml_folder(self, folder_path: str) -> tuple[bool, str]:
        """Validate that a folder exists and contains XML files.
        
        Args:
            folder_path: Path to folder
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not folder_path:
            return False, "Folder path is empty"
        
        if not os.path.exists(folder_path):
            return False, f"Folder does not exist: {folder_path}"
        
        if not os.path.isdir(folder_path):
            return False, f"Path is not a directory: {folder_path}"
        
        xml_files = [f for f in os.listdir(folder_path) if f.endswith('.xml')]
        if not xml_files:
            return False, "No XML files found in folder"
        
        return True, f"Found {len(xml_files)} XML file(s)"
    
    def validate_xml_file(self, file_path: str) -> tuple[bool, str]:
        """Validate that a file exists and is an XML file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not file_path:
            return False, "File path is empty"
        
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
        
        if not file_path.endswith('.xml'):
            return False, "File is not an XML file"
        
        return True, "Valid XML file"
    
    def ensure_directory_exists(self, file_path: str) -> bool:
        """Ensure that the directory for a file path exists.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if directory exists or was created
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            return True
        except Exception:
            return False
