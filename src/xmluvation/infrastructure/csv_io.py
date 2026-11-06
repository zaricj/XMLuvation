"""CSV reading/writing helpers (stdlib ``csv`` for exact round-trips, pandas for tables)."""

from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd

from ..domain.errors import CsvReadError, OutputFileError, ValidationError

CANDIDATE_DELIMITERS = (",", ";", "\t", "|")
_UTF8_BOM = b"\xef\xbb\xbf"


def detect_delimiter(path: Path) -> str:
    """Sniff the delimiter from the first 4 KiB, falling back to the most frequent candidate."""
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        sample = handle.read(4096)
    if not sample.strip():
        raise ValidationError("The selected CSV file is empty.", title="Delimiter Detection Error")
    try:
        return csv.Sniffer().sniff(sample, delimiters="".join(CANDIDATE_DELIMITERS)).delimiter
    except csv.Error:
        lines = [line for line in sample.splitlines() if line.strip()][:10]
        ranked: list[tuple[int, int, str]] = []
        for delimiter in CANDIDATE_DELIMITERS:
            counts = [c for c in (line.count(delimiter) for line in lines) if c > 0]
            if counts:
                ranked.append((len(counts), sum(counts), delimiter))
        return max(ranked)[2] if ranked else ","


def _has_bom(path: Path) -> bool:
    with path.open("rb") as handle:
        return handle.read(3) == _UTF8_BOM


def _read_rows(path: Path, delimiter: str) -> list[list[str]]:
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            with path.open(newline="", encoding=encoding) as handle:
                return list(csv.reader(handle, delimiter=delimiter))
        except UnicodeDecodeError:
            continue
    raise CsvReadError(f"Cannot decode {path.name} as UTF-8 or Latin-1.")


def read_headers(path: Path) -> list[str]:
    """Header row of a CSV file (only the first line is read)."""
    delimiter = detect_delimiter(path)
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            with path.open(newline="", encoding=encoding) as handle:
                return [h.strip() for h in next(csv.reader(handle, delimiter=delimiter), [])]
        except UnicodeDecodeError:
            continue
    raise CsvReadError(f"Cannot decode {path.name} as UTF-8 or Latin-1.")


def read_first_column(path: Path) -> list[str]:
    """Values of the first column, header row excluded, empty cells skipped."""
    rows = _read_rows(path, detect_delimiter(path))
    return [row[0].strip() for row in rows[1:] if row and row[0].strip()]


def atomic_write_text(path: Path, write: Any, *, newline: str | None = "", encoding: str) -> None:
    """Write via a temp file in the same directory, then replace ``path`` atomically."""
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", newline=newline, encoding=encoding) as handle:
            write(handle)
        os.replace(tmp_name, path)
    except PermissionError as exc:
        Path(tmp_name).unlink(missing_ok=True)
        raise OutputFileError(
            f"Cannot write {path.name}. Is it open in another program (e.g. Excel)?"
        ) from exc
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def drop_column(path: Path, index: int, expected_name: str) -> None:
    """Remove one column and rewrite the file, keeping every other cell's text unchanged.

    The delimiter and a UTF-8 BOM are preserved. ``expected_name`` guards against the
    file having changed since its headers were read.
    """
    delimiter = detect_delimiter(path)
    rows = _read_rows(path, delimiter)
    if not rows:
        raise CsvReadError("The CSV file is empty or malformed.", title="CSV Error")
    header = [h.strip() for h in rows[0]]
    if not 0 <= index < len(header) or header[index] != expected_name.strip():
        raise ValidationError(
            f"Column '{expected_name}' does not exist in the CSV file.", title="Column Not Found"
        )
    trimmed = [row[:index] + row[index + 1 :] for row in rows]
    encoding = "utf-8-sig" if _has_bom(path) else "utf-8"

    def write(handle: Any) -> None:
        csv.writer(handle, delimiter=delimiter, lineterminator="\r\n").writerows(trimmed)

    atomic_write_text(path, write, encoding=encoding)


def load_dataframe(path: Path, delimiter: str) -> pd.DataFrame:
    """Read a CSV for conversion: fast C engine first, tolerant Python engine as fallback."""
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "latin-1"):
        for engine in ("c", "python"):
            try:
                return pd.read_csv(
                    path,
                    sep=delimiter,
                    encoding=encoding,
                    engine=engine,
                    quotechar='"',
                    skipinitialspace=True,
                )
            except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as exc:
                last_error = exc
    raise CsvReadError(f"Unable to read the CSV file with delimiter '{delimiter}': {last_error}")


def load_table(path: Path) -> pd.DataFrame:
    """Read a CSV for display in the table viewer (delimiter detected automatically)."""
    return load_dataframe(path, detect_delimiter(path))
