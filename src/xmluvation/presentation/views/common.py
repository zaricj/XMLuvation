"""Small view helpers: message boxes, file dialogs, opening files and folders."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QLineEdit, QMessageBox, QWidget

from ..viewmodels.base import Level, ViewModel


def show_message(parent: QWidget | None, level: str, title: str, message: str) -> None:
    match level:
        case Level.CRITICAL:
            QMessageBox.critical(parent, title, message)
        case Level.WARNING:
            QMessageBox.warning(parent, title, message)
        case _:
            QMessageBox.information(parent, title, message)


def connect_notifications(view: QWidget, *view_models: ViewModel) -> None:
    for vm in view_models:
        vm.notify.connect(lambda level, title, message: show_message(view, level, title, message))


def ask_yes_no(parent: QWidget | None, title: str, question: str) -> bool:
    reply = QMessageBox.question(
        parent,
        title,
        question,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes


def browse_folder_into(parent: QWidget, caption: str, target: QLineEdit) -> None:
    current = target.text().strip()
    folder = (
        QFileDialog.getExistingDirectory(parent, caption, current)
        if current
        else (QFileDialog.getExistingDirectory(parent, caption))
    )
    if folder:
        target.setText(folder)


def browse_open_file(parent: QWidget, caption: str, file_filter: str) -> str:
    file_name, _ = QFileDialog.getOpenFileName(parent, caption=caption, filter=file_filter)
    return file_name


def browse_open_file_into(
    parent: QWidget, caption: str, target: QLineEdit, file_filter: str
) -> None:
    file_name = browse_open_file(parent, caption, file_filter)
    if file_name:
        target.setText(file_name)


def browse_save_file_into(
    parent: QWidget, caption: str, target: QLineEdit, file_filter: str, placeholder: str = ""
) -> None:
    file_name, _ = QFileDialog.getSaveFileName(
        parent, caption=caption, dir=placeholder, filter=file_filter
    )
    if file_name:
        target.setText(file_name)


def open_path(path: str | Path) -> bool:
    """Open a file or folder with the system's default application."""
    text = str(path).strip()
    if not text or not Path(text).exists():
        return False
    return QDesktopServices.openUrl(QUrl.fromLocalFile(text))
