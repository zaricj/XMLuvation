"""User preferences: theme, exit prompt, grouping option, XML preview limit."""

from __future__ import annotations

from PySide6.QtCore import QByteArray, Signal

from ...infrastructure.settings_store import DEFAULT_THEME, SettingsStore
from ..themes import THEMES
from .base import ViewModel

MAX_PREVIEW_LIMIT_MB = 2048


class SettingsViewModel(ViewModel):
    theme_changed = Signal(str)
    preview_limit_changed = Signal(int)

    def __init__(self, store: SettingsStore) -> None:
        super().__init__()
        self._store = store

    @property
    def theme(self) -> str:
        key = self._store.theme
        return key if key in THEMES else DEFAULT_THEME

    def set_theme(self, key: str) -> None:
        if key not in THEMES:
            self.warning("Theme Error", f"Unknown theme: {key}")
            return
        self._store.theme = key
        self.theme_changed.emit(key)

    @property
    def prompt_on_exit(self) -> bool:
        return self._store.prompt_on_exit

    def set_prompt_on_exit(self, value: bool) -> None:
        self._store.prompt_on_exit = value

    @property
    def group_matches(self) -> bool:
        return self._store.group_matches

    def set_group_matches(self, value: bool) -> None:
        self._store.group_matches = value

    @property
    def preview_limit_mb(self) -> int:
        return self._store.xml_preview_limit_mb

    def set_preview_limit_mb(self, value: int) -> None:
        value = max(1, min(int(value), MAX_PREVIEW_LIMIT_MB))
        self._store.xml_preview_limit_mb = value
        self.preview_limit_changed.emit(value)
        self.log_appended.emit(f"XML preview limit set to {value} MB.")

    def window_state(self) -> tuple[QByteArray | None, QByteArray | None]:
        return self._store.window_state()

    def save_window_state(self, geometry: QByteArray, state: QByteArray) -> None:
        self._store.set_window_state(geometry, state)
        self._store.sync()
