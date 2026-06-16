# src/views/csv_profile_view.py
import pandas as pd
from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PySide6.QtCore import Signal

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.main import MainWindow


class TabCSVConversionView(QWidget):
    """Manages the widgets inside your file grouping conversion layout panels."""

    conversion_requested = Signal(str, str)

    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()
        self.window = main_window
        # Access the UI mapping through the window registry reference safely
        self.ui = main_window.ui
        self._wire_widget_events()

    def _wire_widget_events(self) -> None:
        # Every attribute resolves perfectly with native Python autocompletion!
        self.ui.button_browse_csv_conversion_path_input.clicked.connect(
            self._on_browse_input
        )
        self.ui.button_profile_cleanup_browse_csv_file_path.clicked.connect(
            self._on_browse_profile_csv
        )
        self.ui.button_clear_table.clicked.connect(self._clear_data_grid)

    def _on_browse_input(self) -> None:
        # Pass self.window as the parent context so dialog loops remain modal
        file_path, _ = QFileDialog.getOpenFileName(
            self.window, "Select CSV File for Target Conversion", "", "CSV File (*.csv)"
        )
        if file_path:
            self.ui.line_edit_csv_conversion_path_input.setText(file_path)

    def _on_browse_profile_csv(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self.window, "Open Visualization Dataset", "", "CSV Target Logs (*.csv)"
        )
        if file_path:
            self.ui.line_edit_profile_cleanup_csv_file_path.setText(file_path)
            try:
                df = pd.read_csv(file_path)
                # self.display_dataframe(df)
            except Exception as ex:
                QMessageBox.critical(
                    self.window,
                    "I/O Error",
                    f"Failed to mount file structure: {str(ex)}",
                )

    def _clear_data_grid(self) -> None:
        self.ui.table_csv_data.setModel(None)

    # def display_dataframe(self, df: pd.DataFrame) -> None:
    #     from modules.pandas_model import PandasModel
    #     if df.empty:
    #         self.ui.table_csv_data.setModel(None)
    #         return
    #     self.ui.table_csv_data.setModel(PandasModel(df))
    #     self.ui.table_csv_data.resizeColumnsToContents()
