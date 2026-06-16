# src/views/main_window.py
from PySide6.QtWidgets import QMainWindow
from src.views.XMLuvation_ui import Ui_MainWindow

from src.views.xml_xpath_view import XmlXpathView
from src.views.csv_profile_view import CsvProfileView

class MainWindow(QMainWindow):
    """The root UI window compiling pre-built UI definitions and distributing contexts."""
    def __init__(self) -> None:
        super().__init__()
        self._load_ui_manifest()
        self._mount_sub_views()

    def _load_ui_manifest(self) -> None:
        self.ui = Ui_MainWindow()
        # setupUi mounts all designer widgets directly onto this MainWindow instance (self)
        self.ui.setupUi(self)
        
        # FIX: Central widget must be a QWidget instance from the ui container
        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("XMLuvation Suite")

    def _mount_sub_views(self) -> None:
        """
        Passes the parent window context (self) downward so sub-views can
        natively look up auto-compiled widgets attached to the main class.
        """
        # Pass 'self' as the window context mapping provider
        self.xml_xpath_tab = XmlXpathView(self) 
        self.csv_profile_tab = CsvProfileView(self)

    def set_global_loading_state(self, is_loading: bool) -> None:
        """Centralized control of global animations or status indicators."""
        if hasattr(self.ui, 'label_loading_gif'):
            self.ui.label_loading_gif.setVisible(is_loading)
        
        # Safely updates the native status bar widget managed by the compiled ui
        self.ui.text_edit_program_output.showMessage("Processing Active Task..." if is_loading else "Ready")