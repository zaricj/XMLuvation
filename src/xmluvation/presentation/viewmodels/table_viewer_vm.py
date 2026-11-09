"""CSV table viewer with live filtering.

Loading and filtering both run on worker threads; the GUI thread only swaps in the
finished :class:`TableData` or row selection. Filter input is debounced, and results of
superseded filter runs are dropped (generation counter), so typing never queues up work.
"""

from __future__ import annotations

import gc
from pathlib import Path

import numpy as np
from PySide6.QtCore import QTimer, Signal

from ...application.csv_tools import load_csv_table
from ..models.table_model import TableData, TableModel, filter_rows
from ..tasks import TaskHandle, TaskRunner
from .base import ViewModel

FILTER_DEBOUNCE_MS = 200


class TableViewerViewModel(ViewModel):
    has_table_changed = Signal(bool)
    loading_changed = Signal(bool)
    filtering_changed = Signal(bool)

    def __init__(self, runner: TaskRunner) -> None:
        super().__init__()
        self._runner = runner
        self.model = TableModel(parent=self)
        self._load_handle: TaskHandle | None = None
        self._filter_handle: TaskHandle | None = None
        self._filter_text = ""
        self._filter_generation = 0
        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(FILTER_DEBOUNCE_MS)
        self._filter_timer.timeout.connect(self._filter_now)

    # -- loading -------------------------------------------------------------------------

    def load(self, file_path: str) -> None:
        if not file_path:
            return
        if self._load_handle is not None:
            self._load_handle.cancel()
        path = Path(file_path)
        self.loading_changed.emit(True)
        handle = self._runner.start(
            lambda ctx: TableData.from_dataframe(load_csv_table(path, ctx.token)),
            on_success=lambda data: self._loaded(handle, data),
            on_error=lambda e: self.report_error(e, "Exception loading CSV file"),
            on_finished=lambda: self._load_finished(handle),
        )
        self._load_handle = handle

    def _load_finished(self, handle: TaskHandle) -> None:
        if self._load_handle is handle:
            self._load_handle = None
            self.loading_changed.emit(False)

    def _loaded(self, handle: TaskHandle, data: TableData) -> None:
        if self._load_handle is not handle:
            return  # superseded by a newer load or cleared meanwhile
        self._cancel_filter()
        self._filter_text = ""
        self.model.set_table(data)  # drops the previous table
        gc.collect()
        self.has_table_changed.emit(True)

    # -- filtering -----------------------------------------------------------------------

    def set_filter(self, text: str) -> None:
        self._filter_text = text.strip()
        self._filter_timer.start()

    def _filter_now(self) -> None:
        self._cancel_filter()
        generation = self._filter_generation
        data, text = self.model.data_store, self._filter_text
        if not text:
            self.model.apply_filter(None)
            return
        self.filtering_changed.emit(True)
        self._filter_handle = self._runner.start(
            lambda _ctx: filter_rows(data, text),
            on_success=lambda rows: self._filtered(generation, rows),
            on_error=lambda e: self.report_error(e, "Filtering the table failed"),
            on_finished=lambda: self._filter_finished(generation),
        )

    def _filtered(self, generation: int, rows: np.ndarray | None) -> None:
        if generation == self._filter_generation:
            self.model.apply_filter(rows)

    def _filter_finished(self, generation: int) -> None:
        if generation == self._filter_generation:
            self._filter_handle = None
            self.filtering_changed.emit(False)

    def _cancel_filter(self) -> None:
        """Invalidate any running filter task; its result will be ignored."""
        self._filter_generation += 1
        if self._filter_handle is not None:
            self._filter_handle.cancel()
            self._filter_handle = None
            self.filtering_changed.emit(False)

    # -- teardown ------------------------------------------------------------------------

    def clear(self) -> None:
        self._filter_timer.stop()
        self._cancel_filter()
        self._filter_text = ""
        if self._load_handle is not None:
            self._load_handle.cancel()
            self._load_handle = None
            self.loading_changed.emit(False)
        self.model.clear()
        gc.collect()  # a large table is millions of str objects; reclaim them now
        self.has_table_changed.emit(False)
