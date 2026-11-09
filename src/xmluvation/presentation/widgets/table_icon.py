"""Outline "table" icon, drawn in code.

Qt's Windows icon engine has no glyph for any table-like theme icon (``FormatJustifyFill``
and the freedesktop table/spreadsheet names all resolve to null icons). This engine draws
a matching outline table in the application palette's ``Text`` color, which is the color
the Windows engine uses for the other sidebar icons, so all of them look alike.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRect, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QGuiApplication,
    QIcon,
    QIconEngine,
    QPainter,
    QPalette,
    QPen,
    QPixmap,
)

_GRID = 16.0  # drawing is designed on a 16 x 16 grid and scaled to the requested size


class TableIconEngine(QIconEngine):
    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State) -> None:
        group = (
            QPalette.ColorGroup.Disabled
            if mode == QIcon.Mode.Disabled
            else QPalette.ColorGroup.Active
        )
        color: QColor = QGuiApplication.palette().color(group, QPalette.ColorRole.Text)
        side = min(rect.width(), rect.height())
        scale = side / _GRID
        origin = QPointF(
            rect.x() + (rect.width() - side) / 2, rect.y() + (rect.height() - side) / 2
        )

        def point(x: float, y: float) -> QPointF:
            return QPointF(origin.x() + x * scale, origin.y() + y * scale)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(color, max(1.0, scale))
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        frame = QRectF(point(1.5, 2.5), point(14.5, 13.5))
        painter.drawRoundedRect(frame, 2 * scale, 2 * scale)
        painter.drawLine(point(1.5, 6), point(14.5, 6))  # header row
        painter.drawLine(point(1.5, 9.75), point(14.5, 9.75))
        painter.drawLine(point(6, 6), point(6, 13.5))  # first column
        painter.restore()

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        self.paint(painter, QRect(0, 0, size.width(), size.height()), mode, state)
        painter.end()
        return pixmap

    def clone(self) -> QIconEngine:
        return TableIconEngine()


def table_icon() -> QIcon:
    return QIcon(TableIconEngine())
