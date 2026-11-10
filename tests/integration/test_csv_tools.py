from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from xmluvation.application.cancellation import NullReporter
from xmluvation.application.csv_tools import (
    convert_csv,
    drop_csv_column,
    parse_delimiter,
    read_csv_headers,
    suggested_output_type,
)
from xmluvation.domain.errors import CsvReadError, ValidationError
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


def test_table_load_reads_text_in_chunks_and_can_be_cancelled(tmp_path: Path, monkeypatch) -> None:
    from xmluvation.application.cancellation import CancellationToken
    from xmluvation.application.csv_tools import load_csv_table
    from xmluvation.domain.errors import Cancelled
    from xmluvation.infrastructure import csv_io

    monkeypatch.setattr(csv_io, "TABLE_CHUNK_ROWS", 2)
    path = tmp_path / "t.csv"
    path.write_text("id;v\n001;\n002;x\n003;NA\n", encoding="utf-8")
    df = load_csv_table(path)
    assert df["id"].tolist() == ["001", "002", "003"]  # text, leading zeros kept
    assert df["v"].tolist() == ["", "x", "NA"]  # no NaN conversion
    token = CancellationToken()
    token.cancel()
    with pytest.raises(Cancelled):
        load_csv_table(path, token)


def test_detect_ignores_delimiters_inside_quoted_multiline_sql(tmp_path: Path) -> None:
    # csv.Sniffer picks "|" here: every SQL line has "||" and no comma.
    sql = "SELECT a||b||c\n  FROM tab t\n WHERE t.x = 1 || 2\n   AND y = 3"
    text = "ID,Statement\n" + "".join(f'{i},"{sql}"\n' for i in range(30))
    assert detect_delimiter(_write(tmp_path / "sql.csv", text)) == ","


def test_detect_semicolon_with_decimal_commas(tmp_path: Path) -> None:
    assert detect_delimiter(_write(tmp_path / "d.csv", "a;b\n1,5;2,25\n3,0;4,1\n")) == ";"


def test_detect_single_column_defaults_to_comma(tmp_path: Path) -> None:
    assert detect_delimiter(_write(tmp_path / "one.csv", "Name\nA\nB\n")) == ","


@pytest.mark.parametrize(
    ("text", "expected"),
    [(",", ","), (" ; ", ";"), ("|", "|"), ("Tab", "\t"), ("\\t", "\t"), ("\t", "\t")],
)
def test_parse_delimiter(text: str, expected: str) -> None:
    assert parse_delimiter(text) == expected


@pytest.mark.parametrize("text", ["", ",,", '"', "abc"])
def test_parse_delimiter_rejects_invalid(text: str) -> None:
    with pytest.raises(ValidationError, match="not a valid delimiter"):
        parse_delimiter(text)


def test_convert_with_manual_delimiter_overrides_detection(tmp_path: Path) -> None:
    src = _write(tmp_path / "m.csv", 'A|B\n"x,y"|1\n"z,w"|2\n')
    result = convert_csv(str(src), "JSON", False, NullReporter(), delimiter_text="|")
    assert result.delimiter == "|"
    assert json.loads(result.output.read_text(encoding="utf-8")) == [
        {"A": "x,y", "B": 1},
        {"A": "z,w", "B": 2},
    ]


# ---------------------------------------------------------------- back to CSV

ROUND_TRIP = "Name;ID;Price\nMüller;007;1.75\nSmith;8;2.25\n"
# The index column's header is "Index" in Excel and blank in HTML and Markdown (so it
# comes back with a generated name); JSON records have no index.
INDEX_HEADER = {"EXCEL": "Index;", "HTML": "Column 1;", "MARKDOWN": "Column 1;", "JSON": ""}


@pytest.mark.parametrize("fmt", ["EXCEL", "HTML", "JSON", "MARKDOWN"])
@pytest.mark.parametrize("index", [False, True])
def test_converted_files_convert_back_to_the_same_csv(tmp_path: Path, fmt: str, index) -> None:
    src = _write(tmp_path / "data.csv", ROUND_TRIP)
    converted = convert_csv(str(src), fmt, index, NullReporter()).output
    back = convert_csv(str(converted), "CSV", False, NullReporter(), delimiter_text=";")
    assert back.output == tmp_path / "data (2).csv"  # the original is never overwritten
    lines = back.output.read_bytes().decode("utf-8-sig").split("\r\n")
    prefix = INDEX_HEADER[fmt] if index else ""
    assert lines[0] == f"{prefix}Name;ID;Price"
    # Reading the CSV infers types (007 -> 7); every format then keeps the cell text.
    rows = ["Müller;7;1.75", "Smith;8;2.25"]
    if prefix:
        rows = [f"{number};{row}" for number, row in enumerate(rows, 1)]
    assert lines[1:] == [*rows, ""]


def test_csv_output_with_index_counts_from_one(tmp_path: Path) -> None:
    src = _write(tmp_path / "t.json", '[{"A": "x"}, {"A": "y"}]')
    out = convert_csv(str(src), "CSV", True, NullReporter()).output
    assert out.read_bytes() == b"\xef\xbb\xbfIndex,A\r\n1,x\r\n2,y\r\n"


def test_excel_import_reads_first_sheet_as_text(tmp_path: Path) -> None:
    import pandas as pd

    book = tmp_path / "book.xlsx"
    with pd.ExcelWriter(book) as writer:
        pd.DataFrame({"Code": ["007", "1"], "N": [1, 2.5], "E": ["a", None]}).to_excel(
            writer, sheet_name="First", index=False
        )
        pd.DataFrame({"Other": [1]}).to_excel(writer, sheet_name="Second", index=False)
    messages: list[str] = []

    class Collect(NullReporter):
        def message(self, text: str) -> None:
            messages.append(text)

    out = convert_csv(str(book), "CSV", False, Collect()).output
    assert out.read_bytes().decode("utf-8-sig") == "Code,N,E\r\n007,1,a\r\n1,2.5,\r\n"
    assert any("Not converted: Second" in m for m in messages)


def test_json_shapes_and_markdown_escapes(tmp_path: Path) -> None:
    rows = _write(tmp_path / "rows.json", '[["A", "B"], [1.50, true], [null, {"k": 1}]]')
    out = convert_csv(str(rows), "CSV", False, NullReporter()).output
    assert out.read_bytes().decode("utf-8-sig") == 'A,B\r\n1.50,true\r\n,"{""k"": 1}"\r\n'

    columns = _write(tmp_path / "cols.json", '{"A": {"0": "x", "1": "y"}, "B": ["1"]}')
    out = convert_csv(str(columns), "CSV", False, NullReporter()).output
    assert out.read_bytes().decode("utf-8-sig") == "A,B\r\nx,1\r\ny,\r\n"

    md = _write(
        tmp_path / "t.md",
        "Intro text\n\n| A | B |\n|:--|--:|\n| a \\| b | 2 |\n| c |\n\nAfter\n",
    )
    out = convert_csv(str(md), "CSV", False, NullReporter()).output
    assert out.read_bytes().decode("utf-8-sig") == "A,B\r\na | b,2\r\nc,\r\n"


def test_unsupported_conversions_are_rejected(tmp_path: Path) -> None:
    src = _write(tmp_path / "t.csv", "A\n1\n")
    with pytest.raises(ValidationError, match="already is a CSV file"):
        convert_csv(str(src), "CSV", False, NullReporter())
    with pytest.raises(ValidationError, match="Cannot convert from 'txt'"):
        convert_csv(str(_write(tmp_path / "t.txt", "A")), "CSV", False, NullReporter())
    with pytest.raises(CsvReadError, match="no <table>"):
        convert_csv(str(_write(tmp_path / "t.html", "<p>x</p>")), "CSV", False, NullReporter())
    with pytest.raises(CsvReadError, match="does not contain a table"):
        convert_csv(str(_write(tmp_path / "t.json", '{"a": 1}')), "CSV", False, NullReporter())
    with pytest.raises(CsvReadError, match="Cannot read"):
        convert_csv(str(_write(tmp_path / "t.xlsx", "no zip")), "CSV", False, NullReporter())


@pytest.mark.parametrize(
    ("path", "current", "expected"),
    [
        ("a.xlsx", "EXCEL", "CSV"),
        ("a.JSON", "HTML", "CSV"),
        ("a.md", "CSV", None),
        ("a.csv", "CSV", "EXCEL"),
        ("a.csv", "JSON", None),
        ("a.txt", "JSON", None),
        ("", "JSON", None),
    ],
)
def test_suggested_output_type(path: str, current: str, expected: str | None) -> None:
    assert suggested_output_type(path, current) == expected
