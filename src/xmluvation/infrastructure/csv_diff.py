"""Structural comparison of two CSV files (rows and cells).

Algorithm
---------
Built like ``xml_diff``, with data rows in place of child elements:

1. Every data row gets a fingerprint: the hash of its values in the columns both files
   have (matched by name). Columns that only one file has are listed, not compared.
2. The rows are aligned by fingerprint with the patience diff of ``text_diff`` (anchored
   on rows that occur once in each file, ``difflib`` for the gaps). Identical rows are
   skipped, and inserted or deleted rows do not shift the others. (``xml_diff`` uses plain
   ``difflib`` with a size guard: sibling lists are short, a CSV file is one long list.)
3. In each region that differs, rows are paired by the key column (the n-th old row with a
   key value goes with the n-th new row with that value) or, without a key column, by
   position. Paired rows are compared cell by cell; the others are removed or added.
4. With a key column, a removed and an added row with the same key in different regions
   are paired as well. These rows, and rows paired out of order inside a region, moved.

For every row only its text (written as one CSV record) and its fingerprint are kept. The
cells of paired rows are parsed again from that text, so memory stays near the files' size.

The side-by-side view (``TextDiff``) has one line per record, header first, so its line
numbers are the row numbers a spreadsheet shows. Line breaks inside a cell show as ``↵``.
"""

from __future__ import annotations

import csv
from collections import Counter, deque
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from operator import itemgetter
from pathlib import Path

from ..domain.csv_checks import CellChange, RowChange, RowDifference
from ..domain.errors import CsvReadError, ValidationError
from ..domain.text_diff import (
    DiffRow,
    RowKind,
    Span,
    TextDiff,
    inline_spans,
    longest_increasing,
    patience_opcodes,
)
from . import csv_io

LINE_BREAK = "↵"  # ↵
_CHECK_EVERY = 10_000


class _Echo:
    """A "file" whose ``write`` returns its argument: ``csv.writer.writerow`` returns it."""

    def write(self, text: str) -> str:
        return text


def _normalizer(loose: bool) -> Callable[[str], str]:
    if loose:
        return lambda value: value.strip().casefold()
    return lambda value: value


def _display(text: str) -> str:
    return text.replace("\r\n", LINE_BREAK).replace("\r", LINE_BREAK).replace("\n", LINE_BREAK)


@dataclass(slots=True)
class _Table:
    path: Path
    fmt: csv_io.CsvFormat
    raw_header: list[str]
    header: list[str]  # names with surrounding spaces removed
    records: list[str] = field(default_factory=list)
    prints: list[int] = field(default_factory=list)
    keys: list[str] = field(default_factory=list)  # normalized key values (with a key only)

    @property
    def delimiter(self) -> str:
        return self.fmt.delimiter

    def cells(self, index: int) -> list[str]:
        return next(csv.reader([self.records[index]], delimiter=self.delimiter), [])

    def header_record(self) -> str:
        writer = csv.writer(_Echo(), delimiter=self.delimiter, lineterminator="")
        return str(writer.writerow(self.raw_header))


def _open(path: Path) -> _Table:
    fmt = csv_io.csv_format(path)
    with csv_io.csv_rows(path, fmt) as (_fmt, rows):
        first = next(rows, None)
    if not first:
        raise CsvReadError(f"{path.name} is empty.", title="CSV Error")
    header = [name.strip() for name in first]
    duplicates = sorted({name for name, count in Counter(header).items() if count > 1})
    if duplicates:
        raise ValidationError(
            f"{path.name} has duplicate column names: {', '.join(duplicates)}",
            title="Duplicate columns",
        )
    return _Table(path, fmt, first, header)


def _load(
    table: _Table,
    columns: Sequence[int],
    key_column: int | None,
    loose: bool,
    check: Callable[[], None],
) -> None:
    """Read the data rows of ``table``: record text, fingerprint and key of every row."""
    norm = _normalizer(loose)
    writer = csv.writer(_Echo(), delimiter=table.delimiter, lineterminator="")
    records, prints, keys = table.records, table.prints, table.keys
    needed = max([*columns, -1 if key_column is None else key_column]) + 1
    pick = itemgetter(*columns) if len(columns) > 1 else None  # fast path for full rows
    with csv_io.csv_rows(table.path, table.fmt) as (_fmt, rows):
        next(rows, None)  # header
        for count, row in enumerate(rows):
            if count % _CHECK_EVERY == 0:
                check()
            if not row:
                continue  # blank line
            records.append(writer.writerow(row))  # the row as it is, before padding
            if len(row) < needed:
                row = row + [""] * (needed - len(row))
            values = pick(row) if pick is not None else tuple(row[i] for i in columns)
            if loose:
                values = tuple(norm(value) for value in values)
            prints.append(hash(values))
            if key_column is not None:
                keys.append(norm(row[key_column]))


@dataclass(slots=True)
class CsvDiffOutcome:
    differences: list[RowDifference]
    old_columns: list[str]
    new_columns: list[str]
    old_rows: int = 0
    new_rows: int = 0
    unchanged: int = 0
    duplicate_keys: int = 0
    text_diff: TextDiff | None = None

    @property
    def only_in_old(self) -> list[str]:
        return [c for c in self.old_columns if c not in self.new_columns]

    @property
    def only_in_new(self) -> list[str]:
        return [c for c in self.new_columns if c not in self.old_columns]


# Display items: ("equal" | "pair", i, j), ("removed", i, -1), ("added", -1, j), with
# 0-based data row indices; a "pair" carries whether it moved. None = dropped item.
_Item = tuple[str, int, int, bool]


class _Differ:
    def __init__(
        self,
        old: _Table,
        new: _Table,
        key: str,
        norm: Callable[[str], str],
        build_view: bool,
        check: Callable[[], None],
    ) -> None:
        self.old, self.new = old, new
        self.key = key
        self.norm = norm
        self.build_view = build_view
        self.check = check
        self.old_index = {name: i for i, name in enumerate(old.header)}
        self.new_index = {name: i for i, name in enumerate(new.header)}
        self.columns = [name for name in old.header if name in self.new_index]  # compared
        self.items: list[_Item | None] = []
        self.unchanged = 0

    # -- pairing ---------------------------------------------------------------------------

    def run(self) -> None:
        for op, i1, i2, j1, j2 in patience_opcodes(self.old.prints, self.new.prints, self.check):
            self.check()
            if op == "equal":
                self.unchanged += i2 - i1
                if self.build_view:
                    self.items.extend(("equal", i1 + k, j1 + k, False) for k in range(i2 - i1))
            elif self.key:
                self._pair_by_key(i1, i2, j1, j2)
            else:
                self._pair_by_position(i1, i2, j1, j2)
        if self.key:
            self._pair_moved()

    def _pair_by_position(self, i1: int, i2: int, j1: int, j2: int) -> None:
        paired = min(i2 - i1, j2 - j1)
        self.items.extend(("pair", i1 + k, j1 + k, False) for k in range(paired))
        self.items.extend(("removed", i, -1, False) for i in range(i1 + paired, i2))
        self.items.extend(("added", -1, j, False) for j in range(j1 + paired, j2))

    def _pair_by_key(self, i1: int, i2: int, j1: int, j2: int) -> None:
        old_keys, new_keys = self.old.keys, self.new.keys
        pending: dict[str, deque[int]] = {}
        for j in range(j1, j2):
            pending.setdefault(new_keys[j], deque()).append(j)
        partner: dict[int, int] = {}  # new row -> old row
        unmatched: deque[int] = deque()
        for i in range(i1, i2):
            candidates = pending.get(old_keys[i])
            if candidates:
                partner[candidates.popleft()] = i
            else:
                unmatched.append(i)
        # Pairs in the order of both files stay in place; the others moved.
        in_order = {j for j, _i in longest_increasing(sorted(partner.items()))}
        for j in range(j1, j2):
            old_row = partner.get(j)
            if old_row is None:
                self.items.append(("added", -1, j, False))
            elif j in in_order:
                # Removed rows go before the first in-place pair that follows them.
                while unmatched and unmatched[0] < old_row:
                    self.items.append(("removed", unmatched.popleft(), -1, False))
                self.items.append(("pair", old_row, j, False))
            else:
                self.items.append(("pair", old_row, j, True))
        self.items.extend(("removed", i, -1, False) for i in unmatched)

    def _pair_moved(self) -> None:
        """Pair removed and added rows with the same key (from different regions)."""
        removed: dict[str, deque[int]] = {}
        for position, item in enumerate(self.items):
            if item is not None and item[0] == "removed":
                removed.setdefault(self.old.keys[item[1]], deque()).append(position)
        if not removed:
            return
        for position, item in enumerate(self.items):
            if item is None or item[0] != "added":
                continue
            candidates = removed.get(self.new.keys[item[2]])
            if candidates:
                source = candidates.popleft()
                old_row = self.items[source]
                assert old_row is not None
                self.items[source] = None
                self.items[position] = ("pair", old_row[1], item[2], True)

    # -- results ---------------------------------------------------------------------------

    def _cell_changes(self, old_cells: list[str], new_cells: list[str]) -> list[CellChange]:
        changes = []
        for name in self.columns:
            a, b = self.old_index[name], self.new_index[name]
            before = old_cells[a] if a < len(old_cells) else ""
            after = new_cells[b] if b < len(new_cells) else ""
            if self.norm(before) != self.norm(after):
                changes.append(CellChange(name, before, after))
        return changes

    def outcome(self) -> CsvDiffOutcome:
        old, new = self.old, self.new
        differences: list[RowDifference] = []
        rows: list[DiffRow] = []
        if self.build_view:
            rows.append(self._header_row())
        old_key = self.old_index.get(self.key)
        new_key = self.new_index.get(self.key)
        for count, item in enumerate(self.items):
            if count % _CHECK_EVERY == 0:
                self.check()
            if item is None:
                continue
            kind, i, j, moved = item
            if kind == "equal":
                rows.append(DiffRow(RowKind.EQUAL, i + 2, j + 2))
            elif kind == "removed":
                key = _cell(old.cells(i), old_key)
                differences.append(RowDifference(RowChange.REMOVED, i + 2, 0, key))
                rows.append(DiffRow(RowKind.REMOVED, i + 2, 0))
            elif kind == "added":
                key = _cell(new.cells(j), new_key)
                differences.append(RowDifference(RowChange.ADDED, 0, j + 2, key))
                rows.append(DiffRow(RowKind.ADDED, 0, j + 2))
            elif old.prints[i] == new.prints[j]:
                if moved:  # same content at another position: no need to parse the cells
                    key = _cell(new.cells(j), new_key)
                    differences.append(RowDifference(RowChange.MOVED, i + 2, j + 2, key))
                    rows.append(DiffRow(RowKind.CHANGED, i + 2, j + 2))
                else:
                    self.unchanged += 1
                    rows.append(DiffRow(RowKind.EQUAL, i + 2, j + 2))
            else:
                old_cells, new_cells = old.cells(i), new.cells(j)
                changes = self._cell_changes(old_cells, new_cells)
                if not changes and not moved:  # equal fingerprints by hash collision only
                    self.unchanged += 1
                    rows.append(DiffRow(RowKind.EQUAL, i + 2, j + 2))
                    continue
                differences.append(
                    RowDifference(
                        RowChange.MOVED if moved else RowChange.CHANGED,
                        i + 2,
                        j + 2,
                        _cell(new_cells, new_key),
                        tuple(changes),
                    )
                )
                if self.build_view:
                    old_spans, new_spans = self._spans(old_cells, new_cells, changes)
                    rows.append(DiffRow(RowKind.CHANGED, i + 2, j + 2, old_spans, new_spans))
        outcome = CsvDiffOutcome(
            differences,
            old.header,
            new.header,
            old_rows=len(old.records),
            new_rows=len(new.records),
            unchanged=self.unchanged,
        )
        if self.key:
            outcome.duplicate_keys = (len(old.keys) - len(set(old.keys))) + (
                len(new.keys) - len(set(new.keys))
            )
        if self.build_view:
            outcome.text_diff = TextDiff(
                [_display(old.header_record()), *map(_display, old.records)],
                [_display(new.header_record()), *map(_display, new.records)],
                rows,
            )
        return outcome

    def _header_row(self) -> DiffRow:
        old_line = _display(self.old.header_record())
        new_line = _display(self.new.header_record())
        if old_line == new_line:
            return DiffRow(RowKind.EQUAL, 1, 1)
        return DiffRow(RowKind.CHANGED, 1, 1, *inline_spans(old_line, new_line))

    def _spans(
        self, old_cells: list[str], new_cells: list[str], changes: list[CellChange]
    ) -> tuple[tuple[Span, ...], tuple[Span, ...]]:
        old_offsets = _cell_offsets(old_cells, self.old.delimiter)
        new_offsets = _cell_offsets(new_cells, self.new.delimiter)
        old_spans: list[Span] = []
        new_spans: list[Span] = []
        for change in changes:
            old_start, old_text = old_offsets(self.old_index[change.column])
            new_start, new_text = new_offsets(self.new_index[change.column])
            before, after = inline_spans(old_text, new_text)
            old_spans.extend((old_start + a, old_start + b) for a, b in before)
            new_spans.extend((new_start + a, new_start + b) for a, b in after)
        return tuple(sorted(old_spans)), tuple(sorted(new_spans))


def _cell(cells: list[str], index: int | None) -> str:
    return cells[index] if index is not None and index < len(cells) else ""


def _cell_offsets(cells: list[str], delimiter: str) -> Callable[[int], tuple[int, str]]:
    """``column -> (start, displayed text)`` of a cell inside the displayed record."""
    writer = csv.writer(_Echo(), delimiter=delimiter, lineterminator="")
    if len(cells) == 1:  # a lone empty cell is written as ""
        texts = [_display(writer.writerow(cells))]
    else:
        texts = [_display(writer.writerow([cell])) if cell else "" for cell in cells]
    starts = []
    position = 0
    for text in texts:
        starts.append(position)
        position += len(text) + len(delimiter)
    end = max(position - len(delimiter), 0)

    def offset(column: int) -> tuple[int, str]:
        if column < len(texts):
            return starts[column], texts[column]
        return end, ""  # the row is shorter than the header

    return offset


def diff_files(
    old_path: Path,
    new_path: Path,
    *,
    key: str = "",
    loose: bool = False,
    build_view: bool = True,
    check_cancelled: Callable[[], None] = lambda: None,
) -> CsvDiffOutcome:
    """Differences from ``old_path`` to ``new_path``, in the order of the new file.

    ``key`` names the column that identifies a row ("" pairs rows by position). With
    ``loose``, values (and keys) that differ only in case or surrounding spaces are equal.
    ``build_view`` also returns the side-by-side ``TextDiff`` of both files.
    """
    norm = _normalizer(loose)
    old, new = _open(old_path), _open(new_path)
    if key:
        for table in (old, new):
            if key not in table.header:
                raise ValidationError(
                    f"The key column '{key}' does not exist in {table.path.name}.",
                    title="Key not found",
                )
    common = set(new.header)
    columns = [name for name in old.header if name in common]
    old_key = old.header.index(key) if key else None
    new_key = new.header.index(key) if key else None
    _load(old, [old.header.index(c) for c in columns], old_key, loose, check_cancelled)
    _load(new, [new.header.index(c) for c in columns], new_key, loose, check_cancelled)
    check_cancelled()
    differ = _Differ(old, new, key, norm, build_view, check_cancelled)
    differ.run()
    return differ.outcome()
