"""Use case: evaluate XPath expressions over a folder of XML files and write one CSV file."""

from __future__ import annotations

import csv
import logging
import os
import time
from collections import deque
from collections.abc import Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from ..domain.errors import OutputFileError, ValidationError, XmlParseError
from ..domain.models import ExportResult, ExportSpec, FileError
from ..domain.rows import csv_columns
from ..domain.xpath_text import duplicate_headers, is_value_xpath, parse_headers
from ..infrastructure.xml_engine import (
    FileOutcome,
    XPathCache,
    evaluate_file,
    list_xml_files,
    validate_xpath,
)
from .cancellation import CancellationToken, ProgressReporter

log = logging.getLogger(__name__)

MAX_WORKERS = 32


def default_worker_count() -> int:
    return min(os.cpu_count() or 4, MAX_WORKERS)


def make_spec(
    folder: str,
    xpaths: Sequence[str],
    headers_text: str,
    output: str,
    group_matches: bool,
    max_workers: int | None = None,
) -> ExportSpec:
    """Validate raw UI input and build an :class:`ExportSpec`. Raises :class:`ValidationError`."""
    folder_path = Path(folder.strip()) if folder.strip() else None
    if folder_path is None or not folder_path.is_dir():
        raise ValidationError(
            "Please select a valid XML folder directory.", title="Invalid XML Folder"
        )
    output_text = output.strip()
    if not output_text:
        raise ValidationError("Please select a CSV output directory.", title="Invalid CSV Output")
    output_path = Path(output_text)
    if output_path.suffix.lower() != ".csv":
        raise ValidationError(
            "Please set a valid output file path ending in .csv.",
            title="CSV Output Path is Invalid",
        )
    if not xpaths:
        raise ValidationError(
            "Please add at least one XPath expression.", title="No XPath Expressions"
        )
    headers = parse_headers(headers_text)
    if not headers:
        raise ValidationError(
            "No headers or XPath expressions found. Please add expressions and headers.",
            title="Empty Configuration",
        )
    if len(headers) != len(xpaths):
        raise ValidationError(
            f"CSV headers length ({len(headers)}) doesn't match XPath expressions "
            f"length ({len(xpaths)})",
            title="Header/XPath Length Mismatch",
        )
    duplicates = duplicate_headers(headers)
    if duplicates:
        raise ValidationError(
            "Each CSV header must be unique, otherwise columns overwrite each other.\n"
            f"Duplicate: {', '.join(duplicates)}",
            title="Duplicate CSV Headers",
        )
    for xpath in xpaths:
        validate_xpath(xpath)
    return ExportSpec(
        folder=folder_path,
        xpaths=tuple(xpaths),
        headers=tuple(headers),
        output=output_path,
        group_matches=group_matches,
        max_workers=max(1, min(max_workers or default_worker_count(), MAX_WORKERS)),
    )


def _process(path: Path, spec: ExportSpec, cache: XPathCache) -> FileOutcome:
    return evaluate_file(path, spec.xpaths, spec.headers, spec.group_matches, cache)


def run_export(
    spec: ExportSpec, reporter: ProgressReporter, token: CancellationToken
) -> ExportResult:
    """Run the export. Rows are written in file-name order.

    Files are processed in parallel with a bounded number of files in flight, and
    results are written by this thread only. Per-file problems are collected in
    ``ExportResult.errors``; a failing output file raises :class:`OutputFileError`.
    On cancellation the CSV contains the rows written so far.
    """
    started = time.perf_counter()
    result = ExportResult(output=spec.output)
    files = list_xml_files(spec.folder)
    result.total_files = len(files)
    if not files:
        raise ValidationError("No XML files found in selected folder.", title="No XML Files Found")

    columns = csv_columns(spec.headers, [is_value_xpath(x) for x in spec.xpaths])
    reporter.message(
        f"Starting search and CSV export of {len(files)} files with {spec.max_workers} threads..."
    )
    try:
        spec.output.parent.mkdir(parents=True, exist_ok=True)
        handle = spec.output.open("w", newline="", encoding="utf-8", buffering=1_048_576)
    except PermissionError as exc:
        raise OutputFileError(
            f"Cannot write {spec.output}.\nIs the file open in another program (e.g. Excel)?"
        ) from exc
    except OSError as exc:
        raise OutputFileError(f"Cannot write {spec.output}: {exc}") from exc

    cache = XPathCache()
    window = spec.max_workers * 2
    with handle, ThreadPoolExecutor(spec.max_workers, thread_name_prefix="XMLProcessor") as pool:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        pending: deque[tuple[Path, Future[FileOutcome]]] = deque()
        next_index = 0
        try:
            while pending or next_index < len(files):
                while not token.cancelled and next_index < len(files) and len(pending) < window:
                    path = files[next_index]
                    pending.append((path, pool.submit(_process, path, spec, cache)))
                    next_index += 1
                if token.cancelled:
                    result.cancelled = True
                    break
                path, future = pending.popleft()
                _collect(path, future, writer, result)
                reporter.progress(
                    result.processed_files,
                    result.total_files,
                    f"Processed {result.processed_files}/{result.total_files}",
                )
        except OSError as exc:
            raise OutputFileError(f"Writing {spec.output} failed: {exc}") from exc
        finally:
            for _, future in pending:
                future.cancel()
    result.elapsed_seconds = time.perf_counter() - started
    return result


def _collect(
    path: Path, future: Future[FileOutcome], writer: csv.DictWriter[str], result: ExportResult
) -> None:
    result.processed_files += 1
    try:
        outcome = future.result()
    except XmlParseError as exc:
        log.warning("Skipped unparsable file %s: %s", path, exc.message)
        result.errors.append(FileError(path.name, exc.message))
        return
    except Exception as exc:  # unexpected per-file failure: log, report, continue
        log.exception("Unexpected error while processing %s", path)
        result.errors.append(FileError(path.name, f"{type(exc).__name__}: {exc}"))
        return
    for message in outcome.errors:
        log.warning("%s: %s", path.name, message)
        result.errors.append(FileError(path.name, message))
    if outcome.rows:
        writer.writerows(outcome.rows)
        result.rows_written += len(outcome.rows)
        result.files_with_matches += 1
    result.total_matches += outcome.total_matches


def summary_text(result: ExportResult, max_errors: int = 20) -> str:
    """User-facing completion message (same wording as 1.3.x, plus error details)."""
    title = (
        "CSV export aborted by user." if result.cancelled else "CSV export completed successfully!"
    )
    lines = [
        title,
        f"Files processed: {result.processed_files}/{result.total_files}",
        f"Files with matches: {result.files_with_matches}",
        f"Total matches found: {result.total_matches}",
        f"Rows written to CSV: {result.rows_written}",
        f"Output saved: {result.output}",
        f"Elapsed time: {result.elapsed_seconds:.2f} seconds",
    ]
    if result.errors:
        lines.append(f"Errors encountered: {len(result.errors)}")
        lines.extend(f"  {e.file_name}: {e.message}" for e in result.errors[:max_errors])
        if len(result.errors) > max_errors:
            lines.append(f"  ... and {len(result.errors) - max_errors} more (see log file)")
    return "\n".join(lines)
