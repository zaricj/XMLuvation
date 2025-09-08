from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QMessageBox,
)
from PySide6.QtGui import QIcon, QAction, QCloseEvent
from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    QFile,
    QTextStream,
    QIODevice,
    QSettings,
    QThreadPool,
)

import sys
import os

from resources.ui.XMLuvation_ui import Ui_MainWindow

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Check if the application is running in a PyInstaller bundle
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Running in a PyInstaller bundle, BASE_DIR points to the bundle's root
    ROOT_DIR: str = sys._MEIPASS
else:
    # Running in a normal Python environment
    ROOT_DIR: str = os.path.dirname(CURRENT_DIR)
    # At work it's C:\Users\ZaricJ\Documents\Main\02_Entwicklung_und_Tools\GitHub\XMLuvation\src

# Path Constants
# LOG_FILE_PATH: str = os.path.join(ROOT_DIR, "logs","xmluvation.log")
GUI_CONFIG_FILE_PATH: str = os.path.join(CURRENT_DIR, "config", "config.json")
GUI_CONFIG_DIRECTORY: str = os.path.join(CURRENT_DIR, "config")
DARK_THEME_PATH: str = os.path.join(
    CURRENT_DIR, "resources", "themes", "dark_theme.qss"
)
LIGHT_THEME_PATH: str = os.path.join(
    CURRENT_DIR, "resources", "themes", "light_theme.qss"
)
ICON_PATH: str = os.path.join(CURRENT_DIR, "resources", "icons", "xml_256px.ico")
DARK_THEME_QMENU_ICON: str = os.path.join(
    CURRENT_DIR, "resources", "images", "dark.png"
)
LIGHT_THEME_QMENU_ICON: str = os.path.join(
    CURRENT_DIR, "resources", "images", "light.png"
)

# App related constants
APP_VERSION: str = "v1.2.1"
APP_NAME: str = "XMLuvation"
AUTHOR: str = "Jovan"


class MainWindow(QMainWindow):
    progress_updated = Signal(int)
    update_input_file_signal = Signal(str)
    update_output_file_signal = Signal(str)

    def __init__(self):
        super().__init__()

        # Create and set up the UI
        self.paths_menu = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set window title with a version
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")

        # Initialize all attributes here
        self.initialize_attributes()

        # Setup widgets and visibility states
        self.setup_widgets_and_visibility_states()

        # Create menu bar
        self.create_menu_bar()

        # Initialize the event handler AFTER all attributes are set
        from main_event_handler import UIEventHandler

        self.event_handler = UIEventHandler(self)

    def initialize_attributes(self):
        """Initialize all application attributes"""
        # Import required classes
        from main_state_controller import ComboboxStateHandler
        from main_state_controller import SearchXMLOutputTextHandler
        from modules.config_handler import ConfigHandler

        # XML Data
        self.parsed_xml_data = {}
        self.current_read_xml_file = None
        self.csv_exporter_handler = None

        # Create fixed actions ONCE and store them as instance variables
        self._add_custom_path_action = QAction("Add Custom Path", self)
        # We'll connect this in the event handler

        # Instantiate the controller with a reference to the MainWindow
        self.cb_state_controller = ComboboxStateHandler(
            main_window=self,
            parsed_xml_data=self.parsed_xml_data,
            cb_tag_name=self.ui.combobox_tag_names,
            cb_tag_value=self.ui.combobox_tag_values,
            cb_attr_name=self.ui.combobox_attribute_names,
            cb_attr_value=self.ui.combobox_attribute_values,
        )

        # Instantiate the XML Output search handler
        self.xml_text_searcher = SearchXMLOutputTextHandler(
            main_window=self,
            line_edit_xml_output_find_text=self.ui.line_edit_xml_output_find_text,
            text_edit_xml_output=self.ui.text_edit_xml_output,
        )

        # Settings file for storing application settings
        self.settings = QSettings("Jovan", "XMLuvation")

        # Window geometry restoration
        geometry = self.settings.value("geometry", bytes())
        if geometry:
            self.restoreGeometry(geometry)

        # Recent Xpath expressions settings
        self.recent_xpath_expressions = self.settings.value(
            "recent_xpath_expressions", type=list
        )
        if self.recent_xpath_expressions is None:
            self.recent_xpath_expressions = []

        # Initialize the QThreadPool for running threads
        self.thread_pool = QThreadPool()
        max_threads = (
            self.thread_pool.maxThreadCount()
        )  # PC's max CPU threads (I have 32 Threads on a Ryzen 9 7950X3D)
        self.set_max_threads = max_threads
        self.thread_pool.setMaxThreadCount(max_threads)

        # Keep track of active workers (optional, for cleanup)
        self.active_workers = []
        self.xpath_filters = []
        self.config_handler = ConfigHandler(
            main_window=self,
            config_directory=GUI_CONFIG_DIRECTORY,
            config_file_name=GUI_CONFIG_FILE_PATH,
        )

        # Connect the custom context menu for Listbox
        self.ui.list_widget_xpath_expressions.setContextMenuPolicy(Qt.CustomContextMenu)
        # We'll connect the signal in the event handler

        # Connect the Find action to the default context menu of the XML Output QTextEdit widget
        self.ui.text_edit_xml_output.setContextMenuPolicy(Qt.CustomContextMenu)
        # We'll connect the signal in the event handler

        # Theme Icons in QMenu
        self.light_mode_icon = QIcon(LIGHT_THEME_QMENU_ICON)
        self.dark_mode_icon = QIcon(DARK_THEME_QMENU_ICON)

        # Theme files qss
        self.dark_theme_file = DARK_THEME_PATH
        self.light_theme_file = LIGHT_THEME_PATH

        # Load last used theme or default
        self.current_theme = self.settings.value("app_theme", "dark_theme.qss")

        # Setting for the group matches checkbox
        self.group_matches_setting = self.settings.value(
            "group_matches", self.ui.checkbox_group_matches.isChecked(), type=bool
        )
        if self.group_matches_setting:
            self.ui.checkbox_group_matches.setChecked(self.group_matches_setting)

        # Apply theme and correct icon
        if self.current_theme == "dark_theme.qss":
            self.theme_icon = self.light_mode_icon
            self._initialize_theme(self.dark_theme_file)
        else:
            self.theme_icon = self.dark_mode_icon
            self._initialize_theme(self.light_theme_file)

    def _initialize_theme(self, theme_file):
        """Initialized UI theme files (.qss)

        Args:
            theme_file (str): File path to the .qss theme file
        """
        try:
            file = QFile(theme_file)
            if not file.open(
                QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text
            ):
                return
            else:
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.setStyleSheet(stylesheet)
            file.close()
        except Exception as ex:
            QMessageBox.critical(
                self, "Theme load error", f"Failed to load theme: {str(ex)}"
            )

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        self.recent_xpath_expressions_menu = QMenu("Recent XPath expressions", self)
        self.recent_xpath_expressions_menu.clear()

        for expression in self.recent_xpath_expressions:
            action = QAction(expression, self)
            # We'll connect this in the event handler
            self.recent_xpath_expressions_menu.addAction(action)

        file_menu.addMenu(self.recent_xpath_expressions_menu)

        clear_recent_xpath_expressions_action = QAction(
            "Clear recent XPath expressions", self
        )
        # We'll connect this in the event handler
        file_menu.addAction(clear_recent_xpath_expressions_action)

        file_menu.addSeparator()

        clear_action = QAction("Clear Output", self)
        # We'll connect this in the event handler
        file_menu.addAction(clear_action)
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Open Menu
        open_menu = menu_bar.addMenu("&Open")
        open_input_action = QAction("Open input XML folder in file explorer", self)
        # We'll connect this in the event handler
        open_menu.addAction(open_input_action)
        open_output_action = QAction("Open output CSV folder in file explorer", self)
        # We'll connect this in the event handler
        open_menu.addAction(open_output_action)
        open_menu.addSeparator()
        open_csv_conversion_input_action = QAction(
            "Open CSV conversion input folder in file explorer", self
        )
        # We'll connect this in the event handler
        open_menu.addAction(open_csv_conversion_input_action)

        # Path Menu
        self.paths_menu = menu_bar.addMenu("&Path")

        # Initially populate the menu. This method will now ensure the correct order.
        # We'll call this in the event handler after it's initialized

        # Add an option to add a new custom path
        self.paths_menu.addAction(self._add_custom_path_action)

        # Settings Menu
        settings_menu = menu_bar.addMenu("&Settings")
        open_paths_manager = QAction("Manage Custom Paths", self)
        # We'll connect this in the event handler
        settings_menu.addAction(open_paths_manager)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        xpath_help_action = QAction("XPath Help", self)
        xpath_help_action.setStatusTip("Open XPath Syntax Help")
        # We'll connect this in the event handler
        help_menu.addAction(xpath_help_action)

        # Theme Menu
        self.toggle_theme_action = menu_bar.addAction(self.theme_icon, "Toggle Theme")
        # We'll connect this in the event handler

        # Store menu actions as attributes so the event handler can access them
        self.clear_recent_xpath_expressions_action = (
            clear_recent_xpath_expressions_action
        )
        self.clear_action = clear_action
        self.open_input_action = open_input_action
        self.open_output_action = open_output_action
        self.open_csv_conversion_input_action = open_csv_conversion_input_action
        self.open_paths_manager = open_paths_manager
        self.xpath_help_action = xpath_help_action

    def setup_widgets_and_visibility_states(self):
        """Setup widgets states"""
        # Hide buttons/widgets
        self.ui.button_find_next.setHidden(True)
        self.ui.button_find_previous.setHidden(True)
        self.ui.button_abort_csv_export.setHidden(True)
        self.ui.label_file_processing.setHidden(True)
        self.ui.line_edit_xml_output_find_text.setHidden(True)

    # ====================================================================================================================== #

    # === SIGNAL CONNECTION HELPERS === #
    def _connect_xml_parsing_signals(self, worker):
        """Connect common signals for most operations."""
        worker.signals.finished.connect(self.on_xmlParsingFinished)
        worker.signals.error_occurred.connect(self.on_errorMessage)
        worker.signals.program_output_progress.connect(self.append_toProgramOutput)

    def _connect_xpath_builder_signals(self, worker):
        """Connect signals for XPath building operations."""
        worker.signals.program_output_progress.connect(self.append_toProgramOutput)
        worker.signals.error_occurred.connect(self.on_errorMessage)
        worker.signals.warning_occurred.connect(self.on_warningMessage)

    def _connect_csv_export_signals(self, worker):
        """Connect signals for CSV export operations."""
        worker.signals.finished.connect(self.on_CSVExportFinished)
        worker.signals.error_occurred.connect(self.on_errorMessage)
        worker.signals.info_occurred.connect(self.on_infoMessage)
        worker.signals.warning_occurred.connect(self.on_warningMessage)
        worker.signals.program_output_progress_append.connect(
            self.append_toProgramOutput
        )
        worker.signals.program_output_progress_set_text.connect(
            self.set_textToProgramOutput
        )
        worker.signals.file_processing_progress.connect(self.on_fileProcessing)
        worker.signals.progressbar_update.connect(self.update_ProgressBar)
        worker.signals.visible_state_widget.connect(self.on_CSVExportStarted)

    def _connect_file_cleanup_signals(self, worker):
        worker.signals.error_occurred.connect(self.on_errorMessage)
        worker.signals.warning_occurred.connect(self.on_warningMessage)
        worker.signals.program_output_progress_append.connect(
            self.append_ToProgramOutputCSVTab
        )
        worker.signals.program_output_progress_set_text.connect(
            self.set_TextToProgramOutputCSVTab
        )
        worker.signals.column_dropped_successfully.connect(
            self.on_columnDroppedSuccessfully
        )

    def _connect_csv_conversion_signals(self, worker):
        """Connect signals for CSV conversion operations."""
        worker.signals.error_occurred.connect(self.on_errorMessage)
        worker.signals.info_occurred.connect(self.on_infoMessage)
        worker.signals.warning_occurred.connect(self.on_warningMessage)

    # === EVENT HANDLERS FOR QMessageBoxes === #
    @Slot(str, str)  # QMessageBox.critical type shit
    def on_errorMessage(self, title, message):
        """Show critical message dialog."""
        QMessageBox.critical(self, title, message)

    @Slot(str, str)  # QMessageBox.information type shit
    def on_infoMessage(self, title, message):
        """Show information message dialog."""
        QMessageBox.information(self, title, message)

    @Slot(str, str)  # QMessageBox.warning type shit
    def on_warningMessage(self, title, message):
        """Show warning message dialog."""
        QMessageBox.warning(self, title, message)

    # === EVENT HANDLER FOR QTextEdit MAIN PROGRAM OUTPUT === #
    @Slot(str)
    def append_toProgramOutput(self, message: str):
        """Handle QTextEdit progress updates with .append() in any class, does the QTextEdit.append("hello world").

        Args:
            message (str): Message to send to the QTextEdit Widget
        """
        self.ui.text_edit_program_output.append(message)

    @Slot(str)
    def set_textToProgramOutput(self, message: str):
        """Handle QTextEdit progress updates with .setText() in any class, does the QTextEdit.setText("hello world")

        Args:
            message (str): Message to send to the QTextEdit Widget
        """
        self.ui.text_edit_program_output.setText(message)

    @Slot(str)
    def append_ToProgramOutputCSVTab(self, message: str):
        """Handle QTextEdit progress updates with .append() in any class, does the QTextEdit.append("hello world").

        Args:
            message (str): Message to send to the QTextEdit Widget
        """
        self.ui.text_edit_csv_conversion_tab_program_output.append(message)

    @Slot(str)
    def set_TextToProgramOutputCSVTab(self, message: str):
        """Handle QTextEdit progress updates with .setText() in any class, does the QTextEdit.setText("hello world")

        Args:
            message (str): Message to send to the QTextEdit Widget
        """
        self.ui.text_edit_csv_conversion_tab_program_output.setText(message)

    @Slot(str)
    def on_columnDroppedSuccessfully(self, index: int):
        """Handle the QComboBox on CSV Header drop

        Args:
            column (str): Current selected text of the QComboBox widget for the CSV header
        """
        # Delete the current dropped column from the csv headers combobox in the 2nd UI tab
        self.ui.combobox_csv_headers.removeItem(index)

    # === XML PARSING ON FINISHED SLOT === #
    @Slot(dict)
    def on_xmlParsingFinished(self, result: dict):
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
            self.current_read_xml_file = result.get("file_path")

            self.ui.text_edit_program_output.append(info_message)

            self.parsed_xml_data = result
            # Pass the new result data (the XML data as dict) to the ComboBoxStateController class
            self.cb_state_controller.set_parsed_data(result)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self, "Error processing parsing results", message)

    @Slot(bool)
    def on_CSVExportStarted(self, state: bool):
        self.ui.button_abort_csv_export.setVisible(state)
        self.ui.label_file_processing.setVisible(state)
        self.event_handler.set_ui_widgets_disabled(state=True)

    @Slot()
    def on_CSVExportFinished(self):
        self.ui.button_abort_csv_export.setVisible(False)
        self.ui.label_file_processing.setVisible(False)
        self.event_handler.set_ui_widgets_disabled(state=False)
        self.ui.progressbar_main.reset()

    @Slot(str)
    def on_fileProcessing(self, message: str):
        """Handle QLabel progress updates for file processing."""
        self.ui.label_file_processing.setText(message)

    @Slot(int)
    def update_ProgressBar(self, progress: int):
        self.ui.progressbar_main.setValue(progress)

    def get_thread_pool_status(self) -> str:
        """Get current thread pool status (useful for debugging).

        Returns:
            str: Active threads: {active_count}/{max_count}
        """
        active_count = self.thread_pool.activeThreadCount()
        max_count = self.thread_pool.maxThreadCount()
        return f"Active threads: {active_count}/{max_count}"

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self,
            "Exit Program",
            "Are you sure you want to exit the program?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.No:
            event.ignore()
            return
        else:
            self.settings.setValue("app_theme", self.current_theme)
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue(
                "group_matches", self.ui.checkbox_group_matches.isChecked()
            )
            super().closeEvent(event)


if __name__ == "__main__":
    # Initialize the application
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
