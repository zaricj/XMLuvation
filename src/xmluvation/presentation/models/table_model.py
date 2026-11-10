"""Virtualized, read-only table model over string columns, with vectorized sort and filter.

Large CSV files are the norm here (exports with hundreds of thousands of rows), so:

* Cell data lives in one numpy object array of ``str`` per column, built once off the
  GUI thread (:meth:`TableData.from_dataframe`). ``data()`` is two array lookups.
* Rows are exposed to the view in batches through ``canFetchMore``/``fetchMore``:
  the view only asks for (and sizes columns from) what is scrolled into reach.
* Sorting and filtering compute a row permutation with pandas/numpy instead of a
  ``QSortFilterProxyModel``, which calls ``data()`` from Python for every cell on
  every keystroke. Filtering can run on a worker thread (:func:`filter_rows`) and the
  result is applied with :meth:`TableModel.apply_filter`. The filters themselves are in
  :mod:`table_ops`.
* The vertical header shows each row's number in the file (1 = first data row), so it
  stays meaningful after sorting and filtering.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QBrush, QColor

from .table_ops import FilterSpec, duplicate_mask, filter_spec_rows

_Index = QModelIndex | QPersistentModelIndex

FETCH_BATCH_ROWS = 2_000
DUPLICATE_COLOR = QColor(255, 170, 0, 70)  # readable on light and dark themes


@dataclass(frozen=True, slots=True)
class TableData:
    """Immutable column store; safe to read from worker threads."""

    headers: tuple[str, ...]
    columns: tuple[np.ndarray, ...]  # dtype=object, every item a str
    row_count: int

    @classmethod
    def empty(cls) -> TableData:
        return cls((), (), 0)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> TableData:
        columns = []
        for name in df.columns:
            series = df[name]
            if series.dtype != object or series.isna().any():
                series = series.where(series.notna(), "").astype(str)
            columns.append(series.to_numpy(dtype=object))
        return cls(tuple(str(c) for c in df.columns), tuple(columns), len(df.index))


def filter_rows(data: TableData, text: str) -> np.ndarray | None:
    """Indices of rows where any cell contains ``text`` (case-insensitive), in table order.

    Returns ``None`` (= all rows) for an empty filter. Pure and vectorized per column, so
    it can run on a worker thread against the immutable :class:`TableData`.
    """
    return filter_spec_rows(data, FilterSpec(text=text))


class TableModel(QAbstractTableModel):
    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._data = TableData.empty()
        self._sort_key: tuple[int, Qt.SortOrder] | None = None  # last sort() request
        self._sort_order: np.ndarray | None = None  # permutation of all rows, or table order
        self._filtered: np.ndarray | None = None  # matching rows in table order, or all
        self._view = np.arange(0)  # displayed rows (source indices), sorted and filtered
        self._fetched = 0  # rows exposed to the view so far
        self._duplicate_column: int | None = None
        self._duplicates: np.ndarray | None = None  # per source row: value is duplicated
        self._duplicate_brush = QBrush(DUPLICATE_COLOR)

    # -- content -----------------------------------------------------------------------

    @property
    def data_store(self) -> TableData:
        return self._data

    @property
    def total_rows(self) -> int:
        """Rows matching the filter, including those not fetched by the view yet."""
        return len(self._view)

    @property
    def view_rows(self) -> np.ndarray:
        """Source indices of all rows shown (sorted and filtered), fetched or not."""
        return self._view

    @property
    def filtered_rows(self) -> np.ndarray | None:
        return self._filtered

    def source_row(self, position: int) -> int:
        return int(self._view[position])

    def position_of(self, source_row: int) -> int | None:
        """Display position of a source row, or ``None`` if the filter hides it."""
        found = np.flatnonzero(self._view == source_row)
        return int(found[0]) if len(found) else None

    def ensure_fetched(self, position: int) -> None:
        """Expose rows to the view up to ``position`` (for "go to row")."""
        if position < self._fetched or position >= len(self._view):
            return
        end = min(len(self._view), (position // FETCH_BATCH_ROWS + 1) * FETCH_BATCH_ROWS)
        self.beginInsertRows(QModelIndex(), self._fetched, end - 1)
        self._fetched = end
        self.endInsertRows()

    # -- duplicate highlighting ----------------------------------------------------------

    @property
    def duplicate_column(self) -> int | None:
        return self._duplicate_column

    @property
    def duplicate_rows(self) -> int:
        return int(self._duplicates.sum()) if self._duplicates is not None else 0

    def set_duplicate_column(self, column: int | None) -> None:
        """Highlight cells of ``column`` whose value occurs more than once (``None``: off)."""
        if column is not None and not 0 <= column < len(self._data.columns):
            column = None
        self._duplicate_column = column
        self._duplicates = None if column is None else duplicate_mask(self._data.columns[column])
        if self._fetched and self._data.columns:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(self._fetched - 1, len(self._data.columns) - 1),
                [Qt.ItemDataRole.BackgroundRole],
            )

    def set_table(self, data: TableData) -> None:
        self.beginResetModel()
        self._data = data
        self._sort_order = self._permutation(*self._sort_key) if self._sort_key else None
        self._filtered = None
        self._duplicate_column = None
        self._duplicates = None
        self._rebuild_view()
        self.endResetModel()

    def clear(self) -> None:
        self.set_table(TableData.empty())

    def apply_filter(self, rows: np.ndarray | None) -> None:
        """Show only ``rows`` (as returned by :func:`filter_rows`); ``None`` shows all."""
        self.beginResetModel()
        self._filtered = rows
        self._rebuild_view()
        self.endResetModel()

    def _rebuild_view(self) -> None:
        if self._sort_order is None:
            view = self._filtered if self._filtered is not None else np.arange(self._data.row_count)
        elif self._filtered is None:
            view = self._sort_order
        else:
            keep = np.zeros(self._data.row_count, dtype=bool)
            keep[self._filtered] = True
            view = self._sort_order[keep[self._sort_order]]
        self._view = view
        self._fetched = min(FETCH_BATCH_ROWS, len(view))

    # -- lazy row loading ----------------------------------------------------------------

    def canFetchMore(self, parent: _Index = QModelIndex()) -> bool:  # noqa: B008
        return not parent.isValid() and self._fetched < len(self._view)

    def fetchMore(self, parent: _Index = QModelIndex()) -> None:  # noqa: B008
        if parent.isValid():
            return
        count = min(FETCH_BATCH_ROWS, len(self._view) - self._fetched)
        if count <= 0:
            return
        self.beginInsertRows(QModelIndex(), self._fetched, self._fetched + count - 1)
        self._fetched += count
        self.endInsertRows()

    # -- QAbstractTableModel -------------------------------------------------------------

    def rowCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: B008
        return 0 if parent.isValid() else self._fetched

    def columnCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: B008
        return 0 if parent.isValid() else len(self._data.headers)

    def data(self, index: _Index, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[index.column()][self._view[index.row()]]
        if (
            role == Qt.ItemDataRole.BackgroundRole
            and self._duplicates is not None
            and index.column() == self._duplicate_column
            and self._duplicates[self._view[index.row()]]
        ):
            return self._duplicate_brush
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._data.headers[section] if section < len(self._data.headers) else None
        return str(self._view[section] + 1) if section < len(self._view) else None

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        """Stable string sort of the whole table; the filter is re-applied on top."""
        self._sort_key = (column, order)
        self.beginResetModel()  # a reset, not a layout change: the fetched row count changes
        self._sort_order = self._permutation(column, order)
        self._rebuild_view()
        self.endResetModel()

    def _permutation(self, column: int, order: Qt.SortOrder) -> np.ndarray | None:
        if not 0 <= column < len(self._data.columns):
            return None
        keys = pd.Series(self._data.columns[column], copy=False)
        ascending = order == Qt.SortOrder.AscendingOrder
        return keys.sort_values(ascending=ascending, kind="stable").index.to_numpy()
