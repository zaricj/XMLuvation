"""Binds the Table viewer page to its ViewModel.

The page reads tabular files only: CSV, Excel, HTML, JSON and Markdown tables. Besides
the widgets of the ``.ui`` (quick filter, Open, Close, the table), this view adds the
controls of the viewer's tools in code: quick filter options, recent files, column
filters, the Columns menu, "go to row", export and "send to" the CSV tools.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QPoint, Qt, Signal
from PySide6.QtGui import QAction, QGuiApplication, QIntValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...application.csv_tools import TABLE_SUFFIXES
from ..models.table_ops import ColumnFilter, ColumnStats, FilterOp
from ..viewmodels.table_viewer_vm import TableViewerViewModel
from .common import browse_open_file

if TYPE_CHECKING:
    from ..widgets.data_table import DataTableView
    from .main_window import MainWindow

TABLE_FILTER = (
    "Tables (*.csv *.xlsx *.xlsm *.html *.htm *.json *.md *.markdown);;"
    "CSV File (*.csv);;Excel Workbook (*.xlsx *.xlsm);;HTML (*.html *.htm);;"
    "JSON (*.json);;Markdown (*.md *.markdown);;All files (*)"
)
EXPORT_FILTERS = {"CSV File (*.csv)": ".csv", "Excel Workbook (*.xlsx)": ".xlsx"}

# Targets of "Send to": (menu text, line edit of the CSV tools page, tab of that tool).
SEND_TARGETS = (
    ("Split", "line_edit_split_csv_file_path", "tab_tool_split"),
    ("Compare as the old file", "line_edit_compare_old_csv_file_path", "tab_tool_compare"),
    ("Compare as the new file", "line_edit_compare_new_csv_file_path", "tab_tool_compare"),
    ("Columns", "line_edit_columns_csv_file_path", "tab_tool_columns"),
)


class _ColumnFilterRow(QWidget):
    """One column filter: column, condition, value, match case, remove."""

    changed = Signal()
    removed = Signal(QWidget)

    def __init__(self, headers: list[str], column: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.column = QComboBox()
        self.column.addItems(headers)
        self.column.setCurrentIndex(column)
        self.column.setMinimumWidth(160)
        self.op = QComboBox()
        self.op.addItems([op.value for op in FilterOp])
        self.value = QLineEdit()
        self.value.setPlaceholderText("Value")
        self.value.setClearButtonEnabled(True)
        self.case = QCheckBox("Match case")
        remove = QPushButton("Remove")
        remove.setProperty("role", "flat")
        remove.setToolTip("Remove this column filter.")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(QLabel("Column"))
        layout.addWidget(self.column)
        layout.addWidget(self.op)
        layout.addWidget(self.value, 1)
        layout.addWidget(self.case)
        layout.addWidget(remove)

        self.column.currentIndexChanged.connect(self.changed)
        self.op.currentIndexChanged.connect(self._op_changed)
        self.value.textChanged.connect(self.changed)
        self.case.toggled.connect(self.changed)
        remove.clicked.connect(lambda: self.removed.emit(self))
        self._op_changed()

    def _op_changed(self) -> None:
        needs_value = FilterOp(self.op.currentText()).needs_value
        self.value.setEnabled(needs_value)
        self.case.setEnabled(needs_value)
        self.changed.emit()

    def condition(self) -> ColumnFilter:
        return ColumnFilter(
            self.column.currentIndex(),
            FilterOp(self.op.currentText()),
            self.value.text(),
            self.case.isChecked(),
        )


class _StatsDialog(QDialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle("Column statistics")
        self.setMinimumWidth(420)
        self._form = QFormLayout()
        self._labels: dict[str, QLabel] = {}
        for key in ("Rows", "Empty", "Distinct values", "Duplicated values", "Minimum", "Maximum"):
            label = QLabel()
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self._labels[key] = label
            self._form.addRow(key, label)
        self._top = QTableWidget(0, 2)
        self._top.setHorizontalHeaderLabels(["Most frequent values", "Rows"])
        self._top.verticalHeader().hide()
        self._top.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._top.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)
        self._title = QLabel()
        self._title.setProperty("role", "card-title")
        self._note = QLabel()
        self._note.setProperty("role", "hint")
        self._note.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._note)
        layout.addLayout(self._form)
        layout.addWidget(self._top, 1)
        layout.addWidget(buttons)

    def show_stats(self, stats: ColumnStats, filtered: bool) -> None:
        self._title.setText(stats.name)
        self._note.setText(
            "Of the rows that match the filter." if filtered else "Of all rows of the file."
        )
        kind = "numbers" if stats.numeric else "text"
        self._labels["Rows"].setText(f"{stats.rows:,}")
        self._labels["Empty"].setText(f"{stats.empty:,}")
        self._labels["Distinct values"].setText(f"{stats.distinct:,}")
        self._labels["Duplicated values"].setText(
            f"{stats.duplicate_values:,} values occur more than once "
            f"({stats.duplicate_rows:,} rows)"
        )
        self._labels["Minimum"].setText(f"{stats.minimum}  ({kind})" if stats.minimum else "–")
        self._labels["Maximum"].setText(f"{stats.maximum}  ({kind})" if stats.maximum else "–")
        self._top.setRowCount(len(stats.top))
        for row, (value, count) in enumerate(stats.top):
            self._top.setItem(row, 0, QTableWidgetItem(value))
            count_item = QTableWidgetItem(f"{count:,}")
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._top.setItem(row, 1, count_item)
        self.show()
        self.raise_()


class TableViewerView(QObject):
    def __init__(
        self,
        window: MainWindow,
        vm: TableViewerViewModel,
        show_csv_tool: Callable[[QWidget], None],
    ) -> None:
        super().__init__(window)
        self.window = window
        self.ui = window.ui
        self.vm = vm
        self._show_csv_tool = show_csv_tool
        self.table: DataTableView = self.ui.table_csv_data
        self._filter_rows: list[_ColumnFilterRow] = []
        self._stats_dialog: _StatsDialog | None = None
        self._build_controls()
        self._setup_table()
        self._bind()
        self._table_state(False)

    # ------------------------------------------------------------------ widgets

    def _build_controls(self) -> None:
        ui = self.ui
        toolbar = ui.layout_table_toolbar
        self.check_regex = QCheckBox("Regex")
        self.check_regex.setToolTip("Treat the quick filter as a regular expression.")
        self.check_case = QCheckBox("Match case")
        self.check_case.setToolTip("Make the quick filter case-sensitive.")
        toolbar.insertWidget(1, self.check_regex)
        toolbar.insertWidget(2, self.check_case)
        self.button_recent = QPushButton("Recent")
        self.button_recent.setToolTip("Open a recently viewed file.")
        self.menu_recent = QMenu(self.button_recent)
        self.button_recent.setMenu(self.menu_recent)
        toolbar.insertWidget(toolbar.indexOf(ui.button_load_csv) + 1, self.button_recent)
        ui.button_load_csv.setText("Open…")
        ui.button_load_csv.setToolTip(
            "Open a CSV, Excel, HTML, JSON or Markdown table. "
            "You can also drop a file on the table."
        )

        self.button_add_filter = QPushButton("Add column filter")
        self.button_add_filter.setToolTip(
            "Filter by one column: contains, equals, regex, is empty, is duplicated, ... "
            "All filters must match."
        )
        self.button_columns = QPushButton("Columns")
        self.button_columns.setToolTip("Show, hide, reorder, size and freeze columns.")
        self.menu_columns = QMenu(self.button_columns)
        self.button_columns.setMenu(self.menu_columns)
        self.edit_go_to = QLineEdit()
        self.edit_go_to.setPlaceholderText("Go to row…")
        self.edit_go_to.setToolTip(
            "Row number in the file (1 = first data row, as in the row header); press Enter."
        )
        self.edit_go_to.setValidator(QIntValidator(1, 2_000_000_000, self.edit_go_to))
        self.edit_go_to.setFixedWidth(130)
        self.label_message = QLabel()
        self.label_message.setProperty("role", "hint")
        self.label_message.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.button_export = QPushButton("Export view…")
        self.button_export.setToolTip(
            "Save the rows and columns shown (filtered, sorted, hidden columns left out) "
            "as CSV or Excel."
        )
        self.button_send = QPushButton("Send to")
        self.button_send.setToolTip("Use this CSV file in Split, Compare or Columns.")
        self.menu_send = QMenu(self.button_send)
        for text, edit_name, tab_name in SEND_TARGETS:
            action = self.menu_send.addAction(text)
            action.triggered.connect(
                lambda _checked=False, e=edit_name, t=tab_name: self._send_to(e, t)
            )
        self.button_send.setMenu(self.menu_send)

        tools = QHBoxLayout()
        tools.setSpacing(10)
        tools.addWidget(self.button_add_filter)
        tools.addWidget(self.button_columns)
        tools.addWidget(self.edit_go_to)
        tools.addWidget(self.label_message, 1)
        tools.addWidget(self.button_export)
        tools.addWidget(self.button_send)

        self.frame_filters = QFrame()
        self.frame_filters.setProperty("role", "transparent")
        self.layout_filters = QVBoxLayout(self.frame_filters)
        self.layout_filters.setContentsMargins(0, 0, 0, 0)
        self.layout_filters.setSpacing(6)
        self.frame_filters.hide()

        page = ui.layout_page_table
        table_index = page.indexOf(self.table)
        page.insertLayout(table_index, tools)
        page.insertWidget(table_index + 1, self.frame_filters)
        for index in range(page.count()):
            item = page.itemAt(index)
            page.setStretch(index, 1 if item is not None and item.widget() is self.table else 0)

    def _setup_table(self) -> None:
        table = self.table
        table.setModel(self.vm.model)
        table.verticalHeader().setDefaultSectionSize(28)
        table.verticalHeader().setToolTip("Row number in the file (1 = first data row)")
        table.horizontalHeader().setHighlightSections(False)
        table.horizontalHeader().setSectionsMovable(True)
        table.horizontalHeader().setToolTip(
            "Click to sort, drag to reorder, right-click for column tools."
        )
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    # ------------------------------------------------------------------ bindings

    def _bind(self) -> None:
        ui, vm, table = self.ui, self.vm, self.table
        ui.button_load_csv.clicked.connect(self._open)
        ui.button_clear_table.clicked.connect(vm.clear)
        ui.line_edit_filter_table.textChanged.connect(vm.set_filter)
        for box in (self.check_regex, self.check_case):
            box.toggled.connect(
                lambda _on: vm.set_filter_options(
                    self.check_regex.isChecked(), self.check_case.isChecked()
                )
            )
        self.button_add_filter.clicked.connect(lambda: self._add_filter())
        self.menu_columns.aboutToShow.connect(self._fill_columns_menu)
        self.menu_recent.aboutToShow.connect(self._fill_recent_menu)
        self.edit_go_to.returnPressed.connect(self._go_to_row)
        self.button_export.clicked.connect(self._export)
        table.copy_requested.connect(lambda: self._copy(False))
        table.files_dropped.connect(self._files_dropped)
        table.header_menu_requested.connect(self._header_menu)
        table.customContextMenuRequested.connect(self._cell_menu)

        vm.has_table_changed.connect(self._table_state)
        vm.loading_changed.connect(ui.button_load_csv.setDisabled)
        vm.loading_changed.connect(
            lambda busy: ui.label_table_rows.setText("Loading…") if busy else self._update_rows()
        )
        vm.filtering_changed.connect(lambda _busy: self._update_rows())
        vm.filter_error.connect(self._show_filter_error)
        vm.stats_ready.connect(self._show_stats)
        vm.export_running_changed.connect(self.button_export.setDisabled)
        vm.exported.connect(lambda path: self._message(f"Exported to {path}"))
        for signal in (vm.model.modelReset, vm.model.layoutChanged):
            signal.connect(self._update_rows)
        self._update_rows()

    # ------------------------------------------------------------------ file

    def _open(self) -> None:
        start = str(Path(self.vm.path).parent) if self.vm.path else ""
        path = browse_open_file(self.window, "Select a table file", TABLE_FILTER, start)
        if path:
            self.load(path)

    def load(self, path: str) -> None:
        self._message("")
        self.vm.load(path)

    def _files_dropped(self, paths: list[str]) -> None:
        tables = [p for p in paths if Path(p).suffix.lower() in TABLE_SUFFIXES]
        if not tables:
            self._message(f"Only {', '.join(TABLE_SUFFIXES)} files can be opened here.")
            return
        self.load(tables[0])
        if len(tables) > 1:
            self._message(f"Opened {Path(tables[0]).name}; one file at a time.")

    def _fill_recent_menu(self) -> None:
        menu = self.menu_recent
        menu.clear()
        recent = self.vm.recent
        if not recent:
            menu.addAction("No recent files").setEnabled(False)
            return
        for path in recent:
            action = menu.addAction(Path(path).name)
            action.setToolTip(path)
            action.setStatusTip(path)
            action.setEnabled(Path(path).is_file())
            action.triggered.connect(lambda _checked=False, p=path: self.load(p))
        menu.setToolTipsVisible(True)
        menu.addSeparator()
        menu.addAction("Clear recent files").triggered.connect(self.vm.clear_recent)

    def _send_to(self, edit_name: str, tab_name: str) -> None:
        getattr(self.ui, edit_name).setText(self.vm.path)
        self._show_csv_tool(getattr(self.ui, tab_name))

    def _table_state(self, has_table: bool) -> None:
        ui = self.ui
        for widget in (
            ui.button_clear_table,
            ui.line_edit_filter_table,
            self.check_regex,
            self.check_case,
            self.button_add_filter,
            self.button_columns,
            self.edit_go_to,
            self.button_export,
        ):
            widget.setEnabled(has_table)
        self.button_send.setEnabled(has_table and self.vm.is_csv)
        self.button_send.setToolTip(
            "Use this CSV file in Split, Compare or Columns."
            if self.vm.is_csv or not has_table
            else "Only CSV files can be used in the CSV tools. Convert this file first."
        )
        # A new table starts without the filters, column changes and highlights of the last.
        for box in (self.check_regex, self.check_case):
            box.blockSignals(True)
            box.setChecked(False)
            box.blockSignals(False)
        ui.line_edit_filter_table.blockSignals(True)
        ui.line_edit_filter_table.clear()
        ui.line_edit_filter_table.blockSignals(False)
        for row in list(self._filter_rows):
            self._remove_filter(row, notify=False)
        self._reset_columns()
        self._show_filter_error("")
        if has_table:
            self.table.resizeColumnsToContents()  # only fetched rows are measured
            self.window.setWindowFilePath(self.vm.path)
        self._update_rows()

    def _update_rows(self) -> None:
        model = self.vm.model
        total = model.data_store.row_count
        name = Path(self.vm.path).name if self.vm.path else ""
        prefix = f"{name}: " if name else ""
        if total == 0 and model.columnCount() == 0:
            text = ""
        elif model.total_rows == total:
            text = f"{prefix}{total:,} rows"
        else:
            text = f"{prefix}{model.total_rows:,} of {total:,} rows"
        self.ui.label_table_rows.setText(text)
        self.ui.label_table_rows.setToolTip(self.vm.path)

    def _message(self, text: str, error: bool = False) -> None:
        self.label_message.setText(text)
        self.label_message.setToolTip(text)
        self.label_message.setProperty("role", "error" if error else "hint")
        self.label_message.style().unpolish(self.label_message)
        self.label_message.style().polish(self.label_message)

    def _show_filter_error(self, error: str) -> None:
        if error:
            self._message(error, error=True)
        elif self.label_message.property("role") == "error":
            self._message("")

    # ------------------------------------------------------------------ column filters

    def _add_filter(self, column: int = 0) -> None:
        headers = list(self.vm.model.data_store.headers)
        if not headers:
            return
        row = _ColumnFilterRow(headers, column)
        row.changed.connect(self._filters_changed)
        row.removed.connect(lambda widget: self._remove_filter(widget))
        self._filter_rows.append(row)
        self.layout_filters.addWidget(row)
        self.frame_filters.show()
        row.value.setFocus()
        self._filters_changed()

    def _remove_filter(self, row: QWidget, notify: bool = True) -> None:
        if row in self._filter_rows:
            self._filter_rows.remove(row)
        row.setParent(None)
        row.deleteLater()
        self.frame_filters.setVisible(bool(self._filter_rows))
        if notify:
            self._filters_changed()

    def _filters_changed(self) -> None:
        self.vm.set_column_filters([row.condition() for row in self._filter_rows])

    # ------------------------------------------------------------------ columns

    def _visible_columns(self) -> list[int]:
        """Logical indices of the shown columns, in their on-screen order."""
        header = self.table.horizontalHeader()
        return [
            header.logicalIndex(visual)
            for visual in range(header.count())
            if not header.isSectionHidden(header.logicalIndex(visual))
        ]

    def _reset_columns(self) -> None:
        header = self.table.horizontalHeader()
        for logical in range(header.count()):
            header.moveSection(header.visualIndex(logical), logical)
            self.table.setColumnHidden(logical, False)
        self.table.set_frozen_columns(0)
        self.vm.set_duplicate_column(None)

    def _set_hidden(self, column: int, hidden: bool) -> None:
        if hidden and len(self._visible_columns()) <= 1:
            self._message("At least one column stays visible.")
            return
        self.table.setColumnHidden(column, hidden)

    def _fill_columns_menu(self) -> None:
        menu = self.menu_columns
        menu.clear()
        headers = self.vm.model.data_store.headers
        freeze = menu.addAction("Freeze first column")
        freeze.setCheckable(True)
        freeze.setChecked(self.table.frozen_columns > 0)
        freeze.toggled.connect(lambda on: self.table.set_frozen_columns(1 if on else 0))
        menu.addAction("Resize columns to contents").triggered.connect(
            self.table.resizeColumnsToContents
        )
        menu.addAction("Show all columns in their original order").triggered.connect(
            self._restore_columns
        )
        menu.addSeparator()
        shown = menu.addMenu("Show or hide columns")
        header = self.table.horizontalHeader()
        for visual in range(header.count()):
            logical = header.logicalIndex(visual)
            action = QAction(headers[logical], shown)
            action.setCheckable(True)
            action.setChecked(not header.isSectionHidden(logical))
            action.toggled.connect(lambda on, c=logical: self._set_hidden(c, not on))
            shown.addAction(action)

    def _restore_columns(self) -> None:
        frozen = self.table.frozen_columns
        duplicate = self.vm.model.duplicate_column
        self._reset_columns()
        self.table.set_frozen_columns(frozen)
        self.vm.set_duplicate_column(duplicate)

    def _header_menu(self, column: int, position: QPoint) -> None:
        if column < 0:
            return
        name = self.vm.model.data_store.headers[column]
        menu = QMenu(self.table)
        menu.addAction("Sort ascending").triggered.connect(
            lambda: self.table.sortByColumn(column, Qt.SortOrder.AscendingOrder)
        )
        menu.addAction("Sort descending").triggered.connect(
            lambda: self.table.sortByColumn(column, Qt.SortOrder.DescendingOrder)
        )
        menu.addSeparator()
        menu.addAction(f"Filter by “{name}”…").triggered.connect(lambda: self._add_filter(column))
        duplicates = menu.addAction("Highlight duplicate values")
        duplicates.setCheckable(True)
        duplicates.setChecked(self.vm.model.duplicate_column == column)
        duplicates.toggled.connect(lambda on: self._highlight_duplicates(column, on))
        menu.addAction("Column statistics…").triggered.connect(
            lambda: self.vm.request_stats(column)
        )
        menu.addSeparator()
        menu.addAction(f"Hide “{name}”").triggered.connect(lambda: self._set_hidden(column, True))
        menu.addAction("Resize to contents").triggered.connect(
            lambda: self.table.resizeColumnToContents(column)
        )
        visual = self.table.horizontalHeader().visualIndex(column)
        menu.addAction("Freeze columns up to here").triggered.connect(
            lambda: self.table.set_frozen_columns(visual + 1)
        )
        unfreeze = menu.addAction("Unfreeze columns")
        unfreeze.setEnabled(self.table.frozen_columns > 0)
        unfreeze.triggered.connect(lambda: self.table.set_frozen_columns(0))
        menu.exec(position)

    def _highlight_duplicates(self, column: int, on: bool) -> None:
        self.vm.set_duplicate_column(column if on else None)
        if on:
            name = self.vm.model.data_store.headers[column]
            count = self.vm.model.duplicate_rows
            self._message(
                f"{count:,} rows have a duplicated “{name}”."
                if count
                else f"Every “{name}” value is unique."
            )
        else:
            self._message("")

    def _show_stats(self, stats: ColumnStats) -> None:
        if self._stats_dialog is None:
            self._stats_dialog = _StatsDialog(self.window)
        self._stats_dialog.show_stats(stats, self.vm.model.filtered_rows is not None)

    # ------------------------------------------------------------------ rows, copy, export

    def _go_to_row(self) -> None:
        text = self.edit_go_to.text()
        if not text:
            return
        number = int(text)
        position = self.vm.position_of_row(number)
        if position is None:
            total = self.vm.model.data_store.row_count
            self._message(
                f"Row {number:,} is hidden by the filter."
                if 1 <= number <= total
                else f"There is no row {number:,}; the file has {total:,} rows."
            )
            return
        self._message("")
        columns = self._visible_columns()
        index = self.vm.model.index(position, columns[0] if columns else 0)
        self.table.scrollTo(index, self.table.ScrollHint.PositionAtCenter)
        self.table.selectRow(position)
        self.table.setFocus()

    def _selection(self) -> tuple[list[int], list[int]]:
        """Display positions and logical columns of the selection (visible columns only)."""
        rows: set[int] = set()
        columns: set[int] = set()
        selection = self.table.selectionModel().selection()
        for i in range(selection.count()):
            selected = selection.at(i)
            rows.update(range(selected.top(), selected.bottom() + 1))
            columns.update(range(selected.left(), selected.right() + 1))
        ordered = [c for c in self._visible_columns() if c in columns]
        return sorted(rows), ordered

    def _copy(self, headers: bool) -> None:
        rows, columns = self._selection()
        if not rows or not columns:
            return
        QGuiApplication.clipboard().setText(self.vm.copy_text(rows, columns, headers))
        self._message(f"Copied {len(rows):,} rows × {len(columns):,} columns.")

    def _cell_menu(self, position: QPoint) -> None:
        if not self.vm.model.columnCount():
            return
        menu = QMenu(self.table)
        has_selection = self.table.selectionModel().hasSelection()
        copy = menu.addAction("Copy")
        copy.setShortcut("Ctrl+C")
        copy.setEnabled(has_selection)
        copy.triggered.connect(lambda: self._copy(False))
        with_headers = menu.addAction("Copy with headers")
        with_headers.setEnabled(has_selection)
        with_headers.triggered.connect(lambda: self._copy(True))
        menu.addAction("Select all loaded rows").triggered.connect(self.table.selectAll)
        menu.addSeparator()
        menu.addAction("Export view…").triggered.connect(self._export)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _export(self) -> None:
        if not self.vm.path:
            return
        source = Path(self.vm.path)
        default = str(source.with_name(f"{source.stem}_view.csv"))
        path, chosen = QFileDialog.getSaveFileName(
            self.window, "Export the rows shown", default, ";;".join(EXPORT_FILTERS)
        )
        if not path:
            return
        suffix = EXPORT_FILTERS.get(chosen, ".csv")
        if Path(path).suffix.lower() not in EXPORT_FILTERS.values():
            path += suffix
        self._message("Exporting…")
        self.vm.export(path, self._visible_columns())
