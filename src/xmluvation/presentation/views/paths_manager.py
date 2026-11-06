"""Window for creating, editing and deleting custom folder paths."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QComboBox, QMessageBox, QWidget

from ..generated.custom_paths_manager_ui import Ui_CustomPathsManagerWidget
from ..viewmodels.presets_vm import PresetsViewModel
from .common import ask_yes_no, browse_folder_into, connect_notifications, open_path


def refill_combobox(combo: QComboBox, items: list[str]) -> None:
    """Replace the items, keeping the current selection if it still exists."""
    current = combo.currentText()
    combo.blockSignals(True)
    combo.clear()
    combo.addItems(items)
    if current in items:
        combo.setCurrentText(current)
    combo.blockSignals(False)


class CustomPathsManager(QWidget):
    def __init__(self, vm: PresetsViewModel, config_dir: Path) -> None:
        super().__init__()
        self.vm = vm
        self.ui = Ui_CustomPathsManagerWidget()
        self.ui.setupUi(self)
        connect_notifications(self, vm)
        vm.changed.connect(self._refresh)

        ui = self.ui
        ui.button_create_custom_path.clicked.connect(self._create)
        ui.button_save_changes.clicked.connect(self._save_changes)
        ui.button_load_action.clicked.connect(self._load)
        ui.button_delete_action.clicked.connect(self._delete)
        ui.button_browse_path_folder.clicked.connect(
            lambda: browse_folder_into(
                self, "Select a folder for the custom path value", ui.line_edit_custom_path_value
            )
        )
        ui.button_open_config_directory.clicked.connect(lambda: open_path(config_dir))
        self._refresh()

    def _refresh(self) -> None:
        refill_combobox(self.ui.combobox_path_names, list(self.vm.custom_paths()))

    def _create(self) -> None:
        name = self.ui.line_edit_custom_path_name.text().strip()
        value = self.ui.line_edit_custom_path_value.text().strip()
        if self.vm.save_custom_path(name, value):
            QMessageBox.information(
                self,
                "Success",
                f"Successfully created a new custom path:\nKey:{name}\nValue:{value}",
            )

    def _save_changes(self) -> None:
        name = self.ui.line_edit_path_name.text().strip()
        value = self.ui.line_edit_path_value.text().strip()
        if self.vm.save_custom_path(name, value):
            QMessageBox.information(
                self, "Action saved", f"Custom path '{name}' has been saved successfully."
            )
            self._clear_inputs()

    def _load(self) -> None:
        name = self.ui.combobox_path_names.currentText()
        if not name:
            self._clear_inputs()
            return
        value = self.vm.custom_paths().get(name)
        if value is None:
            self._clear_inputs()
            QMessageBox.warning(
                self, "Path Not Found", f"The path '{name}' was not found in the configuration."
            )
            return
        self.ui.line_edit_path_name.setText(name)
        self.ui.line_edit_path_value.setText(value)

    def _delete(self) -> None:
        name = self.ui.combobox_path_names.currentText()
        if not name:
            QMessageBox.information(
                self,
                "No configuration to delete",
                "Please select a configuration that you want to delete first from the combobox.",
            )
            return
        question = f"Are you sure you want to delete the path '{name}'?"
        if ask_yes_no(self, "Confirm Delete", question) and self.vm.delete_custom_path(name):
            self._clear_inputs()

    def _clear_inputs(self) -> None:
        self.ui.line_edit_path_name.clear()
        self.ui.line_edit_path_value.clear()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.vm.dispose()
        super().closeEvent(event)
