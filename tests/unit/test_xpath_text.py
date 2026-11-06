from __future__ import annotations

import json

import pytest

from tests.conftest import GOLDEN
from xmluvation.domain.models import BuildCriteria, Operator
from xmluvation.domain.xpath_text import (
    duplicate_headers,
    find_row_anchor,
    generate_header,
    is_value_xpath,
    parse_headers,
    smart_split,
)


def test_smart_split_matches_legacy(builder_golden: dict) -> None:
    for case in builder_golden["split"]:
        assert smart_split(case["input"]) == case["expected"]


def test_find_row_anchor_matches_legacy(golden_cases: dict) -> None:
    legacy = json.loads((GOLDEN / "anchor.json").read_text(encoding="utf-8"))
    for name, xpaths in golden_cases["anchor"].items():
        anchor = find_row_anchor(xpaths)
        if legacy[name] is None:
            assert anchor is None, name
        else:
            assert anchor is not None
            assert [anchor.anchor, anchor.relative] == legacy[name], name


@pytest.mark.parametrize(
    ("xpath", "expected"),
    [
        ("//a/@id", True),
        ("//a/text()", True),
        ("//a/text() ", True),
        ("//a[@id]", False),
        ("count(//a)", False),
        ("//ns:a/@ns:id", True),
    ],
)
def test_is_value_xpath(xpath: str, expected: bool) -> None:
    assert is_value_xpath(xpath) is expected


def test_parse_headers_and_duplicates() -> None:
    assert parse_headers(" A, B ,, C ") == ["A", "B", "C"]
    assert duplicate_headers(["A", "B", "A", "A", "C", "B"]) == ["A", "B"]


def test_generate_header_from_xpath_segments() -> None:
    assert generate_header("//field/filter/@id", None, []) == "filter @id"
    assert generate_header("@id", None, []) == "Header"


def test_generate_header_uses_criteria_only_when_expression_was_built_from_them() -> None:
    criteria = BuildCriteria("field", "", "name", "", Operator.EQUALS)
    assert generate_header("//field[@name]/@name", criteria, []) == "field @name"
    # typed by hand -> derived from the expression, not from stale combobox selections
    assert generate_header("//node/@id", criteria, []) == "node @id"


def test_generate_header_never_returns_duplicate_or_none() -> None:
    header = generate_header("//a/@id", None, ["a @id", "a @id (2)"])
    assert header == "a @id (3)"
