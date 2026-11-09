"""CSV reading/writing helpers (stdlib ``csv`` for exact round-trips, pandas for tables)."""

from __future__ import annotations

import codecs
import csv
import io
import itertools
import os
import tempfile
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

import pandas as pd

from ..domain.errors import CsvReadError, OutputFileError, ValidationError

CANDIDATE_DELIMITERS = (",", ";", "\t", "|")
_UTF8_BOM = b"\xef\xbb\xbf"
_DECODE_CHUNK = 1 << 20
TABLE_CHUNK_ROWS = 100_000


_SNIFF_SAMPLE_CHARS = 64 * 1024
_SNIFF_MAX_RECORDS = 50

DELIMITER_NAMES = {",": "comma", ";": "semicolon", "\t": "tab", "|": "pipe"}


def describe_delimiter(delimiter: str) -> str:
    """Readable form for messages, e.g. ``'\\t' (tab)``."""
    name = DELIMITER_NAMES.get(delimiter)
    shown = "\\t" if delimiter == "\t" else delimiter
    return f"'{shown}' ({name})" if name else f"'{shown}'"


def _field_counts(sample: str, delimiter: str, truncated: bool) -> list[int]:
    """Fields per record when ``sample`` is parsed quote-aware with ``delimiter``."""
    try:
        counts = [
            len(row)
            for row in itertools.islice(
                csv.reader(io.StringIO(sample), delimiter=delimiter), _SNIFF_MAX_RECORDS + 1
            )
            if row
        ]
    except csv.Error:
        return []
    if truncated and len(counts) > 1:
        counts.pop()  # the last record may be cut off mid-way
    return counts[:_SNIFF_MAX_RECORDS]


def detect_delimiter(path: Path) -> str:
    """Detect the delimiter from the start of the file.

    Each candidate is tried with a quote-aware parse: the winner splits the header into
    at least two columns and gives the most records with the header's column count.
    This keeps delimiters inside quoted cells (``||`` in SQL text, multi-line values)
    from winning, which line-based sniffing (``csv.Sniffer``) gets wrong. The sniffer
    only breaks ties.
    """
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        sample = handle.read(_SNIFF_SAMPLE_CHARS)
        truncated = bool(handle.read(1))
    if not sample.strip():
        raise ValidationError("The selected CSV file is empty.", title="Delimiter Detection Error")
    try:
        sniffed = csv.Sniffer().sniff(sample, delimiters="".join(CANDIDATE_DELIMITERS)).delimiter
    except csv.Error:
        sniffed = None

    ranked: list[tuple[float, bool, int, str]] = []
    for delimiter in CANDIDATE_DELIMITERS:
        counts = _field_counts(sample, delimiter, truncated)
        if not counts or counts[0] < 2:
            continue
        consistency = sum(1 for c in counts if c == counts[0]) / len(counts)
        ranked.append((consistency, delimiter == sniffed, counts[0], delimiter))
    if ranked:
        return max(ranked)[3]
    return sniffed or ","


def _has_bom(path: Path) -> bool:
    with path.open("rb") as handle:
        return handle.read(3) == _UTF8_BOM


def _text_encoding(path: Path) -> str:
    """``utf-8-sig`` if the whole file decodes as UTF-8, else ``latin-1``.

    Decodes incrementally in 1 MiB chunks, so memory stays constant for any file size.
    """
    decoder = codecs.getincrementaldecoder("utf-8-sig")()
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(_DECODE_CHUNK):
                decoder.decode(chunk)
        decoder.decode(b"", final=True)
    except UnicodeDecodeError:
        return "latin-1"
    return "utf-8-sig"


def _iter_rows(path: Path, delimiter: str) -> Iterator[list[str]]:
    """Stream CSV rows (never holds more than one row in memory)."""
    with path.open(newline="", encoding=_text_encoding(path)) as handle:
        yield from csv.reader(handle, delimiter=delimiter)


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
    rows = _iter_rows(path, detect_delimiter(path))
    next(rows, None)  # header
    return [row[0].strip() for row in rows if row and row[0].strip()]


@contextmanager
def atomic_writer(path: Path, *, encoding: str, newline: str | None = "") -> Iterator[TextIO]:
    """Yield a handle to a temp file next to ``path``; replace ``path`` with it on success.

    The replacement happens when the ``with`` block ends, so a reader of ``path`` opened
    inside the block is closed first (Windows cannot replace a file that is still open).
    On any error the temp file is removed and ``path`` stays untouched.
    """
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", newline=newline, encoding=encoding) as handle:
            yield handle
        os.replace(tmp_name, path)
    except PermissionError as exc:
        Path(tmp_name).unlink(missing_ok=True)
        raise OutputFileError(
            f"Cannot write {path.name}. Is it open in another program (e.g. Excel)?"
        ) from exc
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def atomic_write_text(path: Path, write: Any, *, newline: str | None = "", encoding: str) -> None:
    """Write via a temp file in the same directory, then replace ``path`` atomically."""
    with atomic_writer(path, encoding=encoding, newline=newline) as handle:
        write(handle)


@dataclass(frozen=True, slots=True)
class CsvFormat:
    """How a CSV file is written, so derived files can be written the same way."""

    delimiter: str
    read_encoding: str  # "utf-8-sig" or "latin-1"
    bom: bool

    @property
    def write_encoding(self) -> str:
        if self.read_encoding == "latin-1":
            return "latin-1"
        return "utf-8-sig" if self.bom else "utf-8"


def csv_format(path: Path) -> CsvFormat:
    return CsvFormat(detect_delimiter(path), _text_encoding(path), _has_bom(path))


@contextmanager
def csv_rows(
    path: Path, fmt: CsvFormat | None = None
) -> Iterator[tuple[CsvFormat, Iterator[list[str]]]]:
    """Stream the rows of a CSV file (header included) together with its format."""
    fmt = fmt or csv_format(path)
    with path.open(newline="", encoding=fmt.read_encoding) as handle:
        yield fmt, csv.reader(handle, delimiter=fmt.delimiter)


def csv_writer(handle: TextIO, fmt: CsvFormat) -> Any:
    return csv.writer(handle, delimiter=fmt.delimiter, lineterminator="\r\n")


def open_csv_for_writing(path: Path, fmt: CsvFormat, *, append: bool = False) -> TextIO:
    """Open ``path`` for writing in ``fmt``'s encoding (a BOM is only written at offset 0)."""
    return path.open("a" if append else "w", newline="", encoding=fmt.write_encoding)


def rewrite_columns(
    source: Path,
    target: Path,
    columns: Sequence[tuple[int, str]],
    expected_header: Sequence[str],
) -> int:
    """Write ``source`` to ``target`` with only ``columns`` (source index, new header name).

    Columns are written in the given order; every data cell keeps its exact text, and the
    delimiter, encoding and BOM of the source are kept. ``target`` may be ``source``: the
    file is replaced atomically. ``expected_header`` guards against the file having changed
    since its header was read. Returns the number of data rows written.
    """
    indices = [index for index, _name in columns]
    fmt = csv_format(source)
    written = 0
    with (
        atomic_writer(target, encoding=fmt.write_encoding) as out,
        csv_rows(source, fmt) as (_fmt, rows),  # closed before ``out`` replaces ``target``
    ):
        first = next(rows, None)
        if not first:
            raise CsvReadError("The CSV file is empty or malformed.", title="CSV Error")
        header = [h.strip() for h in first]
        if header != [h.strip() for h in expected_header]:
            raise ValidationError(
                "The CSV file's columns changed since it was opened. Load it again.",
                title="CSV file changed",
            )
        if any(not 0 <= index < len(header) for index in indices):
            raise ValidationError(
                "Column does not exist in the CSV file.", title="Column Not Found"
            )
        writer = csv_writer(out, fmt)
        writer.writerow([name for _index, name in columns])
        for row in rows:
            writer.writerow([row[i] if i < len(row) else "" for i in indices])
            written += 1
    return written


def drop_column(path: Path, index: int, expected_name: str) -> None:
    """Remove one column and rewrite the file in place (see :func:`rewrite_columns`)."""
    header = read_headers(path)
    if not 0 <= index < len(header) or header[index] != expected_name.strip():
        raise ValidationError(
            f"Column '{expected_name}' does not exist in the CSV file.", title="Column Not Found"
        )
    with csv_rows(path) as (_fmt, rows):
        raw_header = next(rows)
    keep = [(i, raw_header[i]) for i in range(len(raw_header)) if i != index]
    rewrite_columns(path, path, keep, header)


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


def load_table(path: Path, check_cancelled: Callable[[], None] | None = None) -> pd.DataFrame:
    """Read a CSV for display in the table viewer (delimiter detected automatically).

    Every cell is read as text (no type inference, empty cells stay ``""``). The file is
    read in chunks so ``check_cancelled`` can stop a long load; chunks are collected in a
    list and concatenated once at the end (no repeated ``concat`` in the loop).
    """
    delimiter = detect_delimiter(path)
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "latin-1"):
        for engine in ("c", "python"):
            chunks: list[pd.DataFrame] = []
            try:
                with pd.read_csv(
                    path,
                    sep=delimiter,
                    encoding=encoding,
                    engine=engine,
                    quotechar='"',
                    skipinitialspace=True,
                    dtype=str,
                    keep_default_na=False,
                    chunksize=TABLE_CHUNK_ROWS,
                ) as reader:
                    for chunk in reader:
                        if check_cancelled is not None:
                            check_cancelled()
                        chunks.append(chunk)
            except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as exc:
                last_error = exc
                continue
            except pd.errors.EmptyDataError:
                return pd.DataFrame()
            if not chunks:
                return pd.DataFrame()
            if len(chunks) == 1:
                return chunks[0]
            return pd.concat(chunks, ignore_index=True)
    raise CsvReadError(f"Unable to read the CSV file with delimiter '{delimiter}': {last_error}")
