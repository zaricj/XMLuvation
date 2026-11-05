from __future__ import annotations

import json
from pathlib import Path

import pytest

from xmluvation.application.presets import PresetService
from xmluvation.domain.errors import ValidationError
from xmluvation.infrastructure.config_store import ConfigStore


def test_missing_file_is_created(tmp_path: Path) -> None:
    path = tmp_path / "config" / "config.json"
    ConfigStore(path)
    assert json.loads(path.read_text(encoding="utf-8")) == {}


def test_invalid_json_is_backed_up_not_wiped(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"custom_paths": {"A": "C:/x"', encoding="utf-8")
    store = ConfigStore(path)
    backups = list(tmp_path.glob("config.corrupt-*.json"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == '{"custom_paths": {"A": "C:/x"'
    assert store.load_warning and backups[0].name in store.load_warning


def test_two_services_do_not_lose_updates(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    a = PresetService(ConfigStore(path))
    b = PresetService(ConfigStore(path))  # e.g. a second window with its own instance
    a.save_custom_path("P", "C:/p")
    b.save_preset("X", ["//a/@id"], ["ID"])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["custom_paths"] == {"P": "C:/p"}
    assert data["custom_xpaths_autofill"] == {
        "X": {"xpath_expression": ["//a/@id"], "csv_header": ["ID"]}
    }


def test_names_with_dots_are_kept_flat(tmp_path: Path) -> None:
    service = PresetService(ConfigStore(tmp_path / "c.json"))
    service.save_preset("v1.2 Filter", ["//a"], ["A"])
    assert [p.name for p in service.presets()] == ["v1.2 Filter"]
    service.delete_preset("v1.2 Filter")
    assert service.presets() == []


def test_external_edit_is_picked_up(tmp_path: Path) -> None:
    path = tmp_path / "c.json"
    service = PresetService(ConfigStore(path))
    path.write_text(json.dumps({"custom_paths": {"Hand": "D:/edited"}}), encoding="utf-8")
    assert service.custom_paths() == {"Hand": "D:/edited"}


def test_listeners_are_notified(tmp_path: Path) -> None:
    service = PresetService(ConfigStore(tmp_path / "c.json"))
    calls: list[int] = []
    service.subscribe(lambda: calls.append(1))
    service.save_custom_path("A", "B")
    assert calls == [1]


def test_reads_existing_repository_format(tmp_path: Path) -> None:
    path = tmp_path / "c.json"
    path.write_text(
        json.dumps(
            {
                "custom_xpaths_autofill": {
                    "Preset": {"xpath_expression": ["//a/@x\n"], "csv_header": ["X"]}
                },
                "custom_paths": {"NESIST02": "C:\\Exports"},
            }
        ),
        encoding="utf-8",
    )
    service = PresetService(ConfigStore(path))
    preset = service.preset("Preset")
    assert preset is not None and preset.xpaths == ("//a/@x\n",)
    assert service.custom_paths() == {"NESIST02": "C:\\Exports"}


@pytest.mark.parametrize(
    ("name", "xpaths", "headers", "message"),
    [
        ("", ["a"], ["A"], "name"),
        ("n", [], ["A"], "at least one"),
        ("n", ["a", "b"], ["A"], "same number"),
    ],
)
def test_preset_validation(
    tmp_path: Path, name: str, xpaths: list[str], headers: list[str], message: str
) -> None:
    service = PresetService(ConfigStore(tmp_path / "c.json"))
    with pytest.raises(ValidationError, match=message):
        service.save_preset(name, xpaths, headers)


def test_custom_path_requires_name_and_value(tmp_path: Path) -> None:
    service = PresetService(ConfigStore(tmp_path / "c.json"))
    with pytest.raises(ValidationError):
        service.save_custom_path("Name", "")
