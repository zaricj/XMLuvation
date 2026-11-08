"""Text-level rules for XPath expressions and CSV headers (no XML evaluation here)."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .models import BuildCriteria
from .xpath_build import build_xpath

_TEXT_XPATH = re.compile(r"/text\(\)\s*$")
_ATTR_XPATH = re.compile(r"/@[\w:-]+\s*$")


def smart_split(text: str) -> list[str]:
    """Split comma-separated XPath expressions, ignoring commas inside quotes, () and [].

    Empty parts are dropped.
    """
    result: list[str] = []
    current: list[str] = []
    in_single = in_double = False
    depth = 0
    for char in text:
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        if not in_single and not in_double:
            if char in "([":
                depth += 1
            elif char in ")]":
                depth -= 1
        if char == "," and not in_single and not in_double and depth == 0:
            result.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        result.append("".join(current).strip())
    return [part for part in result if part]


def is_value_xpath(xpath: str) -> bool:
    """True if the XPath selects string values (``.../text()`` or ``.../@attr``)."""
    xpath = xpath.strip()
    return bool(_TEXT_XPATH.search(xpath) or _ATTR_XPATH.search(xpath))


@dataclass(frozen=True, slots=True)
class RowAnchor:
    """Common element path of several XPaths, so each anchor element becomes one CSV row.

    ``relative`` maps each original XPath to the path evaluated relative to the anchor.
    """

    anchor: str
    relative: dict[str, str]


def find_row_anchor(xpaths: Sequence[str]) -> RowAnchor | None:
    """Find the common leading path of value XPaths (only for simple paths without predicates).

    Evaluating every column relative to the same anchor element keeps cells of one
    element on the same row and leaves ``""`` where an element lacks a node.
    """
    if len(xpaths) < 2 or any("[" in x for x in xpaths):
        return None
    parts = [x.strip().split("/") for x in xpaths]
    common: list[str] = []
    for segments in zip(*parts, strict=False):
        if len(set(segments)) != 1:
            break
        common.append(segments[0])
    anchor = "/".join(common)
    if not anchor.strip("/") or any(len(p) <= len(common) for p in parts):
        return None
    relative = {x: "/".join(p[len(common) :]) for x, p in zip(xpaths, parts, strict=True)}
    if any(r.startswith("/") or not r for r in relative.values()):
        return None
    return RowAnchor(anchor, relative)


def parse_headers(raw: str) -> list[str]:
    """Split the comma-separated header input into trimmed, non-empty headers."""
    return [h.strip() for h in raw.split(",") if h.strip()]


def duplicate_headers(headers: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for header in headers:
        if header in seen and header not in duplicates:
            duplicates.append(header)
        seen.add(header)
    return duplicates


def _header_from_criteria(c: BuildCriteria) -> str:
    match (c.tag, c.tag_value, c.attribute, c.attribute_value):
        case (tag, "", "", ""):
            return tag
        case (tag, value, "", ""):
            return f"{tag} {value}"
        case (tag, "", attr, ""):
            return f"{tag} @{attr}"
        case (tag, "", attr, attr_value):
            return f"{tag} {attr} {attr_value}"
        case (tag, value, attr, ""):
            return f"{tag} {value} {attr}"
        case (tag, value, attr, attr_value):
            return f"{tag} {value} {attr} {attr_value}"
    return "Header"


def _header_from_xpath(xpath: str) -> str:
    segments = xpath.strip().split("/")
    if len(segments) < 2:
        return "Header"
    return f"{segments[-2]} {segments[-1]}".strip() or "Header"


def generate_header(xpath: str, criteria: BuildCriteria | None, existing: Sequence[str]) -> str:
    """Suggest a CSV header for ``xpath`` that is not already in ``existing``.

    If the expression is exactly what the builder produces from ``criteria`` the header
    is derived from the selections (e.g. ``"filter @id"``); otherwise from the last two
    path segments of the expression. Duplicates get a numeric suffix.
    """
    if criteria is not None and criteria.tag and build_xpath(criteria) == xpath.strip():
        base = _header_from_criteria(criteria.normalized())
    else:
        base = _header_from_xpath(xpath)
    # Headers are stored comma-separated, so a generated header must not contain commas.
    base = " ".join(base.replace(",", " ").split()) or "Header"
    taken = {h.strip() for h in existing}
    header, counter = base, 2
    while header in taken:
        header = f"{base} ({counter})"
        counter += 1
    return header
