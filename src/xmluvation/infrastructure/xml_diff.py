"""Structural comparison of two XML documents (elements, attributes and text).

Algorithm
---------
Every element gets a fingerprint of its whole subtree (tag, attributes, text, tail and
the children's fingerprints), computed bottom-up once per document. Comparing two
elements then works on their child lists in two passes:

1. Align the children by fingerprint (``difflib``). Identical subtrees are skipped, and an
   element inserted in the middle of many similar siblings does not shift the others.
2. In each region that differs, align the children by tag. Children paired here are
   compared recursively; the rest are reported as added or removed elements.

Comments and processing instructions are ignored. Namespaced names are shown with the
document's prefix (``ns:name``). Work is done with an explicit stack, so deep documents
cannot exhaust Python's recursion limit.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lxml import etree

from ..domain.errors import XmlParseError
from ..domain.text_diff import align as _align
from ..domain.xml_checks import Change, NodeKind, XmlDifference

MAX_DIFFERENCES = 100_000
SNIPPET_CHARS = 200

Element = Any  # lxml's etree._Element (not exported as a public type)


@dataclass(slots=True)
class DiffOutcome:
    differences: list[XmlDifference]
    truncated: bool
    old_elements: int
    new_elements: int


class _LimitReached(Exception):
    pass


def _parse(path: Path) -> Element:
    parser = etree.XMLParser(
        resolve_entities="internal",
        no_network=True,
        load_dtd=False,
        huge_tree=True,
        remove_comments=True,
        remove_pis=True,
    )
    try:
        return etree.parse(str(path), parser).getroot()
    except etree.XMLSyntaxError as exc:
        raise XmlParseError(f"{path.name} is not well-formed XML:\n{exc}") from exc
    except OSError as exc:
        raise XmlParseError(f"Cannot read {path.name}:\n{exc}") from exc


def _normalizer(ignore_whitespace: bool) -> Callable[[str | None], str]:
    if ignore_whitespace:
        return lambda text: " ".join(text.split()) if text else ""
    return lambda text: text or ""


def _elements(root: Element) -> list[Element]:
    return [el for el in root.iter() if isinstance(el.tag, str)]


def _fingerprints(
    root: Element, norm: Callable[[str | None], str], check: Callable[[], None]
) -> dict[Element, int]:
    prints: dict[Element, int] = {}
    elements = _elements(root)
    # Reversed document order visits every child before its parent.
    for count, el in enumerate(reversed(elements)):
        if count % 10_000 == 0:
            check()
        prints[el] = hash(
            (
                el.tag,
                tuple(sorted(el.attrib.items())),
                norm(el.text),
                norm(el.tail) if el is not root else "",
                tuple(prints[child] for child in el if isinstance(child.tag, str)),
            )
        )
    return prints


def _display_name(el: Element, name: str) -> str:
    """``{uri}local`` as ``prefix:local`` (or ``local`` for the default namespace)."""
    if not name.startswith("{"):
        return name
    uri, local = name[1:].split("}", 1)
    prefix = next((p for p, u in el.nsmap.items() if u == uri and p), None)
    return f"{prefix}:{local}" if prefix else local


def _child_paths(parent_path: str, children: Sequence[Element]) -> list[str]:
    totals = Counter(child.tag for child in children)
    seen: Counter[str] = Counter()
    paths = []
    for child in children:
        seen[child.tag] += 1
        index = f"[{seen[child.tag]}]" if totals[child.tag] > 1 else ""
        paths.append(f"{parent_path}/{_display_name(child, child.tag)}{index}")
    return paths


def _snippet(el: Element, norm: Callable[[str | None], str]) -> str:
    """Start tag with attributes, the beginning of the text and the number of children."""
    attributes = "".join(
        f' {_display_name(el, name)}="{value}"' for name, value in el.attrib.items()
    )
    text = " ".join(norm(el.text).split())
    children = sum(1 for child in el if isinstance(child.tag, str))
    snippet = f"<{_display_name(el, el.tag)}{attributes}>{text}"
    if children:
        snippet += f" … ({children} child element{'s' if children != 1 else ''})"
    return snippet if len(snippet) <= SNIPPET_CHARS else snippet[: SNIPPET_CHARS - 1] + "…"


def _value(text: str) -> str:
    return text if len(text) <= SNIPPET_CHARS * 5 else text[: SNIPPET_CHARS * 5 - 1] + "…"


# Stack entries: ("pair", old, new, old_path, new_path) or ("diff", XmlDifference).
_Entry = tuple[Any, ...]


class _Differ:
    def __init__(
        self,
        norm: Callable[[str | None], str],
        old_prints: dict[Element, int],
        new_prints: dict[Element, int],
        limit: int,
        check: Callable[[], None],
    ) -> None:
        self.norm = norm
        self.old_prints = old_prints
        self.new_prints = new_prints
        self.limit = limit
        self.check = check
        self.out: list[XmlDifference] = []

    def add(self, difference: XmlDifference) -> None:
        if len(self.out) >= self.limit:
            raise _LimitReached
        self.out.append(difference)

    def removed(self, el: Element, path: str) -> XmlDifference:
        return XmlDifference(
            Change.REMOVED,
            NodeKind.ELEMENT,
            path,
            _display_name(el, el.tag),
            old_value=_snippet(el, self.norm),
            old_line=el.sourceline or 0,
        )

    def added(self, el: Element, path: str) -> XmlDifference:
        return XmlDifference(
            Change.ADDED,
            NodeKind.ELEMENT,
            path,
            _display_name(el, el.tag),
            new_value=_snippet(el, self.norm),
            new_line=el.sourceline or 0,
        )

    def run(self, old_root: Element, new_root: Element) -> None:
        old_path = f"/{_display_name(old_root, old_root.tag)}"
        new_path = f"/{_display_name(new_root, new_root.tag)}"
        if old_root.tag != new_root.tag:
            self.add(self.removed(old_root, old_path))
            self.add(self.added(new_root, new_path))
            return
        stack: list[_Entry] = [("pair", old_root, new_root, old_path, new_path)]
        while stack:
            self.check()
            entry = stack.pop()
            if entry[0] == "diff":
                self.add(entry[1])
                continue
            _, old, new, old_path, new_path = entry
            if self.old_prints[old] == self.new_prints[new]:
                continue
            self._compare_node(old, new, old_path, new_path)
            stack.extend(reversed(self._child_entries(old, new, old_path, new_path)))

    def _compare_node(self, old: Element, new: Element, old_path: str, new_path: str) -> None:
        old_line, new_line = old.sourceline or 0, new.sourceline or 0
        for name in sorted(set(old.attrib) | set(new.attrib)):
            before, after = old.attrib.get(name), new.attrib.get(name)
            if before == after:
                continue
            if before is None:
                change, path = Change.ADDED, new_path
            elif after is None:
                change, path = Change.REMOVED, old_path
            else:
                change, path = Change.CHANGED, new_path
            self.add(
                XmlDifference(
                    change,
                    NodeKind.ATTRIBUTE,
                    f"{path}/@{_display_name(new if after is not None else old, name)}",
                    _display_name(new if after is not None else old, name),
                    _value(before or ""),
                    _value(after or ""),
                    old_line if before is not None else 0,
                    new_line if after is not None else 0,
                )
            )
        name = _display_name(new, new.tag)
        for kind, before, after in (
            (NodeKind.TEXT, old.text, new.text),
            (NodeKind.TAIL, old.tail, new.tail),
        ):
            if self.norm(before) != self.norm(after):
                self.add(
                    XmlDifference(
                        Change.CHANGED,
                        kind,
                        new_path,
                        name,
                        _value(self.norm(before)),
                        _value(self.norm(after)),
                        old_line,
                        new_line,
                    )
                )

    def _child_entries(
        self, old: Element, new: Element, old_path: str, new_path: str
    ) -> list[_Entry]:
        old_children = [c for c in old if isinstance(c.tag, str)]
        new_children = [c for c in new if isinstance(c.tag, str)]
        old_paths = _child_paths(old_path, old_children)
        new_paths = _child_paths(new_path, new_children)
        entries: list[_Entry] = []

        def pair(i: int, j: int) -> None:
            entries.append(("pair", old_children[i], new_children[j], old_paths[i], new_paths[j]))

        def removed(i: int) -> None:
            entries.append(("diff", self.removed(old_children[i], old_paths[i])))

        def added(j: int) -> None:
            entries.append(("diff", self.added(new_children[j], new_paths[j])))

        by_print = _align(
            [self.old_prints[c] for c in old_children], [self.new_prints[c] for c in new_children]
        )
        for op, i1, i2, j1, j2 in by_print:
            if op == "equal":
                continue  # identical subtrees
            by_tag = _align(
                [c.tag for c in old_children[i1:i2]], [c.tag for c in new_children[j1:j2]]
            )
            for tag_op, a1, a2, b1, b2 in by_tag:
                if tag_op == "equal":
                    for offset in range(a2 - a1):
                        pair(i1 + a1 + offset, j1 + b1 + offset)
                    continue
                # Pair the n-th old and n-th new element of each tag; the rest differ.
                pending: dict[str, list[int]] = {}
                for j in range(j1 + b1, j1 + b2):
                    pending.setdefault(new_children[j].tag, []).append(j)
                unmatched_old = []
                for i in range(i1 + a1, i1 + a2):
                    candidates = pending.get(old_children[i].tag)
                    if candidates:
                        pair(i, candidates.pop(0))
                    else:
                        unmatched_old.append(i)
                for i in unmatched_old:
                    removed(i)
                for j in sorted(j for rest in pending.values() for j in rest):
                    added(j)
        return entries


_BOMS = (
    (b"\xef\xbb\xbf", "utf-8"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
)
_DECLARED_ENCODING = re.compile(rb"""<\?xml[^>]*?encoding\s*=\s*["']([A-Za-z0-9._:-]+)["']""")


def read_text(path: Path) -> str:
    """The file's text, decoded by its BOM or XML declaration (UTF-8 if neither says).

    Undecodable bytes become U+FFFD instead of failing: the text is only displayed.
    """
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise XmlParseError(f"Cannot read {path.name}:\n{exc}") from exc
    for bom, encoding in _BOMS:
        if data.startswith(bom):
            return data[len(bom) :].decode(encoding, errors="replace")
    match = _DECLARED_ENCODING.match(data[:256])
    encoding = match.group(1).decode("ascii") if match else "utf-8"
    try:
        return data.decode(encoding, errors="replace")
    except LookupError:  # unknown encoding name in the declaration
        return data.decode("utf-8", errors="replace")


def diff_files(
    old_path: Path,
    new_path: Path,
    *,
    ignore_whitespace: bool = True,
    check_cancelled: Callable[[], None] = lambda: None,
    limit: int = MAX_DIFFERENCES,
) -> DiffOutcome:
    """Differences from ``old_path`` to ``new_path``, in document order."""
    norm = _normalizer(ignore_whitespace)
    old_root = _parse(old_path)
    check_cancelled()
    new_root = _parse(new_path)
    check_cancelled()
    old_prints = _fingerprints(old_root, norm, check_cancelled)
    new_prints = _fingerprints(new_root, norm, check_cancelled)
    differ = _Differ(norm, old_prints, new_prints, limit, check_cancelled)
    truncated = False
    try:
        differ.run(old_root, new_root)
    except _LimitReached:
        truncated = True
    return DiffOutcome(differ.out, truncated, len(old_prints), len(new_prints))
