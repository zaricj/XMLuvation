"""Split, compare and column editing on real files in a temporary directory."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from xmluvation.application import csv_split
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
    assert result.unchanged == 1
    assert result.only_in_old == ["Gone"] and result.only_in_new == ["Extra"]
    assert result.report == tmp_path / "new_vs_old_diff.csv"
    assert _rows(result.report) == [  # in file order; changed cells in the old file's column order
        ["Status", "ID", "Column", "Old value", "New value"],
        ["removed", "2", "", "", ""],
        ["changed", "3", "Name", "Carl", "Karl"],
        ["changed", "3", "City", "Ulm", "Munich"],
        ["added", "4", "", "", ""],
    ]
    assert "1 removed, 1 added, 1 changed rows (2 cells), 1 unchanged." in summary_lines(result)[0]


def test_compare_loose_mode_and_duplicate_keys(tmp_path: Path) -> None:
    old = _write(tmp_path / "a.csv", "K,V\nx,Hello\nx,second\ny,1\n")
    new = _write(tmp_path / "b.csv", "K,V\nx, hello \nx,SECOND\ny,1\n")
    strict = compare_csv(str(old), str(new), "K", False, NullReporter(), CancellationToken())
    assert strict.changed_cells == 2 and strict.duplicate_keys == 2
    loose = compare_csv(str(old), str(new), "K", True, NullReporter(), CancellationToken())
    assert loose.identical and loose.unchanged == 3
    assert loose.report.name == "b_vs_a_diff (2).csv"  # the first report is kept


def test_compare_requires_key_in_both_files(tmp_path: Path) -> None:
    old = _write(tmp_path / "a.csv", "K,V\n1,2\n")
    new = _write(tmp_path / "b.csv", "X,V\n1,2\n")
    with pytest.raises(ValidationError, match="key column 'K' does not exist in b.csv"):
        compare_csv(str(old), str(new), "K", False, NullReporter(), CancellationToken())


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
