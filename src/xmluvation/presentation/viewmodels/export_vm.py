"""Running the XPath search + CSV export, and the folder's XML file count."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QTimer, Signal

from ...application.export_xpath_csv import make_spec, run_export, summary_text
from ...application.xml_inspection import count_xml_files
from ...domain.errors import XMLuvationError
from ...domain.models import ExportResult
from ..tasks import TaskHandle, TaskRunner
from .base import ViewModel

FOLDER_COUNT_DEBOUNCE_MS = 300


class ExportViewModel(ViewModel):
    running_changed = Signal(bool)
    progress_changed = Signal(int)  # percent
    status_changed = Signal(str)  # "Processed i/n"
    folder_count_changed = Signal(str)

    def __init__(self, runner: TaskRunner) -> None:
        super().__init__()
        self._runner = runner
        self._handle: TaskHandle | None = None
        self._count_timer = QTimer(self)
        self._count_timer.setSingleShot(True)
        self._count_timer.setInterval(FOLDER_COUNT_DEBOUNCE_MS)
        self._count_timer.timeout.connect(self._count_now)
        self._count_folder = ""
        self._count_generation = 0

    @property
    def running(self) -> bool:
        return self._handle is not None

    def start(
        self,
        folder: str,
        output: str,
        headers_text: str,
        expressions: Sequence[str],
        group_matches: bool,
    ) -> None:
        if self._handle is not None:
            return
        try:
            spec = make_spec(folder, expressions, headers_text, output, group_matches)
        except XMLuvationError as exc:
            self.report_error(exc)
            return
        self.progress_changed.emit(0)
        self.status_changed.emit("")
        self.running_changed.emit(True)
        self._handle = self._runner.start(
            lambda ctx: run_export(spec, ctx, ctx.token),
            on_success=self._finished,
            on_error=lambda e: self.report_error(e, "CSV Export Error"),
            on_progress=self._progress,
            on_message=self.log_appended.emit,
            on_finished=self._cleanup,
        )

    def cancel(self) -> None:
        if self._handle is not None:
            self.log_appended.emit("Aborting CSV export...")
            self._handle.cancel()

    def _progress(self, done: int, total: int, text: str) -> None:
        self.progress_changed.emit(int(done * 100 / total) if total else 0)
        self.status_changed.emit(text)

    def _finished(self, result: ExportResult) -> None:
        self.log_replaced.emit(summary_text(result))

    def _cleanup(self) -> None:
        self._handle = None
        self.running_changed.emit(False)

    # -- folder file count (debounced, off the GUI thread) ------------------------------

    def folder_changed(self, folder: str) -> None:
        self._count_folder = folder
        self._count_timer.start()

    def _count_now(self) -> None:
        self._count_generation += 1
        generation, folder = self._count_generation, self._count_folder
        self._runner.start(
            lambda _ctx: count_xml_files(folder),
            on_success=lambda count: self._count_done(generation, count),
            on_error=lambda e: self._count_done(generation, e),
        )

    def _count_done(self, generation: int, result: object) -> None:
        if generation != self._count_generation:
            return  # a newer request is pending
        if isinstance(result, BaseException):
            self.folder_count_changed.emit(f"Error counting XML files: {result}")
        elif result is None:
            self.folder_count_changed.emit("")
        else:
            self.folder_count_changed.emit(
                f"Found {result} XML Files" if result else "No XML files found"
            )
