"""Construct XPath 1.0 expressions from the builder's tag/attribute selections."""

from __future__ import annotations

import math

from .models import BuildCriteria, Operator


def xpath_literal(value: str) -> str:
    """Return ``value`` as a valid XPath 1.0 string literal.

    XPath 1.0 has no escape sequences, so a value containing both quote characters
    is expressed with ``concat()``.
    """
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    pieces: list[str] = []
    for index, part in enumerate(parts):
        if part:
            pieces.append(f"'{part}'")
        if index < len(parts) - 1:
            pieces.append('"\'"')
    return f"concat({', '.join(pieces)})"


def _is_number(value: str) -> bool:
    try:
        return math.isfinite(float(value))
    except ValueError:
        return False


def _comparison_operand(value: str) -> str:
    # Numbers stay unquoted so XPath compares numerically (the legacy behaviour);
    # anything else is quoted so it cannot be misread as a path expression.
    return value if _is_number(value) else xpath_literal(value)


def _predicate(subject: str, value: str, operator: Operator) -> str:
    match operator:
        case Operator.CONTAINS:
            return f"contains({subject}, {xpath_literal(value)})"
        case Operator.STARTS_WITH:
            return f"starts-with({subject}, {xpath_literal(value)})"
        case Operator.GREATER:
            return f"{subject} > {_comparison_operand(value)}"
        case Operator.SMALLER:
            return f"{subject} < {_comparison_operand(value)}"
        case _:
            return f"{subject}={xpath_literal(value)}"


def build_xpath(criteria: BuildCriteria) -> str:
    """Build an XPath expression; returns ``""`` when no tag is selected.

    * tag only                      -> ``//tag/text()``
    * tag + attribute               -> ``//tag[@attr]/@attr``
    * tag + value and/or attr value -> ``//tag[predicates]`` (selects the element)
    """
    c = criteria.normalized()
    if not c.tag:
        return ""

    predicates: list[str] = []
    if c.tag_value:
        predicates.append(_predicate("text()", c.tag_value, c.operator))
    if c.attribute:
        if c.attribute_value:
            predicates.append(_predicate(f"@{c.attribute}", c.attribute_value, c.operator))
        else:
            predicates.append(f"@{c.attribute}")

    xpath = f"//{c.tag}"
    if predicates:
        xpath += f"[{' and '.join(predicates)}]"

    if c.attribute and not c.attribute_value and not c.tag_value:
        xpath += f"/@{c.attribute}"
    elif not c.attribute and not c.tag_value:
        xpath += "/text()"
    return xpath
