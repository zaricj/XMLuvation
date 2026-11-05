"""CSV tab: conversion, header removal and Lobster profile cleanup."""

from __future__ import annotations

from PySide6.QtCore import Signal

from ...application.csv_tools import (
    ConversionResult,
    convert_csv,
    drop_csv_column,
    read_csv_headers,
)
from ...application.profile_cleanup import (
    CleanupPlan,
    CleanupResult,
    apply_cleanup,
    describe_plan,
    plan_cleanup,
)
from ..tasks import TaskRunner
from .base import ViewModel


class CsvToolsViewModel(ViewModel):
    """``log_appended`` targets the CSV tab's output pane."""

    busy_changed = Signal(bool)  # loading animation
    converted_file_changed = Signal(str)
    headers_changed = Signal(list)  # [] disables the header combobox
    column_dropped = Signal(int)
    cleanup_confirmation_requested = Signal(object)  # CleanupPlan
    cleanup_running_changed = Signal(bool)

    def __init__(self, runner: TaskRunner) -> None:
        super().__init__()
        self._runner = runner
        self._headers_generation = 0

    # -- conversion ---------------------------------------------------------------------

    def convert(self, csv_path: str, output_type: str, write_index: bool) -> None:
        self.busy_changed.emit(True)
        self._runner.start(
            lambda ctx: convert_csv(csv_path, output_type, write_index, ctx),
            on_success=self._converted,
            on_error=lambda e: self.report_error(e, "Conversion Error"),
            on_message=self.log_appended.emit,
            on_finished=lambda: self.busy_changed.emit(False),
        )

    def _converted(self, result: ConversionResult) -> None:
        self.log_appended.emit(
            f"Successfully converted:\n{result.source.name} -> {result.output.name}"
        )
        self.converted_file_changed.emit(str(result.output))

    # -- headers / column drop -------------------------------------------------------

    def csv_path_changed(self, csv_path: str) -> None:
        self._headers_generation += 1
        generation = self._headers_generation
        if not csv_path.strip():
            self.headers_changed.emit([])
            return
        self._runner.start(
            lambda _ctx: read_csv_headers(csv_path),
            on_success=lambda headers: self._headers_read(generation, headers),
            on_error=lambda e: self._headers_failed(generation, e),
        )

    def _headers_read(self, generation: int, headers: list[str]) -> None:
        if generation == self._headers_generation:
            self.headers_changed.emit(headers)

    def _headers_failed(self, generation: int, error: BaseException) -> None:
        if generation == self._headers_generation:
            self.headers_changed.emit([])
            self.report_error(error, "Exception reading CSV headers")

    def drop_column(self, csv_path: str, column: str, index: int) -> None:
        self._runner.start(
            lambda _ctx: drop_csv_column(csv_path, column, index),
            on_success=lambda _r: self._column_dropped(column, index),
            on_error=lambda e: self.report_error(e, "CSV Operation Failed"),
        )

    def _column_dropped(self, column: str, index: int) -> None:
        self.log_appended.emit(f"Successfully dropped column '{column}' and saved the updated CSV.")
        self.column_dropped.emit(index)

    # -- profile cleanup ----------------------------------------------------------------

    def plan_cleanup(self, csv_path: str, folder: str) -> None:
        self.cleanup_running_changed.emit(True)
        self._runner.start(
            lambda _ctx: plan_cleanup(csv_path, folder),
            on_success=self._planned,
            on_error=self._cleanup_failed,
        )

    def _planned(self, plan: CleanupPlan) -> None:
        for line in describe_plan(plan):
            self.log_appended.emit(line)
        if not plan.delete:
            self.log_appended.emit("Cleanup completed. Nothing to delete.")
            self.cleanup_running_changed.emit(False)
            return
        self.cleanup_confirmation_requested.emit(plan)

    def _cleanup_failed(self, error: BaseException) -> None:
        self.cleanup_running_changed.emit(False)
        self.report_error(error, "Cleanup Error")

    def confirm_cleanup(self, plan: CleanupPlan, confirmed: bool) -> None:
        if not confirmed:
            self.log_appended.emit("Cleanup cancelled. No files were deleted.")
            self.cleanup_running_changed.emit(False)
            return
        self._runner.start(
            lambda ctx: apply_cleanup(plan, ctx, ctx.token),
            on_success=self._cleaned,
            on_error=self._cleanup_failed,
            on_message=self.log_appended.emit,
            on_finished=lambda: self.cleanup_running_changed.emit(False),
        )

    def _cleaned(self, result: CleanupResult) -> None:
        summary = f"Cleanup completed. Deleted {len(result.deleted)} files."
        if result.failed:
            summary += f" {len(result.failed)} file(s) could not be deleted."
        self.log_appended.emit(summary)
