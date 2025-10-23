from services.xml_parser_service import XMLParserService

class XMLController:
    """Handles all XML-related operations"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.xml_service = XMLParserService()
        self.current_xml_file = None
        self.parsed_data = {}
    
    def browse_xml_folder(self):
        """Handle XML folder browsing"""
        folder = QFileDialog.getExistingDirectory(
            self.main_window, 
            "Select directory that contains XML files"
        )
        if folder:
            self.main_window.ui.line_edit_xml_folder_path_input.setText(folder)
            self._update_file_count(folder)
    
    def read_xml_file(self):
        """Handle XML file reading"""
        file_name, _ = QFileDialog.getOpenFileName(
            self.main_window, 
            "Select XML File", 
            "", 
            "XML File (*.xml)"
        )
        if file_name:
            self.parse_xml_file(file_name)
    
    def parse_xml_file(self, file_path: str):
        """Parse XML file using worker thread"""
        worker = self.xml_service.create_parser_worker(file_path)
        self._connect_parser_signals(worker)
        self.main_window.thread_pool.start(worker)
    
    def _update_file_count(self, folder: str):
        """Update XML file count in status bar"""
        try:
            count = sum(1 for f in os.listdir(folder) if f.endswith(".xml"))
            self.main_window.ui.statusbar_xml_files_count.setText(
                f"Found {count} XML Files"
            )
        except Exception as e:
            self.main_window.ui.statusbar_xml_files_count.setText(
                f"Error counting XML files: {e}"
            )

