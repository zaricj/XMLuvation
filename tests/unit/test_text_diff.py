from __future__ import annotations

import random

import pytest

from xmluvation.domain.errors import Cancelled
from xmluvation.domain.text_diff import RowKind, diff_lines, inline_spans, split_lines


def _kinds(old: list[str], new: list[str], **options: bool) -> list[tuple[str, int, int]]:
    return [
        (row.kind.value, row.old_number, row.new_number)
        for row in diff_lines(old, new, **options).rows
    ]


def _assert_complete(old: list[str], new: list[str]) -> None:
    """Every line of both sides appears exactly once, in order."""
    rows = diff_lines(old, new).rows
    assert [row.old_number for row in rows if row.old_number] == list(range(1, len(old) + 1))
    assert [row.new_number for row in rows if row.new_number] == list(range(1, len(new) + 1))


def test_split_lines_matches_parser_line_numbers() -> None:
    assert split_lines("a\r\nb\rc\nd\n") == ["a", "b", "c", "d"]
    assert split_lines("a\x0cb") == ["a\x0cb"]  # form feed is not a line break
    assert split_lines("") == []
    assert split_lines("a\n\n") == ["a", ""]


def test_rows_align_insertions_deletions_and_changes() -> None:
    old = ["<r>", "  <a>1</a>", "  <b>2</b>", "  <c>3</c>", "</r>"]
    new = ["<r>", "  <a>1</a>", "  <x>9</x>", "  <c>4</c>", "  <d>5</d>", "</r>"]
    assert _kinds(old, new) == [
        ("equal", 1, 1),
        ("equal", 2, 2),
        ("changed", 3, 3),
        ("changed", 4, 4),
        ("added", 0, 5),
        ("equal", 5, 6),
    ]
    diff = diff_lines(old, new)
    assert diff.hunks == [2]
    assert (diff.count(RowKind.CHANGED), diff.count(RowKind.ADDED)) == (2, 1)
    assert not diff.identical


def test_inserted_block_between_repeated_lines_keeps_the_rest_equal() -> None:
    item = ["  <item>", "    <flag>true</flag>", "  </item>"]
    old = ["<root>", *item * 50, "</root>"]
    new = ["<root>", *item * 20, "  <new/>", *item * 30, "</root>"]
    diff = diff_lines(old, new)
    assert diff.count(RowKind.ADDED) == 1
    assert diff.count(RowKind.REMOVED) == diff.count(RowKind.CHANGED) == 0


def test_whitespace_option() -> None:
    old, new = ["<a>", "  <b/>", "</a>"], ["<a>", "\t<b/>", "</a>"]
    assert diff_lines(old, new, ignore_whitespace=True).identical
    assert _kinds(old, new)[1] == ("changed", 2, 2)


def test_inline_spans_mark_only_the_changed_characters() -> None:
    old_spans, new_spans = inline_spans("<Timeout>30</Timeout>", "<Timeout>45</Timeout>")
    assert old_spans == ((9, 11),) and new_spans == ((9, 11),)
    assert inline_spans("ACME", "ACME Corp") == ((), ((4, 9),))
    assert inline_spans("abc", "xyz") == (((0, 3),), ((0, 3),))  # nothing in common


@pytest.mark.parametrize("seed", range(20))
def test_random_edits_keep_every_line(seed: int) -> None:
    rng = random.Random(seed)
    old = [rng.choice(["<a>", "</a>", "<b/>", f"<id>{n}</id>", ""]) for n in range(300)]
    new = list(old)
    for _ in range(30):
        position = rng.randrange(len(new) + 1)
        match rng.randrange(3):
            case 0:
                new.insert(position, f"<new>{position}</new>")
            case 1 if position < len(new):
                del new[position]
            case _ if position < len(new):
                new[position] += " x"
    _assert_complete(old, new)
    _assert_complete(new, old)
    _assert_complete([], new)
    _assert_complete(old, [])


def test_large_inputs_are_fast_and_cancellable() -> None:
    old = [f"<item><id>{n}</id><flag>true</flag></item>" for n in range(200_000)]
    new = list(old)
    new[1_000] = "<changed/>"
    new.insert(150_000, "<inserted/>")
    diff = diff_lines(old, new)
    assert (diff.count(RowKind.CHANGED), diff.count(RowKind.ADDED)) == (1, 1)

    def cancel() -> None:
        raise Cancelled

    with pytest.raises(Cancelled):
        diff_lines(old, [*new, "x"], check_cancelled=cancel)
