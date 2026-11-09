"""CSV tools page: split a file, compare two files, and edit columns."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import Signal

from ...application.csv_compare import CompareResult, compare_csv, summary_lines
from ...application.csv_split import SplitMode, SplitResult, split_csv
from ...application.csv_tools import ColumnEdit, ColumnEditResult, save_column_edits
from ..tasks import TaskHandle, TaskRunner
from .base import ViewModel
from .header_reader import HeaderReader


class CsvTransformsViewModel(ViewModel):
    """``log_appended`` targets the CSV tools output pane."""

    split_running_changed = Signal(bool)
    split_finished = Signal(object)  # SplitResult
    compare_running_changed = Signal(bool)
    compare_finished = Signal(object)  # CompareResult
    columns_running_changed = Signal(bool)
    columns_saved = Signal(object)  # ColumnEditResult

    def __init__(self, runner: TaskRunner) -> None:
        super().__init__()
        self._runner = runner
        self.split_headers = HeaderReader(runner, self)
        self.compare_headers = HeaderReader(runner, self)  # columns of the old file (key choice)
        self.column_headers = HeaderReader(runner, self)
        for reader in (self.split_headers, self.compare_headers, self.column_headers):
            reader.failed.connect(lambda e: self.report_error(e, "Cannot read CSV headers"))
        self._split: TaskHandle | None = None
        self._compare: TaskHandle | None = None

    # -- split ---------------------------------------------------------------------------

    def split(self, path: str, by_column: bool, rows_per_file: int, column: str) -> None:
        mode = SplitMode.COLUMN if by_column else SplitMode.ROWS
        self.split_running_changed.emit(True)
        self._split = self._runner.start(
            lambda ctx: split_csv(
                path,
                mode,
                rows_per_file=rows_per_file,
                column=column,
                reporter=ctx,
                token=ctx.token,
            ),
            on_success=self._split_done,
            on_error=lambda e: self.report_error(e, "Split failed"),
            on_message=self.log_appended.emit,
            on_cancelled=lambda: self.log_appended.emit("Split cancelled. No files were kept."),
            on_finished=self._split_ended,
        )

    def cancel_split(self) -> None:
        if self._split is not None:
            self._split.cancel()

    def _split_ended(self) -> None:
        self._split = None
        self.split_running_changed.emit(False)

    def _split_done(self, result: SplitResult) -> None:
        self.log_appended.emit(
            f"Split {result.rows:,} rows into {len(result.files):,} files in {result.folder}"
        )
        self.split_finished.emit(result)

    # -- compare -------------------------------------------------------------------------

    def compare(self, old_path: str, new_path: str, key: str, loose: bool) -> None:
        self.compare_running_changed.emit(True)
        self._compare = self._runner.start(
            lambda ctx: compare_csv(old_path, new_path, key, loose, ctx, ctx.token),
            on_success=self._compare_done,
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

    def _compare_done(self, result: CompareResult) -> None:
        for line in summary_lines(result):
            self.log_appended.emit(line)
        self.log_appended.emit(f"Report saved: {result.report}")
        self.compare_finished.emit(result)

    # -- columns -------------------------------------------------------------------------

    def save_columns(self, path: str, columns: Sequence[tuple[int, str]], overwrite: bool) -> None:
        edits = [ColumnEdit(index, name) for index, name in columns]
        header = self.column_headers.headers
        self.columns_running_changed.emit(True)
        self._runner.start(
            lambda _ctx: save_column_edits(path, edits, header, overwrite),
            on_success=self._columns_done,
            on_error=lambda e: self.report_error(e, "Saving columns failed"),
            on_finished=lambda: self.columns_running_changed.emit(False),
        )

    def _columns_done(self, result: ColumnEditResult) -> None:
        removed = f", removed {result.removed}" if result.removed else ""
        self.log_appended.emit(
            f"Saved {result.columns} column(s){removed} for {result.rows:,} rows: {result.output}"
        )
        source = self.column_headers.path
        if source and result.output == Path(source):
            self.column_headers.reload()  # the file was overwritten: show its new columns
        self.columns_saved.emit(result)
