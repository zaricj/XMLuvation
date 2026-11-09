"""Number text helpers for the small converters on the CSV tools page."""

from __future__ import annotations

import re

_IGNORED = str.maketrans("", "", " _\t")
_HEX = re.compile(r"([+-]?)(?:0[xX]|#)?([0-9a-fA-F]+)")


def parse_hex(text: str) -> int | None:
    """Parse a hexadecimal number; ``None`` for empty input.

    An optional sign, a ``0x``/``#`` prefix, spaces and underscores are accepted
    (``"0x1F_4"`` -> 500). Raises :class:`ValueError` for anything else.
    """
    value = text.translate(_IGNORED)
    if not value:
        return None
    match = _HEX.fullmatch(value)
    if match is None:
        raise ValueError(f"not a hexadecimal number: {text!r}")
    number = int(match.group(2), 16)
    return -number if match.group(1) == "-" else number
