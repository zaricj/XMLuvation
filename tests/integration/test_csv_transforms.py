"""Split, compare and column editing on real files in a temporary directory."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from xmluvation.application import csv_compare, csv_split
from xmluvation.application.cancellation import CancellationToken, NullReporter
from xmluvation.application.csv_compare import compare_csv, summary_lines
from xmluvation.application.csv_split import SplitMode, split_csv
from xmluvation.application.csv_tools import ColumnEdit, save_column_edits
from xmluvation.domain.errors import Cancelled, ValidationError


def _write(path: Path, text: str, *, bom: bool = False, encoding: str = "utf-8") -> Path:
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode(encoding))
    return path


def _rows(path: Path, delimiter: str = ",") -> list[list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.reader(handle, delimiter=delimiter))


# ---------------------------------------------------------------------------- split


def test_split_by_rows_repeats_header_and_keeps_format(tmp_path: Path) -> None:
    src = _write(tmp_path / "data.csv", 'ID;Name\r\n1;a\r\n2;b\r\n3;"c;d"\r\n', bom=True)
    result = split_csv(
        str(src),
        SplitMode.ROWS,
        rows_per_file=2,
        reporter=NullReporter(),
        token=CancellationToken(),
    )
    assert result.folder == tmp_path / "data_split"
    assert [p.name for p in result.files] == ["data_part001.csv", "data_part002.csv"]
    assert result.rows == 3
    first, second = (p.read_bytes() for p in result.files)
    assert first == b"\xef\xbb\xbfID;Name\r\n1;a\r\n2;b\r\n"
    assert second == b'\xef\xbb\xbfID;Name\r\n3;"c;d"\r\n'


def test_split_by_value_uses_safe_unique_names(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(csv_split, "MAX_OPEN_FILES", 2)  # force handles to be reopened
    text = "Unit,V\nkg,1\nKG,2\na/b,3\n,4\nkg,5\npcs,6\na/b,7\n"
    src = _write(tmp_path / "u.csv", text)
    result = split_csv(
        str(src),
        SplitMode.COLUMN,
        column="Unit",
        reporter=NullReporter(),
        token=CancellationToken(),
    )
    by_name = {p.name: _rows(p) for p in result.files}
    assert set(by_name) == {"(empty).csv", "a_b.csv", "kg.csv", "KG (2).csv", "pcs.csv"}
    assert by_name["kg.csv"] == [["Unit", "V"], ["kg", "1"], ["kg", "5"]]
    assert by_name["a_b.csv"] == [["Unit", "V"], ["a/b", "3"], ["a/b", "7"]]
    assert by_name["(empty).csv"] == [["Unit", "V"], ["", "4"]]


def test_split_never_overwrites_and_cleans_up_on_failure(tmp_path: Path, monkeypatch) -> None:
    src = _write(tmp_path / "x.csv", "A\n1\n2\n3\n")
    (tmp_path / "x_split").mkdir()
    result = split_csv(
        str(src),
        SplitMode.ROWS,
        rows_per_file=10,
        reporter=NullReporter(),
        token=CancellationToken(),
    )
    assert result.folder.name == "x_split (2)"

    monkeypatch.setattr(csv_split, "MAX_PARTS_BY_VALUE", 2)
    with pytest.raises(ValidationError, match="different values"):
        split_csv(
            str(src),
            SplitMode.COLUMN,
            column="A",
            reporter=NullReporter(),
            token=CancellationToken(),
        )
    token = CancellationToken()
    token.cancel()
    monkeypatch.setattr(csv_split, "_CHECK_EVERY", 1)
    with pytest.raises(Cancelled):
        split_csv(str(src), SplitMode.ROWS, rows_per_file=1, reporter=NullReporter(), token=token)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["x.csv", "x_split", "x_split (2)"]


def test_split_rejects_unknown_column_and_empty_file(tmp_path: Path) -> None:
    src = _write(tmp_path / "x.csv", "A,B\n")
    for kwargs in ({"column": "C"}, {}):
        mode = SplitMode.COLUMN if kwargs else SplitMode.ROWS
        with pytest.raises(ValidationError):
            split_csv(str(src), mode, reporter=NullReporter(), token=CancellationToken(), **kwargs)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["x.csv"]


# ---------------------------------------------------------------------------- compare


def test_compare_reports_added_removed_and_changed_cells(tmp_path: Path) -> None:
    old = _write(
        tmp_path / "old.csv", "ID,Name,City,Gone\n1,Anna,Berlin,x\n2,Bob,Köln,y\n3,Carl,Ulm,z\n"
    )
    new = _write(
        tmp_path / "new.csv",
        "ID;City;Name;Extra\n1;Berlin;Anna;e\n3;Munich;Karl;e\n4;Bonn;Dora;e\n",
    )
    result = compare_csv(str(old), str(new), "ID", False, NullReporter(), CancellationToken())
    assert (result.removed, result.added, result.changed_rows, result.changed_cells) == (1, 1, 1, 2)
    assert result.unchanged == 1 and result.moved == 0
    assert result.only_in_old == ["Gone"] and result.only_in_new == ["Extra"]
    assert result.report == tmp_path / "new_vs_old_diff.csv"
    assert _rows(result.report) == [  # in the new file's order; cells in the old column order
        ["Status", "Old row", "New row", "ID", "Column", "Old value", "New value"],
        ["removed", "3", "", "2", "", "", ""],
        ["changed", "4", "3", "3", "Name", "Carl", "Karl"],
        ["changed", "4", "3", "3", "City", "Ulm", "Munich"],
        ["added", "", "4", "4", "", "", ""],
    ]
    assert (
        "1 removed, 1 added, 1 changed rows (2 changed cells), 1 unchanged."
        in summary_lines(result)[0]
    )


def test_compare_shows_rows_side_by_side_with_changed_cells_marked(tmp_path: Path) -> None:
    old = _write(tmp_path / "old.csv", "ID,Name\n1,Anna\n2,Bob\n3,Carl\n")
    new = _write(tmp_path / "new.csv", "ID,Name\n1,Anna\n3,Karl\n4,Dora\n")
    result = compare_csv(str(old), str(new), "ID", False, NullReporter(), CancellationToken())
    diff = result.text_diff
    assert diff is not None and diff.old_lines[0] == "ID,Name"
    shown = [
        (row.kind.value, row.old_number, row.new_number, row.old_spans, row.new_spans)
        for row in diff.rows
    ]
    assert shown == [
        ("equal", 1, 1, (), ()),
        ("equal", 2, 2, (), ()),
        ("removed", 3, 0, (), ()),
        ("changed", 4, 3, ((2, 3),), ((2, 3),)),  # "C" -> "K" inside the Name cell
        ("added", 0, 4, (), ()),
    ]


def test_compare_detects_moved_rows_by_key(tmp_path: Path) -> None:
    rows = [f"{i},value {i}" for i in range(1, 21)]
    old = _write(tmp_path / "old.csv", "K,V\n" + "\n".join(rows) + "\n")
    moved = rows[1:15] + [rows[0].replace("value 1", "value one")] + rows[15:]
    new = _write(tmp_path / "new.csv", "K,V\n" + "\n".join(moved) + "\n")
    result = compare_csv(str(old), str(new), "K", False, NullReporter(), CancellationToken())
    assert (result.moved, result.changed_rows, result.removed, result.added) == (1, 0, 0, 0)
    assert result.unchanged == 19 and result.changed_cells == 1
    assert _rows(result.report)[1] == ["moved", "2", "16", "1", "V", "value 1", "value one"]
    assert "0 changed, 1 moved rows (1 changed cells), 19 unchanged." in summary_lines(result)[0]


def test_compare_without_key_aligns_rows_by_content(tmp_path: Path) -> None:
    old = _write(tmp_path / "a.csv", "A,B\nx,1\ny,2\nz,3\n")
    new = _write(tmp_path / "b.csv", "A,B\nx,1\nnew,0\ny,2\nz,4\n")
    result = compare_csv(str(old), str(new), "", False, NullReporter(), CancellationToken())
    assert (result.added, result.changed_rows, result.unchanged) == (1, 1, 2)
    assert _rows(result.report) == [
        ["Status", "Old row", "New row", "Column", "Old value", "New value"],
        ["added", "", "3", "", "", ""],
        ["changed", "4", "5", "B", "3", "4"],
    ]
    assert any("paired by their position" in line for line in summary_lines(result))


def test_compare_keeps_line_breaks_inside_cells(tmp_path: Path) -> None:
    old = _write(tmp_path / "a.csv", 'K,Text\n1,"one\ntwo"\n2,x\n')
    new = _write(tmp_path / "b.csv", 'K,Text\n1,"one\nTWO"\n2,x\n')
    result = compare_csv(str(old), str(new), "K", False, NullReporter(), CancellationToken())
    assert result.changed_cells == 1
    assert _rows(result.report)[1] == ["changed", "2", "2", "1", "Text", "one\ntwo", "one\nTWO"]
    assert result.text_diff is not None
    assert result.text_diff.new_lines[1] == '1,"one\u21b5TWO"'
    assert result.text_diff.rows[1].new_spans == ((7, 10),)


def test_compare_handles_short_rows(tmp_path: Path) -> None:
    old = _write(tmp_path / "a.csv", "K,V,W\n1,x\n2,y,z\n")
    new = _write(tmp_path / "b.csv", "K,V,W\n1,x,\n2,y\n")
    result = compare_csv(str(old), str(new), "K", False, NullReporter(), CancellationToken())
    assert result.changed_cells == 1 and result.unchanged == 1  # a missing cell is empty
    assert result.text_diff is not None
    assert result.text_diff.old_lines[1:] == ["1,x", "2,y,z"]  # shown as written
    assert result.text_diff.rows[2].old_spans == ((4, 5),)


def test_compare_loose_mode_and_duplicate_keys(tmp_path: Path) -> None:
    old = _write(tmp_path / "a.csv", "K,V\nx,Hello\nx,second\ny,1\n")
    new = _write(tmp_path / "b.csv", "K,V\nx, hello \nx,SECOND\ny,1\n")
    strict = compare_csv(str(old), str(new), "K", False, NullReporter(), CancellationToken())
    assert strict.changed_cells == 2 and strict.duplicate_keys == 2
    assert strict.report is not None and strict.report.name == "b_vs_a_diff.csv"
    loose = compare_csv(str(old), str(new), "K", True, NullReporter(), CancellationToken())
    assert loose.identical and loose.unchanged == 3
    assert loose.report is None  # nothing to report
    assert summary_lines(loose)[0] == "No differences: 3 rows match."


def test_compare_does_not_show_large_files_side_by_side(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(csv_compare, "MAX_TEXT_DIFF_BYTES", 4)
    old = _write(tmp_path / "a.csv", "K,V\n1,2\n")
    new = _write(tmp_path / "b.csv", "K,V\n1,3\n")
    result = compare_csv(str(old), str(new), "K", False, NullReporter(), CancellationToken())
    assert result.text_diff is None and "not shown side by side" in result.text_diff_note
    assert result.changed_cells == 1


def test_compare_requires_key_in_both_files(tmp_path: Path) -> None:
    old = _write(tmp_path / "a.csv", "K,V\n1,2\n")
    new = _write(tmp_path / "b.csv", "X,V\n1,2\n")
    with pytest.raises(ValidationError, match="key column 'K' does not exist in b.csv"):
        compare_csv(str(old), str(new), "K", False, NullReporter(), CancellationToken())


def test_compare_can_be_cancelled(tmp_path: Path) -> None:
    old = _write(tmp_path / "a.csv", "K,V\n1,2\n")
    token = CancellationToken()
    token.cancel()
    with pytest.raises(Cancelled):
        compare_csv(str(old), str(old), "K", False, NullReporter(), token)


# ---------------------------------------------------------------------------- columns


def test_column_edits_reorder_rename_and_drop_exactly(tmp_path: Path) -> None:
    src = _write(tmp_path / "c.csv", 'A;B;C\r\n1;"x;y";0042\r\n2;;\r\n', bom=True)
    result = save_column_edits(
        str(src), [ColumnEdit(2, "Code"), ColumnEdit(0, "A")], ["A", "B", "C"], overwrite=False
    )
    assert result.output == tmp_path / "c_edited.csv"
    assert (result.columns, result.removed, result.rows) == (2, 1, 2)
    assert result.output.read_bytes() == b"\xef\xbb\xbfCode;A\r\n0042;1\r\n;2\r\n"
    assert src.read_bytes().startswith(b"\xef\xbb\xbfA;B;C")  # source untouched


def test_column_edits_overwrite_and_keep_latin1(tmp_path: Path) -> None:
    src = _write(tmp_path / "l.csv", "Name,Ort\nMüller,Köln\n", encoding="latin-1")
    save_column_edits(str(src), [ColumnEdit(1, "Stadt")], ["Name", "Ort"], overwrite=True)
    assert src.read_bytes() == "Stadt\r\nKöln\r\n".encode("latin-1")


@pytest.mark.parametrize(
    ("edits", "header", "message"),
    [
        ([], ["A"], "at least one column"),
        ([ColumnEdit(0, " ")], ["A"], "cannot be empty"),
        ([ColumnEdit(0, "X"), ColumnEdit(1, "x")], ["A", "B"], "Duplicate: X, x"),
        ([ColumnEdit(0, "A")], ["A", "Z"], "changed since it was opened"),
    ],
)
def test_column_edits_validation(tmp_path: Path, edits, header, message) -> None:  # noqa: ANN001
    src = _write(tmp_path / "v.csv", "A,B\n1,2\n")
    with pytest.raises(ValidationError, match=message):
        save_column_edits(str(src), edits, header, overwrite=True)
    assert src.read_text(encoding="utf-8") == "A,B\n1,2\n"
