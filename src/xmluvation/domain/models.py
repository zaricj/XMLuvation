"""Domain value objects shared by the application, infrastructure and presentation layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class Operator(StrEnum):
    """Comparison used by the XPath builder for tag values and attribute values."""

    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    GREATER = "greater"
    SMALLER = "smaller"


@dataclass(frozen=True, slots=True)
class BuildCriteria:
    """Selections from the XPath builder. Empty strings mean "not selected"."""

    tag: str = ""
    tag_value: str = ""
    attribute: str = ""
    attribute_value: str = ""
    operator: Operator = Operator.EQUALS

    def normalized(self) -> BuildCriteria:
        return BuildCriteria(
            self.tag.strip(),
            self.tag_value.strip(),
            self.attribute.strip(),
            self.attribute_value.strip(),
            self.operator,
        )


@dataclass(frozen=True, slots=True)
class ColumnValues:
    """Values extracted from one XML file for one XPath column.

    ``is_value_column`` is True for XPaths that select strings (attributes or ``text()``);
    those produce one CSV cell per match. Other XPaths produce a single match count.
    """

    header: str
    is_value_column: bool
    values: tuple[str, ...] = ()
    match_total: int = 0


@dataclass(frozen=True, slots=True)
class ExportSpec:
    """Everything needed to run an XPath search over a folder and write a CSV file."""

    folder: Path
    xpaths: tuple[str, ...]
    headers: tuple[str, ...]
    output: Path
    group_matches: bool
    max_workers: int


@dataclass(frozen=True, slots=True)
class FileError:
    file_name: str
    message: str


@dataclass(slots=True)
class ExportResult:
    output: Path
    total_files: int = 0
    processed_files: int = 0
    files_with_matches: int = 0
    total_matches: int = 0
    rows_written: int = 0
    elapsed_seconds: float = 0.0
    cancelled: bool = False
    errors: list[FileError] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class XmlIndex:
    """Summary of one XML document used to fill the XPath builder and the preview."""

    file_path: Path
    root_tag: str
    element_count: int
    encoding: str
    size_bytes: int
    tags: tuple[str, ...]
    namespaces: tuple[str, ...]
    tag_to_values: dict[str, tuple[str, ...]]
    tag_to_attributes: dict[str, tuple[str, ...]]
    tag_attr_to_values: dict[tuple[str, str], tuple[str, ...]]
    preview_text: str
    preview_truncated: bool
    values_capped: bool = False  # some value lists hold only the first MAX_DISTINCT_VALUES


@dataclass(frozen=True, slots=True)
class XPathPreset:
    """A named set of XPath expressions with their CSV headers ("autofill")."""

    name: str
    xpaths: tuple[str, ...]
    headers: tuple[str, ...]
