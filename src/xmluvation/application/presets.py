"""Use cases for the configuration file: custom folder paths and XPath presets ("autofill")."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from ..domain.errors import ValidationError
from ..domain.models import XPathPreset
from ..infrastructure.config_store import ConfigData, ConfigStore

PATHS_KEY = "custom_paths"
PRESETS_KEY = "custom_xpaths_autofill"
_XPATHS = "xpath_expression"
_HEADERS = "csv_header"


def _section(data: ConfigData, key: str) -> dict[str, object]:
    section = data.get(key)
    if not isinstance(section, dict):
        section = data[key] = {}
    return section


class PresetService:
    def __init__(self, store: ConfigStore) -> None:
        self._store = store

    @property
    def load_warning(self) -> str | None:
        return self._store.load_warning

    def subscribe(self, listener: Callable[[], None]) -> None:
        self._store.subscribe(listener)

    def unsubscribe(self, listener: Callable[[], None]) -> None:
        self._store.unsubscribe(listener)

    # -- custom paths -------------------------------------------------------------------

    def custom_paths(self) -> dict[str, str]:
        section = self._store.read().get(PATHS_KEY, {})
        if not isinstance(section, dict):
            return {}
        return {str(k): str(v) for k, v in section.items()}

    def save_custom_path(self, name: str, path: str) -> None:
        name, path = name.strip(), path.strip()
        if not name:
            raise ValidationError(
                "Please fill in the path name in order to save the custom path.",
                title="Missing path name",
            )
        if not path:
            raise ValidationError(
                "Please fill in the path value in order to save the custom path.",
                title="Missing path value",
            )
        self._store.update(lambda data: _section(data, PATHS_KEY).__setitem__(name, path))

    def delete_custom_path(self, name: str) -> None:
        self._store.update(lambda data: _section(data, PATHS_KEY).pop(name, None))

    # -- XPath presets ------------------------------------------------------------------

    def presets(self) -> list[XPathPreset]:
        section = self._store.read().get(PRESETS_KEY, {})
        if not isinstance(section, dict):
            return []
        result = []
        for name, value in section.items():
            if isinstance(value, dict):
                result.append(
                    XPathPreset(
                        str(name),
                        tuple(str(x) for x in value.get(_XPATHS, []) or []),
                        tuple(str(h) for h in value.get(_HEADERS, []) or []),
                    )
                )
        return result

    def preset(self, name: str) -> XPathPreset | None:
        return next((p for p in self.presets() if p.name == name), None)

    def save_preset(self, name: str, xpaths: Sequence[str], headers: Sequence[str]) -> None:
        name = name.strip()
        if not name:
            raise ValidationError(
                "Please set a name for the configuration.", title="Input validation failed!"
            )
        if not xpaths or not headers:
            raise ValidationError(
                "Please add at least one item to each list.", title="Input validation failed!"
            )
        if len(xpaths) != len(headers):
            raise ValidationError(
                "All lists must have the same number of items.", title="Input validation failed!"
            )
        entry = {_XPATHS: list(xpaths), _HEADERS: list(headers)}
        self._store.update(lambda data: _section(data, PRESETS_KEY).__setitem__(name, entry))

    def delete_preset(self, name: str) -> None:
        self._store.update(lambda data: _section(data, PRESETS_KEY).pop(name, None))
