"""Outline "</>" (markup) icon for the XML tools page, drawn in code.

Like :mod:`.table_icon`: no Windows theme icon looks like markup, so this engine draws
one in the palette's ``Text`` color to match the other sidebar icons.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRect, QSize, Qt
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


class CodeIconEngine(QIconEngine):
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
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolyline([point(5, 4.5), point(1.5, 8), point(5, 11.5)])  # <
        painter.drawPolyline([point(11, 4.5), point(14.5, 8), point(11, 11.5)])  # >
        painter.drawLine(point(9.25, 3), point(6.75, 13))  # /
        painter.restore()

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        self.paint(painter, QRect(0, 0, size.width(), size.height()), mode, state)
        painter.end()
        return pixmap

    def clone(self) -> QIconEngine:
        return CodeIconEngine()


def code_icon() -> QIcon:
    return QIcon(CodeIconEngine())
