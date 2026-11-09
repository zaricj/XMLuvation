from __future__ import annotations

import pandas as pd
from PySide6.QtCore import QModelIndex, Qt

from xmluvation.presentation.models import table_model
from xmluvation.presentation.models.table_model import TableData, TableModel, filter_rows


def _model(df: pd.DataFrame) -> TableModel:
    model = TableModel()
    model.set_table(TableData.from_dataframe(df))
    return model


def _column(model: TableModel, column: int) -> list[str]:
    while model.canFetchMore(QModelIndex()):
        model.fetchMore(QModelIndex())
    return [model.data(model.index(r, column)) for r in range(model.rowCount())]


def test_rows_are_fetched_in_batches(qtbot, monkeypatch) -> None:
    monkeypatch.setattr(table_model, "FETCH_BATCH_ROWS", 10)
    model = _model(pd.DataFrame({"n": [str(i) for i in range(25)]}))
    assert model.rowCount() == 10 and model.total_rows == 25
    assert model.canFetchMore(QModelIndex())
    model.fetchMore(QModelIndex())
    model.fetchMore(QModelIndex())
    assert model.rowCount() == 25 and not model.canFetchMore(QModelIndex())


def test_missing_values_display_as_empty_text(qtbot) -> None:
    model = _model(pd.DataFrame({"a": [1.5, None], "b": ["x", None]}))
    assert _column(model, 0) == ["1.5", ""]
    assert _column(model, 1) == ["x", ""]


def test_filter_is_case_insensitive_literal_over_all_columns() -> None:
    data = TableData.from_dataframe(
        pd.DataFrame({"Name": ["Anna", "Bob", "a.b"], "City": ["Berlin", "Köln", "BERLIN"]})
    )
    assert filter_rows(data, "berlin").tolist() == [0, 2]
    assert filter_rows(data, ".").tolist() == [2]  # not a regex
    assert filter_rows(data, "") is None


def test_sort_is_stable_and_combines_with_filter(qtbot) -> None:
    df = pd.DataFrame({"k": ["b", "a", "b", "a"], "v": ["1", "2", "3", "4"]})
    model = _model(df)
    model.sort(0, Qt.SortOrder.AscendingOrder)
    assert _column(model, 1) == ["2", "4", "1", "3"]
    model.apply_filter(filter_rows(model.data_store, "b"))
    assert _column(model, 1) == ["1", "3"]
    model.sort(1, Qt.SortOrder.DescendingOrder)
    assert _column(model, 1) == ["3", "1"]
    model.apply_filter(None)
    assert _column(model, 1) == ["4", "3", "2", "1"]


def test_new_table_keeps_the_header_sort(qtbot) -> None:
    model = _model(pd.DataFrame({"k": ["x"]}))
    model.sort(0, Qt.SortOrder.DescendingOrder)
    model.set_table(TableData.from_dataframe(pd.DataFrame({"k": ["a", "c", "b"]})))
    assert _column(model, 0) == ["c", "b", "a"]
