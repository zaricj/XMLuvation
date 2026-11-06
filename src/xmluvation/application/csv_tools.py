"""Use cases on CSV files: conversion, header listing, column removal, table loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..domain.errors import ValidationError
from ..infrastructure import csv_io
from ..infrastructure.tabular_export import OutputFormat, output_path_for, write_table
from .cancellation import ProgressReporter


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


def convert_csv(
    path_text: str, output_type: str, write_index: bool, reporter: ProgressReporter
) -> ConversionResult:
    source = _existing_csv(
        path_text,
        title="CSV Input File Error",
        message="No CSV file has been selected for conversion.\nPlease select a CSV file.",
    )
    if source.suffix.lower() != ".csv":
        raise ValidationError(
            f"Cannot convert from '{source.suffix.lstrip('.')}' files; select a .csv file.",
            title="Unsupported Conversion",
        )
    try:
        fmt = OutputFormat(output_type)
    except ValueError as exc:
        raise ValidationError(f"Unsupported output type: {output_type}") from exc

    delimiter = csv_io.detect_delimiter(source)
    reporter.message(f"Detected delimiter: '{delimiter}'")
    df = csv_io.load_dataframe(source, delimiter)
    if df.empty and len(df.columns) == 0:
        raise ValidationError("The CSV file could be read, but it does not contain any columns.")
    target = output_path_for(source, fmt)
    reporter.message("Starting conversion, please wait...")
    write_table(df, target, fmt, write_index)
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


def load_csv_table(path: Path) -> pd.DataFrame:
    return csv_io.load_table(path)
