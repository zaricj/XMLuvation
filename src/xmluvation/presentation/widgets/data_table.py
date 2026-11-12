"""Table view of the table viewer page: frozen leading columns, copy, file drops.

Frozen columns follow Qt's "frozen column" example: a second ``QTableView`` on top of the
left edge shows only the first visual columns. It shares the model and the selection,
and its scrolling, row heights, column widths, order and visibility follow the main view.
The header row of a ``QTableView`` never scrolls, so it is always "frozen".

The widget only reports intent (``copy_requested``, ``files_dropped``,
``header_menu_requested``); building the copied text and loading files is done by the
page's view, which knows the data.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QAbstractItemModel, QPoint, Qt, Signal
from PySide6.QtGui import (
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QKeyEvent,
    QKeySequence,
    QResizeEvent,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QScrollBar,
    QTableView,
    QWidget,
)


class DataTableView(QTableView):
    copy_requested = Signal()
    files_dropped = Signal(list)  # local file paths
    header_menu_requested = Signal(int, QPoint)  # logical column, global position

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._frozen_count = 0
        self._syncing = False
        self._frozen = QTableView(self)
        self._frozen.setObjectName("table_frozen_columns")
        self._frozen.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # No frame or theme border: the viewport must be exactly as high as the main one,
        # or the scroll ranges differ and the last rows end up a few pixels apart.
        self._frozen.setFrameShape(QFrame.Shape.NoFrame)
        self._frozen.setStyleSheet(
            "QTableView#table_frozen_columns"
            " { border: none; border-radius: 0; margin: 0; padding: 0; }"
        )
        self._frozen.verticalHeader().hide()
        self._frozen.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._frozen.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._frozen.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self._frozen.horizontalHeader().setHighlightSections(False)
        self._frozen.setVerticalScrollMode(self.verticalScrollMode())
        self._frozen.hide()
        self.viewport().stackUnder(self._frozen)

        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        for header in (self.horizontalHeader(), self._frozen.horizontalHeader()):
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header.customContextMenuRequested.connect(
                lambda pos, h=header: self.header_menu_requested.emit(
                    h.logicalIndexAt(pos), h.mapToGlobal(pos)
                )
            )
        self._frozen.horizontalHeader().sectionClicked.connect(self._frozen_header_clicked)
        self.horizontalHeader().sectionResized.connect(self._section_resized)
        self.horizontalHeader().sectionMoved.connect(lambda *_: self._sync_columns())
        self.horizontalHeader().sortIndicatorChanged.connect(
            lambda column, order: self._frozen.horizontalHeader().setSortIndicator(column, order)
        )
        self.verticalHeader().sectionResized.connect(
            lambda row, _old, size: self._frozen.setRowHeight(row, size)
        )
        self._frozen.verticalScrollBar().valueChanged.connect(
            self._follow(self.verticalScrollBar())
        )
        self.verticalScrollBar().valueChanged.connect(
            self._follow(self._frozen.verticalScrollBar())
        )

    # -- model ---------------------------------------------------------------------------

    def setModel(self, model: QAbstractItemModel | None) -> None:  # noqa: N802 (Qt API)
        super().setModel(model)
        self._frozen.setModel(model)
        self._frozen.setSelectionModel(self.selectionModel())
        if model is not None:
            model.modelReset.connect(self._sync_columns)
            model.columnsInserted.connect(lambda *_: self._sync_columns())
        self._sync_columns()

    def setAlternatingRowColors(self, enable: bool) -> None:  # noqa: N802 (Qt API)
        super().setAlternatingRowColors(enable)
        self._frozen.setAlternatingRowColors(enable)

    def setVerticalScrollMode(  # noqa: N802 (Qt API)
        self, mode: QAbstractItemView.ScrollMode
    ) -> None:
        super().setVerticalScrollMode(mode)
        self._frozen.setVerticalScrollMode(mode)  # same scroll units as the main view

    def setColumnHidden(self, column: int, hide: bool) -> None:  # noqa: N802 (Qt API)
        super().setColumnHidden(column, hide)
        self._sync_columns()

    # -- frozen columns ------------------------------------------------------------------

    @property
    def frozen_columns(self) -> int:
        return self._frozen_count

    def set_frozen_columns(self, count: int) -> None:
        """Keep the first ``count`` visual columns in place while scrolling sideways."""
        self._frozen_count = max(0, count)
        self._sync_columns()

    def frozen_view(self) -> QTableView:
        return self._frozen

    def _sync_columns(self) -> None:
        model = self.model()
        columns = model.columnCount() if model is not None else 0
        main, frozen = self.horizontalHeader(), self._frozen.horizontalHeader()
        self._frozen.verticalHeader().setDefaultSectionSize(
            self.verticalHeader().defaultSectionSize()
        )
        # Same visual order as the main view, then hide everything not frozen.
        for visual in range(columns):
            logical = main.logicalIndex(visual)
            current = frozen.visualIndex(logical)
            if current != visual:
                frozen.moveSection(current, visual)
        for visual in range(columns):
            logical = main.logicalIndex(visual)
            hidden = visual >= self._frozen_count or self.isColumnHidden(logical)
            self._frozen.setColumnHidden(logical, hidden)
            self._frozen.setColumnWidth(logical, self.columnWidth(logical))
        self._frozen.setVisible(self._frozen_count > 0 and columns > 0)
        frozen.setSortIndicatorShown(main.isSortIndicatorShown())
        frozen.setSortIndicator(main.sortIndicatorSection(), main.sortIndicatorOrder())
        self._update_frozen_geometry()

    def _section_resized(self, logical: int, _old: int, size: int) -> None:
        self._frozen.setColumnWidth(logical, size)
        self._update_frozen_geometry()

    def _frozen_width(self) -> int:
        main = self.horizontalHeader()
        width = 0
        for visual in range(min(self._frozen_count, main.count())):
            logical = main.logicalIndex(visual)
            if not self.isColumnHidden(logical):
                width += self.columnWidth(logical)
        return width

    def _update_frozen_geometry(self) -> None:
        if self._frozen.isHidden():
            return
        frame = self.frameWidth()
        self._frozen.setGeometry(
            self.verticalHeader().width() + frame,
            frame,
            min(self._frozen_width(), self.viewport().width()),
            self.viewport().height() + self.horizontalHeader().height(),
        )

    def _frozen_header_clicked(self, logical: int) -> None:
        """Sort by a frozen column like a click on the main header would."""
        if not self.isSortingEnabled():
            return
        main = self.horizontalHeader()
        order = Qt.SortOrder.AscendingOrder
        if main.sortIndicatorSection() == logical:
            ascending = main.sortIndicatorOrder() == Qt.SortOrder.AscendingOrder
            order = Qt.SortOrder.DescendingOrder if ascending else Qt.SortOrder.AscendingOrder
        self.sortByColumn(logical, order)
        self._frozen.horizontalHeader().setSortIndicator(logical, order)

    def _follow(self, target: QScrollBar) -> Callable[[int], None]:
        def move(value: int) -> None:
            if not self._syncing:
                self._syncing = True
                target.setValue(value)
                self._syncing = False

        return move

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802 (Qt API)
        super().resizeEvent(event)
        self._update_frozen_geometry()

    def updateGeometries(self) -> None:  # noqa: N802 (Qt API)
        super().updateGeometries()
        self._update_frozen_geometry()

    # -- keyboard and drops --------------------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802 (Qt API)
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    @staticmethod
    def _local_files(event: QDropEvent | QDragEnterEvent | QDragMoveEvent) -> list[str]:
        mime = event.mimeData()
        if not mime.hasUrls():
            return []
        return [url.toLocalFile() for url in mime.urls() if url.isLocalFile()]

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802 (Qt API)
        if self._local_files(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:  # noqa: N802 (Qt API)
        if self._local_files(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802 (Qt API)
        files = self._local_files(event)
        if files:
            event.acceptProposedAction()
            self.files_dropped.emit(files)
        else:
            event.ignore()
