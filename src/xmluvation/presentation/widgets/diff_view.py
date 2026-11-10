"""Side-by-side text diff, as in an IDE: old file left, new file right, scrolled together.

Removed and changed lines are red on the left, added and changed lines green on the right,
and the characters that differ inside a changed line are marked more strongly. Where one
side has no line, a hatched filler row keeps both sides aligned. A strip on the right
shows where the changes are in the whole file (click it to jump there); F7 / Shift+F7
go to the next / previous change.

Backgrounds are painted per visible row in ``paintEvent`` (no extra selections or block
formats), so files with hundreds of thousands of lines stay responsive.

Colors come from the active style sheet::

    DiffView {
        qproperty-removedLineColor: rgba(248, 81, 73, 40);
        qproperty-removedTextColor: rgba(248, 81, 73, 110);
        qproperty-addedLineColor: rgba(46, 160, 67, 40);
        qproperty-addedTextColor: rgba(46, 160, 67, 110);
        qproperty-fillerColor: rgba(140, 146, 160, 60);
        qproperty-lineNumberColor: #7d8494;
    }
"""

from __future__ import annotations

import bisect
from collections.abc import Callable

from PySide6.QtCore import Property, QEvent, QRect, QRectF, QSize, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QKeySequence,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QResizeEvent,
    QShortcut,
    QTextLine,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...domain.text_diff import RowKind, TextDiff

# Row styles of one pane.
_PLAIN, _REMOVED, _ADDED, _FILLER = 0, 1, 2, 3
# Overview run kinds: _REMOVED (left half), _ADDED (right half), changed (both halves).
_RUN_CHANGED = 4
CONTEXT_ROWS = 3  # rows shown above a change when jumping to it

Span = tuple[int, int]


def _cursor_x(line: QTextLine, position: int) -> float:
    value = line.cursorToX(position)
    return float(value[0] if isinstance(value, tuple) else value)


class _Colors:
    def __init__(self) -> None:
        self.removed_line = QColor(248, 81, 73, 40)
        self.removed_text = QColor(248, 81, 73, 110)
        self.added_line = QColor(46, 160, 67, 40)
        self.added_text = QColor(46, 160, 67, 110)
        self.filler = QColor(140, 146, 160, 60)
        self.line_number = QColor("#7d8494")

    def line(self, style: int) -> QColor | None:
        return {_REMOVED: self.removed_line, _ADDED: self.added_line}.get(style)

    def text(self, style: int) -> QColor:
        return self.removed_text if style == _REMOVED else self.added_text


class _Gutter(QWidget):
    def __init__(self, pane: _Pane) -> None:
        super().__init__(pane)
        self._pane = pane

    def sizeHint(self) -> QSize:
        return QSize(self._pane.gutter_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        self._pane.paint_gutter(self, event)


class _Pane(QPlainTextEdit):
    """Read-only text with a gutter of original line numbers and diff backgrounds."""

    def __init__(self, colors: _Colors, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._colors = colors
        self._numbers: list[int] = []
        self._styles = bytearray()
        self._spans: dict[int, tuple[Span, ...]] = {}
        self.setProperty("role", "code")
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self._gutter = _Gutter(self)
        self.updateRequest.connect(self._update_gutter)
        self._update_margins()

    # -- content -------------------------------------------------------------------------

    def set_rows(
        self,
        text: str,
        numbers: list[int],
        styles: bytearray,
        spans: dict[int, tuple[Span, ...]],
    ) -> None:
        self._numbers, self._styles, self._spans = numbers, styles, spans
        self.setPlainText(text)
        self._update_margins()

    def style_at(self, row: int) -> int:
        return self._styles[row] if 0 <= row < len(self._styles) else _PLAIN

    # -- geometry ------------------------------------------------------------------------

    def gutter_width(self) -> int:
        digits = max(3, len(str(max(self._numbers, default=0))))
        return 16 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_margins(self) -> None:
        self.setViewportMargins(self.gutter_width(), 0, 0, 0)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self._place_gutter()

    def _place_gutter(self) -> None:
        viewport = self.viewport().geometry()
        width = self.gutter_width()
        self._gutter.setGeometry(
            QRect(viewport.left() - width, viewport.top(), width, viewport.height())
        )

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._place_gutter()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.FontChange:  # the style sheet sets the code font
            self._update_margins()

    def _update_gutter(self, rect: QRect, dy: int) -> None:
        if dy:
            self._gutter.scroll(0, dy)
        else:
            self._gutter.update(0, rect.y(), self._gutter.width(), rect.height())

    # -- painting ------------------------------------------------------------------------

    def _visible_rows(self, bottom: int) -> list[tuple[int, QRectF, object]]:
        rows = []
        offset = self.contentOffset()
        block = self.firstVisibleBlock()
        while block.isValid():
            geometry = self.blockBoundingGeometry(block).translated(offset)
            if geometry.top() > bottom:
                break
            if block.isVisible():
                rows.append((block.blockNumber(), geometry, block))
            block = block.next()
        return rows

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self.viewport())
        width = self.viewport().width()
        colors = self._colors
        filler = QBrush(colors.filler, Qt.BrushStyle.BDiagPattern)
        for row, geometry, block in self._visible_rows(event.rect().bottom()):
            style = self.style_at(row)
            band = QRectF(0, geometry.top(), width, geometry.height())
            if style == _FILLER:
                painter.fillRect(band, filler)
                continue
            line_color = colors.line(style)
            if line_color is None:
                continue
            painter.fillRect(band, line_color)
            spans = self._spans.get(row)
            layout = block.layout()  # type: ignore[attr-defined]
            if not spans or layout.lineCount() == 0:
                continue
            line = layout.lineAt(0)
            left = geometry.left() + layout.position().x()
            for start, end in spans:
                x1, x2 = _cursor_x(line, start), _cursor_x(line, end)
                painter.fillRect(
                    QRectF(left + x1, geometry.top(), max(x2 - x1, 2.0), geometry.height()),
                    colors.text(style),
                )
        painter.end()
        super().paintEvent(event)

    def paint_gutter(self, gutter: QWidget, event: QPaintEvent) -> None:
        painter = QPainter(gutter)
        painter.setFont(self.font())
        painter.setPen(self._colors.line_number)
        right = gutter.width() - 8
        shift = self.viewport().y() - gutter.y()  # viewport rows -> gutter rows
        for row, geometry, _block in self._visible_rows(event.rect().bottom() - shift):
            top = round(geometry.top()) + shift
            height = round(geometry.height())
            line_color = self._colors.line(self.style_at(row))
            if line_color is not None:
                painter.fillRect(QRect(0, top, gutter.width(), height), line_color)
            number = self._numbers[row] if row < len(self._numbers) else 0
            if number:
                painter.drawText(
                    QRect(0, top, right, height),
                    int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter),
                    str(number),
                )
        painter.end()


class _Overview(QWidget):
    """Where the changes are in the whole file; a click scrolls there."""

    def __init__(self, colors: _Colors, jump: Callable[[int], None]) -> None:
        super().__init__()
        self._colors = colors
        self._jump = jump
        self._rows = 0
        self._runs: list[tuple[int, int, int]] = []  # first row, end row, left/right style
        self._visible = (0, 0)
        self.setFixedWidth(12)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Overview of all changes; click to go there.")

    def set_runs(self, rows: int, runs: list[tuple[int, int, int]]) -> None:
        self._rows, self._runs = rows, runs
        self.update()

    def set_visible_rows(self, first: int, count: int) -> None:
        self._visible = (first, count)
        self.update()

    def _y(self, row: int) -> float:
        return row * self.height() / self._rows if self._rows else 0.0

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self._rows:
            return
        painter = QPainter(self)
        half = self.width() / 2
        for start, end, kind in self._runs:
            top = self._y(start)
            height = max(self._y(end) - top, 2.0)
            if kind in (_REMOVED, _RUN_CHANGED):
                painter.fillRect(QRectF(0, top, half, height), self._colors.removed_text)
            if kind in (_ADDED, _RUN_CHANGED):
                painter.fillRect(QRectF(half, top, half, height), self._colors.added_text)
        first, count = self._visible
        if count < self._rows:
            shade = QColor(self._colors.line_number)
            shade.setAlpha(45)
            top = self._y(first)
            painter.fillRect(QRectF(0, top, self.width(), self._y(first + count) - top), shade)
        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._rows and self.height():
            self._jump(int(event.position().y() * self._rows / self.height()))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.mousePressEvent(event)


def _side(pane: _Pane, beside: QWidget | None = None) -> tuple[QWidget, QLabel]:
    """A file name label above ``pane`` (and ``beside``, at the pane's height)."""
    box = QWidget()
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    label = QLabel()
    label.setProperty("role", "field-label")
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    layout.addWidget(label)
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(4)
    row.addWidget(pane, 1)
    if beside is not None:
        row.addWidget(beside)
    layout.addLayout(row, 1)
    return box, label


class DiffView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._colors = _Colors()
        self._hunks: list[int] = []
        self._current: int | None = None
        self._current_top = -1
        self._syncing = False

        self._left = _Pane(self._colors)
        self._right = _Pane(self._colors)
        self._overview = _Overview(self._colors, self._jump_to_row)

        self._summary = QLabel()
        self._summary.setProperty("role", "hint")
        self._position = QLabel()
        self._position.setProperty("role", "hint")
        self._previous = QPushButton("Previous change")
        self._previous.setToolTip("Go to the previous change (Shift+F7).")
        self._next = QPushButton("Next change")
        self._next.setToolTip("Go to the next change (F7).")
        self._previous.clicked.connect(self.previous_change)
        self._next.clicked.connect(self.next_change)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(10)
        toolbar.addWidget(self._summary, 1)
        toolbar.addWidget(self._position)
        toolbar.addWidget(self._previous)
        toolbar.addWidget(self._next)

        left_box, self._left_name = _side(self._left)
        right_box, self._right_name = _side(self._right, self._overview)
        panes = QHBoxLayout()
        panes.setContentsMargins(0, 0, 0, 0)
        panes.setSpacing(8)
        panes.addWidget(left_box, 1)
        panes.addWidget(right_box, 1)
        self._panes = QFrame()
        self._panes.setLayout(panes)
        self._panes.setProperty("role", "transparent")

        self._note = QLabel()
        self._note.setWordWrap(True)
        self._note.setProperty("role", "hint")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addLayout(toolbar)
        layout.addWidget(self._note)
        layout.addWidget(self._panes, 1)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._sync(self._left.verticalScrollBar(), self._right.verticalScrollBar())
        self._sync(self._left.horizontalScrollBar(), self._right.horizontalScrollBar())
        self._right.verticalScrollBar().valueChanged.connect(self._scrolled)
        self._right.verticalScrollBar().rangeChanged.connect(lambda *_: self._scrolled())
        for key, slot in (("F7", self.next_change), ("Shift+F7", self.previous_change)):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            shortcut.activated.connect(slot)
        self.clear()

    # -- colors (set from the style sheet) -----------------------------------------------

    def _color_property(attribute: str) -> Property:
        def getter(self: DiffView) -> QColor:
            return QColor(getattr(self._colors, attribute))

        def setter(self: DiffView, color: QColor) -> None:
            setattr(self._colors, attribute, QColor(color))
            for widget in (self._left.viewport(), self._right.viewport(), self._overview):
                widget.update()
            self._left._gutter.update()
            self._right._gutter.update()

        return Property(QColor, getter, setter)

    removedLineColor = _color_property("removed_line")
    removedTextColor = _color_property("removed_text")
    addedLineColor = _color_property("added_line")
    addedTextColor = _color_property("added_text")
    fillerColor = _color_property("filler")
    lineNumberColor = _color_property("line_number")
    del _color_property

    # -- content -------------------------------------------------------------------------

    def clear(self, note: str = "") -> None:
        self.set_diff(None, note=note)

    def set_diff(
        self, diff: TextDiff | None, old_name: str = "", new_name: str = "", note: str = ""
    ) -> None:
        self._note.setText(note)
        self._note.setVisible(bool(note))
        self._panes.setVisible(diff is not None)
        self._current, self._current_top = None, -1
        if diff is None:
            self._hunks = []
            self._summary.setText("")
            for pane in (self._left, self._right):
                pane.set_rows("", [], bytearray(), {})
            self._overview.set_runs(0, [])
            self._update_navigation()
            return
        self._left_name.setText(f"Old: {old_name}")
        self._right_name.setText(f"New: {new_name}")
        self._fill(diff)
        self._hunks = diff.hunks
        self._summary.setText(_summary(diff))
        self._left.verticalScrollBar().setValue(0)
        self._update_navigation()
        if self._hunks:
            self.next_change()

    def _fill(self, diff: TextDiff) -> None:
        old_text: list[str] = []
        new_text: list[str] = []
        old_numbers: list[int] = []
        new_numbers: list[int] = []
        old_styles = bytearray(len(diff.rows))
        new_styles = bytearray(len(diff.rows))
        old_spans: dict[int, tuple[Span, ...]] = {}
        new_spans: dict[int, tuple[Span, ...]] = {}
        runs: list[tuple[int, int, int]] = []
        for index, row in enumerate(diff.rows):
            old_numbers.append(row.old_number)
            new_numbers.append(row.new_number)
            old_text.append(diff.old_lines[row.old_number - 1] if row.old_number else "")
            new_text.append(diff.new_lines[row.new_number - 1] if row.new_number else "")
            if row.kind is RowKind.EQUAL:
                continue
            old_styles[index] = _REMOVED if row.old_number else _FILLER
            new_styles[index] = _ADDED if row.new_number else _FILLER
            if row.old_spans:
                old_spans[index] = row.old_spans
            if row.new_spans:
                new_spans[index] = row.new_spans
            kind = {
                RowKind.REMOVED: _REMOVED,
                RowKind.ADDED: _ADDED,
            }.get(row.kind, _RUN_CHANGED)
            if runs and runs[-1][1] == index and runs[-1][2] == kind:
                runs[-1] = (runs[-1][0], index + 1, kind)
            else:
                runs.append((index, index + 1, kind))
        self._left.set_rows("\n".join(old_text), old_numbers, old_styles, old_spans)
        self._right.set_rows("\n".join(new_text), new_numbers, new_styles, new_spans)
        self._overview.set_runs(len(diff.rows), runs)

    # -- scrolling and navigation --------------------------------------------------------

    def _sync(self, first: QScrollBar, second: QScrollBar) -> None:
        def follow(target: QScrollBar) -> Callable[[int], None]:
            def move(value: int) -> None:
                if not self._syncing:
                    self._syncing = True
                    target.setValue(value)
                    self._syncing = False

            return move

        first.valueChanged.connect(follow(second))
        second.valueChanged.connect(follow(first))

    def _top_row(self) -> int:
        return self._right.verticalScrollBar().value()

    def _scrolled(self) -> None:
        bar = self._right.verticalScrollBar()
        self._overview.set_visible_rows(bar.value(), bar.pageStep())
        self._update_navigation()

    def _jump_to_row(self, row: int) -> None:
        self._right.verticalScrollBar().setValue(max(0, row - CONTEXT_ROWS))

    def _go_to(self, index: int) -> None:
        self._jump_to_row(self._hunks[index])
        self._current, self._current_top = index, self._top_row()
        self._update_navigation()

    def _anchor(self) -> int | None:
        """The change last jumped to, if the view has not been scrolled since."""
        return self._current if self._top_row() == self._current_top else None

    def _next_index(self) -> int | None:
        anchor = self._anchor()
        if anchor is not None:
            index = anchor + 1
        else:
            # A change is "below" when jumping to it would scroll down (at the very top,
            # changes in the first rows count as well).
            top = self._top_row()
            index = bisect.bisect_right(self._hunks, top + CONTEXT_ROWS if top else -1)
        return index if index < len(self._hunks) else None

    def _previous_index(self) -> int | None:
        anchor = self._anchor()
        if anchor is not None:
            index = anchor - 1
        else:
            index = bisect.bisect_left(self._hunks, self._top_row() + CONTEXT_ROWS) - 1
        return index if index >= 0 else None

    def next_change(self) -> None:
        index = self._next_index()
        if index is not None:
            self._go_to(index)

    def previous_change(self) -> None:
        index = self._previous_index()
        if index is not None:
            self._go_to(index)

    def _update_navigation(self) -> None:
        total = len(self._hunks)
        anchor = self._anchor()
        if not total:
            self._position.setText("")
        elif anchor is not None:
            self._position.setText(f"Change {anchor + 1} of {total:,}")
        else:
            self._position.setText(f"{total:,} change{'s' if total != 1 else ''}")
        self._next.setEnabled(self._next_index() is not None)
        self._previous.setEnabled(self._previous_index() is not None)

    # -- for tests -----------------------------------------------------------------------

    def pane_texts(self) -> tuple[str, str]:
        return self._left.toPlainText(), self._right.toPlainText()

    def position_text(self) -> str:
        return self._position.text()


def _summary(diff: TextDiff) -> str:
    if diff.identical:
        return "The files are identical line by line."
    parts = []
    for kind, label in (
        (RowKind.CHANGED, "changed"),
        (RowKind.REMOVED, "removed"),
        (RowKind.ADDED, "added"),
    ):
        count = diff.count(kind)
        if count:
            parts.append(f"{count:,} {label}")
    return f"Lines: {', '.join(parts)}."
