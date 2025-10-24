# controllers/ui_controller.py
"""
UIController - Handles general UI state changes and coordination.
No business logic, only UI updates and state management.
"""
from typing import TYPE_CHECKING
from PySide6.QtCore import QFile, QIODevice, QTextStream
from PySide6.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class UIController:
    """Controller for general UI operations - UI coordination only, no business logic."""
    
    def __init__(self, main_window: 'MainWindow'):
        """Initialize UIController.
        
        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
    
    def toggle_theme(self):
        """Toggle between dark and light theme."""
        if self.main_window.current_theme == "dark_theme.qss":
            self._apply_theme(self.main_window.light_theme_file, "light_theme.qss")
            self.main_window.theme_icon = self.main_window.dark_mode_icon
        else:
            self._apply_theme(self.main_window.dark_theme_file, "dark_theme.qss")
            self.main_window.theme_icon = self.main_window.light_mode_icon
        
        # Save setting
        self.main_window.settings.setValue("app_theme", self.main_window.current_theme)
    
    def _apply_theme(self, theme_file: str, theme_name: str):
        """Apply a theme from file.
        
        Args:
            theme_file: Path to theme file
            theme_name: Name of theme for settings
        """
        try:
            file = QFile(theme_file)
            if file.open(QIODevice.ReadOnly | QIODevice.Text):
                stream = QTextStream(file)
                stylesheet = stream.readAll()
                self.main_window.setStyleSheet(stylesheet)
                file.close()
                self.main_window.current_theme = theme_name
        except Exception as ex:
            QMessageBox.critical(
                self.main_window,
                "Theme Error",
                f"Failed to load theme: {str(ex)}"
            )
    
    def clear_output(self, output_widget=None):
        """Clear output text widget.
        
        Args:
            output_widget: Widget to clear, defaults to program output
        """
        if output_widget is None:
            output_widget = self.main_window.ui.text_edit_program_output
        output_widget.clear()
    
    def show_progress(self, show: bool = True):
        """Show or hide progress indicators.
        
        Args:
            show: True to show, False to hide
        """
        if show:
            self.main_window.ui.progressbar_main.show()
            self.main_window.ui.label_file_processing.show()
        else:
            self.main_window.ui.progressbar_main.hide()
            self.main_window.ui.label_file_processing.hide()
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update progress bar and label.
        
        Args:
            current: Current progress value
            total: Total value
            message: Progress message
        """
        if total > 0:
            progress = int((current / total) * 100)
            self.main_window.ui.progressbar_main.setValue(progress)
        if message:
            self.main_window.ui.label_file_processing.setText(message)
    
    def enable_controls(self, enabled: bool = True):
        """Enable or disable main controls.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.main_window.ui.button_start_csv_export.setEnabled(enabled)
        self.main_window.ui.button_read_xml.setEnabled(enabled)
        self.main_window.ui.button_browse_xml_folder.setEnabled(enabled)
    
    def show_info(self, title: str, message: str):
        """Show information message box.
        
        Args:
            title: Dialog title
            message: Dialog message
        """
        QMessageBox.information(self.main_window, title, message)
    
    def show_warning(self, title: str, message: str):
        """Show warning message box.
        
        Args:
            title: Dialog title
            message: Dialog message
        """
        QMessageBox.warning(self.main_window, title, message)
    
    def show_error(self, title: str, message: str):
        """Show error message box.
        
        Args:
            title: Dialog title
            message: Dialog message
        """
        QMessageBox.critical(self.main_window, title, message)
