"""Reads a CSV file's header row in the background whenever its path changes."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from ...application.csv_tools import read_csv_headers
from ..tasks import TaskRunner


class HeaderReader(QObject):
    """``set_path`` -> ``headers_changed(list)``; only the latest request is delivered.

    ``failed(BaseException)`` reports unreadable files; ``headers_changed([])`` is emitted
    for empty paths, non-CSV paths and failures, so views can simply disable their inputs.
    """

    headers_changed = Signal(list)
    failed = Signal(object)

    def __init__(self, runner: TaskRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runner = runner
        self._generation = 0
        self._path = ""
        self._headers: list[str] = []

    @property
    def path(self) -> str:
        return self._path

    @property
    def headers(self) -> list[str]:
        """Header names of ``path`` as last read (stripped)."""
        return list(self._headers)

    def set_path(self, path: str) -> None:
        self._generation += 1
        generation = self._generation
        self._path = path.strip()
        if not self._path:
            self._deliver(generation, [])
            return
        target = self._path
        self._runner.start(
            lambda _ctx: read_csv_headers(target),
            on_success=lambda headers: self._deliver(generation, headers),
            on_error=lambda error: self._fail(generation, error),
        )

    def reload(self) -> None:
        self.set_path(self._path)

    def _deliver(self, generation: int, headers: list[str]) -> None:
        if generation == self._generation:
            self._headers = list(headers)
            self.headers_changed.emit(list(headers))

    def _fail(self, generation: int, error: BaseException) -> None:
        if generation == self._generation:
            self._deliver(generation, [])
            self.failed.emit(error)
