"""JSON configuration file (custom paths and XPath presets).

One instance is shared by the whole application. Every change is applied to the
latest file content and written atomically, so edits made in different windows - or
by hand in a text editor - are not lost. A file that is not valid JSON is moved
aside to ``config.corrupt-<timestamp>.json`` instead of being overwritten.
"""

from __future__ import annotations

import copy
import json
import logging
import threading
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from .csv_io import atomic_write_text

log = logging.getLogger(__name__)

ConfigData = dict[str, Any]


class ConfigStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.load_warning: str | None = None
        self._lock = threading.RLock()
        self._listeners: list[Callable[[], None]] = []
        self._stamp: tuple[int, int] | None = None
        self._data: ConfigData = {}
        self._load()

    # -- public API -------------------------------------------------------------------

    def read(self) -> ConfigData:
        """A deep copy of the current configuration (reloaded if the file changed)."""
        with self._lock:
            self._reload_if_changed()
            return copy.deepcopy(self._data)

    def update(self, mutate: Callable[[ConfigData], object]) -> None:
        """Apply ``mutate`` to the latest data, save atomically and notify listeners."""
        with self._lock:
            self._reload_if_changed()
            data = copy.deepcopy(self._data)
            mutate(data)
            self._save(data)
            self._data = data
        for listener in list(self._listeners):
            listener()

    def subscribe(self, listener: Callable[[], None]) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[], None]) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    # -- internals --------------------------------------------------------------------

    def _current_stamp(self) -> tuple[int, int] | None:
        try:
            stat = self.path.stat()
        except FileNotFoundError:
            return None
        return (stat.st_mtime_ns, stat.st_size)

    def _reload_if_changed(self) -> None:
        if self._current_stamp() != self._stamp:
            self._load()

    def _load(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save({})
            self._data = {}
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("top-level JSON value is not an object")
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as exc:
            backup = self.path.with_name(
                f"{self.path.stem}.corrupt-{datetime.now():%Y%m%d-%H%M%S}{self.path.suffix}"
            )
            self.path.replace(backup)
            log.warning("Invalid config %s moved to %s: %s", self.path, backup, exc)
            self.load_warning = (
                f"{self.path.name} contained invalid JSON ({exc}).\n"
                f"It was moved to {backup.name} and a new, empty configuration was created."
            )
            self._save({})
            data = {}
        self._data = data
        self._stamp = self._current_stamp()

    def _save(self, data: ConfigData) -> None:
        atomic_write_text(
            self.path,
            lambda handle: json.dump(data, handle, indent=4),
            newline=None,  # platform line endings, as before
            encoding="utf-8",
        )
        self._stamp = self._current_stamp()
