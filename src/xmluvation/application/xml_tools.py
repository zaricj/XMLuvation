"""Use cases on XML files: validate against an XSD schema, compare two documents.

Both write a CSV report (UTF-8 with BOM, so Excel shows umlauts correctly); no report is
written when there is nothing to list. Validation also returns its problems for display,
and compare returns a line-by-line text diff of both files for the side-by-side view.
"""

from __future__ import annotations

import csv
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from ..domain.errors import OutputFileError, ValidationError
from ..domain.text_diff import TextDiff, diff_lines, split_lines
from ..domain.xml_checks import Change, SchemaIssue
from ..infrastructure import xml_diff, xml_validation
from ..infrastructure.xml_engine import list_xml_files
from .cancellation import CancellationToken, ProgressReporter
from .output_paths import unique_path

VALIDATION_COLUMNS = ("File", "Line", "Column", "Level", "Message", "Path")
DIFF_COLUMNS = ("Change", "Node", "Path", "Name", "Old value", "New value", "Old line", "New line")
# Larger files are compared and reported, but not shown side by side.
MAX_TEXT_DIFF_BYTES = 16 * 1024 * 1024


def _existing_file(path_text: str, message: str, title: str) -> Path:
    path = Path(path_text.strip()) if path_text.strip() else None
    if path is None or not path.is_file():
        raise ValidationError(message, title=title)
    return path


def _write_report(path: Path, header: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    try:
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\r\n")
            writer.writerow(header)
            writer.writerows(rows)
    except OSError as exc:
        raise OutputFileError(f"Cannot write the report {path}:\n{exc}") from exc


# ---------------------------------------------------------------------------- validation


@dataclass(slots=True)
class SchemaValidationResult:
    schema: Path
    files: int = 0
    invalid_files: list[str] = field(default_factory=list)
    issues: int = 0
    levels: Counter[str] = field(default_factory=Counter)
    report: Path | None = None
    capped_files: list[str] = field(default_factory=list)
    problems: list[SchemaIssue] = field(default_factory=list)

    @property
    def valid_files(self) -> int:
        return self.files - len(self.invalid_files)

    @property
    def all_valid(self) -> bool:
        return not self.invalid_files


def _xml_targets(target_text: str) -> tuple[list[Path], Path]:
    """Files to validate and the folder the report goes to."""
    text = target_text.strip()
    target = Path(text) if text else None
    if target is not None and target.is_file():
        return [target], target.parent
    if target is not None and target.is_dir():
        files = list_xml_files(target)
        if not files:
            raise ValidationError(
                f"There are no .xml files in\n{target}", title="No XML files found"
            )
        return files, target
    raise ValidationError(
        "Please select an XML file or a folder with XML files to validate.",
        title="XML file not found",
    )


def validate_against_schema(
    schema_text: str,
    target_text: str,
    reporter: ProgressReporter,
    token: CancellationToken,
) -> SchemaValidationResult:
    """Validate one XML file, or every ``*.xml`` file directly in a folder, against an XSD."""
    schema_path = _existing_file(
        schema_text, "Please select the XSD schema file.", "Schema not found"
    )
    files, report_folder = _xml_targets(target_text)
    reporter.message(f"Loading schema {schema_path.name}...")
    schema = xml_validation.load_schema(schema_path)
    result = SchemaValidationResult(schema_path, files=len(files))
    issues: list[SchemaIssue] = []
    reporter.message(f"Validating {len(files):,} file(s)...")
    for done, path in enumerate(files):
        token.raise_if_cancelled()
        reporter.progress(done, len(files), path.name)
        found = xml_validation.validate_file(schema, path)
        if found:
            result.invalid_files.append(path.name)
            if len(found) >= xml_validation.MAX_ISSUES_PER_FILE:
                result.capped_files.append(path.name)
            issues.extend(found)
    reporter.progress(len(files), len(files))
    result.issues = len(issues)
    result.problems = issues
    result.levels = Counter(issue.level for issue in issues)
    if issues:
        result.report = unique_path(report_folder / f"{schema_path.stem}_validation.csv")
        _write_report(
            result.report,
            VALIDATION_COLUMNS,
            ((i.file, i.line or "", i.column or "", i.level, i.message, i.path) for i in issues),
        )
    return result


def validation_summary(result: SchemaValidationResult) -> list[str]:
    if result.all_valid:
        noun = "file is" if result.files == 1 else f"{result.files:,} files are"
        return [f"Valid: the {noun} valid against {result.schema.name}."]
    levels = ", ".join(
        f"{count:,} {level}{'s' if count != 1 and level in ('error', 'warning') else ''}"
        for level, count in result.levels.most_common()
    )
    lines = [
        f"{len(result.invalid_files):,} of {result.files:,} file(s) are not valid "
        f"against {result.schema.name} ({levels}).",
    ]
    if result.files > 1:
        shown = ", ".join(result.invalid_files[:10])
        more = (
            f" and {len(result.invalid_files) - 10:,} more"
            if len(result.invalid_files) > 10
            else ""
        )
        lines.append(f"Invalid: {shown}{more}")
    if result.capped_files:
        lines.append(
            f"Only the first {xml_validation.MAX_ISSUES_PER_FILE:,} problems are listed for: "
            + ", ".join(result.capped_files[:5])
        )
    return lines


def format_issue(issue: SchemaIssue) -> str:
    """``file:line:column: level: message`` (as compilers print it), plus the node path."""
    where = issue.file
    if issue.line:
        where += f":{issue.line}"
        if issue.column:
            where += f":{issue.column}"
    text = f"{where}: {issue.level}: {issue.message}"
    return f"{text}\n    at {issue.path}" if issue.path else text


# ---------------------------------------------------------------------------- compare


@dataclass(slots=True)
class XmlCompareResult:
    old: Path
    new: Path
    report: Path | None = None
    counts: Counter[str] = field(default_factory=Counter)
    differences: int = 0
    truncated: bool = False
    old_elements: int = 0
    new_elements: int = 0
    text_diff: TextDiff | None = None
    text_diff_note: str = ""  # why ``text_diff`` is missing

    @property
    def identical(self) -> bool:
        return self.differences == 0


def compare_xml(
    old_text: str,
    new_text: str,
    ignore_whitespace: bool,
    reporter: ProgressReporter,
    token: CancellationToken,
) -> XmlCompareResult:
    """Compare two XML documents element by element and write a difference report."""
    old_path = _existing_file(old_text, "Please select the old XML file.", "XML file not found")
    new_path = _existing_file(new_text, "Please select the new XML file.", "XML file not found")
    reporter.message(f"Comparing {old_path.name} with {new_path.name}...")
    outcome = xml_diff.diff_files(
        old_path,
        new_path,
        ignore_whitespace=ignore_whitespace,
        check_cancelled=token.raise_if_cancelled,
    )
    result = XmlCompareResult(
        old_path,
        new_path,
        differences=len(outcome.differences),
        truncated=outcome.truncated,
        old_elements=outcome.old_elements,
        new_elements=outcome.new_elements,
        counts=Counter(f"{d.kind} {d.change}" for d in outcome.differences),
    )
    _attach_text_diff(result, ignore_whitespace, reporter, token)
    if outcome.differences:
        result.report = unique_path(
            new_path.with_name(f"{new_path.stem}_vs_{old_path.stem}_xmldiff.csv")
        )
        _write_report(
            result.report,
            DIFF_COLUMNS,
            (
                (
                    d.change,
                    d.kind,
                    d.path,
                    d.name,
                    d.old_value,
                    d.new_value,
                    d.old_line or "",
                    d.new_line or "",
                )
                for d in outcome.differences
            ),
        )
    return result


def _attach_text_diff(
    result: XmlCompareResult,
    ignore_whitespace: bool,
    reporter: ProgressReporter,
    token: CancellationToken,
) -> None:
    too_large = [
        path.name for path in (result.old, result.new) if path.stat().st_size > MAX_TEXT_DIFF_BYTES
    ]
    if too_large:
        result.text_diff_note = (
            f"{' and '.join(too_large)} {'is' if len(too_large) == 1 else 'are'} larger than "
            f"{MAX_TEXT_DIFF_BYTES // (1024 * 1024)} MB, so the files are not shown side by "
            "side. The report lists every difference."
        )
        return
    reporter.message("Comparing the files line by line...")
    old_lines = split_lines(xml_diff.read_text(result.old))
    new_lines = split_lines(xml_diff.read_text(result.new))
    token.raise_if_cancelled()
    result.text_diff = diff_lines(
        old_lines,
        new_lines,
        ignore_whitespace=ignore_whitespace,
        check_cancelled=token.raise_if_cancelled,
    )


def compare_summary(result: XmlCompareResult) -> list[str]:
    if result.identical:
        return [
            f"No differences: both documents have the same {result.new_elements:,} elements, "
            "attributes and text."
        ]
    by_change = Counter[str]()
    for key, count in result.counts.items():
        by_change[key.rsplit(" ", 1)[1]] += count
    parts = [
        f"{by_change[change]:,} {change}"
        for change in (Change.ADDED, Change.REMOVED, Change.CHANGED)
        if by_change[change]
    ]
    lines = [f"{result.differences:,} difference(s): {', '.join(parts)}."]
    details = ", ".join(f"{count:,} {key}" for key, count in sorted(result.counts.items()))
    lines.append(f"Details: {details}.")
    if result.truncated:
        lines.append(
            f"Stopped after {xml_diff.MAX_DIFFERENCES:,} differences; "
            "the files are probably not two versions of the same document."
        )
    return lines
