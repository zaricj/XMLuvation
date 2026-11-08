"""lxml adapter: parsing, XPath compilation/evaluation and document inspection.

Parser policy
-------------
* Network access and DTD loading are disabled; only internal entities are expanded
  (lxml's default since 5.0, set explicitly here).
* The export parser uses ``recover=True`` and ``huge_tree=True`` (legacy behaviour):
  profile exports can be very large, and partially broken files still yield results.
* The inspection parser is strict so the user sees syntax errors when reading a file.
"""

from __future__ import annotations

import logging
import re
import threading
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lxml import etree

from ..domain.errors import InvalidXPathError, XmlParseError
from ..domain.models import ColumnValues, XmlIndex
from ..domain.rows import build_rows
from ..domain.xpath_text import find_row_anchor, is_value_xpath

log = logging.getLogger(__name__)

_ENCODING_DECL = re.compile(rb"""encoding\s*=\s*["']([A-Za-z0-9._-]+)["']""")


def export_parser() -> etree.XMLParser:
    return etree.XMLParser(
        recover=True, huge_tree=True, resolve_entities="internal", no_network=True, load_dtd=False
    )


def inspect_parser() -> etree.XMLParser:
    return etree.XMLParser(resolve_entities="internal", no_network=True, load_dtd=False)


def compile_xpath(expression: str) -> etree.XPath:
    """Compile an XPath 1.0 expression. Raises :class:`InvalidXPathError`."""
    try:
        return etree.XPath(expression, smart_strings=False)
    except etree.XPathSyntaxError as exc:
        raise InvalidXPathError(expression, str(exc)) from exc


def validate_xpath(expression: str) -> None:
    compile_xpath(expression)


class XPathCache:
    """Compiled XPaths, cached per thread (compile once per worker, not once per file)."""

    def __init__(self) -> None:
        self._local = threading.local()

    def get(self, expression: str) -> etree.XPath:
        cache: dict[str, etree.XPath] | None = getattr(self._local, "cache", None)
        if cache is None:
            cache = self._local.cache = {}
        compiled = cache.get(expression)
        if compiled is None:
            compiled = cache[expression] = compile_xpath(expression)
        return compiled


def format_match_value(match: Any) -> str:
    """Normalise an XPath result item to single-line text."""
    if isinstance(match, str):
        value = match.strip()
    elif isinstance(match, (bool, int, float)):
        value = str(match)
    elif getattr(match, "text", None):
        value = match.text.strip()
    elif hasattr(match, "tag"):
        value = f"<{match.tag}>"
    else:
        value = "" if match is None else str(match)
    if "\n" in value or "\r" in value:
        value = value.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    return value


def list_xml_files(folder: Path) -> list[Path]:
    """``*.xml`` files directly in ``folder`` (case-insensitive), sorted by name."""
    files = [p for p in folder.iterdir() if p.suffix.lower() == ".xml" and p.is_file()]
    return sorted(files, key=lambda p: (p.name.casefold(), p.name))


def count_xml_files(folder: Path) -> int:
    return sum(1 for p in folder.iterdir() if p.suffix.lower() == ".xml" and p.is_file())


@dataclass(slots=True)
class FileOutcome:
    rows: list[dict[str, str]] = field(default_factory=list)
    total_matches: int = 0
    errors: list[str] = field(default_factory=list)


def parse_for_export(path: Path) -> etree._Element:
    try:
        tree = etree.parse(str(path), export_parser())
    except (etree.XMLSyntaxError, OSError) as exc:
        raise XmlParseError(f"{path.name}: {exc}") from exc
    root = tree.getroot()
    if root is None:
        raise XmlParseError(f"{path.name}: document is empty")
    return root


def _evaluate(compiled: etree.XPath, context: Any, expression: str, errors: list[str]) -> Any:
    try:
        return compiled(context)
    except etree.XPathEvalError as exc:
        errors.append(f"XPath '{expression}' failed: {exc}")
        return []


def evaluate_file(
    path: Path,
    xpaths: Sequence[str],
    headers: Sequence[str],
    group_matches: bool,
    cache: XPathCache,
) -> FileOutcome:
    """Evaluate all XPaths against one file and build its CSV rows.

    XPaths are evaluated with the document's root element as context node.
    Raises :class:`XmlParseError` if the file cannot be parsed at all.
    """
    root = parse_for_export(path)
    outcome = FileOutcome()

    row_elements: list[Any] = []
    relative: dict[str, str] = {}
    if not group_matches:
        anchor = find_row_anchor([x for x in xpaths if is_value_xpath(x)])
        if anchor is not None:
            found = _evaluate(cache.get(anchor.anchor), root, anchor.anchor, outcome.errors)
            row_elements = list(found) if isinstance(found, list) else []
            relative = anchor.relative

    columns: list[ColumnValues] = []
    for xpath, header in zip(xpaths, headers, strict=True):
        if is_value_xpath(xpath):
            if row_elements and xpath in relative:
                rel = cache.get(relative[xpath])
                values = []
                for element in row_elements:
                    found = _evaluate(rel, element, relative[xpath], outcome.errors)
                    values.append(format_match_value(found[0]) if found else "")
                match_total = sum(1 for v in values if v)
            else:
                matches = _evaluate(cache.get(xpath), root, xpath, outcome.errors)
                values = [format_match_value(m) for m in _as_list(matches)]
                match_total = len(values)
            columns.append(ColumnValues(header, True, tuple(values), match_total))
        else:
            matches = _evaluate(cache.get(xpath), root, xpath, outcome.errors)
            columns.append(ColumnValues(header, False, (), _match_count(matches, xpath, outcome)))

    outcome.rows, outcome.total_matches = build_rows(path.stem, columns, group_matches)
    return outcome


def _as_list(result: Any) -> list[Any]:
    return result if isinstance(result, list) else [result]


def _match_count(result: Any, xpath: str, outcome: FileOutcome) -> int:
    if isinstance(result, list):
        return len(result)
    if isinstance(result, bool):
        return int(result)
    if isinstance(result, float) and result.is_integer() and result >= 0:
        return int(result)  # e.g. count(...)
    outcome.errors.append(
        f"XPath '{xpath}' returned a single value ({result!r}); "
        "end it with /text() or /@attribute to export values"
    )
    return 0


# --------------------------------------------------------------------------- inspection


def detect_declared_encoding(path: Path) -> str:
    with path.open("rb") as handle:
        head = handle.read(512)
    match = _ENCODING_DECL.search(head.split(b"?>", 1)[0]) if head.startswith(b"<?xml") else None
    return match.group(1).decode("ascii") if match else "utf-8"


class _IndexBuilder:
    def __init__(self) -> None:
        self.tags: set[str] = set()
        self.namespaces: set[str] = set()
        self.tag_to_values: dict[str, set[str]] = {}
        self.tag_to_attributes: dict[str, set[str]] = {}
        self.tag_attr_to_values: dict[tuple[str, str], set[str]] = {}
        self.element_count = 0  # includes comments and processing instructions

    def add(self, element: Any) -> None:
        self.element_count += 1
        tag = element.tag
        if not isinstance(tag, str):  # comment / processing instruction / entity
            return
        self.tags.add(tag)
        if tag.startswith("{"):
            self.namespaces.add(tag[1:].split("}", 1)[0])
        text = element.text
        if text and text.strip():
            self.tag_to_values.setdefault(tag, set()).add(text.strip())
        for attr, value in element.attrib.items():
            self.tag_to_attributes.setdefault(tag, set()).add(attr)
            self.tag_attr_to_values.setdefault((tag, attr), set()).add(value)

    def build(
        self, path: Path, root_tag: str, encoding: str, size: int, preview: str, truncated: bool
    ) -> XmlIndex:
        return XmlIndex(
            file_path=path,
            root_tag=root_tag,
            element_count=self.element_count,
            encoding=encoding,
            size_bytes=size,
            tags=tuple(sorted(self.tags)),
            namespaces=tuple(sorted(self.namespaces)),
            tag_to_values={k: tuple(sorted(v)) for k, v in self.tag_to_values.items()},
            tag_to_attributes={k: tuple(sorted(v)) for k, v in self.tag_to_attributes.items()},
            tag_attr_to_values={k: tuple(sorted(v)) for k, v in self.tag_attr_to_values.items()},
            preview_text=preview,
            preview_truncated=truncated,
        )


def inspect_file(path: Path, preview_limit_bytes: int) -> XmlIndex:
    """Index tags/attributes/values and produce a text preview.

    Files up to ``preview_limit_bytes`` are fully parsed and pretty-printed. Larger
    files are indexed in streaming mode and the preview shows the beginning of the
    raw text only. Raises :class:`XmlParseError`.
    """
    size = path.stat().st_size
    encoding = detect_declared_encoding(path)
    builder = _IndexBuilder()
    try:
        if size <= preview_limit_bytes:
            root = etree.parse(str(path), inspect_parser()).getroot()
            for element in root.iter():
                builder.add(element)
            preview = etree.tostring(root, encoding="unicode", pretty_print=True)
            return builder.build(path, root.tag, encoding, size, preview, False)
        root_tag = _stream_index(path, builder)
    except (etree.XMLSyntaxError, OSError) as exc:
        raise XmlParseError(str(exc)) from exc
    return builder.build(
        path, root_tag, encoding, size, _raw_preview(path, preview_limit_bytes, encoding), True
    )


def _stream_index(path: Path, builder: _IndexBuilder) -> str:
    root_tag = ""
    events: Iterable[tuple[str, Any]] = etree.iterparse(
        str(path),
        events=("start", "end", "comment", "pi"),
        resolve_entities="internal",
        no_network=True,
        load_dtd=False,
    )
    for event, element in events:
        if event == "start":
            if not root_tag:
                root_tag = element.tag
            continue
        builder.add(element)
        if event == "end":
            element.clear(keep_tail=True)
            parent = element.getparent()
            if parent is not None:
                while element.getprevious() is not None:
                    del parent[0]
    return root_tag


def _raw_preview(path: Path, limit_bytes: int, encoding: str) -> str:
    with path.open("rb") as handle:
        head = handle.read(limit_bytes)
    try:
        text = head.decode(encoding, errors="replace")
    except LookupError:
        text = head.decode("utf-8", errors="replace")
    cut = text.rfind("\n")
    return text[:cut] if cut > 0 else text
