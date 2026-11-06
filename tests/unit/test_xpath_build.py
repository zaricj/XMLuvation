from __future__ import annotations

import pytest
from lxml import etree

from xmluvation.domain.models import BuildCriteria, Operator
from xmluvation.domain.xpath_build import build_xpath, xpath_literal


def _legacy_expectation(case: dict) -> str:
    """Legacy output, except non-numeric >/< operands are now quoted (bug fix)."""
    expected: str = case["expected"]
    if case["operator"] in ("greater", "smaller"):
        sign = ">" if case["operator"] == "greater" else "<"
        for value in (case["tag_value"], case["attribute_value"]):
            if value and not value.replace(".", "").isdigit():
                expected = expected.replace(f" {sign} {value}", f" {sign} '{value}'")
    return expected


def test_builder_matches_legacy_outputs(builder_golden: dict) -> None:
    for case in builder_golden["build"]:
        criteria = BuildCriteria(
            case["tag"],
            case["tag_value"],
            case["attribute"],
            case["attribute_value"],
            Operator(case["operator"]),
        )
        assert build_xpath(criteria) == _legacy_expectation(case), case


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("plain", "'plain'"),
        ("O'Brien", '"O\'Brien"'),
        ('say "hi"', "'say \"hi\"'"),
        ('it\'s "x"', "concat('it', \"'\", 's \"x\"')"),
        ("'", '"\'"'),
    ],
)
def test_xpath_literal(value: str, expected: str) -> None:
    assert xpath_literal(value) == expected


@pytest.mark.parametrize("value", ["O'Brien", 'a"b', 'it\'s "x"', "'''", "", "a,b"])
def test_literal_round_trips_through_lxml(value: str) -> None:
    root = etree.fromstring("<r/>")
    root.text = value
    assert root.xpath(f"string(.)={xpath_literal(value)}") is True


def test_builder_escapes_quotes_and_compiles() -> None:
    xpath = build_xpath(BuildCriteria("a", "O'Brien", "", "", Operator.CONTAINS))
    assert xpath == '//a[contains(text(), "O\'Brien")]'
    etree.XPath(xpath)


def test_no_tag_builds_nothing() -> None:
    assert build_xpath(BuildCriteria("", "x", "id", "1")) == ""
