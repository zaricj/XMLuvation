"""Use cases on CSV files: conversion (to and from CSV), header listing, column removal,
table loading."""

from __future__ import annotations

import gc
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..domain.errors import ValidationError
from ..infrastructure import csv_io, tabular_import
from ..infrastructure.tabular_export import OutputFormat, output_path_for, write_table
from .cancellation import CancellationToken, ProgressReporter
from .output_paths import unique_path


@dataclass(frozen=True, slots=True)
class ConversionResult:
    source: Path
    output: Path
    delimiter: str


def _existing_csv(path_text: str, *, title: str, message: str) -> Path:
    path = Path(path_text.strip()) if path_text.strip() else None
    if path is None or not path.is_file():
        raise ValidationError(message, title=title)
    return path


def parse_delimiter(text: str) -> str:
    r"""A user-entered delimiter: one character, or ``Tab`` / ``\t`` for a tab."""
    if text == "\t" or text.strip().casefold() in {"tab", r"\t"}:
        return "\t"
    value = text if text == " " else text.strip()
    if len(value) != 1 or value in {'"', "\r", "\n"}:
        raise ValidationError(
            f"'{text}' is not a valid delimiter.\n"
            "Enter a single character such as , ; or |, or 'Tab' for a tab.",
            title="Invalid Delimiter",
        )
    return value


def suggested_output_type(path_text: str, current: str) -> str | None:
    """The output type to switch to after the input file changed, if ``current`` no longer fits.

    A non-CSV input (Excel, HTML, ...) is converted to CSV; a CSV input cannot be.
    """
    text = path_text.strip()
    source = tabular_import.format_of(Path(text)) if text else None
    if source is None:
        return None
    if source is OutputFormat.CSV and current == OutputFormat.CSV:
        return OutputFormat.EXCEL.value
    if source is not OutputFormat.CSV and current != OutputFormat.CSV:
        return OutputFormat.CSV.value
    return None


def convert_csv(
    path_text: str,
    output_type: str,
    write_index: bool,
    reporter: ProgressReporter,
    delimiter_text: str | None = None,
) -> ConversionResult:
    """Convert a CSV file to another format, or an Excel/HTML/JSON/Markdown table to CSV.

    ``delimiter_text`` is the delimiter of a CSV input (instead of detecting it) or of a
    CSV output (instead of a comma). A CSV output never overwrites an existing file.
    """
    source = _existing_csv(
        path_text,
        title="Input File Error",
        message="No file has been selected for conversion.\nPlease select a file to convert.",
    )
    source_format = tabular_import.format_of(source)
    if source_format is None:
        raise ValidationError(
            f"Cannot convert from '{source.suffix.lstrip('.')}' files; select a CSV, "
            "Excel (.xlsx), HTML, JSON or Markdown file.",
            title="Unsupported Conversion",
        )
    try:
        fmt = OutputFormat(output_type)
    except ValueError as exc:
        raise ValidationError(f"Unsupported output type: {output_type}") from exc
    if fmt is source_format:
        raise ValidationError(
            f"{source.name} already is a {fmt.label} file. Choose another output format.",
            title="Unsupported Conversion",
        )

    delimiter = parse_delimiter(delimiter_text) if delimiter_text is not None else None
    if source_format is OutputFormat.CSV:
        if delimiter is not None:
            reporter.message(f"Using delimiter: {csv_io.describe_delimiter(delimiter)}")
        else:
            delimiter = csv_io.detect_delimiter(source)
            reporter.message(f"Detected delimiter: {csv_io.describe_delimiter(delimiter)}")
        df = csv_io.load_dataframe(source, delimiter)
    else:
        reporter.message(f"Reading {source.name} ({source_format.label})...")
        df = tabular_import.read_table(source, source_format, reporter.message)
        delimiter = delimiter if delimiter is not None else ","
    try:
        if df.empty and len(df.columns) == 0:
            raise ValidationError(
                f"{source.name} could be read, but it does not contain any columns."
            )
        target = output_path_for(source, fmt)
        if fmt is OutputFormat.CSV:
            target = unique_path(target)  # e.g. the CSV this file was made from
            reporter.message(f"Writing CSV with delimiter {csv_io.describe_delimiter(delimiter)}")
        reporter.message("Starting conversion, please wait...")
        write_table(df, target, fmt, write_index, delimiter)
    finally:
        del df
        gc.collect()  # the DataFrame and writer buffers can be several times the CSV size
    return ConversionResult(source, target, delimiter)


def read_csv_headers(path_text: str) -> list[str]:
    """Headers of a ``.csv`` file, or ``[]`` if the path is not an existing CSV file."""
    path = Path(path_text.strip()) if path_text.strip() else None
    if path is None or path.suffix.lower() != ".csv" or not path.is_file():
        return []
    return csv_io.read_headers(path)


def drop_csv_column(path_text: str, column: str, index: int) -> None:
    path = _existing_csv(
        path_text, title="CSV file not found", message="Please select a CSV file first."
    )
    if not column or index < 0:
        raise ValidationError(
            "Please select a header from the combobox first.", title="Header not selected"
        )
    csv_io.drop_column(path, index, column)


@dataclass(frozen=True, slots=True)
class ColumnEdit:
    """One output column: its position in the source file and its (new) header name."""

    source_index: int
    name: str


@dataclass(frozen=True, slots=True)
class ColumnEditResult:
    output: Path
    columns: int
    removed: int
    rows: int


def save_column_edits(
    path_text: str,
    edits: Sequence[ColumnEdit],
    original_header: Sequence[str],
    overwrite: bool,
) -> ColumnEditResult:
    """Write the CSV with the given columns, in the given order and with the given names.

    The result goes to ``<name>_edited.csv`` (never overwriting an existing file) unless
    ``overwrite`` is set, in which case the source is replaced atomically.
    """
    source = _existing_csv(
        path_text, title="CSV file not found", message="Please select a CSV file first."
    )
    if not edits:
        raise ValidationError(
            "Keep at least one column; a CSV file without columns cannot be saved.",
            title="No columns selected",
        )
    names = [edit.name.strip() for edit in edits]
    if any(not name for name in names):
        raise ValidationError("Column names cannot be empty.", title="Empty column name")
    counts = Counter(name.casefold() for name in names)
    duplicates = sorted({name for name in names if counts[name.casefold()] > 1})
    if duplicates:
        raise ValidationError(
            f"Each column needs a unique name. Duplicate: {', '.join(duplicates)}",
            title="Duplicate column names",
        )
    target = source if overwrite else unique_path(source.with_name(f"{source.stem}_edited.csv"))
    rows = csv_io.rewrite_columns(
        source,
        target,
        [(edit.source_index, name) for edit, name in zip(edits, names, strict=True)],
        original_header,
    )
    removed = len(original_header) - len({edit.source_index for edit in edits})
    return ColumnEditResult(target, len(edits), removed, rows)


def load_csv_table(path: Path, token: CancellationToken | None = None) -> pd.DataFrame:
    """All cells as text, for display. Raises ``Cancelled`` between chunks if cancelled."""
    check = token.raise_if_cancelled if token is not None else None
    try:
        return csv_io.load_table(path, check)
    except BaseException:
        gc.collect()  # free chunks read before the failure/cancellation
        raise
