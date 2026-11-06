from __future__ import annotations

from PySide6.QtWidgets import QDialog, QWidget

from ..generated.exit_dialog_ui import Ui_ExitAppDialog


class ExitDialog(QDialog):
    """ "Do you really want to quit?" with a "don't ask again" option."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ui = Ui_ExitAppDialog()
        self.ui.setupUi(self)

    @property
    def dont_ask_again(self) -> bool:
        return self.ui.check_box_dont_ask_again.isChecked()
