"""Use case: compare two CSV files by a key column and write a difference report.

Rows are matched by the key column. If a key occurs more than once, its occurrences are
matched in order (first with first, second with second). The report is a CSV file with
one row per removed or added row and one row per changed cell::

    Status, <key>, Column, Old value, New value

Both files are loaded as text (pandas, all columns ``str``) and compared column by column
with vectorized operations, so memory use is roughly three times the two files' size.
"""

from __future__ import annotations

import gc
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from ..domain.errors import ValidationError
from ..infrastructure import csv_io
from .cancellation import CancellationToken, ProgressReporter
from .output_paths import unique_path

STATUS_REMOVED = "removed"
STATUS_ADDED = "added"
STATUS_CHANGED = "changed"
REPORT_COLUMNS = ("Status", "Key", "Column", "Old value", "New value")
_OCCURRENCE = "\x00occurrence"
_OLD, _NEW = "\x00old", "\x00new"


@dataclass(slots=True)
class CompareResult:
    report: Path
    key: str
    old_rows: int = 0
    new_rows: int = 0
    removed: int = 0
    added: int = 0
    changed_rows: int = 0
    changed_cells: int = 0
    unchanged: int = 0
    duplicate_keys: int = 0
    only_in_old: list[str] = field(default_factory=list)
    only_in_new: list[str] = field(default_factory=list)

    @property
    def identical(self) -> bool:
        return not (self.removed or self.added or self.changed_rows)


def _existing(path_text: str, which: str) -> Path:
    path = Path(path_text.strip()) if path_text.strip() else None
    if path is None or not path.is_file():
        raise ValidationError(f"Please select the {which} CSV file.", title="CSV file not found")
    return path


def _load(path: Path, token: CancellationToken) -> pd.DataFrame:
    df = csv_io.load_table(path, token.raise_if_cancelled)
    df.columns = [str(c).strip() for c in df.columns]
    if df.columns.duplicated().any():
        duplicates = sorted(set(df.columns[df.columns.duplicated()]))
        raise ValidationError(
            f"{path.name} has duplicate column names: {', '.join(duplicates)}",
            title="Duplicate columns",
        )
    return df


def _normalized(series: pd.Series, loose: bool) -> pd.Series:
    series = series.fillna("")
    return series.str.strip().str.casefold() if loose else series


def compare_csv(
    old_text: str,
    new_text: str,
    key: str,
    ignore_case_and_spaces: bool,
    reporter: ProgressReporter,
    token: CancellationToken,
) -> CompareResult:
    old_path, new_path = _existing(old_text, "old"), _existing(new_text, "new")
    key = key.strip()
    if not key:
        raise ValidationError("Please choose the key column.", title="No key column")

    reporter.message(f"Reading {old_path.name} and {new_path.name}...")
    old, new = _load(old_path, token), _load(new_path, token)
    for df, path in ((old, old_path), (new, new_path)):
        if key not in df.columns:
            raise ValidationError(
                f"The key column '{key}' does not exist in {path.name}.", title="Key not found"
            )
    token.raise_if_cancelled()

    report = unique_path(new_path.with_name(f"{new_path.stem}_vs_{old_path.stem}_diff.csv"))
    result = CompareResult(report, key, old_rows=len(old.index), new_rows=len(new.index))
    result.only_in_old = [c for c in old.columns if c not in new.columns]
    result.only_in_new = [c for c in new.columns if c not in old.columns]
    common = [c for c in old.columns if c in new.columns and c != key]
    result.duplicate_keys = int(old[key].duplicated().sum() + new[key].duplicated().sum())

    reporter.message("Comparing rows...")
    match_keys = [key, _OCCURRENCE]
    old[_OCCURRENCE] = old.groupby(key, sort=False).cumcount()
    new[_OCCURRENCE] = new.groupby(key, sort=False).cumcount()
    merged = old[[*match_keys, *common]].merge(
        new[[*match_keys, *common]],
        on=match_keys,
        how="outer",
        suffixes=(_OLD, _NEW),
        indicator=True,
        sort=False,
    )
    del old, new
    token.raise_if_cancelled()

    removed = merged["_merge"] == "left_only"
    added = merged["_merge"] == "right_only"
    both = merged["_merge"] == "both"
    result.removed, result.added = int(removed.sum()), int(added.sum())

    parts: list[pd.DataFrame] = []
    for status, mask in ((STATUS_REMOVED, removed), (STATUS_ADDED, added)):
        if mask.any():
            parts.append(
                pd.DataFrame({"Status": status, "Key": merged.loc[mask, key], "_order": -1})
            )

    changed_any = pd.Series(False, index=merged.index)
    for order, column in enumerate(common):
        old_values, new_values = merged[column + _OLD], merged[column + _NEW]
        differs = both & (
            _normalized(old_values, ignore_case_and_spaces)
            != _normalized(new_values, ignore_case_and_spaces)
        )
        if differs.any():
            changed_any |= differs
            parts.append(
                pd.DataFrame(
                    {
                        "Status": STATUS_CHANGED,
                        "Key": merged.loc[differs, key],
                        "Column": column,
                        "Old value": old_values[differs],
                        "New value": new_values[differs],
                        "_order": order,
                    }
                )
            )
        token.raise_if_cancelled()
    result.changed_rows = int(changed_any.sum())
    result.unchanged = int(both.sum()) - result.changed_rows

    if parts:
        rows = pd.concat(parts)  # one concatenation, after all parts are built
        rows["_row"] = rows.index
        rows = rows.sort_values(["_row", "_order"], kind="stable")
        result.changed_cells = int((rows["Status"] == STATUS_CHANGED).sum())
        rows = rows.reindex(columns=list(REPORT_COLUMNS)).fillna("")
    else:
        rows = pd.DataFrame(columns=list(REPORT_COLUMNS))
    rows = rows.rename(columns={"Key": key if key not in REPORT_COLUMNS else f"Key ({key})"})
    rows.to_csv(report, index=False, encoding="utf-8-sig")
    del merged, rows, parts
    gc.collect()
    return result


def summary_lines(result: CompareResult) -> list[str]:
    if result.identical:
        lines = [f"No differences: {result.unchanged:,} rows match."]
    else:
        lines = [
            f"{result.removed:,} removed, {result.added:,} added, {result.changed_rows:,} changed "
            f"rows ({result.changed_cells:,} cells), {result.unchanged:,} unchanged."
        ]
    if result.only_in_old:
        lines.append(f"Columns only in the old file: {', '.join(result.only_in_old)}")
    if result.only_in_new:
        lines.append(f"Columns only in the new file: {', '.join(result.only_in_new)}")
    if result.duplicate_keys:
        lines.append(
            f"{result.duplicate_keys:,} duplicate key(s) were matched by their order of appearance."
        )
    return lines
