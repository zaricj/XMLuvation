"""Use case: compare two CSV files row by row and cell by cell.

Rows are aligned by their content and paired by an optional key column (see
``infrastructure/csv_diff.py``). The result holds both files side by side for display
and, when the files differ, a report CSV saved next to the new file with one row per
removed, added or moved row and one row per changed cell::

    Status, Old row, New row, [<key>,] Column, Old value, New value

Row numbers count the header as row 1, as in a spreadsheet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..domain.csv_checks import RowChange, RowDifference
from ..domain.errors import ValidationError
from ..domain.text_diff import TextDiff
from ..infrastructure import csv_diff, csv_io
from .cancellation import CancellationToken, ProgressReporter
from .output_paths import replace_report

# Larger files are compared and reported, but not shown side by side.
MAX_TEXT_DIFF_BYTES = 16 * 1024 * 1024


@dataclass(slots=True)
class CompareResult:
    old: Path
    new: Path
    key: str = ""
    report: Path | None = None
    old_rows: int = 0
    new_rows: int = 0
    removed: int = 0
    added: int = 0
    changed_rows: int = 0
    moved: int = 0
    changed_cells: int = 0
    unchanged: int = 0
    duplicate_keys: int = 0
    only_in_old: list[str] = field(default_factory=list)
    only_in_new: list[str] = field(default_factory=list)
    text_diff: TextDiff | None = None
    text_diff_note: str = ""  # why ``text_diff`` is missing

    @property
    def identical(self) -> bool:
        return not (self.removed or self.added or self.changed_rows or self.moved)


def _existing(path_text: str, which: str) -> Path:
    path = Path(path_text.strip()) if path_text.strip() else None
    if path is None or not path.is_file():
        raise ValidationError(f"Please select the {which} CSV file.", title="CSV file not found")
    return path


def _report_columns(key: str) -> list[str]:
    columns = ["Status", "Old row", "New row", "Column", "Old value", "New value"]
    if key:
        columns.insert(3, key if key not in columns else f"Key ({key})")
    return columns


def _report_rows(differences: list[RowDifference], key: str) -> list[list[object]]:
    rows: list[list[object]] = []
    for d in differences:
        start: list[object] = [d.change, d.old_row or "", d.new_row or ""]
        if key:
            start.append(d.key)
        if d.cells:
            rows.extend([*start, c.column, c.old_value, c.new_value] for c in d.cells)
        else:
            rows.append([*start, "", "", ""])
    return rows


def compare_csv(
    old_text: str,
    new_text: str,
    key: str,
    ignore_case_and_spaces: bool,
    reporter: ProgressReporter,
    token: CancellationToken,
) -> CompareResult:
    """Compare two CSV files; ``key`` ("" for none) is the column that identifies a row."""
    old_path, new_path = _existing(old_text, "old"), _existing(new_text, "new")
    key = key.strip()
    too_large = [p.name for p in (old_path, new_path) if p.stat().st_size > MAX_TEXT_DIFF_BYTES]

    reporter.message(f"Comparing {old_path.name} with {new_path.name}...")
    outcome = csv_diff.diff_files(
        old_path,
        new_path,
        key=key,
        loose=ignore_case_and_spaces,
        build_view=not too_large,
        check_cancelled=token.raise_if_cancelled,
    )
    result = CompareResult(
        old_path,
        new_path,
        key,
        old_rows=outcome.old_rows,
        new_rows=outcome.new_rows,
        unchanged=outcome.unchanged,
        duplicate_keys=outcome.duplicate_keys,
        only_in_old=outcome.only_in_old,
        only_in_new=outcome.only_in_new,
        text_diff=outcome.text_diff,
    )
    for d in outcome.differences:
        if d.change is RowChange.REMOVED:
            result.removed += 1
        elif d.change is RowChange.ADDED:
            result.added += 1
        elif d.change is RowChange.MOVED:
            result.moved += 1
        else:
            result.changed_rows += 1
        result.changed_cells += len(d.cells)
    if too_large:
        result.text_diff_note = (
            f"{' and '.join(too_large)} {'is' if len(too_large) == 1 else 'are'} larger than "
            f"{MAX_TEXT_DIFF_BYTES // (1024 * 1024)} MB, so the files are not shown side by "
            "side. The report lists every difference."
        )
    token.raise_if_cancelled()
    # The previous report of these two files is replaced (or removed if they now match).
    report = replace_report(new_path.with_name(f"{new_path.stem}_vs_{old_path.stem}_diff.csv"))
    if outcome.differences:
        result.report = report
        csv_io.write_report(
            result.report, _report_columns(key), _report_rows(outcome.differences, key)
        )
    return result


def summary_lines(result: CompareResult) -> list[str]:
    if result.identical:
        lines = [f"No differences: {result.unchanged:,} rows match."]
    else:
        moved = f", {result.moved:,} moved" if result.moved else ""
        lines = [
            f"{result.removed:,} removed, {result.added:,} added, {result.changed_rows:,} changed"
            f"{moved} rows ({result.changed_cells:,} changed cells), "
            f"{result.unchanged:,} unchanged."
        ]
    if not result.key and not result.identical:
        lines.append("No key column: changed rows were paired by their position.")
    if result.only_in_old:
        lines.append(f"Columns only in the old file: {', '.join(result.only_in_old)}")
    if result.only_in_new:
        lines.append(f"Columns only in the new file: {', '.join(result.only_in_new)}")
    if result.duplicate_keys:
        lines.append(
            f"{result.duplicate_keys:,} duplicate key(s) were matched by their order of appearance."
        )
    return lines
