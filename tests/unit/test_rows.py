from __future__ import annotations

from xmluvation.domain.models import ColumnValues
from xmluvation.domain.rows import build_rows, csv_columns


def test_ungrouped_pads_shorter_columns() -> None:
    rows, total = build_rows(
        "f",
        [ColumnValues("A", True, ("1", "2"), 2), ColumnValues("B", True, ("x",), 1)],
        group_matches=False,
    )
    assert total == 3
    assert rows == [{"Filename": "f", "A": "1", "B": "x"}, {"Filename": "f", "A": "2", "B": ""}]


def test_grouped_joins_non_empty_values() -> None:
    rows, _ = build_rows("f", [ColumnValues("A", True, ("1", "", "3"), 3)], group_matches=True)
    assert rows == [{"Filename": "f", "A": "1; 3"}]


def test_count_column_only_on_first_row() -> None:
    rows, total = build_rows(
        "f",
        [ColumnValues("E", False, (), 4), ColumnValues("A", True, ("a", "b"), 2)],
        group_matches=False,
    )
    assert total == 6
    assert rows[0]["E Match Count"] == "4"
    assert rows[1]["E Match Count"] == ""


def test_no_matches_no_rows() -> None:
    assert build_rows("f", [ColumnValues("A", True, (), 0)], False) == ([], 0)


def test_rows_without_content_are_skipped_when_ungrouped() -> None:
    rows, _ = build_rows("f", [ColumnValues("A", True, ("", "x"), 1)], False)
    assert rows == [{"Filename": "f", "A": "x"}]


def test_csv_columns() -> None:
    assert csv_columns(["A", "B"], [True, False]) == ["Filename", "A", "B Match Count"]
