# File: controllers/signal_handlers.py
"""
Refactored signal handler mixin that delegates to specialized handler classes.
This provides a backward-compatible interface while separating concerns.
"""
from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon, QMovie
from PySide6.QtCore import Slot
from typing import List, TYPE_CHECKING

from gui.main.XMLuvation_ui import Ui_MainWindow

if TYPE_CHECKING:
    from PySide6.QtCore import QSettings
    from controllers.modules_controller import ComboboxStateHandler, SearchXMLOutputTextHandler
    from handlers.config_handler import ConfigHandler
    from main import MainWindow
    from services.ui_state_manager import UIStateManager
    from utils.helper_methods import HelperMethods


class SignalHandlerMixin:
    """
    Mixin class that provides signal handling interface using specialized handlers.
    Delegates responsibilities to focused handler classes for better separation of concerns.
    """
    # Type hints for attributes accessed in this mixin
    ui: Ui_MainWindow
    recent_xpath_expressions: List[str]
    settings: 'QSettings'
    cb_state_controller: 'ComboboxStateHandler'
    set_max_threads: int
    current_theme: str
    config_handler: 'ConfigHandler'
    theme_icon: QIcon
    xml_text_searcher: 'SearchXMLOutputTextHandler'
    _main_thread_loading_movie_ref: QMovie | None = None
    helper: 'HelperMethods'
    ui_state_manager: 'UIStateManager'  # UI state management service
    
    def initialize_handlers(self):
        """Initialize all specialized event handlers."""
        from handlers.menu_action_handler import MenuActionHandler
        from handlers.button_event_handler import ButtonEventHandler
        from handlers.widget_event_handler import WidgetEventHandler
        from handlers.context_menu_handler import ContextMenuHandler
        from handlers.keyboard_shortcut_handler import KeyboardShortcutHandler
        from controllers.signal_connector import SignalConnector
        
        self.menu_handler = MenuActionHandler(self)
        self.button_handler = ButtonEventHandler(self)
        self.widget_handler = WidgetEventHandler(self)
        self.context_menu_handler = ContextMenuHandler(self)
        self.keyboard_handler = KeyboardShortcutHandler(self)
        self.signal_connector = SignalConnector(self)
        
    def connect_menu_bar_actions(self):
        """Connect all menu bar actions to their handlers."""
        self.menu_handler.connect_signals()

    def connect_ui_events(self):
        """Connect all UI element events to their handlers."""
        self.button_handler.connect_signals()
        self.widget_handler.connect_signals()
        self.context_menu_handler.connect_signals()
        self.keyboard_handler.connect_signals()
    
    # Signal connection methods for workers (delegated to SignalConnector)
    def connect_xml_parsing_signals(self, worker):
        """Connect signals for XML parsing operations."""
        self.signal_connector.connect_xml_parsing_signals(worker)
    
    def connect_xpath_builder_signals(self, worker):
        """Connect signals for XPath building operations."""
        self.signal_connector.connect_xpath_builder_signals(worker)
    
    def connect_csv_export_signals(self, worker):
        """Connect signals for CSV export operations."""
        self.signal_connector.connect_csv_export_signals(worker)
    
    def connect_file_cleanup_signals(self, worker):
        """Connect signals for file cleanup operations."""
        self.signal_connector.connect_file_cleanup_signals(worker)
    
    def connect_csv_conversion_signals(self, worker):
        """Connect signals for CSV conversion operations."""
        self.signal_connector.connect_csv_conversion_signals(worker)
    
    # Helper methods for UI state management (delegated to UIStateManager)
    def _set_ui_widgets_disabled(self, state: bool):
        """Helper to disable/enable UI widgets during operations."""
        self.ui_state_manager.set_main_widgets_disabled(state)
    
    def _set_ui_widgets_table_disabled(self, state: bool):
        """Helper to disable/enable table widgets."""
        self.ui_state_manager.set_table_widgets_disabled(state)
    
    # ============= SLOT METHODS FOR WORKER SIGNALS =============
    
    # === Message Box Slots ===
    @Slot(str, str)
    def handle_critical_message(self, title: str, message: str):
        """Show critical message dialog."""
        QMessageBox.critical(self, title, message)

    @Slot(str, str)
    def handle_info_message(self, title: str, message: str):
        """Show information message dialog."""
        QMessageBox.information(self, title, message)

    @Slot(str, str)
    def handle_warning_message(self, title: str, message: str):
        """Show warning message dialog."""
        QMessageBox.warning(self, title, message)

    # === Progress and Output Slots ===
    @Slot(int)
    def handle_progress_bar_update(self, progress: int):
        """Handle progress bar updates."""
        self.ui.progressbar_main.setValue(progress)

    @Slot(str)
    def handle_program_output_append(self, message: str):
        """Handle QTextEdit progress updates with append."""
        self.ui.text_edit_program_output.append(message)

    @Slot(str)
    def handle_program_output_set_text(self, message: str):
        """Handle QTextEdit progress updates with setText."""
        self.ui.text_edit_program_output.setText(message)

    @Slot(str)
    def handle_csv_tab_output_append(self, message: str):
        """Handle CSV tab QTextEdit progress updates with append."""
        self.ui.text_edit_csv_output.append(message)

    @Slot(str)
    def handle_csv_tab_output_set_text(self, message: str):
        """Handle CSV tab QTextEdit progress updates with setText."""
        self.ui.text_edit_csv_output.setText(message)
        
    @Slot(str)
    def handler_set_converted_file_path(self, file_path: str):
        """Set the file path of the converted file in the "Open File" QLineEdit."""
        self.ui.line_edit_csv_conversion_open_file_path.setText(file_path)
        
    @Slot()
    def handle_start_loading_gif(self):
        """Handle starting the loading GIF - creates QMovie on main thread."""
        try:
            root = Path(__file__).parent.parent
            gif = root / "gui" / "resources" / "gifs" / "loading_circle_small.gif"
            
            # Create QMovie on the MAIN thread
            movie = QMovie(str(gif))
            
            if not movie.isValid():
                QMessageBox.warning(self, "GIF Not Found", f"GIF file not found or invalid: {gif}")
                return
                
            self._main_thread_loading_movie_ref = movie
            self.ui.label_loading_gif.setMovie(movie)
            movie.start()
            self.ui.label_loading_gif.setVisible(True)
        except Exception as e:
            QMessageBox.critical(self, "GIF Error", f"Error loading GIF: {e}")
            return
            
    @Slot()
    def handle_stop_loading_gif(self):
        """Handle stopping the loading GIF."""
        movie = self._main_thread_loading_movie_ref
        if movie:
            movie.stop()
            movie.deleteLater()  # Clean up the QMovie object
            self._main_thread_loading_movie_ref = None
        self.ui.label_loading_gif.clear()
        self.ui.label_loading_gif.setVisible(False)

    @Slot(str)
    def handle_file_processing_label(self, message: str):
        """Handle QLabel progress updates for file processing."""
        self.ui.label_file_processing.setText(message)

    # === Specific Feature Slots ===
    @Slot(int)
    def handle_csv_column_dropped(self, index: int):
        """Handle CSV column drop completion."""
        self.ui.combobox_csv_headers.removeItem(index)

    @Slot(dict)
    def handle_xml_parsing_finished(self, result: dict):
        """Handle XML parsing completion."""
        try:
            from modules.xml_parser import set_xml_content_to_widget

            xml_content = result.get("xml_string", "")
            # Add highlighter for XML files then add to QTextEdit
            set_xml_content_to_widget(self.ui.text_edit_xml_output, xml_content)
            self.ui.text_edit_xml_output.setPlainText(xml_content)

            # Fill the combo boxes with unique tags and attributes
            tags = result.get("tags", [])
            attributes = result.get("attributes", [])
            tag_values = result.get("tag_values", [])
            attribute_values = result.get("attribute_values", [])

            self.ui.combobox_tag_names.clear()
            self.ui.combobox_tag_names.addItems(tags)
            self.ui.combobox_attribute_names.clear()
            self.ui.combobox_attribute_names.addItems(attributes)

            self.ui.combobox_tag_values.clear()
            self.ui.combobox_tag_values.addItems(tag_values)
            self.ui.combobox_attribute_values.clear()
            self.ui.combobox_attribute_values.addItems(attribute_values)

            # Enable ComboBoxes
            self.ui.combobox_tag_names.setDisabled(False)
            self.ui.combobox_attribute_names.setDisabled(False)
            self.ui.combobox_tag_values.setDisabled(False)
            self.ui.combobox_attribute_values.setDisabled(False)

            # Display additional info
            info_message = f"File: {result.get('file_path', 'Unknown')}\n"
            info_message += f"Root element: {result.get('root_tag', 'Unknown')}\n"
            info_message += f"Total elements: {result.get('element_count', 0)}\n"
            info_message += f"Unique tags: {len(result.get('tags', []))}\n"
            info_message += f"Encoding: {result.get('encoding', 'Unknown')}"

            # Save XML file in initialized variable
            self._current_read_xml_file_ref = result.get("file_path")
            self.ui.text_edit_program_output.append(info_message)

            self._parsed_xml_data_ref = result
            # Pass the new result data to the ComboBoxStateController
            self.cb_state_controller.set_parsed_data(result)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Error processing parsing results", message)

    @Slot(str)
    def handle_visible_state_widget(self):
        """Handle CSV export start."""
        self.ui_state_manager.set_csv_export_widgets_state(exporting=True)

    @Slot(str)
    def handle_csv_export_finished(self):
        """Handle CSV export completion."""
        self.ui_state_manager.set_csv_export_widgets_state(exporting=False)

