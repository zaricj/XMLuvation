"""Line-by-line, side-by-side text diff (the "two panes, red and green" view of an IDE).

Algorithm
---------
Lines are matched with a *patience* diff: inside a region, lines that occur exactly once
on each side are used as anchors (longest increasing run of them), and the gaps between
anchors are processed the same way. The common start and end of every region are matched
first. A gap without unique lines is aligned with ``difflib`` (with "autojunk" when it is
large); a gap too large even for that is paired line by line by position.

``difflib`` alone is quadratic on XML, where lines like ``</item>`` repeat thousands of
times; anchoring on unique lines (ids, names, values) keeps large files fast and gives
the alignment a reader expects.

Within a changed line, the differing characters are marked as well (``DiffRow.old_spans``
and ``new_spans``).
"""

from __future__ import annotations

import bisect
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from enum import StrEnum

# Gaps without unique lines are aligned with difflib up to this many line comparisons.
_DIFFLIB_LIMIT = 250_000
# Larger gaps up to this many lines per side use difflib with autojunk (~0.1 s at 10,000
# lines); beyond that their lines are paired by position.
_JUNK_DIFFLIB_LINES = 30_000
# Character-level marking inside a changed line up to this many character comparisons.
_INLINE_LIMIT = 40_000
# Below this share of matching characters, a changed line is marked as a whole.
_INLINE_MIN_RATIO = 0.4

Span = tuple[int, int]
Opcode = tuple[str, int, int, int, int]


class RowKind(StrEnum):
    EQUAL = "equal"
    CHANGED = "changed"  # a line on both sides, with different content
    REMOVED = "removed"  # a line only in the old text
    ADDED = "added"  # a line only in the new text


@dataclass(frozen=True, slots=True)
class DiffRow:
    """One row of the side-by-side view. Line numbers are 1-based, 0 = no line on that side."""

    kind: RowKind
    old_number: int
    new_number: int
    old_spans: tuple[Span, ...] = ()
    new_spans: tuple[Span, ...] = ()


@dataclass(slots=True)
class TextDiff:
    old_lines: list[str]
    new_lines: list[str]
    rows: list[DiffRow] = field(default_factory=list)

    @property
    def hunks(self) -> list[int]:
        """Index of the first row of every block of consecutive changed rows."""
        starts = []
        previous_equal = True
        for index, row in enumerate(self.rows):
            equal = row.kind is RowKind.EQUAL
            if not equal and previous_equal:
                starts.append(index)
            previous_equal = equal
        return starts

    def count(self, kind: RowKind) -> int:
        return sum(1 for row in self.rows if row.kind is kind)

    @property
    def identical(self) -> bool:
        return all(row.kind is RowKind.EQUAL for row in self.rows)


def split_lines(text: str) -> list[str]:
    """Lines as numbered by XML parsers and editors (``\\r\\n``, ``\\r`` or ``\\n`` only).

    ``str.splitlines`` also splits on form feeds and Unicode separators, which would shift
    the line numbers against the ones in the report.
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()  # a final newline ends the last line, it does not start a new one
    return lines


def _no_check() -> None:
    return None


def _longest_increasing(pairs: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Longest run of ``pairs`` (sorted by first item) that also increases in the second."""
    tails: list[int] = []  # second item of the last pair of the best run of each length
    tail_index: list[int] = []
    previous = [-1] * len(pairs)
    for index, (_i, j) in enumerate(pairs):
        position = bisect.bisect_left(tails, j)
        if position == len(tails):
            tails.append(j)
            tail_index.append(index)
        else:
            tails[position] = j
            tail_index[position] = index
        previous[index] = tail_index[position - 1] if position else -1
    run = []
    index = tail_index[-1] if tail_index else -1
    while index != -1:
        run.append(pairs[index])
        index = previous[index]
    run.reverse()
    return run


def _matches(
    a: Sequence[str], b: Sequence[str], check: Callable[[], None]
) -> list[tuple[int, int]]:
    """Matched line pairs ``(i, j)``, increasing in both indices."""
    matched: list[tuple[int, int]] = []
    regions = [(0, len(a), 0, len(b))]
    while regions:
        check()
        a_lo, a_hi, b_lo, b_hi = regions.pop()
        while a_lo < a_hi and b_lo < b_hi and a[a_lo] == b[b_lo]:
            matched.append((a_lo, b_lo))
            a_lo, b_lo = a_lo + 1, b_lo + 1
        while a_lo < a_hi and b_lo < b_hi and a[a_hi - 1] == b[b_hi - 1]:
            a_hi, b_hi = a_hi - 1, b_hi - 1
            matched.append((a_hi, b_hi))
        if a_lo == a_hi or b_lo == b_hi:
            continue
        a_counts = Counter(a[a_lo:a_hi])
        b_first: dict[str, int] = {}
        b_counts: Counter[str] = Counter()
        for j in range(b_lo, b_hi):
            b_counts[b[j]] += 1
            b_first.setdefault(b[j], j)
        unique = [
            (i, b_first[a[i]])
            for i in range(a_lo, a_hi)
            if a_counts[a[i]] == 1 and b_counts.get(a[i]) == 1
        ]
        anchors = _longest_increasing(unique)
        if anchors:
            matched.extend(anchors)
            bounds = [(a_lo - 1, b_lo - 1), *anchors, (a_hi, b_hi)]
            for (i1, j1), (i2, j2) in zip(bounds, bounds[1:], strict=False):
                if i2 - i1 > 1 and j2 - j1 > 1:
                    regions.append((i1 + 1, i2, j1 + 1, j2))
            continue
        exact = (a_hi - a_lo) * (b_hi - b_lo) <= _DIFFLIB_LIMIT
        if exact or max(a_hi - a_lo, b_hi - b_lo) <= _JUNK_DIFFLIB_LINES:
            # Larger gaps: difflib's "autojunk" skips very frequent lines (``</item>``)
            # as match starts, which keeps it fast enough there.
            matcher = SequenceMatcher(None, a[a_lo:a_hi], b[b_lo:b_hi], autojunk=not exact)
            for block in matcher.get_matching_blocks():
                matched.extend((a_lo + block.a + k, b_lo + block.b + k) for k in range(block.size))
        # Otherwise nothing matches here: the region becomes one block of changed lines.
    matched.sort()
    return matched


def _opcodes(a: Sequence[str], b: Sequence[str], check: Callable[[], None]) -> list[Opcode]:
    ops: list[Opcode] = []
    i = j = 0
    for mi, mj in [*_matches(a, b, check), (len(a), len(b))]:
        if i < mi and j < mj:
            ops.append(("replace", i, mi, j, mj))
        elif i < mi:
            ops.append(("delete", i, mi, j, j))
        elif j < mj:
            ops.append(("insert", i, i, j, mj))
        if mi < len(a) and mj < len(b):
            if ops and ops[-1][0] == "equal" and ops[-1][2] == mi:
                _, i1, _i2, j1, _j2 = ops[-1]
                ops[-1] = ("equal", i1, mi + 1, j1, mj + 1)
            else:
                ops.append(("equal", mi, mi + 1, mj, mj + 1))
        i, j = mi + 1, mj + 1
    return ops


def inline_spans(old: str, new: str) -> tuple[tuple[Span, ...], tuple[Span, ...]]:
    """Character ranges that differ between two versions of a line."""
    prefix = 0
    limit = min(len(old), len(new))
    while prefix < limit and old[prefix] == new[prefix]:
        prefix += 1
    suffix = 0
    while suffix < limit - prefix and old[len(old) - 1 - suffix] == new[len(new) - 1 - suffix]:
        suffix += 1
    old_mid, new_mid = old[prefix : len(old) - suffix], new[prefix : len(new) - suffix]
    if old_mid and new_mid and len(old_mid) * len(new_mid) <= _INLINE_LIMIT:
        matcher = SequenceMatcher(None, old_mid, new_mid, autojunk=False)
        if matcher.ratio() >= _INLINE_MIN_RATIO:
            old_spans: list[Span] = []
            new_spans: list[Span] = []
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    continue
                if i2 > i1:
                    old_spans.append((prefix + i1, prefix + i2))
                if j2 > j1:
                    new_spans.append((prefix + j1, prefix + j2))
            return tuple(old_spans), tuple(new_spans)
    return (
        ((prefix, prefix + len(old_mid)),) if old_mid else (),
        ((prefix, prefix + len(new_mid)),) if new_mid else (),
    )


def _whitespace_key(line: str) -> str:
    return " ".join(line.split())


def diff_lines(
    old_lines: list[str],
    new_lines: list[str],
    *,
    ignore_whitespace: bool = False,
    check_cancelled: Callable[[], None] = _no_check,
) -> TextDiff:
    """Side-by-side rows from ``old_lines`` to ``new_lines``.

    With ``ignore_whitespace``, lines that differ only in spaces and indentation count as
    equal (blank lines still count).
    """
    if ignore_whitespace:
        a = [_whitespace_key(line) for line in old_lines]
        b = [_whitespace_key(line) for line in new_lines]
    else:
        a, b = old_lines, new_lines
    result = TextDiff(old_lines, new_lines)
    rows = result.rows
    for tag, i1, i2, j1, j2 in _opcodes(a, b, check_cancelled):
        if tag == "equal":
            rows.extend(DiffRow(RowKind.EQUAL, i1 + k + 1, j1 + k + 1) for k in range(i2 - i1))
            continue
        paired = min(i2 - i1, j2 - j1)
        for k in range(paired):
            i, j = i1 + k, j1 + k
            if a[i] == b[j]:
                rows.append(DiffRow(RowKind.EQUAL, i + 1, j + 1))
            else:
                old_spans, new_spans = inline_spans(old_lines[i], new_lines[j])
                rows.append(DiffRow(RowKind.CHANGED, i + 1, j + 1, old_spans, new_spans))
        rows.extend(DiffRow(RowKind.REMOVED, i + 1, 0) for i in range(i1 + paired, i2))
        rows.extend(DiffRow(RowKind.ADDED, 0, j + 1) for j in range(j1 + paired, j2))
    return result
