"""Indeterminate progress indicator: a thin bar with diagonal stripes that move while busy.

Used where the duration of the work is unknown (CSV conversion, column removal, profile
clean-up). It always keeps its place in the layout and paints nothing while idle, so
starting or finishing work never shifts the buttons next to it.

Colors come from the active style sheet::

    BusyBar {
        qproperty-trackColor: #2c3038;
        qproperty-stripeColor: #5b7cfa;
    }
"""

from __future__ import annotations

from PySide6.QtCore import Property, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QPolygonF
from PySide6.QtWidgets import QSizePolicy, QWidget

FRAME_MS = 16  # ~60 fps while running
STRIPE_PERIOD = 16  # px between stripe starts
STRIPE_SPEED = 0.6  # px per frame


class BusyBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._running = False
        self._offset = 0.0
        self._track = QColor("#2c3038")
        self._stripe = QColor("#5b7cfa")
        self._timer = QTimer(self)
        self._timer.setInterval(FRAME_MS)
        self._timer.timeout.connect(self._advance)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(6)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    # -- state -------------------------------------------------------------------------

    @property
    def running(self) -> bool:
        return self._running

    def set_running(self, running: bool) -> None:
        if running == self._running:
            return
        self._running = running
        self.setToolTip("Working…" if running else "")
        self._sync_timer()
        self.update()

    def start(self) -> None:
        self.set_running(True)

    def stop(self) -> None:
        self.set_running(False)

    def _sync_timer(self) -> None:
        # Animate only while running and on screen; a hidden page costs nothing.
        if self._running and self.isVisible():
            self._timer.start()
        else:
            self._timer.stop()

    def showEvent(self, event) -> None:  # noqa: ANN001
        super().showEvent(event)
        self._sync_timer()

    def hideEvent(self, event) -> None:  # noqa: ANN001
        super().hideEvent(event)
        self._sync_timer()

    def _advance(self) -> None:
        self._offset = (self._offset + STRIPE_SPEED) % STRIPE_PERIOD
        self.update()

    # -- style-sheet properties ----------------------------------------------------------

    def _get_track(self) -> QColor:
        return self._track

    def _set_track(self, color: QColor) -> None:
        self._track = QColor(color)
        self.update()

    def _get_stripe(self) -> QColor:
        return self._stripe

    def _set_stripe(self, color: QColor) -> None:
        self._stripe = QColor(color)
        self.update()

    trackColor = Property(QColor, _get_track, _set_track)
    stripeColor = Property(QColor, _get_stripe, _set_stripe)

    # -- painting --------------------------------------------------------------------------

    def paintEvent(self, _event: QPaintEvent) -> None:
        if not self._running:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        radius = rect.height() / 2
        clip = QPainterPath()
        clip.addRoundedRect(rect, radius, radius)
        painter.setClipPath(clip)
        painter.fillRect(rect, self._track)

        height = rect.height()
        half = STRIPE_PERIOD / 2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._stripe)
        x = -STRIPE_PERIOD - height + self._offset
        while x < rect.width():
            painter.drawPolygon(
                QPolygonF(
                    [
                        QPointF(x, height),
                        QPointF(x + height, 0),
                        QPointF(x + height + half, 0),
                        QPointF(x + half, height),
                    ]
                )
            )
            x += STRIPE_PERIOD
        painter.end()
