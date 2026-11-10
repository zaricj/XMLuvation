"""Value objects for the structural comparison of two CSV files."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RowChange(StrEnum):
    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    MOVED = "moved"  # matched by key at another position (its cells may differ as well)


@dataclass(frozen=True, slots=True)
class CellChange:
    column: str
    old_value: str
    new_value: str


@dataclass(frozen=True, slots=True)
class RowDifference:
    """One row that differs between two CSV files.

    Row numbers count the header as row 1 (as Excel does); 0 means the row does not
    exist on that side. ``key`` is the row's value in the key column ("" without one).
    """

    change: RowChange
    old_row: int
    new_row: int
    key: str = ""
    cells: tuple[CellChange, ...] = ()
