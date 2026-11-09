"""File name rules for Lobster profile exports."""

from __future__ import annotations

import re

_STAR_SUFFIX = re.compile(r"_\*([^*]+)\*$")
_FORBIDDEN = '<>:"|?*'


def sanitize_filename_for_windows(filename: str) -> str:
    """Mimic how Windows stores an exported profile name.

    ``Name_*FB*`` becomes ``Name_FB``; characters Windows forbids are removed.
    """
    filename = _STAR_SUFFIX.sub(r"_\1", filename)
    for char in _FORBIDDEN:
        filename = filename.replace(char, "")
    return filename


def profile_file_name(entry: str) -> str:
    """CSV entry (profile name) -> expected XML file name."""
    name = entry.strip()
    if not name.lower().endswith(".xml"):
        name += ".xml"
    return name


_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"{p}{n}" for p in ("COM", "LPT") for n in range(1, 10)}
_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
MAX_STEM_LENGTH = 80


def safe_file_stem(value: str, empty: str = "(empty)") -> str:
    """Turn a cell value into a Windows-safe file name stem (no extension)."""
    stem = _UNSAFE.sub("_", value.strip())[:MAX_STEM_LENGTH].rstrip(". ")
    if not stem:
        return empty
    if stem.split(".", 1)[0].upper() in _RESERVED:
        stem = f"_{stem}"
    return stem


class UniqueStems:
    """Hand out file name stems that stay unique on case-insensitive file systems."""

    def __init__(self) -> None:
        self._taken: set[str] = set()

    def claim(self, stem: str) -> str:
        candidate, number = stem, 2
        while candidate.casefold() in self._taken:
            candidate = f"{stem} ({number})"
            number += 1
        self._taken.add(candidate.casefold())
        return candidate
