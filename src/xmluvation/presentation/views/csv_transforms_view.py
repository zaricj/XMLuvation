"""Binds the Split, Compare and Columns tools of the CSV tools page to their ViewModel."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QComboBox, QLineEdit, QListWidgetItem, QSizePolicy

from ...application.csv_compare import CompareResult, summary_lines
from ...application.csv_split import EXCEL_ROWS_PER_SHEET, SplitResult
from ...application.csv_tools import ColumnEditResult
from ..viewmodels.csv_transforms_vm import CsvTransformsViewModel
from .common import browse_open_file_into, open_path

if TYPE_CHECKING:
    from .main_window import MainWindow

_SOURCE_INDEX = Qt.ItemDataRole.UserRole
_ORIGINAL_NAME = Qt.ItemDataRole.UserRole + 1
CSV_FILTER = "CSV File (*.csv)"
# Last entry of the key combobox: compare without a key column.
NO_KEY_TEXT = "(no key: pair rows by position)"
_NO_KEY = "no-key"


def _refill(combo: QComboBox, items: list[str]) -> None:
    current = combo.currentText()
    combo.blockSignals(True)
    combo.clear()
    combo.addItems(items)
    if current in items:
        combo.setCurrentText(current)
    elif items:
        combo.setCurrentIndex(0)  # with placeholder text, Qt leaves the index at -1
    combo.blockSignals(False)
    combo.setDisabled(not items)


def _show_path(edit: QLineEdit, path: str) -> None:
    edit.setText(path)
    edit.setCursorPosition(0)
    edit.setToolTip(path)


class CsvTransformsView(QObject):
    def __init__(
        self,
        window: MainWindow,
        vm: CsvTransformsViewModel,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.ui = window.ui
        self.vm = vm
        for frame in (
            self.ui.frame_split_result,
            self.ui.frame_compare_result,
            self.ui.frame_columns_result,
        ):
            frame.hide()
        self._show_diff_card(False)
        self._bind_split()
        self._bind_compare()
        self._bind_columns()

    def _browse(self, target: QLineEdit, caption: str = "Select CSV file") -> None:
        browse_open_file_into(self.window, caption, target, CSV_FILTER)

    # ------------------------------------------------------------------ split

    def _bind_split(self) -> None:
        ui, vm = self.ui, self.vm
        ui.button_split_browse_csv_file_path.clicked.connect(
            lambda: self._browse(ui.line_edit_split_csv_file_path, "Select CSV file to split")
        )
        ui.line_edit_split_csv_file_path.textChanged.connect(vm.split_headers.set_path)
        vm.split_headers.headers_changed.connect(self._show_split_columns)
        ui.button_split_excel_rows.clicked.connect(
            lambda: ui.spin_box_split_rows.setValue(EXCEL_ROWS_PER_SHEET)
        )
        ui.radio_split_by_rows.toggled.connect(self._split_mode_changed)
        ui.button_split_start.clicked.connect(
            lambda: vm.split(
                ui.line_edit_split_csv_file_path.text(),
                ui.radio_split_by_column.isChecked(),
                ui.spin_box_split_rows.value(),
                ui.combobox_split_column.currentText(),
            )
        )
        ui.button_split_cancel.clicked.connect(vm.cancel_split)
        ui.button_split_show_folder.clicked.connect(
            lambda: open_path(ui.line_edit_split_result_path.text())
        )
        vm.split_running_changed.connect(self._set_splitting)
        vm.split_finished.connect(self._split_done)
        _refill(ui.combobox_split_column, [])
        self._split_mode_changed(ui.radio_split_by_rows.isChecked())
        self._set_splitting(False)

    def _show_split_columns(self, headers: list[str]) -> None:
        _refill(self.ui.combobox_split_column, headers)
        self._split_mode_changed(self.ui.radio_split_by_rows.isChecked())

    def _split_mode_changed(self, by_rows: bool) -> None:
        ui = self.ui
        ui.spin_box_split_rows.setEnabled(by_rows)
        ui.button_split_excel_rows.setEnabled(by_rows)
        ui.combobox_split_column.setEnabled(not by_rows and ui.combobox_split_column.count() > 0)

    def _set_splitting(self, running: bool) -> None:
        ui = self.ui
        ui.busy_bar_split.set_running(running)
        ui.button_split_start.setDisabled(running)
        ui.button_split_cancel.setVisible(running)
        ui.button_split_browse_csv_file_path.setDisabled(running)
        if running:
            ui.frame_split_result.hide()

    def _split_done(self, result: SplitResult) -> None:
        ui = self.ui
        ui.label_split_result.setText(f"{len(result.files):,} files in")
        _show_path(ui.line_edit_split_result_path, str(result.folder))
        ui.frame_split_result.show()

    # ------------------------------------------------------------------ compare

    def _bind_compare(self) -> None:
        ui, vm = self.ui, self.vm
        ui.button_compare_old_browse_csv_file_path.clicked.connect(
            lambda: self._browse(ui.line_edit_compare_old_csv_file_path, "Select the old CSV file")
        )
        ui.button_compare_new_browse_csv_file_path.clicked.connect(
            lambda: self._browse(ui.line_edit_compare_new_csv_file_path, "Select the new CSV file")
        )
        ui.line_edit_compare_old_csv_file_path.textChanged.connect(vm.compare_headers.set_path)
        vm.compare_headers.headers_changed.connect(self._show_compare_keys)
        ui.button_compare_start.clicked.connect(
            lambda: vm.compare(
                ui.line_edit_compare_old_csv_file_path.text(),
                ui.line_edit_compare_new_csv_file_path.text(),
                self._compare_key(),
                ui.checkbox_compare_loose.isChecked(),
            )
        )
        ui.button_compare_cancel.clicked.connect(vm.cancel_compare)
        ui.button_compare_open_report.clicked.connect(
            lambda: open_path(ui.line_edit_compare_result_path.text())
        )
        vm.compare_running_changed.connect(self._set_comparing)
        vm.compare_finished.connect(self._compare_done)
        _refill(ui.combobox_compare_key, [])
        self._set_comparing(False)

    def _show_compare_keys(self, headers: list[str]) -> None:
        combo = self.ui.combobox_compare_key
        _refill(combo, headers)
        if headers:
            combo.addItem(NO_KEY_TEXT, _NO_KEY)

    def _compare_key(self) -> str:
        combo = self.ui.combobox_compare_key
        return "" if combo.currentData() == _NO_KEY else combo.currentText()

    def _set_comparing(self, running: bool) -> None:
        ui = self.ui
        ui.busy_bar_compare.set_running(running)
        ui.button_compare_start.setDisabled(running)
        ui.button_compare_cancel.setVisible(running)
        if running:
            ui.frame_compare_result.hide()
            self._show_diff_card(False)

    def _compare_done(self, result: CompareResult) -> None:
        ui = self.ui
        ui.label_compare_summary.setText("\n".join(summary_lines(result)))
        has_report = result.report is not None
        _show_path(ui.line_edit_compare_result_path, str(result.report) if has_report else "")
        for widget in (
            ui.label_compare_result,
            ui.line_edit_compare_result_path,
            ui.button_compare_open_report,
        ):
            widget.setVisible(has_report)
        ui.frame_compare_result.show()
        ui.diff_view_csv_compare.set_diff(
            result.text_diff, result.old.name, result.new.name, result.text_diff_note, unit="row"
        )
        self._show_diff_card(True)
        # Bring the side-by-side view into sight once the layout has its new height.
        QTimer.singleShot(
            0, lambda: ui.scroll_tab_tool_compare.ensureWidgetVisible(ui.card_compare_diff)
        )

    def _show_diff_card(self, visible: bool) -> None:
        """While shown, the side-by-side card takes the free height of the tab."""
        ui = self.ui
        if not visible:
            ui.diff_view_csv_compare.clear()  # release the text of large files
        ui.card_compare_diff.setVisible(visible)
        ui.spacer_14.changeSize(
            0 if visible else 20,
            0 if visible else 40,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed if visible else QSizePolicy.Policy.Expanding,
        )
        ui.layout_scroll_tab_tool_compare_contents.invalidate()

    # ------------------------------------------------------------------ columns

    def _bind_columns(self) -> None:
        ui, vm = self.ui, self.vm
        columns = ui.list_widget_columns
        ui.button_columns_browse_csv_file_path.clicked.connect(
            lambda: self._browse(ui.line_edit_columns_csv_file_path, "Select CSV file to edit")
        )
        ui.line_edit_columns_csv_file_path.textChanged.connect(vm.column_headers.set_path)
        ui.line_edit_columns_csv_file_path.textChanged.connect(ui.frame_columns_result.hide)
        vm.column_headers.headers_changed.connect(self._show_columns)
        ui.button_columns_up.clicked.connect(lambda: self._move_column(-1))
        ui.button_columns_down.clicked.connect(lambda: self._move_column(1))
        ui.button_columns_all.clicked.connect(lambda: self._check_all(True))
        ui.button_columns_none.clicked.connect(lambda: self._check_all(False))
        ui.button_columns_reset.clicked.connect(
            lambda: self._show_columns(vm.column_headers.headers)
        )
        ui.button_columns_save.clicked.connect(self._save_columns)
        ui.button_columns_open_result.clicked.connect(
            lambda: open_path(ui.line_edit_columns_result_path.text())
        )
        ui.button_columns_show_folder.clicked.connect(
            lambda: open_path(os.path.dirname(ui.line_edit_columns_result_path.text()))
        )
        columns.itemChanged.connect(lambda _item: self._update_columns_status())
        columns.model().rowsMoved.connect(lambda *_args: self._update_columns_status())
        for key, step in ((Qt.Key.Key_Up, -1), (Qt.Key.Key_Down, 1)):
            shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL | key), columns)
            shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
            shortcut.activated.connect(lambda s=step: self._move_column(s))
        vm.columns_running_changed.connect(self._set_saving_columns)
        vm.columns_saved.connect(self._columns_saved)
        self._show_columns([])

    def _show_columns(self, headers: list[str]) -> None:
        columns = self.ui.list_widget_columns
        columns.blockSignals(True)
        columns.clear()
        for index, name in enumerate(headers):
            item = QListWidgetItem(name)
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEditable
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsDragEnabled
            )
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(_SOURCE_INDEX, index)
            item.setData(_ORIGINAL_NAME, name)
            columns.addItem(item)
        columns.blockSignals(False)
        has_columns = bool(headers)
        for widget in (
            columns,
            self.ui.button_columns_up,
            self.ui.button_columns_down,
            self.ui.button_columns_all,
            self.ui.button_columns_none,
            self.ui.button_columns_reset,
            self.ui.checkbox_columns_overwrite,
        ):
            widget.setEnabled(has_columns)
        self._update_columns_status()

    def _items(self) -> list[QListWidgetItem]:
        columns = self.ui.list_widget_columns
        return [columns.item(row) for row in range(columns.count())]

    def _edits(self) -> list[tuple[int, str]]:
        return [
            (int(item.data(_SOURCE_INDEX)), item.text())
            for item in self._items()
            if item.checkState() == Qt.CheckState.Checked
        ]

    def _update_columns_status(self) -> None:
        items = self._items()
        if not items:
            self.ui.label_columns_status.setText("")
            self.ui.button_columns_save.setEnabled(False)
            return
        kept = [item for item in items if item.checkState() == Qt.CheckState.Checked]
        renamed = sum(1 for item in kept if item.text() != item.data(_ORIGINAL_NAME))
        moved = [int(item.data(_SOURCE_INDEX)) for item in items] != list(range(len(items)))
        parts = [f"Keeping {len(kept)} of {len(items)} columns"]
        if renamed:
            parts.append(f"{renamed} renamed")
        if moved:
            parts.append("order changed")
        self.ui.label_columns_status.setText(", ".join(parts) + ".")
        self.ui.button_columns_save.setEnabled(bool(kept))

    def _move_column(self, step: int) -> None:
        columns = self.ui.list_widget_columns
        row = columns.currentRow()
        target = row + step
        if row < 0 or not 0 <= target < columns.count():
            return
        item = columns.takeItem(row)
        columns.insertItem(target, item)
        columns.setCurrentRow(target)
        self._update_columns_status()

    def _check_all(self, checked: bool) -> None:
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        columns = self.ui.list_widget_columns
        columns.blockSignals(True)
        for item in self._items():
            item.setCheckState(state)
        columns.blockSignals(False)
        self._update_columns_status()

    def _save_columns(self) -> None:
        self.vm.save_columns(
            self.ui.line_edit_columns_csv_file_path.text(),
            self._edits(),
            self.ui.checkbox_columns_overwrite.isChecked(),
        )

    def _set_saving_columns(self, running: bool) -> None:
        ui = self.ui
        ui.busy_bar_columns.set_running(running)
        ui.button_columns_save.setDisabled(running)
        ui.list_widget_columns.setDisabled(running)
        if running:
            ui.frame_columns_result.hide()
        else:
            ui.list_widget_columns.setEnabled(ui.list_widget_columns.count() > 0)
            self._update_columns_status()

    def _columns_saved(self, result: ColumnEditResult) -> None:
        _show_path(self.ui.line_edit_columns_result_path, str(result.output))
        self.ui.frame_columns_result.show()
