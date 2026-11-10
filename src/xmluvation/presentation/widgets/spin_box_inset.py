"""Keep the number of every spin box inside its styled border (Qt 6.12 work-around).

Qt 6.12 lays out the text field of a style-sheet-styled spin box at the box's left edge:
the left border and padding are ignored (top and bottom are applied), so the number is
drawn under the border, as if it were behind the widget. The editor ignores style
sheets of its own, so this application-wide event filter restores the theme's text
inset (``themes.SPIN_BOX_TEXT_INSET``) with text margins on the editor.

Only the part Qt left out is added: the margin is the inset minus where Qt placed the
editor. A Qt version that places the editor correctly therefore gets no extra margin.
The margin is recomputed whenever a spin box is polished (shown, or the style sheet
changed) and whenever Qt moves or resizes its editor.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractSpinBox, QApplication, QLineEdit

EDITOR_NAME = "qt_spinbox_lineedit"


class SpinBoxTextInset(QObject):
    """Use :meth:`for_app`: the style sheet is application-wide, so is this filter."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._inset = 0

    @classmethod
    def for_app(cls, app: QApplication) -> SpinBoxTextInset:
        """The application's one instance, installed as an event filter on first use."""
        existing = app.findChild(cls, "spin_box_text_inset")
        if isinstance(existing, cls):
            return existing
        instance = cls(app)
        instance.setObjectName("spin_box_text_inset")
        app.installEventFilter(instance)
        return instance

    @property
    def inset(self) -> int:
        return self._inset

    def set_inset(self, inset: int) -> None:
        """Use ``inset`` px (the theme's left border + padding) for all spin boxes."""
        self._inset = max(0, inset)
        for widget in QApplication.allWidgets():
            if isinstance(widget, QAbstractSpinBox):
                self.apply(widget)

    def apply(self, spin: QAbstractSpinBox) -> None:
        editor = spin.findChild(QLineEdit, EDITOR_NAME)
        if editor is None:
            return
        margin = max(0, self._inset - editor.x())
        if editor.textMargins().left() != margin:
            editor.setTextMargins(margin, 0, margin, 0)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802 (Qt API)
        kind = event.type()
        if kind == QEvent.Type.Polish and isinstance(watched, QAbstractSpinBox):
            self.apply(watched)
        elif (
            kind in (QEvent.Type.Move, QEvent.Type.Resize)
            and isinstance(watched, QLineEdit)
            and watched.objectName() == EDITOR_NAME
        ):
            spin = watched.parent()
            if isinstance(spin, QAbstractSpinBox):
                self.apply(spin)
        return False
