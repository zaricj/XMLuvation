"""Binds the XML tools page (Validate against XSD, Compare) to its ViewModel."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLineEdit

from ...application.xml_tools import (
    SchemaValidationResult,
    XmlCompareResult,
    compare_summary,
    validation_summary,
)
from ..viewmodels.xml_tools_vm import XmlToolsViewModel
from .common import browse_folder_into, browse_open_file_into, open_path

if TYPE_CHECKING:
    from .main_window import MainWindow

XML_FILTER = "XML File (*.xml);;All files (*)"
XSD_FILTER = "XML Schema (*.xsd);;All files (*)"


def _show_path(edit: QLineEdit, path: str) -> None:
    edit.setText(path)
    edit.setCursorPosition(0)
    edit.setToolTip(path)


class XmlToolsView(QObject):
    def __init__(
        self,
        window: MainWindow,
        vm: XmlToolsViewModel,
        view_in_table: Callable[[str], None],
    ) -> None:
        super().__init__(window)
        self.window = window
        self.ui = window.ui
        self.vm = vm
        self._view_in_table = view_in_table
        self.ui.frame_validate_result.hide()
        self.ui.frame_xml_compare_result.hide()
        self._bind_validate()
        self._bind_compare()

    # ------------------------------------------------------------------ validate

    def _bind_validate(self) -> None:
        ui, vm, window = self.ui, self.vm, self.window
        ui.button_validate_browse_schema.clicked.connect(
            lambda: browse_open_file_into(
                window, "Select XSD schema", ui.line_edit_validate_schema_path, XSD_FILTER
            )
        )
        ui.button_validate_browse_file.clicked.connect(
            lambda: browse_open_file_into(
                window, "Select XML file to validate", ui.line_edit_validate_xml_path, XML_FILTER
            )
        )
        ui.button_validate_browse_folder.clicked.connect(
            lambda: browse_folder_into(
                window, "Select folder with XML files", ui.line_edit_validate_xml_path
            )
        )
        ui.button_validate_start.clicked.connect(
            lambda: vm.validate(
                ui.line_edit_validate_schema_path.text(), ui.line_edit_validate_xml_path.text()
            )
        )
        ui.button_validate_cancel.clicked.connect(vm.cancel_validation)
        ui.button_validate_view_report.clicked.connect(
            lambda: self._view_in_table(ui.line_edit_validate_result_path.text())
        )
        ui.button_validate_open_report.clicked.connect(
            lambda: open_path(ui.line_edit_validate_result_path.text())
        )
        vm.validation_running_changed.connect(self._set_validating)
        vm.validation_progress.connect(
            lambda done, total: ui.label_validate_progress.setText(
                f"{done:,} / {total:,}" if total > 1 else ""
            )
        )
        vm.validation_finished.connect(self._validated)
        self._set_validating(False)

    def _set_validating(self, running: bool) -> None:
        ui = self.ui
        ui.busy_bar_validate.set_running(running)
        ui.button_validate_start.setDisabled(running)
        ui.button_validate_cancel.setVisible(running)
        for widget in (
            ui.button_validate_browse_schema,
            ui.button_validate_browse_file,
            ui.button_validate_browse_folder,
        ):
            widget.setDisabled(running)
        ui.label_validate_progress.setText("")
        if running:
            ui.frame_validate_result.hide()

    def _validated(self, result: SchemaValidationResult) -> None:
        ui = self.ui
        ui.label_validate_summary.setText("\n".join(validation_summary(result)))
        has_report = result.report is not None
        _show_path(ui.line_edit_validate_result_path, str(result.report) if has_report else "")
        for widget in (
            ui.label_validate_result,
            ui.line_edit_validate_result_path,
            ui.button_validate_view_report,
            ui.button_validate_open_report,
        ):
            widget.setVisible(has_report)
        ui.frame_validate_result.show()

    # ------------------------------------------------------------------ compare

    def _bind_compare(self) -> None:
        ui, vm, window = self.ui, self.vm, self.window
        ui.button_xml_compare_old_browse.clicked.connect(
            lambda: browse_open_file_into(
                window, "Select the old XML file", ui.line_edit_xml_compare_old_path, XML_FILTER
            )
        )
        ui.button_xml_compare_new_browse.clicked.connect(
            lambda: browse_open_file_into(
                window, "Select the new XML file", ui.line_edit_xml_compare_new_path, XML_FILTER
            )
        )
        ui.button_xml_compare_start.clicked.connect(
            lambda: vm.compare(
                ui.line_edit_xml_compare_old_path.text(),
                ui.line_edit_xml_compare_new_path.text(),
                ui.checkbox_xml_compare_ignore_whitespace.isChecked(),
            )
        )
        ui.button_xml_compare_cancel.clicked.connect(vm.cancel_compare)
        ui.button_xml_compare_view_report.clicked.connect(
            lambda: self._view_in_table(ui.line_edit_xml_compare_result_path.text())
        )
        ui.button_xml_compare_open_report.clicked.connect(
            lambda: open_path(ui.line_edit_xml_compare_result_path.text())
        )
        vm.compare_running_changed.connect(self._set_comparing)
        vm.compare_finished.connect(self._compared)
        self._set_comparing(False)

    def _set_comparing(self, running: bool) -> None:
        ui = self.ui
        ui.busy_bar_xml_compare.set_running(running)
        ui.button_xml_compare_start.setDisabled(running)
        ui.button_xml_compare_cancel.setVisible(running)
        if running:
            ui.frame_xml_compare_result.hide()

    def _compared(self, result: XmlCompareResult) -> None:
        ui = self.ui
        ui.label_xml_compare_summary.setText("\n".join(compare_summary(result)))
        has_report = result.report is not None
        _show_path(ui.line_edit_xml_compare_result_path, str(result.report) if has_report else "")
        for widget in (
            ui.label_xml_compare_result,
            ui.line_edit_xml_compare_result_path,
            ui.button_xml_compare_view_report,
            ui.button_xml_compare_open_report,
        ):
            widget.setVisible(has_report)
        ui.frame_xml_compare_result.show()
