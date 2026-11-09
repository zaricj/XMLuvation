"""XML tools page: validate XML files against an XSD, compare two XML files."""

from __future__ import annotations

from PySide6.QtCore import Signal

from ...application.xml_tools import (
    SchemaValidationResult,
    XmlCompareResult,
    compare_summary,
    compare_xml,
    validate_against_schema,
    validation_summary,
)
from ..tasks import TaskHandle, TaskRunner
from .base import ViewModel


class XmlToolsViewModel(ViewModel):
    """``log_appended`` targets the XML tools output pane."""

    validation_running_changed = Signal(bool)
    validation_finished = Signal(object)  # SchemaValidationResult
    validation_progress = Signal(int, int)
    compare_running_changed = Signal(bool)
    compare_finished = Signal(object)  # XmlCompareResult

    def __init__(self, runner: TaskRunner) -> None:
        super().__init__()
        self._runner = runner
        self._validation: TaskHandle | None = None
        self._compare: TaskHandle | None = None

    # -- validate ------------------------------------------------------------------------

    def validate(self, schema_path: str, target_path: str) -> None:
        self.validation_running_changed.emit(True)
        self._validation = self._runner.start(
            lambda ctx: validate_against_schema(schema_path, target_path, ctx, ctx.token),
            on_success=self._validated,
            on_error=lambda e: self.report_error(e, "Validation failed"),
            on_message=self.log_appended.emit,
            on_progress=lambda done, total, _text: self.validation_progress.emit(done, total),
            on_cancelled=lambda: self.log_appended.emit("Validation cancelled."),
            on_finished=self._validation_ended,
        )

    def cancel_validation(self) -> None:
        if self._validation is not None:
            self._validation.cancel()

    def _validation_ended(self) -> None:
        self._validation = None
        self.validation_running_changed.emit(False)

    def _validated(self, result: SchemaValidationResult) -> None:
        for line in validation_summary(result):
            self.log_appended.emit(line)
        if result.report is not None:
            self.log_appended.emit(f"Report saved: {result.report}")
        self.validation_finished.emit(result)

    # -- compare -------------------------------------------------------------------------

    def compare(self, old_path: str, new_path: str, ignore_whitespace: bool) -> None:
        self.compare_running_changed.emit(True)
        self._compare = self._runner.start(
            lambda ctx: compare_xml(old_path, new_path, ignore_whitespace, ctx, ctx.token),
            on_success=self._compared,
            on_error=lambda e: self.report_error(e, "Compare failed"),
            on_message=self.log_appended.emit,
            on_cancelled=lambda: self.log_appended.emit("Compare cancelled."),
            on_finished=self._compare_ended,
        )

    def cancel_compare(self) -> None:
        if self._compare is not None:
            self._compare.cancel()

    def _compare_ended(self) -> None:
        self._compare = None
        self.compare_running_changed.emit(False)

    def _compared(self, result: XmlCompareResult) -> None:
        for line in compare_summary(result):
            self.log_appended.emit(line)
        if result.report is not None:
            self.log_appended.emit(f"Report saved: {result.report}")
        self.compare_finished.emit(result)
