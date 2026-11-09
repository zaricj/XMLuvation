"""Icons that keep their normal look when their item is selected.

Qt's Windows theme icons paint the ``Selected`` mode in the palette's highlighted-text
color (black with the default palette). On the sidebar, whose selected item is styled by
the theme instead, that turns the selected page's icon black. Wrapping an icon in
:class:`SteadyIconEngine` paints ``Selected`` and ``Active`` like ``Normal``; ``Disabled``
keeps its dimmed look.
"""

from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QIcon, QIconEngine, QPainter, QPixmap


def _steady(mode: QIcon.Mode) -> QIcon.Mode:
    return QIcon.Mode.Disabled if mode == QIcon.Mode.Disabled else QIcon.Mode.Normal


class SteadyIconEngine(QIconEngine):
    def __init__(self, source: QIcon) -> None:
        super().__init__()
        self._source = QIcon(source)

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State) -> None:
        self._source.paint(painter, rect, Qt.AlignmentFlag.AlignCenter, _steady(mode), state)

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        return self._source.pixmap(size, _steady(mode), state)

    def actualSize(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QSize:
        return self._source.actualSize(size, _steady(mode), state)

    def isNull(self) -> bool:
        return self._source.isNull()

    def clone(self) -> QIconEngine:
        return SteadyIconEngine(self._source)


def steady_icon(icon: QIcon) -> QIcon:
    return QIcon(SteadyIconEngine(icon))
