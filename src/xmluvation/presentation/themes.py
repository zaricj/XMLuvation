"""Theme registry. Style sheets are compiled into the Qt resource file (``:/styles/...``)."""

from __future__ import annotations

from PySide6.QtCore import QFile, QIODevice, QTextStream
from PySide6.QtGui import QColor, QGuiApplication, QPalette

# key (persisted in settings) -> resource path; order = theme menu order
THEMES: dict[str, str] = {
    "dark_theme_default": ":/styles/dark_theme.qss",
    "light_theme_default": ":/styles/light_theme.qss",
    "dark_theme_yellow": ":/styles/other/dark_theme_yellow.qss",
    "dark_theme_peach": ":/styles/other/dark_theme_peach.qss",
    "dark_theme_qlementine": ":/styles/other/dark_theme_qlementine.qss",
    "dark_theme_metallic_spaceship": ":/styles/other/dark_theme_metallic_spaceship.qss",
}


LIGHT_THEMES = frozenset({"light_theme_default"})

# Left border + padding of a spin box in each theme, in px: the text inset that Qt 6.12
# leaves out (see widgets/spin_box_inset.py). Keep in sync with the QSpinBox rules of the
# style sheets; themes that do not style spin boxes need none.
SPIN_BOX_TEXT_INSET = {
    "dark_theme_default": 9,
    "light_theme_default": 9,
    "dark_theme_yellow": 4,
    "dark_theme_qlementine": 9,
    "dark_theme_metallic_spaceship": 7,
}


def spin_box_text_inset(key: str) -> int:
    return SPIN_BOX_TEXT_INSET.get(key, 0)


# Icon colors (normal, disabled) per theme brightness. Qt's Windows theme icons and the
# drawn table icon paint in the application palette's Text color, which style sheets do
# not change, so it is set here; otherwise icons follow the Windows light/dark setting.
_ICON_COLORS = {
    False: ("#e6e8ec", "#6b717c"),  # dark themes: light icons
    True: ("#1c2027", "#a0a6b1"),  # light themes: near-black icons
}


def apply_icon_palette(app: QGuiApplication, key: str) -> None:
    normal, disabled = _ICON_COLORS[key in LIGHT_THEMES]
    palette = app.palette()
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
        palette.setColor(group, QPalette.ColorRole.Text, QColor(normal))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(disabled))
    app.setPalette(palette)


def theme_label(key: str) -> str:
    return key.replace("_", " ").title()


def load_stylesheet(key: str) -> str:
    """Read a theme's style sheet. Raises ``KeyError``/``OSError`` if unavailable."""
    from .generated import xmluvation_resources_rc  # noqa: F401  (registers ":/" resources)

    file = QFile(THEMES[key])
    if not file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
        raise OSError(f"Cannot open theme resource {THEMES[key]}")
    try:
        return QTextStream(file).readAll()
    finally:
        file.close()
