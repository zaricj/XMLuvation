"""Turn per-file XPath results into CSV rows."""

from __future__ import annotations

from collections.abc import Sequence

from .models import ColumnValues

FILENAME_COLUMN = "Filename"
MATCH_COUNT_SUFFIX = " Match Count"


def column_name(header: str, is_value_column: bool) -> str:
    """CSV column name: value XPaths use the header, other XPaths report a match count."""
    return header if is_value_column else f"{header}{MATCH_COUNT_SUFFIX}"


def csv_columns(headers: Sequence[str], value_flags: Sequence[bool]) -> list[str]:
    columns = [FILENAME_COLUMN]
    for header, is_value in zip(headers, value_flags, strict=True):
        name = column_name(header, is_value)
        if name not in columns:
            columns.append(name)
    return columns


def build_rows(
    file_stem: str, columns: Sequence[ColumnValues], group_matches: bool
) -> tuple[list[dict[str, str]], int]:
    """Build CSV rows for one file. Returns ``(rows, total_matches)``.

    * Grouped: one row per file, multiple matches joined with ``"; "``.
    * Ungrouped: one row per match index; shorter columns are padded with ``""``.
    * Count columns only fill the first row.
    * Files without any match produce no rows.
    """
    total_matches = 0
    max_rows = 1
    for column in columns:
        if column.is_value_column:
            if column.values:
                total_matches += column.match_total
                max_rows = max(max_rows, len(column.values))
        else:
            total_matches += column.match_total

    if total_matches <= 0:
        return [], 0

    rows: list[dict[str, str]] = []
    for row_index in range(1 if group_matches else max_rows):
        row = {FILENAME_COLUMN: file_stem}
        has_content = False
        for column in columns:
            name = column_name(column.header, column.is_value_column)
            if column.is_value_column:
                if group_matches:
                    non_empty = [v for v in column.values if v]
                    row[name] = "; ".join(non_empty)
                    has_content = has_content or bool(non_empty)
                elif row_index < len(column.values):
                    row[name] = column.values[row_index]
                    has_content = has_content or bool(column.values[row_index])
                else:
                    row[name] = ""
            else:
                first_row = row_index == 0 and column.match_total > 0
                row[name] = str(column.match_total) if first_row else ""
                has_content = has_content or first_row
        if has_content or group_matches:
            rows.append(row)
    return rows, total_matches
