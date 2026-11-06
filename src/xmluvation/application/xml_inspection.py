"""Use cases for a single XML file: inspection for the builder, XPath validation, folder counts."""

from __future__ import annotations

from pathlib import Path

from ..domain.models import XmlIndex
from ..infrastructure import xml_engine

BYTES_PER_MB = 1024 * 1024


def inspect_xml_file(path: Path, preview_limit_mb: int) -> XmlIndex:
    return xml_engine.inspect_file(path, max(1, preview_limit_mb) * BYTES_PER_MB)


def validate_xpath(expression: str) -> None:
    """Raises :class:`~xmluvation.domain.errors.InvalidXPathError` if invalid."""
    xml_engine.validate_xpath(expression)


def count_xml_files(folder_text: str) -> int | None:
    """Number of XML files in the folder, or ``None`` if it is not a directory."""
    folder = Path(folder_text.strip()) if folder_text.strip() else None
    if folder is None or not folder.is_dir():
        return None
    return xml_engine.count_xml_files(folder)
