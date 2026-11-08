"""Cancellation and progress reporting contract between use cases and their callers."""

from __future__ import annotations

import threading
from typing import Protocol

from ..domain.errors import Cancelled


class CancellationToken:
    """Thread-safe flag that a long-running use case polls."""

    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def raise_if_cancelled(self) -> None:
        if self._event.is_set():
            raise Cancelled()


class ProgressReporter(Protocol):
    """Callbacks a use case may call from its worker thread."""

    def progress(self, done: int, total: int, text: str = "") -> None: ...

    def message(self, text: str) -> None: ...


class NullReporter:
    def progress(self, done: int, total: int, text: str = "") -> None:
        pass

    def message(self, text: str) -> None:
        pass
