"""Table viewer: open a table file, filter, sort, inspect columns, copy and export.

Loading, filtering, column statistics and export run on worker threads; the GUI thread
only swaps in the finished :class:`TableData` or row selection. Filter input is
debounced, and results of superseded filter runs are dropped (generation counter), so
typing never queues up work.
"""

from __future__ import annotations

import gc
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

import numpy as np
from PySide6.QtCore import QTimer, Signal

from ...application.csv_tools import export_table, is_csv_file, load_table_file
from ...infrastructure.settings_store import MAX_RECENT_FILES, SettingsStore
from ..models.table_model import TableData, TableModel
from ..models.table_ops import (
    ColumnFilter,
    ColumnStats,
    FilterSpec,
    column_stats,
    filter_spec_rows,
    frame,
    regex_error,
    tsv,
)
from ..tasks import TaskHandle, TaskRunner
from .base import ViewModel

FILTER_DEBOUNCE_MS = 200


class TableViewerViewModel(ViewModel):
    has_table_changed = Signal(bool)
    loading_changed = Signal(bool)
    filtering_changed = Signal(bool)
    file_changed = Signal(str)  # path of the open file, "" when closed
    recent_changed = Signal(list)
    filter_error = Signal(str)  # message for an invalid filter, "" when the filter is valid
    stats_ready = Signal(object)  # ColumnStats
    export_running_changed = Signal(bool)
    exported = Signal(str)  # path of the written file

    def __init__(self, runner: TaskRunner, store: SettingsStore | None = None) -> None:
        super().__init__()
        self._runner = runner
        self._store = store
        self._recent: list[str] = store.recent_table_files if store is not None else []
        self.model = TableModel(parent=self)
        self._path = ""
        self._load_handle: TaskHandle | None = None
        self._filter_handle: TaskHandle | None = None
        self._spec = FilterSpec()
        self._filter_generation = 0
        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(FILTER_DEBOUNCE_MS)
        self._filter_timer.timeout.connect(self._filter_now)

    # -- file ----------------------------------------------------------------------------

    @property
    def path(self) -> str:
        return self._path

    @property
    def is_csv(self) -> bool:
        return is_csv_file(self._path)

    @property
    def recent(self) -> list[str]:
        return list(self._recent)

    def _remember(self, path: str) -> None:
        self._recent = [path, *(p for p in self._recent if p != path)][:MAX_RECENT_FILES]
        if self._store is not None:
            self._store.recent_table_files = self._recent
        self.recent_changed.emit(self.recent)

    def clear_recent(self) -> None:
        self._recent = []
        if self._store is not None:
            self._store.recent_table_files = []
        self.recent_changed.emit([])

    # -- loading -------------------------------------------------------------------------

    def load(self, file_path: str) -> None:
        if not file_path:
            return
        if self._load_handle is not None:
            self._load_handle.cancel()
        path = Path(file_path)
        self.loading_changed.emit(True)
        handle = self._runner.start(
            lambda ctx: TableData.from_dataframe(load_table_file(path, ctx.token)),
            on_success=lambda data: self._loaded(handle, str(path), data),
            on_error=lambda e: self.report_error(e, f"Cannot open {path.name}"),
            on_finished=lambda: self._load_finished(handle),
        )
        self._load_handle = handle

    def _load_finished(self, handle: TaskHandle) -> None:
        if self._load_handle is handle:
            self._load_handle = None
            self.loading_changed.emit(False)

    def _loaded(self, handle: TaskHandle, path: str, data: TableData) -> None:
        if self._load_handle is not handle:
            return  # superseded by a newer load or cleared meanwhile
        self._cancel_filter()
        self._spec = FilterSpec()
        self.model.set_table(data)  # drops the previous table
        gc.collect()
        self._path = path
        self._remember(path)
        self.file_changed.emit(path)
        self.has_table_changed.emit(True)

    # -- filtering -----------------------------------------------------------------------

    @property
    def filter_spec(self) -> FilterSpec:
        return self._spec

    def set_filter(self, text: str) -> None:
        """The quick filter: rows where any column contains ``text``."""
        self._set_spec(replace(self._spec, text=text.strip()))

    def set_filter_options(self, regex: bool, case_sensitive: bool) -> None:
        self._set_spec(replace(self._spec, regex=regex, case_sensitive=case_sensitive))

    def set_column_filters(self, filters: Sequence[ColumnFilter]) -> None:
        self._set_spec(replace(self._spec, columns=tuple(filters)))

    def _set_spec(self, spec: FilterSpec) -> None:
        self._spec = spec
        self._filter_timer.start()

    def _filter_now(self) -> None:
        self._cancel_filter()
        generation = self._filter_generation
        data, spec = self.model.data_store, self._spec
        error = regex_error(spec)
        self.filter_error.emit(error or "")
        if error:
            return  # keep showing the last valid result
        if spec.is_empty:
            self.model.apply_filter(None)
            return
        self.filtering_changed.emit(True)
        self._filter_handle = self._runner.start(
            lambda _ctx: filter_spec_rows(data, spec),
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

    # -- columns, rows and selection ------------------------------------------------------

    def set_duplicate_column(self, column: int | None) -> None:
        self.model.set_duplicate_column(column)

    def request_stats(self, column: int) -> None:
        """Statistics of ``column`` over the rows shown now (``stats_ready``)."""
        data, rows = self.model.data_store, self.model.filtered_rows
        self._runner.start(
            lambda _ctx: column_stats(data, column, rows),
            on_success=self._stats_done,
            on_error=lambda e: self.report_error(e, "Column statistics failed"),
        )

    def _stats_done(self, stats: ColumnStats) -> None:
        self.stats_ready.emit(stats)

    def position_of_row(self, number: int) -> int | None:
        """Display position of row ``number`` of the file (1 = first data row).

        ``None`` if there is no such row or the filter hides it; ``ensure_fetched`` has
        made the position available to the view otherwise.
        """
        if not 1 <= number <= self.model.data_store.row_count:
            return None
        position = self.model.position_of(number - 1)
        if position is not None:
            self.model.ensure_fetched(position)
        return position

    def copy_text(self, positions: Sequence[int], columns: Sequence[int], headers: bool) -> str:
        """Tab-separated text of the cells at display ``positions`` and ``columns``."""
        rows = self.model.view_rows[np.asarray(positions, dtype=np.intp)]
        return tsv(self.model.data_store, rows.tolist(), columns, headers)

    def export(self, target: str, columns: Sequence[int]) -> None:
        """Write the rows shown (filtered and sorted) and ``columns`` to CSV or Excel."""
        data, rows = self.model.data_store, self.model.view_rows
        columns = list(columns)
        self.export_running_changed.emit(True)
        self._runner.start(
            lambda _ctx: str(export_table(frame(data, rows, columns), Path(target))),
            on_success=self.exported.emit,
            on_error=lambda e: self.report_error(e, "Export failed"),
            on_finished=lambda: self.export_running_changed.emit(False),
        )

    # -- teardown ------------------------------------------------------------------------

    def clear(self) -> None:
        self._filter_timer.stop()
        self._cancel_filter()
        self._spec = FilterSpec()
        if self._load_handle is not None:
            self._load_handle.cancel()
            self._load_handle = None
            self.loading_changed.emit(False)
        self.model.clear()
        gc.collect()  # a large table is millions of str objects; reclaim them now
        self._path = ""
        self.file_changed.emit("")
        self.has_table_changed.emit(False)
