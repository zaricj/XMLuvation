"""Table viewer operations: filters, statistics, copy text, export frame, model helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
from PySide6.QtCore import QModelIndex, Qt

from xmluvation.presentation.models import table_model
from xmluvation.presentation.models.table_model import TableData, TableModel
from xmluvation.presentation.models.table_ops import (
    ColumnFilter,
    FilterOp,
    FilterSpec,
    column_stats,
    filter_spec_rows,
    frame,
    regex_error,
    tsv,
)

DATA = TableData.from_dataframe(
    pd.DataFrame(
        {
            "ID": ["1", "2", "3", "3", "5"],
            "Name": ["Anna", "bob", "Carl", "", "  "],
            "City": ["Berlin", "Köln", "Ulm", "Ulm", "Bonn"],
        }
    )
)


def _rows(*filters: ColumnFilter, **spec: object) -> list[int] | None:
    rows = filter_spec_rows(DATA, FilterSpec(columns=filters, **spec))  # type: ignore[arg-type]
    return None if rows is None else rows.tolist()


def test_column_filter_conditions() -> None:
    assert _rows(ColumnFilter(1, FilterOp.CONTAINS, "B")) == [1]  # case-insensitive
    assert _rows(ColumnFilter(1, FilterOp.CONTAINS, "B", case_sensitive=True)) == []
    assert _rows(ColumnFilter(1, FilterOp.NOT_CONTAINS, "a")) == [1, 3, 4]
    assert _rows(ColumnFilter(2, FilterOp.EQUALS, "ulm")) == [2, 3]
    assert _rows(ColumnFilter(2, FilterOp.NOT_EQUALS, "Ulm")) == [0, 1, 4]
    assert _rows(ColumnFilter(2, FilterOp.STARTS_WITH, "b")) == [0, 4]
    assert _rows(ColumnFilter(2, FilterOp.ENDS_WITH, "N")) == [0, 1, 4]
    assert _rows(ColumnFilter(1, FilterOp.REGEX, "^[ab]")) == [0, 1]
    assert _rows(ColumnFilter(1, FilterOp.EMPTY)) == [3, 4]  # spaces only count as empty
    assert _rows(ColumnFilter(1, FilterOp.NOT_EMPTY)) == [0, 1, 2]
    assert _rows(ColumnFilter(0, FilterOp.DUPLICATED)) == [2, 3]
    assert _rows(ColumnFilter(0, FilterOp.UNIQUE)) == [0, 1, 4]


def test_filters_combine_and_inactive_ones_are_ignored() -> None:
    assert _rows(ColumnFilter(2, FilterOp.EQUALS, "Ulm"), ColumnFilter(1, FilterOp.NOT_EMPTY)) == [
        2
    ]
    assert _rows(ColumnFilter(1, FilterOp.CONTAINS, "")) is None  # no value yet: no filter
    assert _rows(ColumnFilter(1, FilterOp.EMPTY), text="ul") == [3]


def test_quick_filter_regex_and_case() -> None:
    assert _rows(text="^b") == []  # literal by default
    assert _rows(text="^b", regex=True) == [0, 1, 4]
    assert _rows(text="^b", regex=True, case_sensitive=True) == [1]
    assert regex_error(FilterSpec(text="(", regex=True)) is not None
    assert regex_error(FilterSpec(text="(")) is None  # literal text is never an error
    bad_column = ColumnFilter(0, FilterOp.REGEX, "[")
    assert "Invalid regular expression '['" in str(regex_error(FilterSpec(columns=(bad_column,))))


def test_column_stats_numbers_text_and_filtered_rows() -> None:
    ids = column_stats(DATA, 0, None)
    assert (ids.rows, ids.empty, ids.distinct, ids.duplicate_values, ids.duplicate_rows) == (
        5,
        0,
        4,
        1,
        2,
    )
    assert ids.numeric and (ids.minimum, ids.maximum) == ("1", "5")
    assert ids.top[0] == ("3", 2)
    names = column_stats(DATA, 1, None)
    assert names.empty == 2 and not names.numeric
    assert (names.minimum, names.maximum) == ("Anna", "bob")  # text order
    shown = column_stats(DATA, 2, np.array([2, 3]))
    assert shown.rows == 2 and shown.top == [("Ulm", 2)]


def test_copy_text_is_tab_separated_and_quoted_like_excel() -> None:
    data = TableData.from_dataframe(pd.DataFrame({"A": ["x", 'say "hi"'], "B": ["1\t2", "a\nb"]}))
    assert tsv(data, [0, 1], [1, 0], headers=True) == ('B\tA\r\n"1\t2"\tx\r\n"a\nb"\t"say ""hi"""')
    assert tsv(data, [1], [0]) == '"say ""hi"""'


def test_export_frame_keeps_order_and_duplicate_headers() -> None:
    data = TableData(
        ("A", "A", "B"),
        tuple(np.array(v, dtype=object) for v in (["1", "2"], ["3", "4"], ["5", "6"])),
        2,
    )
    df = frame(data, np.array([1, 0]), [2, 0, 1])
    assert list(df.columns) == ["B", "A", "A"]
    assert df.values.tolist() == [["6", "2", "4"], ["5", "1", "3"]]


def test_model_row_numbers_duplicates_and_go_to(qtbot, monkeypatch) -> None:
    monkeypatch.setattr(table_model, "FETCH_BATCH_ROWS", 2)
    model = TableModel()
    model.set_table(DATA)
    model.sort(2, Qt.SortOrder.DescendingOrder)  # Ulm, Ulm, Köln, Bonn, Berlin
    vertical = Qt.Orientation.Vertical
    assert [model.headerData(i, vertical) for i in range(2)] == ["3", "4"]  # rows in the file
    assert model.position_of(0) == 4 and model.rowCount() == 2
    model.ensure_fetched(4)
    assert model.rowCount() == 5
    model.set_duplicate_column(2)
    assert model.duplicate_rows == 2
    background = Qt.ItemDataRole.BackgroundRole
    assert model.data(model.index(0, 2), background) is not None  # Ulm
    assert model.data(model.index(0, 1), background) is None  # other column
    assert model.data(model.index(2, 2), background) is None  # Köln
    model.apply_filter(np.array([1, 2]))
    assert model.position_of(0) is None
    model.set_duplicate_column(None)
    assert model.data(model.index(0, 2), background) is None
    assert not model.canFetchMore(QModelIndex())


def test_frozen_columns_stay_in_place_and_follow_the_main_view(qtbot) -> None:
    from xmluvation.presentation.widgets.data_table import DataTableView

    model = TableModel()
    model.set_table(
        TableData.from_dataframe(
            pd.DataFrame({f"C{c}": [f"r{r}c{c}" for r in range(200)] for c in range(8)})
        )
    )
    view = DataTableView()
    qtbot.addWidget(view)
    view.setModel(model)
    view.resize(400, 300)
    view.show()
    for column in range(8):
        view.setColumnWidth(column, 120)
    frozen = view.frozen_view()
    assert frozen.isHidden()

    view.set_frozen_columns(2)
    assert not frozen.isHidden() and frozen.width() == 240
    assert [frozen.isColumnHidden(c) for c in range(4)] == [False, False, True, True]
    assert frozen.selectionModel() is view.selectionModel()

    view.horizontalScrollBar().setValue(view.horizontalScrollBar().maximum())
    assert frozen.x() == view.verticalHeader().width() + view.frameWidth()  # did not scroll
    for mode in (view.ScrollMode.ScrollPerItem, view.ScrollMode.ScrollPerPixel):
        view.setVerticalScrollMode(mode)
        assert frozen.verticalScrollMode() == mode
        assert frozen.verticalScrollBar().maximum() == view.verticalScrollBar().maximum()
        view.verticalScrollBar().setValue(50)
        assert frozen.verticalScrollBar().value() == view.verticalScrollBar().value() == 50
        frozen.verticalScrollBar().setValue(20)  # e.g. the mouse wheel over a frozen column
        assert view.verticalScrollBar().value() == 20

    view.setColumnWidth(0, 60)  # widths, hidden columns and order follow the main view
    assert frozen.columnWidth(0) == 60 and frozen.width() == 180
    view.setColumnHidden(1, True)
    assert frozen.isColumnHidden(1) and frozen.width() == 60
    view.horizontalHeader().moveSection(5, 0)
    assert not frozen.isColumnHidden(5) and frozen.horizontalHeader().visualIndex(5) == 0

    view.sortByColumn(0, Qt.SortOrder.DescendingOrder)
    assert frozen.horizontalHeader().sortIndicatorSection() == 0
    view.set_frozen_columns(0)
    assert frozen.isHidden()
