from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QIcon, QPixmap

from xmluvation.presentation.widgets.steady_icon import steady_icon


def _solid(color: str) -> QPixmap:
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor(color))
    return pixmap


def _color(icon: QIcon, mode: QIcon.Mode) -> str:
    return icon.pixmap(QSize(16, 16), mode).toImage().pixelColor(8, 8).name()


def test_steady_icon_keeps_normal_look_when_selected(qtbot) -> None:
    icon = QIcon()
    icon.addPixmap(_solid("#ffffff"), QIcon.Mode.Normal)
    icon.addPixmap(_solid("#000000"), QIcon.Mode.Selected)  # like Windows theme icons
    icon.addPixmap(_solid("#808080"), QIcon.Mode.Disabled)
    steady = steady_icon(icon)
    assert _color(icon, QIcon.Mode.Selected) == "#000000"
    assert _color(steady, QIcon.Mode.Selected) == "#ffffff"
    assert _color(steady, QIcon.Mode.Active) == "#ffffff"
    assert _color(steady, QIcon.Mode.Disabled) == "#808080"


def test_theme_sets_icon_color(qtbot, window) -> None:
    from PySide6.QtGui import QGuiApplication, QPalette

    def text() -> str:
        return QGuiApplication.palette().color(QPalette.ColorRole.Text).name()

    window.vms.settings.set_theme("light_theme_default")
    assert text() == "#1c2027"
    window.vms.settings.set_theme("dark_theme_peach")
    assert text() == "#e6e8ec"
