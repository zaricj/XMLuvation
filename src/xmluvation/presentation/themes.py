"""Theme registry. Style sheets are compiled into the Qt resource file (``:/styles/...``)."""

from __future__ import annotations

from PySide6.QtCore import QFile, QIODevice, QTextStream

# key (persisted in settings) -> resource path; order = theme menu order
THEMES: dict[str, str] = {
    "dark_theme_default": ":/styles/dark_theme.qss",
    "light_theme_default": ":/styles/light_theme.qss",
    "dark_theme_yellow": ":/styles/other/dark_theme_yellow.qss",
    "dark_theme_peach": ":/styles/other/dark_theme_peach.qss",
    "dark_theme_qlementine": ":/styles/other/dark_theme_qlementine.qss",
    "dark_theme_metallic_spaceship": ":/styles/other/dark_theme_metallic_spaceship.qss",
}


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
