"""Custom paths and XPath presets, backed by the shared configuration file.

Each window creates its own instance (so notifications go to that window); all
instances observe the same :class:`PresetService` and refresh when any one changes it.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Signal

from ...application.presets import PresetService
from ...domain.errors import XMLuvationError
from ...domain.models import XPathPreset
from .base import ViewModel


class PresetsViewModel(ViewModel):
    changed = Signal()

    def __init__(self, service: PresetService) -> None:
        super().__init__()
        self._service = service
        service.subscribe(self._on_store_changed)

    def dispose(self) -> None:
        self._service.unsubscribe(self._on_store_changed)

    def _on_store_changed(self) -> None:
        self.changed.emit()

    @property
    def load_warning(self) -> str | None:
        return self._service.load_warning

    def custom_paths(self) -> dict[str, str]:
        return self._service.custom_paths()

    def presets(self) -> list[XPathPreset]:
        return self._service.presets()

    def preset(self, name: str) -> XPathPreset | None:
        return self._service.preset(name)

    def _run(self, action: str, fn: Callable[..., None], *args: object) -> bool:
        try:
            fn(*args)
        except XMLuvationError as exc:
            self.report_error(exc)
            return False
        except OSError as exc:
            self.critical("Error", f"An error occurred while trying to {action}: {exc}")
            return False
        return True

    def save_custom_path(self, name: str, path: str) -> bool:
        return self._run("save the custom path", self._service.save_custom_path, name, path)

    def delete_custom_path(self, name: str) -> bool:
        return self._run("delete the custom path", self._service.delete_custom_path, name)

    def save_preset(self, name: str, xpaths: Sequence[str], headers: Sequence[str]) -> bool:
        return self._run("save the configuration", self._service.save_preset, name, xpaths, headers)

    def delete_preset(self, name: str) -> bool:
        return self._run("delete the configuration", self._service.delete_preset, name)
