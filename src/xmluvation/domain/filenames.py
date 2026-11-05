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
