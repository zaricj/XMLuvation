"""Composition root: creates the QApplication, services and ViewModels and wires them together."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from types import TracebackType

from PySide6.QtWidgets import QApplication, QMessageBox

from .. import __version__
from ..application.presets import PresetService
from ..infrastructure.config_store import ConfigStore
from ..infrastructure.settings_store import SettingsStore
from ..presentation.tasks import TaskRunner
from ..presentation.viewmodels.csv_tools_vm import CsvToolsViewModel
from ..presentation.viewmodels.csv_transforms_vm import CsvTransformsViewModel
from ..presentation.viewmodels.export_vm import ExportViewModel
from ..presentation.viewmodels.presets_vm import PresetsViewModel
from ..presentation.viewmodels.settings_vm import SettingsViewModel
from ..presentation.viewmodels.table_viewer_vm import TableViewerViewModel
from ..presentation.viewmodels.xml_inspector_vm import XmlInspectorViewModel
from ..presentation.viewmodels.xml_tools_vm import XmlToolsViewModel
from ..presentation.viewmodels.xpath_workspace_vm import XPathWorkspaceViewModel
from ..presentation.views.main_window import MainViewModels, MainWindow
from . import paths

APP_NAME = "XMLuvation"
log = logging.getLogger("xmluvation")


def configure_logging(directory: Path) -> Path | None:
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(threadName)s %(name)s: %(message)s"
    )
    log_file: Path | None = None
    try:
        directory.mkdir(parents=True, exist_ok=True)
        log_file = directory / "xmluvation.log"
        handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        handler.setFormatter(formatter)
        root.addHandler(handler)
    except OSError:
        log_file = None
    if sys.stderr is not None:  # absent in windowed builds
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        root.addHandler(stream)
    return log_file


def install_excepthook(log_file: Path | None) -> None:
    def hook(exc_type: type[BaseException], exc: BaseException, tb: TracebackType | None) -> None:
        log.critical("Unhandled exception", exc_info=(exc_type, exc, tb))
        if QApplication.instance() is not None:
            where = f"\n\nDetails were written to:\n{log_file}" if log_file else ""
            QMessageBox.critical(None, "Unexpected error", f"{exc_type.__name__}: {exc}{where}")

    sys.excepthook = hook


def build_main_window(
    settings: SettingsStore | None = None, config_path: Path | None = None
) -> MainWindow:
    """Create services, ViewModels and the main window (also used by UI tests)."""
    settings = settings or SettingsStore()
    config_path = config_path or paths.config_file()
    runner = TaskRunner()
    service = PresetService(ConfigStore(config_path))
    settings_vm = SettingsViewModel(settings)
    vms = MainViewModels(
        settings=settings_vm,
        workspace=XPathWorkspaceViewModel(settings),
        inspector=XmlInspectorViewModel(runner, lambda: settings_vm.preview_limit_mb),
        export=ExportViewModel(runner),
        csv_tools=CsvToolsViewModel(runner),
        transforms=CsvTransformsViewModel(runner),
        xml_tools=XmlToolsViewModel(runner),
        table=TableViewerViewModel(runner, settings),
        presets=PresetsViewModel(service),
        new_presets_vm=lambda: PresetsViewModel(service),
    )
    window = MainWindow(vms, runner, config_path.parent, f"{APP_NAME} v{__version__}")
    runner.setParent(window)
    return window


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Jovan")
    log_file = configure_logging(paths.log_dir())
    install_excepthook(log_file)
    log.info("Starting %s %s (config: %s)", APP_NAME, __version__, paths.config_file())
    window = build_main_window()
    window.show()
    return app.exec()
