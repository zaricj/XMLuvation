"""Validate XML files against an XSD schema with lxml (libxml2, XSD 1.0)."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from ..domain.errors import XmlParseError
from ..domain.xml_checks import SchemaIssue

MAX_ISSUES_PER_FILE = 1_000
_SCHEMA_ERROR_TITLE = "Invalid XSD schema"


def _parser(*, huge_tree: bool = False) -> etree.XMLParser:
    # Same policy as the other parsers: no network, no DTD loading, internal entities only.
    # Local xs:include/xs:import files are still read, relative to the schema file.
    return etree.XMLParser(
        resolve_entities="internal", no_network=True, load_dtd=False, huge_tree=huge_tree
    )


def load_schema(path: Path) -> etree.XMLSchema:
    """Parse and compile an XSD. Raises :class:`XmlParseError` with a readable message."""
    try:
        document = etree.parse(str(path), _parser())
    except etree.XMLSyntaxError as exc:
        raise XmlParseError(
            f"{path.name} is not well-formed XML:\n{exc}", title=_SCHEMA_ERROR_TITLE
        ) from exc
    except OSError as exc:
        raise XmlParseError(f"Cannot read {path.name}:\n{exc}", title=_SCHEMA_ERROR_TITLE) from exc
    try:
        return etree.XMLSchema(document)
    except etree.XMLSchemaParseError as exc:
        raise XmlParseError(
            f"{path.name} is not a valid XSD 1.0 schema:\n{exc}", title=_SCHEMA_ERROR_TITLE
        ) from exc


def validate_file(
    schema: etree.XMLSchema, path: Path, max_issues: int = MAX_ISSUES_PER_FILE
) -> list[SchemaIssue]:
    """Problems in one file, in document order; an empty list means the file is valid."""
    try:
        document = etree.parse(str(path), _parser(huge_tree=True))
    except etree.XMLSyntaxError as exc:
        line, column = exc.position
        return [SchemaIssue(path.name, line, column, "not well-formed", exc.msg)]
    except OSError as exc:
        return [SchemaIssue(path.name, 0, 0, "unreadable", str(exc))]
    if schema.validate(document):
        return []
    return [
        SchemaIssue(
            path.name,
            entry.line,
            entry.column,
            entry.level_name.lower(),
            entry.message,
            entry.path or "",
        )
        for entry in list(schema.error_log)[:max_issues]
    ]
