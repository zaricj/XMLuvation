"""CSV tools page: conversion and Lobster profile cleanup."""

from __future__ import annotations

from PySide6.QtCore import Signal

from ...application.csv_tools import ConversionResult, convert_csv, suggested_output_type
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

    conversion_running_changed = Signal(bool)
    converted_file_changed = Signal(str)
    cleanup_confirmation_requested = Signal(object)  # CleanupPlan
    cleanup_running_changed = Signal(bool)

    def __init__(self, runner: TaskRunner) -> None:
        super().__init__()
        self._runner = runner

    # -- conversion ---------------------------------------------------------------------

    def convert(
        self,
        csv_path: str,
        output_type: str,
        write_index: bool,
        delimiter: str | None = None,
    ) -> None:
        """``delimiter`` (as typed by the user) overrides detection; ``None`` detects it."""
        self.conversion_running_changed.emit(True)
        self._runner.start(
            lambda ctx: convert_csv(csv_path, output_type, write_index, ctx, delimiter),
            on_success=self._converted,
            on_error=lambda e: self.report_error(e, "Conversion Error"),
            on_message=self.log_appended.emit,
            on_finished=lambda: self.conversion_running_changed.emit(False),
        )

    @staticmethod
    def suggested_output_type(path: str, current: str) -> str | None:
        """Output type to select for a newly chosen input file (``None``: keep ``current``)."""
        return suggested_output_type(path, current)

    def _converted(self, result: ConversionResult) -> None:
        self.log_appended.emit(
            f"Successfully converted:\n{result.source.name} -> {result.output.name}"
        )
        self.converted_file_changed.emit(str(result.output))

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
