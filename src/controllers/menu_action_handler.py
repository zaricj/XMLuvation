# File: controllers/menu_action_handler.py
"""Handler for menu bar action events."""
import webbrowser
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


class MenuActionHandler:
    """Handles all menu bar action events."""
    
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window
        
    def connect_signals(self):
        """Connect all menu bar actions to their handlers."""
        ui = self.main_window.ui
        
        # File menu actions
        ui.exit_action.triggered.connect(self.main_window.close)
        ui.open_input_action.triggered.connect(self.on_open_input_directory)
        ui.open_output_action.triggered.connect(self.on_open_output_directory)
        ui.open_csv_conversion_input_action.triggered.connect(self.on_open_csv_conversion_input_directory)
        
        # Tools menu actions
        ui.open_paths_manager.triggered.connect(self.on_open_paths_manager)
        ui.open_pre_built_xpaths_manager_action.triggered.connect(self.on_open_prebuilt_xpaths_manager)
        ui.clear_recent_xpath_expressions_action.triggered.connect(self.on_clear_recent_xpath_expressions)
        
        # Help menu actions
        ui.xpath_help_action.triggered.connect(self.on_xpath_help)
        
        # Settings menu actions
        ui.prompt_on_exit_action.checkableChanged.connect(self.on_prompt_on_exit_checked)
        
        # Theme toggle action
        self.main_window.toggle_theme_action.triggered.connect(self.on_change_theme)
        
        # Connect recent xpath expressions menu
        for action in ui.recent_xpath_expressions_menu.actions():
            action.triggered.connect(
                lambda checked, exp=action.text(): self.on_set_xpath_expression_in_input(exp)
            )
    
    # === Menu Action Handlers ===
    
    @Slot()
    def on_clear_recent_xpath_expressions(self):
        """Clear recent XPath expressions."""
        reply = QMessageBox.question(
            self.main_window,
            "Clear Recent XPath Expressions?",
            "Are you sure you want to clear all recent XPath expressions?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.main_window.recent_xpath_expressions = []
            self.main_window.settings.setValue("recent_xpath_expressions", [])
            self.main_window._update_recent_xpath_expressions_menu()
            self.main_window.ui.text_edit_program_output.setText(
                "Cleared recent XPath expressions."
            )
    
    @Slot()
    def on_open_input_directory(self):
        """Open input directory in file explorer."""
        folder_path = self.main_window.ui.line_edit_xml_folder_path_input.text()
        self.main_window._open_folder_in_file_explorer(folder_path)
    
    @Slot()
    def on_open_output_directory(self):
        """Open output directory in file explorer."""
        csv_path = self.main_window.ui.line_edit_csv_output_path.text()
        if csv_path:
            import os
            folder_path = os.path.dirname(csv_path)
            self.main_window._open_folder_in_file_explorer(folder_path)
        else:
            QMessageBox.warning(
                self.main_window,
                "No Output Path",
                "No CSV output path has been set."
            )
    
    @Slot()
    def on_open_csv_conversion_input_directory(self):
        """Open CSV conversion input directory in file explorer."""
        csv_path = self.main_window.ui.line_edit_csv_conversion_path_input.text()
        if csv_path:
            import os
            folder_path = os.path.dirname(csv_path)
            self.main_window._open_folder_in_file_explorer(folder_path)
        else:
            QMessageBox.warning(
                self.main_window,
                "No Input Path",
                "No CSV conversion input path has been set."
            )
    
    @Slot()
    def on_open_paths_manager(self):
        """Open paths manager window."""
        from gui.widgets.modules.path_manager import CustomPathsManager
        self.w = CustomPathsManager(main_window=self.main_window)
        self.w.show()
    
    @Slot()
    def on_open_prebuilt_xpaths_manager(self):
        """Open prebuilt XPaths manager window."""
        from gui.widgets.modules.pre_built_xpaths_manager import PreBuiltXPathsManager
        self.w = PreBuiltXPathsManager(main_window=self.main_window)
        self.w.show()
    
    @Slot()
    def on_xpath_help(self):
        """Open XPath help webpage."""
        webbrowser.open("https://www.w3schools.com/xml/xpath_syntax.asp")
    
    @Slot()
    def on_change_theme(self):
        """Toggle application theme."""
        if self.main_window.current_theme == "dark_theme.qss":
            self.main_window.toggle_theme_action.setIcon(self.main_window.dark_mode_icon)
            self.main_window._initialize_theme_file(self.main_window.light_theme_file)
            self.main_window.current_theme = "light_theme.qss"
        else:
            self.main_window.toggle_theme_action.setIcon(self.main_window.light_mode_icon)
            self.main_window._initialize_theme_file(self.main_window.dark_theme_file)
            self.main_window.current_theme = "dark_theme.qss"
    
    @Slot()
    def on_prompt_on_exit_checked(self):
        """Handle prompt on exit checkbox toggle."""
        is_checked = self.main_window.ui.prompt_on_exit_action.isChecked()
        self.main_window.settings.setValue("prompt_on_exit", is_checked)
    
    @Slot(str)
    def on_set_xpath_expression_in_input(self, expression: str):
        """Set XPath expression in input field."""
        self.main_window.ui.line_edit_xpath_builder.setText(expression)
