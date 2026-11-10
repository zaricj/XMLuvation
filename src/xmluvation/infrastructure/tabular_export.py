"""Write a DataFrame as Excel, HTML, JSON, Markdown or CSV."""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import Path

import pandas as pd

from ..domain.errors import ValidationError

EXCEL_MAX_ROWS = 1_048_576  # including the header row
EXCEL_MAX_COLUMNS = 16_384
_INVALID_SHEET_CHARS = set("[]:*?/\\")


class OutputFormat(StrEnum):
    """Values match the items of the conversion combobox."""

    EXCEL = "EXCEL"
    HTML = "HTML"
    JSON = "JSON"
    MARKDOWN = "MARKDOWN"
    CSV = "CSV"

    @property
    def extension(self) -> str:
        return {
            "EXCEL": "xlsx",
            "HTML": "html",
            "JSON": "json",
            "MARKDOWN": "md",
            "CSV": "csv",
        }[self.value]

    @property
    def label(self) -> str:
        """Name for messages."""
        return {"EXCEL": "Excel", "MARKDOWN": "Markdown"}.get(self.value, self.value)


def excel_sheet_name(file_path: Path) -> str:
    """Sheet names must be <= 31 characters without ``[]:*?/\\``."""
    name = "".join("_" if c in _INVALID_SHEET_CHARS else c for c in file_path.stem).strip()
    return (name or "Result")[:31]


def excel_table_name(sheet: str) -> str:
    """Excel table names allow letters, digits, ``_`` and ``.`` and must not start with a digit.

    Invalid names make xlsxwriter skip the table, so unsupported characters are replaced.
    """
    name = re.sub(r"[^\w.]", "_", sheet)[:30]
    return name if name and not name[0].isdigit() else f"T_{name}"[:30]


def output_path_for(source: Path, fmt: OutputFormat) -> Path:
    return source.with_suffix(f".{fmt.extension}")


def write_table(
    df: pd.DataFrame,
    target: Path,
    fmt: OutputFormat,
    write_index: bool,
    delimiter: str = ",",
) -> None:
    """``delimiter`` is used for CSV only. The index column, if written, counts from 1."""
    if write_index:
        df = df.set_axis(pd.RangeIndex(1, len(df) + 1), axis="index")
    match fmt:
        case OutputFormat.CSV:
            # Like the app's reports: UTF-8 with BOM (Excel shows umlauts), CRLF lines.
            df.to_csv(
                target,
                sep=delimiter,
                index=write_index,
                index_label="Index" if write_index else None,
                encoding="utf-8-sig",
                lineterminator="\r\n",
            )
        case OutputFormat.HTML:
            df.to_html(target, index=write_index)
        case OutputFormat.JSON:
            df.to_json(target, orient="records", force_ascii=False, indent=2)
        case OutputFormat.MARKDOWN:
            df.to_markdown(target, index=write_index)
        case OutputFormat.EXCEL:
            _write_excel(df, target, write_index)


def _write_excel(df: pd.DataFrame, target: Path, write_index: bool) -> None:
    rows, columns = df.shape
    columns += 1 if write_index else 0
    if rows + 1 > EXCEL_MAX_ROWS or columns > EXCEL_MAX_COLUMNS:
        raise ValidationError(
            f"The table has {rows:,} rows and {columns:,} columns; Excel supports at most "
            f"{EXCEL_MAX_ROWS - 1:,} data rows and {EXCEL_MAX_COLUMNS:,} columns. "
            "Convert to another format instead.",
            title="Too large for Excel",
        )
    sheet = excel_sheet_name(target)
    with pd.ExcelWriter(target, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=sheet, index=write_index)
        worksheet = writer.sheets[sheet]
        settings = [{"header": str(col)} for col in df.columns]
        if write_index:
            settings.insert(0, {"header": str(df.index.name or "Index")})
        worksheet.add_table(
            0,
            0,
            rows,
            columns - 1,
            {
                "columns": settings,
                "style": "Table Style Medium 16",
                "name": excel_table_name(sheet),
                "autofilter": True,
            },
        )
        worksheet.set_column(0, columns - 1, 18)
