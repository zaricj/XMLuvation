"""Value objects for XML schema validation and structural XML comparison."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class SchemaIssue:
    """One problem found while validating an XML file against an XSD.

    ``level`` is ``error``/``warning`` for schema violations, ``not well-formed`` when the
    file is not XML at all, and ``unreadable`` when it could not be opened.
    """

    file: str
    line: int
    column: int
    level: str
    message: str
    path: str = ""


class Change(StrEnum):
    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"


class NodeKind(StrEnum):
    ELEMENT = "element"
    ATTRIBUTE = "attribute"
    TEXT = "text"
    TAIL = "text after element"


@dataclass(frozen=True, slots=True)
class XmlDifference:
    """One difference between two XML documents.

    ``path`` is a readable XPath (``/root/item[2]/name``) in the new document for added
    and changed nodes and in the old document for removed nodes. Line numbers are 0
    when the node does not exist on that side.
    """

    change: Change
    kind: NodeKind
    path: str
    name: str
    old_value: str = ""
    new_value: str = ""
    old_line: int = 0
    new_line: int = 0
