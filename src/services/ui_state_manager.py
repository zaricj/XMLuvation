# File: services/ui_state_manager.py
"""Service for managing UI state and widget states."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


class UIStateManager:
    """
    Manages UI widget states (enabled/disabled, visible/hidden).
    Centralizes UI state management logic for better separation of concerns.
    """
    
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window
        self.ui = main_window.ui
    
    def setup_initial_widget_states(self):
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
    
    def set_csv_export_widgets_state(self, exporting: bool):
        """
        Set widget states during CSV export operation.
        
        Args:
            exporting: True when export is in progress, False when complete
        """
        if exporting:
            # Show progress widgets
            self.ui.button_start_csv_export.hide()
            self.ui.button_abort_csv_export.show()
            self.ui.progressbar_main.show()
            self.ui.label_file_processing.show()
            
            # Disable input widgets
            self.set_main_widgets_disabled(True)
        else:
            # Hide progress widgets
            self.ui.button_start_csv_export.show()
            self.ui.button_abort_csv_export.hide()
            self.ui.progressbar_main.hide()
            self.ui.label_file_processing.hide()
            
            # Enable input widgets
            self.set_main_widgets_disabled(False)
    
    def set_main_widgets_disabled(self, disabled: bool):
        """
        Enable/disable main input widgets.
        
        Args:
            disabled: True to disable widgets, False to enable
        """
        self.ui.button_browse_xml_folder.setDisabled(disabled)
        self.ui.button_read_xml.setDisabled(disabled)
        self.ui.button_build_xpath.setDisabled(disabled)
        self.ui.button_add_xpath_to_list.setDisabled(disabled)
        self.ui.button_browse_csv.setDisabled(disabled)
        self.ui.button_browse_csv_conversion_path_input.setDisabled(disabled)
        self.ui.button_start_csv_export.setDisabled(disabled)
        self.ui.line_edit_xml_folder_path_input.setReadOnly(disabled)
        self.ui.line_edit_csv_output_path.setReadOnly(disabled)
    
    def set_table_widgets_disabled(self, disabled: bool):
        """
        Enable/disable table-related widgets.
        
        Args:
            disabled: True to disable widgets, False to enable
        """
        self.ui.button_clear_table.setDisabled(disabled)
        self.ui.line_edit_filter_table.setDisabled(disabled)
    
    def toggle_search_widgets_visibility(self):
        """Toggle visibility of XML search widgets."""
        is_hidden = self.ui.line_edit_xml_output_find_text.isHidden()
        
        self.ui.line_edit_xml_output_find_text.setHidden(not is_hidden)
        self.ui.button_find_next.setHidden(not is_hidden)
        self.ui.button_find_previous.setHidden(not is_hidden)
        
        if not is_hidden:
            self.ui.line_edit_xml_output_find_text.clear()
    
    def set_loading_gif_state(self, visible: bool, movie=None):
        """
        Show or hide loading GIF.
        
        Args:
            visible: True to show, False to hide
            movie: QMovie object to display (required when visible=True)
        """
        if visible and movie:
            self.ui.label_loading_gif.setMovie(movie)
            movie.start()
            self.ui.label_loading_gif.setVisible(True)
        else:
            if movie:
                movie.stop()
            self.ui.label_loading_gif.clear()
            self.ui.label_loading_gif.setVisible(False)
