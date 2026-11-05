from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QSettings

from xmluvation.infrastructure.settings_store import SettingsStore
from xmluvation.presentation.tasks import TaskRunner


@pytest.fixture
def settings(tmp_path: Path) -> SettingsStore:
    store = SettingsStore(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))
    store.prompt_on_exit = False
    return store


@pytest.fixture
def runner(qtbot) -> TaskRunner:  # noqa: ANN001
    task_runner = TaskRunner()
    yield task_runner
    task_runner.shutdown(5000)


@pytest.fixture
def window(qtbot, settings: SettingsStore, tmp_path: Path):  # noqa: ANN001
    from xmluvation.app.bootstrap import build_main_window

    win = build_main_window(settings, tmp_path / "config" / "config.json")
    qtbot.addWidget(win)
    win.show()
    yield win
    win.runner.shutdown(5000)
