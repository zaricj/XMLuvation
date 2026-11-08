from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from xmluvation.application.cancellation import NullReporter
from xmluvation.application.csv_tools import convert_csv, drop_csv_column, read_csv_headers
from xmluvation.domain.errors import ValidationError
from xmluvation.infrastructure.csv_io import detect_delimiter
from xmluvation.infrastructure.tabular_export import excel_table_name


def _write(path: Path, text: str, bom: bool = False) -> Path:
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
    return path


def test_drop_column_preserves_other_cells_exactly(tmp_path: Path) -> None:
    src = _write(
        tmp_path / "d.csv",
        'ID;Name;Empty;Big\r\n0042;Müller;;12345678901234567890\r\n007;"a;b";;1.50\r\n',
        bom=True,
    )
    assert read_csv_headers(str(src)) == ["ID", "Name", "Empty", "Big"]
    drop_csv_column(str(src), "Name", 1)
    raw = src.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    assert raw.decode("utf-8-sig") == "ID;Empty;Big\r\n0042;;12345678901234567890\r\n007;;1.50\r\n"


def test_drop_column_rejects_stale_selection(tmp_path: Path) -> None:
    src = _write(tmp_path / "d.csv", "A,B\n1,2\n")
    with pytest.raises(ValidationError, match="does not exist"):
        drop_csv_column(str(src), "C", 1)


def test_read_headers_ignores_non_csv(tmp_path: Path) -> None:
    assert read_csv_headers(str(_write(tmp_path / "x.txt", "A,B\n"))) == []
    assert read_csv_headers("") == []


@pytest.mark.parametrize("fmt", ["EXCEL", "HTML", "JSON", "MARKDOWN"])
def test_convert_all_formats(tmp_path: Path, fmt: str) -> None:
    src = _write(tmp_path / "Report 2024.csv", "Filename,ID\nA,1\nB,2\n")
    result = convert_csv(str(src), fmt, False, NullReporter())
    assert result.output.exists()
    assert result.delimiter == ","
    if fmt == "JSON":
        assert json.loads(result.output.read_text(encoding="utf-8")) == [
            {"Filename": "A", "ID": 1},
            {"Filename": "B", "ID": 2},
        ]
    if fmt == "EXCEL":
        with zipfile.ZipFile(result.output) as archive:
            table = archive.read("xl/tables/table1.xml").decode("utf-8")
        assert 'name="Report_2024"' in table and 'ref="A1:B3"' in table


def test_convert_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        convert_csv(str(tmp_path / "missing.csv"), "JSON", False, NullReporter())


def test_detect_semicolon(tmp_path: Path) -> None:
    assert detect_delimiter(_write(tmp_path / "s.csv", "a;b;c\n1;2;3\n")) == ";"


@pytest.mark.parametrize(
    ("sheet", "expected"), [("Report 2024", "Report_2024"), ("2024", "T_2024"), ("ok", "ok")]
)
def test_excel_table_name(sheet: str, expected: str) -> None:
    assert excel_table_name(sheet) == expected
