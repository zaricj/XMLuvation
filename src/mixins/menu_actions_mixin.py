import webbrowser
import os

from PySide6.QtWidgets import QMessageBox, QTextEdit
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING
from utils.ui_helpers import HelperMethods

if TYPE_CHECKING:
    from main import MainWindow

class MenuActionsMixin:
    """Handles menu bar actions only"""
    helper = HelperMethods()
    def connect_menu_bar_actions(self: "MainWindow"):
        """Connect all menu bar actions to their handlers."""
        # Add theme action to Menu Bar at the far right
        self.toggle_theme_action = self.ui.menu_bar.addAction(self.theme_icon, "Toggle Theme")
        self.ui.exit_action.triggered.connect(self.close)
        self.ui.clear_recent_xpath_expressions_action.triggered.connect(self.on_clearRecentXpathExpressions)
        self.ui.open_input_action.triggered.connect(self.on_openInputDirectory)
        self.ui.open_output_action.triggered.connect(self.on_openOutputDirectory)
        self.ui.open_csv_conversion_input_action.triggered.connect(self.on_openCSVConversionInputDirectory)
        self.ui.open_paths_manager.triggered.connect(self.on_openPathsManager)
        self.ui.open_pre_built_xpaths_manager_action.triggered.connect(self.on_openPrebuiltXPathsManager)
        self.ui.xpath_help_action.triggered.connect(self.on_xpathHelp)
        self.ui.prompt_on_exit_action.checkableChanged.connect(self.on_PromptOnExitChecked)
        self.toggle_theme_action.triggered.connect(self.on_changeTheme)

        # Connect recent xpath expressions menu
        for action in self.ui.recent_xpath_expressions_menu.actions():
            action.triggered.connect(
                lambda checked, exp=action.text(): self.on_setXPathExpressionInInput(exp)
            )
            
    @Slot()
    def on_clearRecentXpathExpressions(self: "MainWindow"):
        """Clear recent XPath expressions."""
        reply = QMessageBox.question(
            self,
            "Clear recent XPath expressions",
            "Are you sure you want to clear the list of recent XPath expressions?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.settings.remove("recent_xpath_expressions")
            self.recent_xpath_expressions = []
            self._update_recent_xpath_expressions_menu()

    @Slot()
    def on_clearOutput(self: "MainWindow", text_edit: QTextEdit):
        """Clear selected output text edit."""
        text_edit.clear()

    @Slot()
    def on_openInputDirectory(self: "MainWindow"):
        """Open input XML folder in file explorer."""
        directory = self.ui.line_edit_xml_folder_path_input.text()
        self._open_folder_in_file_explorer(directory)

    @Slot()
    def on_openOutputDirectory(self: "MainWindow"):
        """Open output CSV folder in file explorer."""
        directory = os.path.dirname(self.ui.line_edit_csv_output_path.text()) if self.ui.line_edit_csv_output_path.text() else ""
        self._open_folder_in_file_explorer(directory)

    @Slot()
    def on_openCSVConversionInputDirectory(self: "MainWindow"):
        """Open CSV conversion input folder in file explorer."""
        directory = os.path.dirname(self.ui.line_edit_csv_conversion_path_input.text()) if self.ui.line_edit_csv_conversion_path_input.text() else ""
        self._open_folder_in_file_explorer(directory)

    @Slot() # Opens Pre-built XPaths Manager QWidget
    def on_openPrebuiltXPathsManager(self):
        from ui.widgets.custom.modules.pre_built_xpaths_manager import PreBuiltXPathsManager
        self.w = PreBuiltXPathsManager(main_window=self)
        self.w.show()

    @Slot() # Opens Paths Manager QWidget
    def on_openPathsManager(self):
        """Open paths manager window."""
        from ui.widgets.custom.modules.path_manager import CustomPathsManager
        self.w = CustomPathsManager(main_window=self)
        self.w.show()

    @Slot()
    def on_xpathHelp(self):
        """Open XPath help webpage."""
        webbrowser.open("https://www.w3schools.com/xml/xpath_syntax.asp")

    @Slot()
    def on_changeTheme(self: "MainWindow"):
        """Toggle application theme."""
        if self.current_theme == "dark_theme.qss":
            self.toggle_theme_action.setIcon(self.dark_mode_icon)
            self._initialize_theme_file(self.light_theme_file)
            self.current_theme = "light_theme.qss"
        else:
            self.toggle_theme_action.setIcon(self.light_mode_icon)
            self._initialize_theme_file(self.dark_theme_file)
            self.current_theme = "dark_theme.qss"
            
    @Slot()
    def on_PromptOnExitChecked(self: "MainWindow"):
        """Handle prompt on exit checkbox toggle."""
        is_checked = self.ui.prompt_on_exit_action.isChecked()
        self.settings.setValue("prompt_on_exit", is_checked)