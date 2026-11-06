"""Window for creating and editing XPath presets (the "Autofill" menu)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QListWidget, QMessageBox, QWidget

from ...domain.xpath_text import parse_headers
from ..generated.prebuilt_xpaths_manager_ui import Ui_PreBuiltXPathsManagerWidget
from ..viewmodels.presets_vm import PresetsViewModel
from .common import ask_yes_no, connect_notifications, open_path
from .paths_manager import refill_combobox


def list_items(widget: QListWidget) -> list[str]:
    return [widget.item(i).text() for i in range(widget.count())]


class PreBuiltXPathsManager(QWidget):
    def __init__(self, vm: PresetsViewModel, config_dir: Path) -> None:
        super().__init__()
        self.vm = vm
        self.ui = Ui_PreBuiltXPathsManagerWidget()
        self.ui.setupUi(self)
        self._active_list: QListWidget | None = None
        connect_notifications(self, vm)
        vm.changed.connect(self._refresh)

        ui = self.ui
        ui.button_add_xpath_to_list.clicked.connect(self._add_xpath)
        ui.button_add_csv_header_to_list.clicked.connect(self._add_headers)
        ui.button_save_config.clicked.connect(self._save_new)
        ui.button_save_changes.clicked.connect(self._save_changes)
        ui.button_load_config.clicked.connect(self._load)
        ui.button_delete_config.clicked.connect(self._delete)
        ui.button_remove_selected.clicked.connect(self._remove_selected)
        ui.button_remove_all.clicked.connect(self._remove_all)
        ui.button_open_config_directory.clicked.connect(lambda: open_path(config_dir))
        for widget in self._lists():
            widget.itemClicked.connect(lambda _item, w=widget: self._set_active(w))
        self._refresh()

    def _lists(self) -> list[QListWidget]:
        ui = self.ui
        return [
            ui.list_widget_xpath_expressions,
            ui.list_widget_csv_headers,
            ui.list_widget_edit_xpath_expressions,
            ui.list_widget_edit_csv_headers,
        ]

    def _set_active(self, widget: QListWidget) -> None:
        self._active_list = widget

    def _refresh(self) -> None:
        refill_combobox(self.ui.combobox_xpath_configs, [p.name for p in self.vm.presets()])

    def _add_item(self, text: str, widget: QListWidget) -> None:
        if not text:
            QMessageBox.information(
                self, "Empty String", "Please enter a string that you want to add to the list."
            )
            return
        if text in list_items(widget):
            QMessageBox.warning(
                self, "Duplicate string in list", f"Cannot add duplicate string '{text}' into list:"
            )
            return
        widget.addItem(text)

    def _add_xpath(self) -> None:
        self._add_item(
            self.ui.line_edit_xpath_expression.text(), self.ui.list_widget_xpath_expressions
        )
        self.ui.line_edit_xpath_expression.clear()

    def _add_headers(self) -> None:
        text = self.ui.line_edit_csv_header.text()
        for header in parse_headers(text) if "," in text else [text]:
            self._add_item(header, self.ui.list_widget_csv_headers)
        self.ui.line_edit_csv_header.clear()

    def _save_new(self) -> None:
        ui = self.ui
        name = ui.line_edit_config_name.text().strip()
        xpaths, headers = (
            list_items(ui.list_widget_xpath_expressions),
            list_items(ui.list_widget_csv_headers),
        )
        if self.vm.save_preset(name, xpaths, headers):
            QMessageBox.information(
                self,
                "Configuration saved",
                f"Your configuration '{name}' has been successfully saved!",
            )
            ui.list_widget_xpath_expressions.clear()
            ui.list_widget_csv_headers.clear()
            ui.line_edit_config_name.clear()

    def _save_changes(self) -> None:
        ui = self.ui
        name = ui.combobox_xpath_configs.currentText()
        xpaths = list_items(ui.list_widget_edit_xpath_expressions)
        headers = list_items(ui.list_widget_edit_csv_headers)
        if self.vm.save_preset(name, xpaths, headers):
            QMessageBox.information(
                self,
                "Configuration changes saved",
                f"Your changes to the configuration '{name}' has been successfully saved!",
            )
            ui.list_widget_edit_xpath_expressions.clear()
            ui.list_widget_edit_csv_headers.clear()

    def _load(self) -> None:
        name = self.ui.combobox_xpath_configs.currentText()
        if not name:
            return
        preset = self.vm.preset(name)
        if preset is None or not preset.xpaths:
            QMessageBox.warning(
                self,
                "Configuration not found",
                f"The configuration name '{name}' was not found in the configuration.",
            )
            return
        self.ui.list_widget_edit_xpath_expressions.clear()
        self.ui.list_widget_edit_csv_headers.clear()
        self.ui.list_widget_edit_xpath_expressions.addItems(list(preset.xpaths))
        self.ui.list_widget_edit_csv_headers.addItems(list(preset.headers))

    def _delete(self) -> None:
        name = self.ui.combobox_xpath_configs.currentText()
        if not name:
            QMessageBox.information(
                self, "No action to delete", "Please select an action from the combobox first."
            )
            return
        question = f"Are you sure you want to delete the config '{name}'?"
        if ask_yes_no(self, "Confirm Delete", question) and self.vm.delete_preset(name):
            self.ui.list_widget_edit_xpath_expressions.clear()
            self.ui.list_widget_edit_csv_headers.clear()

    def _remove_selected(self) -> None:
        widget = self._active_list
        if widget is not None and widget.currentRow() != -1:
            widget.takeItem(widget.currentRow())
            return
        QMessageBox.information(self, "No selection", "Please select an item to remove.")

    def _remove_all(self) -> None:
        widget = self._active_list
        if widget is None:
            QMessageBox.information(
                self,
                "No List Selected",
                "Please click on an item in the list you wish to clear before clicking "
                "'Remove All'.",
            )
        elif widget.count() == 0:
            QMessageBox.information(self, "List is empty", "The selected list is already empty.")
        elif ask_yes_no(
            self,
            "Confirm Remove All",
            f"Are you sure you want to remove all {widget.count()} items from this list?",
        ):
            widget.clear()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.vm.dispose()
        super().closeEvent(event)
