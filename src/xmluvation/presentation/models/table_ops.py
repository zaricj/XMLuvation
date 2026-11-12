"""Operations on a loaded table: filtering, column statistics, copy and export data.

All functions are pure and vectorized per column (pandas/numpy) and only read the
immutable :class:`TableData`, so they can run on worker threads. Rows are given as
source row indices (``np.ndarray``) in display order; ``None`` means all rows.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from .table_model import TableData


class FilterOp(StrEnum):
    """Conditions of a column filter; the values are the texts shown in the combobox."""

    CONTAINS = "contains"
    NOT_CONTAINS = "does not contain"
    EQUALS = "equals"
    NOT_EQUALS = "does not equal"
    STARTS_WITH = "starts with"
    ENDS_WITH = "ends with"
    REGEX = "matches regex"
    EMPTY = "is empty"
    NOT_EMPTY = "is not empty"
    DUPLICATED = "is duplicated"
    UNIQUE = "is unique"

    @property
    def needs_value(self) -> bool:
        return self not in _NO_VALUE


_NO_VALUE = {FilterOp.EMPTY, FilterOp.NOT_EMPTY, FilterOp.DUPLICATED, FilterOp.UNIQUE}


@dataclass(frozen=True, slots=True)
class ColumnFilter:
    column: int
    op: FilterOp
    value: str = ""
    case_sensitive: bool = False

    @property
    def active(self) -> bool:
        return not self.op.needs_value or bool(self.value)


@dataclass(frozen=True, slots=True)
class FilterSpec:
    """The quick filter (any column) and the column filters; all conditions must hold."""

    text: str = ""
    regex: bool = False
    case_sensitive: bool = False
    columns: tuple[ColumnFilter, ...] = ()

    @property
    def active_columns(self) -> tuple[ColumnFilter, ...]:
        return tuple(f for f in self.columns if f.active)

    @property
    def is_empty(self) -> bool:
        return not self.text and not self.active_columns


def regex_error(spec: FilterSpec) -> str | None:
    """A message for the first invalid regular expression in ``spec``, if any."""
    patterns = [(spec.text, spec.case_sensitive)] if spec.text and spec.regex else []
    patterns += [(f.value, f.case_sensitive) for f in spec.active_columns if f.op is FilterOp.REGEX]
    for pattern, case_sensitive in patterns:
        try:
            re.compile(pattern, 0 if case_sensitive else re.IGNORECASE)
        except re.error as exc:
            return f"Invalid regular expression '{pattern}': {exc}"
    return None


def _series(column: np.ndarray) -> pd.Series:
    return pd.Series(column, copy=False, dtype=object)


def _contains(series: pd.Series, text: str, case: bool, regex: bool) -> np.ndarray:
    return series.str.contains(text, case=case, regex=regex).to_numpy(dtype=bool, na_value=False)


def duplicate_mask(column: np.ndarray) -> np.ndarray:
    """Rows whose (non-empty) value occurs more than once in ``column``."""
    series = _series(column)
    return (series.duplicated(keep=False) & (series.str.strip() != "")).to_numpy(dtype=bool)


def _column_mask(data: TableData, condition: ColumnFilter) -> np.ndarray:
    column = data.columns[condition.column]
    series = _series(column)
    op, value, case = condition.op, condition.value, condition.case_sensitive
    if op in (FilterOp.EMPTY, FilterOp.NOT_EMPTY):
        empty = (series.str.strip() == "").to_numpy(dtype=bool)
        return empty if op is FilterOp.EMPTY else ~empty
    if op in (FilterOp.DUPLICATED, FilterOp.UNIQUE):
        duplicated = duplicate_mask(column)
        return duplicated if op is FilterOp.DUPLICATED else ~duplicated
    if op in (FilterOp.CONTAINS, FilterOp.NOT_CONTAINS):
        found = _contains(series, value, case, regex=False)
        return found if op is FilterOp.CONTAINS else ~found
    if op is FilterOp.REGEX:
        return _contains(series, value, case, regex=True)
    cells = series if case else series.str.casefold()
    target = value if case else value.casefold()
    if op is FilterOp.STARTS_WITH:
        return cells.str.startswith(target).to_numpy(dtype=bool, na_value=False)
    if op is FilterOp.ENDS_WITH:
        return cells.str.endswith(target).to_numpy(dtype=bool, na_value=False)
    equal = (cells == target).to_numpy(dtype=bool)
    return equal if op is FilterOp.EQUALS else ~equal


def filter_spec_rows(data: TableData, spec: FilterSpec) -> np.ndarray | None:
    """Indices of the rows matching ``spec``, in table order (``None`` = all rows).

    Raises ``re.error`` for an invalid regular expression (check :func:`regex_error`).
    """
    if spec.is_empty or data.row_count == 0:
        return None
    mask = np.ones(data.row_count, dtype=bool)
    if spec.text:
        any_column = np.zeros(data.row_count, dtype=bool)
        for column in data.columns:
            any_column |= _contains(_series(column), spec.text, spec.case_sensitive, spec.regex)
        mask &= any_column
    for condition in spec.active_columns:
        if 0 <= condition.column < len(data.columns):
            mask &= _column_mask(data, condition)
    return np.flatnonzero(mask)


# ---------------------------------------------------------------------------- statistics


@dataclass(frozen=True, slots=True)
class ColumnStats:
    name: str
    rows: int
    empty: int
    distinct: int  # distinct non-empty values
    duplicate_values: int  # distinct non-empty values that occur more than once
    duplicate_rows: int  # rows holding such a value
    numeric: bool  # every non-empty value is a number
    minimum: str = ""
    maximum: str = ""
    top: list[tuple[str, int]] = field(default_factory=list)


def column_stats(
    data: TableData, column: int, rows: np.ndarray | None, top: int = 10
) -> ColumnStats:
    """Statistics of ``column`` over ``rows`` (the rows currently shown)."""
    values = data.columns[column] if rows is None else data.columns[column][rows]
    series = _series(values)
    filled = series[series.str.strip() != ""]
    counts = filled.value_counts(sort=True)
    repeated = counts[counts > 1]
    numbers = pd.to_numeric(filled.str.strip(), errors="coerce")
    numeric = bool(len(filled)) and not numbers.isna().any()
    minimum = maximum = ""
    if numeric:
        values_of = numbers.to_numpy(dtype=float)
        minimum = str(filled.iloc[int(values_of.argmin())]).strip()
        maximum = str(filled.iloc[int(values_of.argmax())]).strip()
    elif len(filled):
        minimum, maximum = str(filled.min()), str(filled.max())
    return ColumnStats(
        name=data.headers[column],
        rows=len(series),
        empty=len(series) - len(filled),
        distinct=len(counts),
        duplicate_values=len(repeated),
        duplicate_rows=int(repeated.sum()),
        numeric=numeric,
        minimum=minimum,
        maximum=maximum,
        top=[(str(value), int(count)) for value, count in counts.head(top).items()],
    )


# ---------------------------------------------------------------------------- copy / export


def frame(data: TableData, rows: np.ndarray | None, columns: Sequence[int]) -> pd.DataFrame:
    """The given rows and columns (in that order) as a text DataFrame."""
    # Keyed by position first, so columns with the same header name are all kept.
    picked = {
        i: (data.columns[c] if rows is None else data.columns[c][rows])
        for i, c in enumerate(columns)
    }
    return pd.DataFrame(picked).set_axis([data.headers[c] for c in columns], axis="columns")


def _tsv_cell(text: str) -> str:
    """Quote a cell like Excel does when it contains a tab, line break or quote."""
    if any(c in text for c in '\t\n\r"'):
        return '"' + text.replace('"', '""') + '"'
    return text


def tsv(data: TableData, rows: Sequence[int], columns: Sequence[int], headers: bool = False) -> str:
    """Tab-separated text of the cells, one line per row (pastes into Excel as cells)."""
    index = np.asarray(rows, dtype=np.intp)
    picked = [data.columns[c][index] for c in columns]
    lines = ["\t".join(_tsv_cell(data.headers[c]) for c in columns)] if headers else []
    lines.extend(
        "\t".join(_tsv_cell(str(cell)) for cell in row) for row in zip(*picked, strict=True)
    )
    return "\r\n".join(lines)
