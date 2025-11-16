# File: services/xml_service_handlers.py
from PySide6.QtWidgets import QMessageBox
from modules.xml_parser import create_xml_parser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow  # import only for type hints, not at runtime


class ParseXMLFileHandler:
    """
    Service Orchestrator: Manages XML file parsing operations.
    
    This class orchestrates XML parsing by:
    - Creating and configuring XML parser worker threads
    - Managing parsing lifecycle
    - Handling parser signal connections
    
    Architectural Role: Service Orchestrator (not a UI event handler)
    The name "Handler" is maintained for backward compatibility.
    """

    def __init__(self, main_window: "MainWindow", xml_file_path: str):
        self.main_window = main_window
        self.xml_file_path = xml_file_path

    def start_xml_parsing(self) -> None:
        """Parse XML file and display content."""
        try:
            xml_parser = create_xml_parser(self.xml_file_path)
            self.main_window.connect_xml_parsing_signals(xml_parser)
            self.main_window.thread_pool.start(xml_parser)
            # Optional: Keep track of the worker
            self.main_window.active_workers.append(xml_parser)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception on starting to pare xml file", message)
