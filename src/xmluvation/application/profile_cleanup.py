"""Use case: delete exported Lobster profile XML files that are not listed in a CSV file.

The work is split into :func:`plan_cleanup` (read-only, shown to the user for
confirmation) and :func:`apply_cleanup` (deletes exactly the planned files).
Only ``*.xml`` files directly inside the folder are ever considered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..domain.errors import ValidationError
from ..domain.filenames import profile_file_name, sanitize_filename_for_windows
from ..infrastructure import csv_io
from ..infrastructure.xml_engine import list_xml_files
from .cancellation import CancellationToken, ProgressReporter


@dataclass(frozen=True, slots=True)
class CleanupPlan:
    folder: Path
    valid_entries: int
    sample_transformations: tuple[str, ...]
    files_in_folder: int
    keep: tuple[Path, ...]
    delete: tuple[Path, ...]
    case_mismatches: tuple[str, ...]


@dataclass(slots=True)
class CleanupResult:
    deleted: list[str] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)
    cancelled: bool = False


def plan_cleanup(csv_text: str, folder_text: str) -> CleanupPlan:
    if not csv_text.strip():
        raise ValidationError(
            "Please select the CSV file that contains the current export of all Lobster profiles",
            title="CSV file not found",
        )
    if not folder_text.strip():
        raise ValidationError(
            "Please select the folder that contains all exported Lobster profiles as XML files",
            title="Folder path not found",
        )
    csv_path, folder = Path(csv_text.strip()), Path(folder_text.strip())
    if not csv_path.is_file():
        raise ValidationError(f"CSV file not found: {csv_path}", title="CSV file not found")
    if not folder.is_dir():
        raise ValidationError(f"Folder not found: {folder}", title="Folder path not found")

    valid: set[str] = set()
    samples: list[str] = []
    for entry in csv_io.read_first_column(csv_path):
        original = profile_file_name(entry)
        sanitized = sanitize_filename_for_windows(original)
        valid.add(sanitized)
        if len(samples) < 3:
            samples.append(f"'{original}' -> '{sanitized}'")
    if not valid:
        raise ValidationError(
            "The CSV file contains no profile names in its first column, so every XML "
            "file would be deleted. Nothing was changed.",
            title="CSV Error",
        )

    valid_lower = {name.lower() for name in valid}
    keep: list[Path] = []
    delete: list[Path] = []
    mismatches: list[str] = []
    files = list_xml_files(folder)
    for path in files:
        if path.name.lower() in valid_lower:
            keep.append(path)
            if path.name not in valid:
                mismatches.append(path.name)
        else:
            delete.append(path)
    return CleanupPlan(
        folder=folder,
        valid_entries=len(valid),
        sample_transformations=tuple(samples),
        files_in_folder=len(files),
        keep=tuple(keep),
        delete=tuple(delete),
        case_mismatches=tuple(mismatches),
    )


def describe_plan(plan: CleanupPlan) -> list[str]:
    lines = [f"Found {plan.valid_entries} valid file entries in CSV"]
    if plan.sample_transformations:
        lines.append("Sample filename transformations:")
        lines.extend(plan.sample_transformations)
    lines.append(f"Found {plan.files_in_folder} XML files in folder")
    lines.extend(
        f"Case mismatch found - File: '{name}' vs CSV entries" for name in plan.case_mismatches
    )
    lines.append(f"Files to keep: {len(plan.keep)}, Files to delete: {len(plan.delete)}")
    return lines


def apply_cleanup(
    plan: CleanupPlan, reporter: ProgressReporter, token: CancellationToken
) -> CleanupResult:
    result = CleanupResult()
    for index, path in enumerate(plan.delete, start=1):
        if token.cancelled:
            result.cancelled = True
            break
        try:
            path.unlink()
        except OSError as exc:
            result.failed.append((path.name, str(exc)))
            reporter.message(f"Failed to delete '{path.name}': {exc}")
        else:
            result.deleted.append(path.name)
            reporter.message(f"Deleted file: '{path.name}'")
        reporter.progress(index, len(plan.delete))
    return result
