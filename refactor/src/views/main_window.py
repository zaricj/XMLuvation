# src/views/main_window.py
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtGui import QCloseEvent, QShowEvent, QGuiApplication
from PySide6.QtCore import QSettings, Slot
from assets.ui.XMLuvation_ui import Ui_MainWindow

from src.views.tab_xml_search_view import TabXMLSearchView
from src.views.tab_csv_conversion_view import TabCSVConversionView

class MainWindow(QMainWindow):
    """The root UI window compiling pre-built UI definitions and distributing contexts."""

    def __init__(self) -> None:
        super().__init__()
        self._load_ui_manifest()
        self._mount_sub_views()
        self.setup_initial_widget_states()
        self.settings = QSettings("Jovan", "XMLuvation")

    def _load_ui_manifest(self) -> None:
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setCentralWidget(self.ui.centralwidget)

    def _mount_sub_views(self) -> None:
        self.xml_xpath_tab = TabXMLSearchView(self)
        self.csv_profile_tab = TabCSVConversionView(self)

    def set_global_loading_state(self, is_loading: bool) -> None:
        if hasattr(self.ui, "label_loading_gif"):
            self.ui.label_loading_gif.setVisible(is_loading)
            
    def setup_initial_widget_states(self) -> None:
        """Setup initial visibility and enabled states for widgets."""
        # Hide widgets initially
        self.ui.button_find_next.hide()
        self.ui.button_find_previous.hide()
        self.ui.button_abort_csv_export.hide()
        self.ui.progressbar_main.hide()
        self.ui.label_file_processing.hide()
        self.ui.line_edit_xml_output_find_text.hide()
        
        # Disable widgets initially
        self.ui.button_clear_table.setDisabled(True)
        self.ui.line_edit_filter_table.setDisabled(True)

    # --------------------------------------------------------
    # Window State Lifecycle Hooks (View Responsibility)
    # --------------------------------------------------------
    def showEvent(self, event: QShowEvent) -> None:
        """Triggered right before the window is displayed on screen."""
        super().showEvent(event)
        self._restore_window_state()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Triggered when the user attempts to close the window."""
        self._save_window_state()
        super().closeEvent(event)

    #--------------------------------------------------------
    # Windows state helper methods
    #--------------------------------------------------------

    def _save_window_state(self) -> None:
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

    def _restore_window_state(self) -> None:
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)

        # Clamp window into current screen space (Prevents off-screen ghosting)
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
            
        available = screen.availableGeometry()
        win_geom = self.frameGeometry()

        if not available.contains(win_geom, proper=False):
            self.resize(
                min(win_geom.width(), available.width()),
                min(win_geom.height(), available.height()),
            )
            self.move(
                max(
                    available.left(),
                    min(win_geom.left(), available.right() - self.width()),
                ),
                max(
                    available.top(),
                    min(win_geom.top(), available.bottom() - self.height()),
                ),
            )
            
    #--------------------------------------------------------
    # QMessageBox methods
    #--------------------------------------------------------
    
    @Slot(str, str)
    def show_info_messagebox(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message )

    @Slot(str, str)
    def show_warning_messagebox(self, title: str, message: str) -> None:
        QMessageBox.warning(self, title, message )

    @Slot(str, str)
    def show_error_messagebox(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message )
