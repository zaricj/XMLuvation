"""Binds the XML tools page (Validate against XSD, Compare) to its ViewModel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QLineEdit, QSizePolicy

from ...application.xml_tools import (
    SchemaValidationResult,
    XmlCompareResult,
    compare_summary,
    format_issue,
    validation_summary,
)
from ..viewmodels.xml_tools_vm import XmlToolsViewModel
from .common import browse_folder_into, browse_open_file_into, open_path

if TYPE_CHECKING:
    from .main_window import MainWindow

XML_FILTER = "XML File (*.xml);;All files (*)"
XSD_FILTER = "XML Schema (*.xsd);;All files (*)"
# More problems than this are only in the report file (a folder can have 1,000 per file).
MAX_SHOWN_PROBLEMS = 5_000


def _show_path(edit: QLineEdit, path: str) -> None:
    edit.setText(path)
    edit.setCursorPosition(0)
    edit.setToolTip(path)


class XmlToolsView(QObject):
    def __init__(
        self,
        window: MainWindow,
        vm: XmlToolsViewModel,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.ui = window.ui
        self.vm = vm
        self.ui.frame_validate_result.hide()
        self.ui.frame_xml_compare_result.hide()
        self._show_diff_card(False)
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
        shown = [format_issue(issue) for issue in result.problems[:MAX_SHOWN_PROBLEMS]]
        hidden = len(result.problems) - len(shown)
        if hidden > 0:
            shown.append(f"... and {hidden:,} more problems, listed in the report file.")
        ui.text_edit_validate_problems.setPlainText("\n".join(shown))
        ui.text_edit_validate_problems.setVisible(bool(shown))
        has_report = result.report is not None
        _show_path(ui.line_edit_validate_result_path, str(result.report) if has_report else "")
        for widget in (
            ui.label_validate_result,
            ui.line_edit_validate_result_path,
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
            self._show_diff_card(False)

    def _compared(self, result: XmlCompareResult) -> None:
        ui = self.ui
        ui.label_xml_compare_summary.setText("\n".join(compare_summary(result)))
        has_report = result.report is not None
        _show_path(ui.line_edit_xml_compare_result_path, str(result.report) if has_report else "")
        for widget in (
            ui.label_xml_compare_result,
            ui.line_edit_xml_compare_result_path,
            ui.button_xml_compare_open_report,
        ):
            widget.setVisible(has_report)
        ui.frame_xml_compare_result.show()
        ui.diff_view_xml_compare.set_diff(
            result.text_diff, result.old.name, result.new.name, result.text_diff_note
        )
        self._show_diff_card(True)
        # Bring the side-by-side view into sight once the layout has its new height.
        QTimer.singleShot(
            0, lambda: ui.scroll_tab_xml_compare.ensureWidgetVisible(ui.card_xml_compare_diff)
        )

    def _show_diff_card(self, visible: bool) -> None:
        """While shown, the side-by-side card takes the free height of the tab."""
        ui = self.ui
        if not visible:
            ui.diff_view_xml_compare.clear()  # release the text of large files
        ui.card_xml_compare_diff.setVisible(visible)
        ui.spacer_xml_102.changeSize(
            0 if visible else 20,
            0 if visible else 40,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed if visible else QSizePolicy.Policy.Expanding,
        )
        ui.layout_scroll_tab_xml_compare_contents.invalidate()
