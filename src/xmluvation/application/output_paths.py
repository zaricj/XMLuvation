"""Choose output locations that never overwrite existing files or folders."""

from __future__ import annotations

from pathlib import Path


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
