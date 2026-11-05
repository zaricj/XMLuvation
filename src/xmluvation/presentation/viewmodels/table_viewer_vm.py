"""CSV table viewer with live filtering."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PySide6.QtCore import QSortFilterProxyModel, Signal

from ...application.csv_tools import load_csv_table
from ..models.table_model import DataFrameTableModel, make_filter_proxy
from ..tasks import TaskRunner
from .base import ViewModel


class TableViewerViewModel(ViewModel):
    has_table_changed = Signal(bool)
    loading_changed = Signal(bool)

    def __init__(self, runner: TaskRunner) -> None:
        super().__init__()
        self._runner = runner
        self.source_model = DataFrameTableModel(parent=self)
        self.model: QSortFilterProxyModel = make_filter_proxy(self.source_model, self)

    def load(self, file_path: str) -> None:
        if not file_path:
            return
        path = Path(file_path)
        self.loading_changed.emit(True)
        self._runner.start(
            lambda _ctx: load_csv_table(path),
            on_success=self._loaded,
            on_error=lambda e: self.report_error(e, "Exception loading CSV file"),
            on_finished=lambda: self.loading_changed.emit(False),
        )

    def _loaded(self, df: pd.DataFrame) -> None:
        self.model.setFilterFixedString("")
        self.source_model.set_dataframe(df)
        self.has_table_changed.emit(True)

    def set_filter(self, text: str) -> None:
        self.model.setFilterFixedString(text.strip())

    def clear(self) -> None:
        self.model.setFilterFixedString("")
        self.source_model.clear()
        self.has_table_changed.emit(False)
