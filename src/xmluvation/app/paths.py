"""Locations of the configuration file and the log directory.

The configuration stays in ``src/config/config.json`` during development (as in 1.3.x).
In a Nuitka standalone build it is ``<install dir>/config/config.json``.
Qt resources (themes, icons, images) are compiled into the package and need no path.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths

PACKAGE_DIR = Path(__file__).resolve().parents[1]


def is_frozen() -> bool:
    return "__compiled__" in globals() or bool(getattr(sys, "frozen", False))


def app_root() -> Path:
    """``src/`` in development; the directory of the executable when frozen."""
    if is_frozen():
        return Path(sys.argv[0]).resolve().parent
    return PACKAGE_DIR.parent


def config_dir() -> Path:
    return app_root() / "config"


def config_file() -> Path:
    return config_dir() / "config.json"


def log_dir() -> Path:
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
    return Path(base) / "logs" if base else app_root() / "logs"
