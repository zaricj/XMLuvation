"""Use case: split one CSV file into several, by row count or by the value of a column.

Rows are streamed: memory use does not depend on the file size. Every part repeats the
header row and keeps the source's delimiter, encoding and exact cell text. Parts are
written into a new folder next to the source, so nothing existing is ever overwritten.
"""

from __future__ import annotations

import shutil
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, TextIO

from ..domain.errors import CsvReadError, ValidationError
from ..domain.filenames import UniqueStems, safe_file_stem
from ..infrastructure import csv_io
from .cancellation import CancellationToken, ProgressReporter
from .output_paths import new_folder

EXCEL_ROWS_PER_SHEET = 1_048_575  # data rows that fit below the header in one Excel sheet
MAX_PARTS_BY_VALUE = 1_000
MAX_OPEN_FILES = 64
_CHECK_EVERY = 10_000
_REPORT_EVERY = 250_000


class SplitMode(StrEnum):
    ROWS = "rows"
    COLUMN = "column"


@dataclass(slots=True)
class SplitResult:
    folder: Path
    files: list[Path] = field(default_factory=list)
    rows: int = 0


def split_csv(
    path_text: str,
    mode: SplitMode,
    *,
    rows_per_file: int = EXCEL_ROWS_PER_SHEET,
    column: str = "",
    reporter: ProgressReporter,
    token: CancellationToken,
) -> SplitResult:
    source = Path(path_text.strip()) if path_text.strip() else None
    if source is None or not source.is_file():
        raise ValidationError("Please select the CSV file to split.", title="CSV file not found")
    if mode is SplitMode.ROWS and rows_per_file < 1:
        raise ValidationError("Rows per file must be at least 1.", title="Invalid row count")

    folder = new_folder(source.parent / f"{source.stem}_split")
    result = SplitResult(folder)
    try:
        with csv_io.csv_rows(source) as (fmt, rows):
            header = next(rows, None)
            if not header:
                raise CsvReadError("The CSV file is empty.", title="CSV Error")
            if mode is SplitMode.ROWS:
                _split_by_rows(source, fmt, header, rows, rows_per_file, result, reporter, token)
            else:
                index = _column_index(header, column)
                _split_by_value(source, fmt, header, rows, index, result, reporter, token)
        if result.rows == 0:
            raise ValidationError(
                "The CSV file has no data rows to split.", title="Nothing to split"
            )
    except BaseException:
        shutil.rmtree(folder, ignore_errors=True)  # the folder was created by this run
        raise
    return result


def _column_index(header: list[str], column: str) -> int:
    names = [h.strip() for h in header]
    if column.strip() not in names:
        raise ValidationError(
            f"Column '{column}' does not exist in the CSV file.", title="Column Not Found"
        )
    return names.index(column.strip())


def _progress(result: SplitResult, reporter: ProgressReporter, token: CancellationToken) -> None:
    if result.rows % _CHECK_EVERY == 0:
        token.raise_if_cancelled()
        if result.rows % _REPORT_EVERY == 0:
            reporter.message(f"Split {result.rows:,} rows into {len(result.files)} file(s)...")


def _split_by_rows(
    source: Path,
    fmt: csv_io.CsvFormat,
    header: list[str],
    rows: Any,
    rows_per_file: int,
    result: SplitResult,
    reporter: ProgressReporter,
    token: CancellationToken,
) -> None:
    handle: TextIO | None = None
    writer: Any = None
    in_part = 0
    try:
        for row in rows:
            if handle is None or in_part == rows_per_file:
                if handle is not None:
                    handle.close()
                part = result.folder / f"{source.stem}_part{len(result.files) + 1:03d}.csv"
                handle = csv_io.open_csv_for_writing(part, fmt)
                writer = csv_io.csv_writer(handle, fmt)
                writer.writerow(header)
                result.files.append(part)
                in_part = 0
            writer.writerow(row)
            in_part += 1
            result.rows += 1
            _progress(result, reporter, token)
    finally:
        if handle is not None:
            handle.close()


class _PartFiles:
    """One output file per value; at most MAX_OPEN_FILES handles open (LRU, reopened to append)."""

    def __init__(self, folder: Path, fmt: csv_io.CsvFormat, header: list[str]) -> None:
        self._folder, self._fmt, self._header = folder, fmt, header
        self._paths: dict[str, Path] = {}
        self._stems = UniqueStems()
        self._open: OrderedDict[str, tuple[TextIO, Any]] = OrderedDict()

    def writer(self, value: str, result: SplitResult) -> Any:
        entry = self._open.get(value)
        if entry is not None:
            self._open.move_to_end(value)
            return entry[1]
        path = self._paths.get(value)
        append = path is not None
        if path is None:
            if len(self._paths) >= MAX_PARTS_BY_VALUE:
                raise ValidationError(
                    f"The column has more than {MAX_PARTS_BY_VALUE:,} different values, which "
                    "would create too many files. Choose another column or split by rows.",
                    title="Too many values",
                )
            path = self._folder / f"{self._stems.claim(safe_file_stem(value))}.csv"
            self._paths[value] = path
            result.files.append(path)
        if len(self._open) >= MAX_OPEN_FILES:
            _value, (old, _writer) = self._open.popitem(last=False)
            old.close()
        handle = csv_io.open_csv_for_writing(path, self._fmt, append=append)
        writer = csv_io.csv_writer(handle, self._fmt)
        if not append:
            writer.writerow(self._header)
        self._open[value] = (handle, writer)
        return writer

    def close(self) -> None:
        for handle, _writer in self._open.values():
            handle.close()
        self._open.clear()


def _split_by_value(
    source: Path,
    fmt: csv_io.CsvFormat,
    header: list[str],
    rows: Any,
    index: int,
    result: SplitResult,
    reporter: ProgressReporter,
    token: CancellationToken,
) -> None:
    parts = _PartFiles(result.folder, fmt, header)
    try:
        for row in rows:
            value = row[index].strip() if index < len(row) else ""
            parts.writer(value, result).writerow(row)
            result.rows += 1
            _progress(result, reporter, token)
    finally:
        parts.close()
    result.files.sort(key=lambda p: p.name.casefold())
