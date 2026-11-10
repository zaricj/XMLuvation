"""Read Excel, HTML, JSON and Markdown tables back into a DataFrame (all cells as text).

The reverse of :mod:`tabular_export`. Cells are kept as text so values like ``007`` or
``1.50`` survive the round trip to CSV unchanged; empty cells stay empty.

* Excel (``.xlsx``/``.xlsm``): the first worksheet (openpyxl).
* HTML: the first ``<table>``; its first row is the header (``th`` or ``td`` cells).
* JSON: a list of objects (``orient="records"``, as written by the converter), a list of
  lists whose first row is the header, or an object of columns (``{"col": [...]}`` or
  ``{"col": {"0": ...}}``).
* Markdown: the first pipe table (``| a | b |`` with a ``|---|---|`` separator row).
"""

from __future__ import annotations

import json
import re
import zipfile
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
from lxml import etree, html

from ..domain.errors import CsvReadError
from .tabular_export import OutputFormat

_SUFFIXES = {
    ".csv": OutputFormat.CSV,
    ".xlsx": OutputFormat.EXCEL,
    ".xlsm": OutputFormat.EXCEL,
    ".html": OutputFormat.HTML,
    ".htm": OutputFormat.HTML,
    ".json": OutputFormat.JSON,
    ".md": OutputFormat.MARKDOWN,
    ".markdown": OutputFormat.MARKDOWN,
}
SUPPORTED_SUFFIXES = tuple(_SUFFIXES)

_MD_SEPARATOR_CELL = re.compile(r"^:?-{1,}:?$")
_MD_SPLIT = re.compile(r"(?<!\\)\|")


def format_of(path: Path) -> OutputFormat | None:
    """The table format of a file, by its extension (``None`` if not supported)."""
    return _SUFFIXES.get(path.suffix.lower())


def read_table(
    path: Path, fmt: OutputFormat, message: Callable[[str], None] = lambda _text: None
) -> pd.DataFrame:
    """Read ``path`` (not CSV) as text cells. ``message`` receives notes for the user."""
    try:
        match fmt:
            case OutputFormat.EXCEL:
                return _read_excel(path, message)
            case OutputFormat.HTML:
                return _read_html(path, message)
            case OutputFormat.JSON:
                return _read_json(path)
            case OutputFormat.MARKDOWN:
                return _read_markdown(path, message)
    except CsvReadError:
        raise
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, etree.ParserError) as exc:
        raise CsvReadError(
            f"Cannot read {path.name} as {fmt.label}:\n{exc}", title="Cannot read file"
        ) from exc
    raise CsvReadError(f"Cannot convert from {fmt.label} files.", title="Cannot read file")


def _frame(header: list[str], rows: list[list[str]]) -> pd.DataFrame:
    """A text DataFrame; short rows are padded, extra cells get generated column names."""
    width = max([len(header), *(len(row) for row in rows)], default=0)
    names = [*header, *(f"Column {n}" for n in range(len(header) + 1, width + 1))]
    names = _unique([name if name else f"Column {n}" for n, name in enumerate(names, 1)])
    padded = [[*row, *([""] * (width - len(row)))] for row in rows]
    return pd.DataFrame(padded, columns=names, dtype=str)


def _unique(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    result = []
    for name in names:
        count = seen.get(name, 0)
        seen[name] = count + 1
        result.append(name if not count else f"{name}.{count}")
    return result


def _text(value: Any) -> str:
    """A JSON value as cell text (objects and arrays stay JSON)."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, dict | list):
        return json.dumps(value, ensure_ascii=False, default=float)  # Decimal -> number
    return str(value)


# ---------------------------------------------------------------------------- Excel


def _read_excel(path: Path, message: Callable[[str], None]) -> pd.DataFrame:
    with pd.ExcelFile(path, engine="openpyxl") as book:
        sheets = [str(name) for name in book.sheet_names]
        if not sheets:
            raise CsvReadError(f"{path.name} contains no worksheets.", title="Cannot read file")
        if len(sheets) > 1:
            message(
                f"The workbook has {len(sheets)} sheets; converting the first one, "
                f"'{sheets[0]}'. Not converted: {', '.join(sheets[1:])}"
            )
        df = pd.read_excel(book, sheet_name=sheets[0], dtype=str, na_filter=False)
    df.columns = _unique(
        [
            f"Column {n}" if str(name).startswith("Unnamed: ") else str(name)
            for n, name in enumerate(df.columns, 1)
        ]
    )
    return df


# ---------------------------------------------------------------------------- HTML


def _read_html(path: Path, message: Callable[[str], None]) -> pd.DataFrame:
    data = path.read_bytes()
    try:
        # pandas writes UTF-8 without a <meta charset>, where lxml would assume Latin-1.
        root = html.document_fromstring(data.decode("utf-8-sig"))
    except UnicodeDecodeError:
        root = html.document_fromstring(data)  # let lxml use the page's declared charset
    tables = root.xpath("//table")
    if not tables:
        raise CsvReadError(f"{path.name} contains no <table>.", title="Cannot read file")
    if len(tables) > 1:
        message(f"The page has {len(tables)} tables; converting the first one.")
    rows = [
        [" ".join(cell.text_content().split()) for cell in row.xpath("./th|./td")]
        for row in tables[0].xpath(".//tr[not(ancestor::table[2])]")
    ]
    rows = [row for row in rows if row]
    if not rows:
        raise CsvReadError(f"The table in {path.name} is empty.", title="Cannot read file")
    return _frame(rows[0], rows[1:])


# ---------------------------------------------------------------------------- JSON


def _read_json(path: Path) -> pd.DataFrame:
    with path.open(encoding="utf-8-sig") as handle:
        # Decimal keeps numbers exactly as written (1.50 stays "1.50").
        data = json.load(handle, parse_float=Decimal)
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        header: list[str] = []
        known: set[str] = set()
        for item in data:
            for key in item:
                if key not in known:
                    known.add(key)
                    header.append(key)
        return _frame(header, [[_text(item.get(key)) for key in header] for item in data])
    if isinstance(data, list) and data and all(isinstance(item, list) for item in data):
        return _frame([_text(v) for v in data[0]], [[_text(v) for v in row] for row in data[1:]])
    if isinstance(data, dict) and data and all(isinstance(v, list | dict) for v in data.values()):
        columns = {
            str(key): list(value.values()) if isinstance(value, dict) else value
            for key, value in data.items()
        }
        height = max(len(values) for values in columns.values())
        return _frame(
            list(columns),
            [
                [_text(values[i]) if i < len(values) else "" for values in columns.values()]
                for i in range(height)
            ],
        )
    raise CsvReadError(
        f"{path.name} does not contain a table. Expected a list of objects "
        '(e.g. [{"Name": "A", "ID": 1}, ...]) or a list of rows.',
        title="Cannot read file",
    )


# ---------------------------------------------------------------------------- Markdown


def _md_cells(line: str) -> list[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]
    return [cell.strip().replace("\\|", "|") for cell in _MD_SPLIT.split(text)]


def _is_separator(line: str) -> bool:
    cells = _md_cells(line)
    return bool(cells) and all(_MD_SEPARATOR_CELL.match(cell) for cell in cells)


def _read_markdown(path: Path, message: Callable[[str], None]) -> pd.DataFrame:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    for index in range(len(lines) - 1):
        if "|" in lines[index] and _is_separator(lines[index + 1]):
            header = _md_cells(lines[index])
            rows = []
            end = index + 2
            while end < len(lines) and "|" in lines[end] and lines[end].strip():
                rows.append(_md_cells(lines[end]))
                end += 1
            if any("|" in line and _is_separator(line) for line in lines[end:]):
                message("The file has more than one table; converting the first one.")
            return _frame(header, rows)
    raise CsvReadError(
        f"{path.name} contains no Markdown table (| a | b | with a |---|---| row below).",
        title="Cannot read file",
    )
