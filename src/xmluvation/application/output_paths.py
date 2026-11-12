"""Choose output locations that never overwrite existing files or folders.

The one exception is a compare report: it always has the same name next to the new file
and replaces the report of the previous compare of the same two files
(:func:`replace_report`). Users who want to keep a report copy it elsewhere.
"""

from __future__ import annotations

from pathlib import Path

from ..domain.errors import OutputFileError


def replace_report(path: Path) -> Path:
    """Delete an earlier report at ``path`` and return ``path`` for the new one."""
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        raise OutputFileError(
            f"Cannot replace the earlier report {path.name}. "
            f"Is it open in another program (e.g. Excel)?\n{exc}"
        ) from exc
    return path


def unique_path(path: Path) -> Path:
    """``path`` if it is free, else ``name (2).ext``, ``name (3).ext``, ..."""
    candidate, number = path, 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem} ({number}){path.suffix}")
        number += 1
    return candidate


def new_folder(path: Path) -> Path:
    """Create and return a new, empty folder at ``path`` or ``path (2)``, ``path (3)``, ..."""
    candidate, number = path, 2
    while True:
        try:
            candidate.mkdir(parents=True)
            return candidate
        except FileExistsError:
            candidate = path.with_name(f"{path.name} ({number})")
            number += 1
