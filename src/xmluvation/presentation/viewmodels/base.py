"""Common ViewModel signals and error-to-notification mapping."""

from __future__ import annotations

import logging
from enum import StrEnum

from PySide6.QtCore import QObject, Signal

from ...domain.errors import ValidationError, XMLuvationError

log = logging.getLogger(__name__)


class Level(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ViewModel(QObject):
    """``notify(level, title, message)`` asks the view for a message box.

    ``log_appended`` / ``log_replaced`` target the window's program-output pane.
    """

    notify = Signal(str, str, str)
    log_appended = Signal(str)
    log_replaced = Signal(str)

    def info(self, title: str, message: str) -> None:
        self.notify.emit(Level.INFO, title, message)

    def warning(self, title: str, message: str) -> None:
        self.notify.emit(Level.WARNING, title, message)

    def critical(self, title: str, message: str) -> None:
        self.notify.emit(Level.CRITICAL, title, message)

    def report_error(self, error: BaseException, fallback_title: str = "Unexpected error") -> None:
        """Validation problems become warnings; other failures become critical messages."""
        if isinstance(error, ValidationError):
            self.warning(error.title, error.message)
        elif isinstance(error, XMLuvationError):
            self.critical(error.title, error.message)
        else:
            log.error("%s: %r", fallback_title, error)
            self.critical(
                fallback_title,
                f"{type(error).__name__}: {error}\n\nDetails were written to the log file.",
            )
