"""User preferences persisted with QSettings (same organisation, application and keys as 1.3.x)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QByteArray, QSettings

DEFAULT_THEME = "dark_theme_default"
DEFAULT_PREVIEW_LIMIT_MB = 20
MAX_RECENT_EXPRESSIONS = 10
MAX_RECENT_FILES = 10


class SettingsStore:
    def __init__(self, settings: QSettings | None = None) -> None:
        self._s = settings if settings is not None else QSettings("Jovan", "XMLuvation")

    def _bool(self, key: str, default: bool) -> bool:
        return bool(self._s.value(key, default, type=bool))

    @property
    def theme(self) -> str:
        return str(self._s.value("app_theme", DEFAULT_THEME))

    @theme.setter
    def theme(self, key: str) -> None:
        self._s.setValue("app_theme", key)

    @property
    def group_matches(self) -> bool:
        return self._bool("group_matches", False)

    @group_matches.setter
    def group_matches(self, value: bool) -> None:
        self._s.setValue("group_matches", value)

    @property
    def prompt_on_exit(self) -> bool:
        return self._bool("prompt_on_exit", True)

    @prompt_on_exit.setter
    def prompt_on_exit(self, value: bool) -> None:
        self._s.setValue("prompt_on_exit", value)

    @property
    def recent_xpath_expressions(self) -> list[str]:
        value: Any = self._s.value("recent_xpath_expressions", [], type=list)
        return [str(v) for v in (value or [])]

    @recent_xpath_expressions.setter
    def recent_xpath_expressions(self, values: list[str]) -> None:
        self._s.setValue("recent_xpath_expressions", values[:MAX_RECENT_EXPRESSIONS])

    @property
    def recent_table_files(self) -> list[str]:
        value: Any = self._s.value("recent_table_files", [], type=list)
        return [str(v) for v in (value or [])]

    @recent_table_files.setter
    def recent_table_files(self, values: list[str]) -> None:
        self._s.setValue("recent_table_files", values[:MAX_RECENT_FILES])

    @property
    def xml_preview_limit_mb(self) -> int:
        value = self._s.value("xml_preview_limit_mb", DEFAULT_PREVIEW_LIMIT_MB, type=int)
        return max(1, int(value))

    @xml_preview_limit_mb.setter
    def xml_preview_limit_mb(self, value: int) -> None:
        self._s.setValue("xml_preview_limit_mb", max(1, int(value)))

    def window_state(self) -> tuple[QByteArray | None, QByteArray | None]:
        return self._s.value("geometry"), self._s.value("windowState")

    def set_window_state(self, geometry: QByteArray, state: QByteArray) -> None:
        self._s.setValue("geometry", geometry)
        self._s.setValue("windowState", state)

    def sync(self) -> None:
        self._s.sync()
