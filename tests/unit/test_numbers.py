from __future__ import annotations

import pytest

from xmluvation.domain.numbers import parse_hex


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1F4", 500),
        ("0x1f4", 500),
        ("#FF", 255),
        ("1F_4", 500),
        (" ff ", 255),
        ("-0x10", -16),
        ("", None),
    ],
)
def test_parse_hex(text: str, expected: int | None) -> None:
    assert parse_hex(text) == expected


@pytest.mark.parametrize("text", ["0x", "G1", "1.5", "--1"])
def test_parse_hex_rejects_invalid(text: str) -> None:
    with pytest.raises(ValueError):
        parse_hex(text)
