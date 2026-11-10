"""Main window: binds the Designer UI to the ViewModels. No business logic lives here."""

from __future__ import annotations

import datetime
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QPoint, Qt, QTimer, QUrl
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QDesktopServices,
    QGuiApplication,
    QKeySequence,
    QShortcut,
    QTextDocument,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QTextEdit,
    QWidget,
)

from ...application.profile_cleanup import CleanupPlan
from ...domain.models import BuildCriteria, Operator, XmlIndex
from ...domain.numbers import parse_hex
from ..generated.main_window_ui import Ui_MainWindow
from ..tasks import TaskRunner
from ..themes import THEMES, apply_icon_palette, load_stylesheet, theme_label
from ..viewmodels.csv_tools_vm import CsvToolsViewModel
from ..viewmodels.csv_transforms_vm import CsvTransformsViewModel
from ..viewmodels.export_vm import ExportViewModel
from ..viewmodels.presets_vm import PresetsViewModel
from ..viewmodels.settings_vm import MAX_PREVIEW_LIMIT_MB, SettingsViewModel
from ..viewmodels.table_viewer_vm import TableViewerViewModel
from ..viewmodels.xml_inspector_vm import XmlInspectorViewModel
from ..viewmodels.xml_tools_vm import XmlToolsViewModel
from ..viewmodels.xpath_workspace_vm import XPathWorkspaceViewModel
from ..widgets.code_icon import code_icon
from ..widgets.steady_icon import steady_icon
from ..widgets.table_icon import table_icon
from .common import (
    ask_yes_no,
    browse_folder_into,
    browse_open_file,
    browse_open_file_into,
    browse_save_file_into,
    connect_notifications,
    open_path,
)
from .csv_transforms_view import CsvTransformsView
from .exit_dialog import ExitDialog
from .paths_manager import CustomPathsManager
from .presets_manager import PreBuiltXPathsManager
from .xml_tools_view import XmlToolsView

XPATH_HELP_URL = "https://www.w3schools.com/xml/xpath_syntax.asp"
CONVERT_FILTER = (
    "Tables (*.csv *.xlsx *.xlsm *.html *.htm *.json *.md *.markdown);;"
    "CSV File (*.csv);;Excel Workbook (*.xlsx *.xlsm);;HTML (*.html *.htm);;"
    "JSON (*.json);;Markdown (*.md *.markdown);;All files (*)"
)

# Sidebar pages (order of list_widget_navigation / stacked_pages) and the output tab each uses.
PAGE_EXTRACT, PAGE_XML_TOOLS, PAGE_CSV_TOOLS, PAGE_TABLE = range(4)
_OUTPUT_TAB_FOR_PAGE = {PAGE_EXTRACT: 0, PAGE_CSV_TOOLS: 1, PAGE_XML_TOOLS: 2}

_GROUP_ON_HELP = """
        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Match 1; Match 2; Match 3 |"""
_GROUP_OFF_HELP = """
        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Match 1         |
        | Data...       | Match 2         |
        | Data...       | Match 3         |"""
_INDEX_ON_HELP = """
        Data will look like this:

        | Index           | Header 1   | Header 2    |
        |-------------------|-------------------|-------------------|
        | 1                  | Data...         | Data...        |
        """
_INDEX_OFF_HELP = """
        Data will look like this:

        | Header 1 | Header 2      |
        |------------------|-------------------|
        | Data...       | Data...         |
        """


@dataclass(frozen=True)
class MainViewModels:
    settings: SettingsViewModel
    workspace: XPathWorkspaceViewModel
    inspector: XmlInspectorViewModel
    export: ExportViewModel
    csv_tools: CsvToolsViewModel
    transforms: CsvTransformsViewModel
    xml_tools: XmlToolsViewModel
    table: TableViewerViewModel
    presets: PresetsViewModel
    new_presets_vm: Callable[[], PresetsViewModel]


def _refill(combo: QComboBox, items: list[str]) -> None:
    combo.clear()
    combo.addItems(items)


class MainWindow(QMainWindow):
    def __init__(
        self, vms: MainViewModels, runner: TaskRunner, config_dir: Path, title: str
    ) -> None:
        super().__init__()
        self.vms = vms
        self.runner = runner
        self.config_dir = config_dir
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self._managers: dict[str, QWidget] = {}

        self._setup_widgets()
        self._setup_navigation()
        self._bind_xpath_builder()
        self._bind_export()
        self._bind_csv_tab()
        self._bind_menus()
        self._bind_context_menus()
        self._bind_messages()
        self._apply_settings()
        self._restore_window_state()

    # ------------------------------------------------------------------ setup

    def _setup_widgets(self) -> None:
        ui = self.ui
        for widget in (
            ui.button_find_next,
            ui.button_find_previous,
            ui.button_abort_csv_export,
            ui.progressbar_main,
            ui.label_file_processing,
            ui.line_edit_xml_output_find_text,
        ):
            widget.hide()
        ui.button_clear_table.setDisabled(True)
        ui.line_edit_filter_table.setDisabled(True)
        ui.frame_conversion_result.hide()
        ui.label_hex_error.hide()
        for widget in (
            ui.list_widget_main_xpath_expressions,
            ui.text_edit_xml_output,
            ui.text_edit_program_output,
            ui.text_edit_csv_output,
            ui.text_edit_xml_tools_output,
        ):
            widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        ui.table_csv_data.setModel(self.vms.table.model)
        ui.table_csv_data.verticalHeader().setDefaultSectionSize(28)
        ui.table_csv_data.horizontalHeader().setHighlightSections(False)
        self._find_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_F), self)
        self._find_shortcut.activated.connect(self._toggle_find)
        ui.line_edit_xml_output_find_text.returnPressed.connect(self._find_from_keyboard)
        ui.splitter_extract.setStretchFactor(0, 3)
        ui.splitter_extract.setStretchFactor(1, 2)
        self.resizeDocks([ui.dock_output], [170], Qt.Orientation.Vertical)

    def _setup_navigation(self) -> None:
        ui = self.ui
        # No Windows theme icon looks like a table, so this one is drawn in code. The theme
        # icons are wrapped so they keep their color on the selected item, like this one.
        navigation = ui.list_widget_navigation
        navigation.item(PAGE_TABLE).setIcon(table_icon())
        navigation.item(PAGE_XML_TOOLS).setIcon(code_icon())
        for page in (PAGE_EXTRACT, PAGE_CSV_TOOLS):
            item = navigation.item(page)
            item.setIcon(steady_icon(item.icon()))
        ui.list_widget_navigation.currentRowChanged.connect(self._show_page)
        for page in (PAGE_EXTRACT, PAGE_XML_TOOLS, PAGE_CSV_TOOLS, PAGE_TABLE):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{page + 1}"), self)
            shortcut.activated.connect(lambda p=page: ui.list_widget_navigation.setCurrentRow(p))
        output_toggle = ui.dock_output.toggleViewAction()
        output_toggle.setText("Output panel")
        output_toggle.setShortcut(QKeySequence("Ctrl+J"))
        ui.view_menu.addAction(output_toggle)
        clear_output = ui.view_menu.addAction("Clear output")
        clear_output.triggered.connect(self._clear_output)
        ui.list_widget_navigation.setCurrentRow(PAGE_EXTRACT)

    def _show_page(self, page: int) -> None:
        if page < 0:
            return
        self.ui.stacked_pages.setCurrentIndex(page)
        tab = _OUTPUT_TAB_FOR_PAGE.get(page)
        if tab is not None:
            self.ui.tab_widget_output.setCurrentIndex(tab)

    def _clear_output(self) -> None:
        self.ui.text_edit_program_output.clear()
        self.ui.text_edit_csv_output.clear()
        self.ui.text_edit_xml_tools_output.clear()

    def _apply_settings(self) -> None:
        settings = self.vms.settings
        self.ui.checkbox_group_matches.blockSignals(True)
        self.ui.checkbox_group_matches.setChecked(settings.group_matches)
        self.ui.checkbox_group_matches.blockSignals(False)
        self.ui.prompt_on_exit_action.setChecked(settings.prompt_on_exit)
        self._apply_theme(settings.theme)

    def _apply_theme(self, key: str) -> None:
        try:
            stylesheet = load_stylesheet(key)
        except (KeyError, OSError) as exc:
            QMessageBox.critical(self, "Theme load error", f"Failed to load theme: {exc}")
            return
        app = QApplication.instance()
        if isinstance(app, QApplication):
            apply_icon_palette(app, key)
            app.setStyleSheet(stylesheet)

    # ------------------------------------------------------------------ XPath builder

    def _criteria(self) -> BuildCriteria:
        ui = self.ui
        operator = Operator.EQUALS
        for button, op in (
            (ui.radio_button_contains, Operator.CONTAINS),
            (ui.radio_button_starts_with, Operator.STARTS_WITH),
            (ui.radio_button_greater, Operator.GREATER),
            (ui.radio_button_smaller, Operator.SMALLER),
        ):
            if button.isChecked():
                operator = op
        return BuildCriteria(
            ui.combobox_tag_names.currentText(),
            ui.combobox_tag_values.currentText(),
            ui.combobox_attribute_names.currentText(),
            ui.combobox_attribute_values.currentText(),
            operator,
        )

    def _bind_xpath_builder(self) -> None:
        ui, inspector, workspace = self.ui, self.vms.inspector, self.vms.workspace

        ui.button_browse_xml_folder.clicked.connect(
            lambda: browse_folder_into(
                self, "Select directory that contains XML files", ui.line_edit_xml_folder_path_input
            )
        )
        ui.button_read_xml.clicked.connect(self._read_xml)
        ui.button_build_xpath.clicked.connect(lambda: workspace.build_expression(self._criteria()))
        ui.button_add_xpath_to_list.clicked.connect(
            lambda: workspace.add_expressions(ui.line_edit_xpath_builder.text(), self._criteria())
        )
        ui.button_find_next.clicked.connect(lambda: self._find(backward=False))
        ui.button_find_previous.clicked.connect(lambda: self._find(backward=True))

        ui.combobox_tag_names.currentTextChanged.connect(inspector.select_tag)
        ui.combobox_attribute_names.currentTextChanged.connect(
            lambda attr: inspector.select_attribute(ui.combobox_tag_names.currentText(), attr)
        )
        inspector.loading_changed.connect(ui.button_read_xml.setDisabled)
        inspector.document_loaded.connect(self._show_document)
        inspector.tags_changed.connect(self._show_tags)
        inspector.attributes_changed.connect(self._show_attributes)
        inspector.tag_values_changed.connect(self._show_tag_values)
        inspector.attribute_values_changed.connect(self._show_attribute_values)

        workspace.expressions_changed.connect(self._show_expressions)
        workspace.headers_text_changed.connect(ui.line_edit_csv_headers_input.setText)
        workspace.expression_input_changed.connect(ui.line_edit_xpath_builder.setText)
        workspace.recent_changed.connect(self._show_recent)
        ui.line_edit_csv_headers_input.textChanged.connect(workspace.set_headers_text)
        self._show_recent(workspace.recent)

    def _read_xml(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Select XML File", "", "XML File (*.xml)")
        if not file_name:
            return
        self.ui.text_edit_program_output.clear()
        self.ui.line_edit_xml_folder_path_input.setText(os.path.dirname(file_name))
        self.vms.inspector.load(file_name)

    def _show_document(self, index: XmlIndex) -> None:
        self.ui.text_edit_xml_output.setPlainText(index.preview_text)

    def _show_tags(self, tags: list[str]) -> None:
        ui = self.ui
        for combo in (
            ui.combobox_tag_names,
            ui.combobox_tag_values,
            ui.combobox_attribute_names,
            ui.combobox_attribute_values,
        ):
            combo.setDisabled(False)
        _refill(ui.combobox_tag_names, tags)  # selecting the first tag fills the others

    def _show_attributes(self, attributes: list[str]) -> None:
        ui = self.ui
        _refill(ui.combobox_attribute_names, attributes)
        ui.combobox_attribute_names.setDisabled(not attributes)
        if not attributes:
            ui.combobox_attribute_values.clear()
            ui.combobox_attribute_values.setDisabled(True)

    def _show_tag_values(self, values: list[str]) -> None:
        has_values = any(v.strip() for v in values)
        _refill(self.ui.combobox_tag_values, values if has_values else [])
        self.ui.combobox_tag_values.setDisabled(not has_values)

    def _show_attribute_values(self, values: list[str]) -> None:
        _refill(self.ui.combobox_attribute_values, values)
        self.ui.combobox_attribute_values.setDisabled(not values)

    def _show_expressions(self, expressions: list[str]) -> None:
        widget = self.ui.list_widget_main_xpath_expressions
        widget.clear()
        widget.addItems(expressions)

    def _show_recent(self, expressions: list[str]) -> None:
        menu = self.ui.recent_xpath_expressions_menu
        menu.clear()
        for expression in expressions:
            action = menu.addAction(expression)
            action.triggered.connect(
                lambda _checked=False, exp=expression: self.vms.workspace.use_recent(exp)
            )

    def _toggle_find(self) -> None:
        ui = self.ui
        show = ui.line_edit_xml_output_find_text.isHidden()
        for widget in (
            ui.line_edit_xml_output_find_text,
            ui.button_find_next,
            ui.button_find_previous,
        ):
            widget.setVisible(show)
        if show:
            ui.line_edit_xml_output_find_text.setFocus()
        else:
            ui.line_edit_xml_output_find_text.clear()

    def _find_from_keyboard(self) -> None:
        modifiers = QGuiApplication.keyboardModifiers()
        self._find(backward=bool(modifiers & Qt.KeyboardModifier.ShiftModifier))

    def _find(self, backward: bool) -> None:
        text = self.ui.line_edit_xml_output_find_text.text()
        if not text:
            QMessageBox.information(
                self, "Find text input is empty", "No text has been entered for search criteria."
            )
            return
        if backward:
            self.ui.text_edit_xml_output.find(text, QTextDocument.FindFlag.FindBackward)
        else:
            self.ui.text_edit_xml_output.find(text)

    # ------------------------------------------------------------------ export

    def _bind_export(self) -> None:
        ui, export, workspace = self.ui, self.vms.export, self.vms.workspace
        ui.button_browse_csv.clicked.connect(
            lambda: browse_save_file_into(
                self,
                "Save as",
                ui.line_edit_csv_output_path,
                "CSV File (*.csv)",
                f"Evaluation_{datetime.datetime.now():%Y.%m.%d_%H%M}.csv",
            )
        )
        ui.button_start_csv_export.clicked.connect(
            lambda: export.start(
                ui.line_edit_xml_folder_path_input.text(),
                ui.line_edit_csv_output_path.text(),
                ui.line_edit_csv_headers_input.text(),
                workspace.expressions,
                ui.checkbox_group_matches.isChecked(),
            )
        )
        ui.button_abort_csv_export.clicked.connect(export.cancel)
        ui.button_pass_csv_to_converter.linkActivated.connect(self._pass_csv_to_converter)
        ui.line_edit_xml_folder_path_input.textChanged.connect(export.folder_changed)
        ui.checkbox_group_matches.toggled.connect(self._group_matches_toggled)

        export.running_changed.connect(self._set_exporting)
        export.progress_changed.connect(ui.progressbar_main.setValue)
        export.status_changed.connect(ui.label_file_processing.setText)
        export.folder_count_changed.connect(ui.statusbar_xml_files_count.setText)

    def _set_exporting(self, exporting: bool) -> None:
        ui = self.ui
        ui.button_start_csv_export.setVisible(not exporting)
        ui.button_abort_csv_export.setVisible(exporting)
        ui.progressbar_main.setVisible(exporting)
        ui.label_file_processing.setVisible(exporting)
        for widget in (
            ui.button_browse_xml_folder,
            ui.button_read_xml,
            ui.button_build_xpath,
            ui.button_add_xpath_to_list,
            ui.button_browse_csv,
            ui.button_browse_csv_conversion_path_input,
            ui.button_start_csv_export,
        ):
            widget.setDisabled(exporting)
        ui.line_edit_xml_folder_path_input.setReadOnly(exporting)
        ui.line_edit_csv_output_path.setReadOnly(exporting)

    def _group_matches_toggled(self, checked: bool) -> None:
        self.vms.settings.set_group_matches(checked)
        if checked:
            self.ui.text_edit_program_output.setText(
                "Group Matches is enabled. All matches for each XPath expression will be grouped "
                f"together in the CSV output.\n{_GROUP_ON_HELP}"
            )
        else:
            self.ui.text_edit_program_output.setText(
                "Group Matches is disabled. Each match will be listed separately in the CSV "
                f"output.\n{_GROUP_OFF_HELP}"
            )

    def _pass_csv_to_converter(self) -> None:
        ui = self.ui
        if not ui.line_edit_csv_output_path.text():
            QMessageBox.information(
                self,
                "CSV output not set",
                "No CSV output for exporting has been set.\n"
                "Cannot copy path to CSV converter input field.",
            )
            return
        ui.line_edit_csv_conversion_path_input.setText(ui.line_edit_csv_output_path.text())
        ui.list_widget_navigation.setCurrentRow(PAGE_CSV_TOOLS)

    # ------------------------------------------------------------------ CSV tab

    def _bind_csv_tab(self) -> None:
        ui, csv_vm, table = self.ui, self.vms.csv_tools, self.vms.table
        ui.button_browse_csv_conversion_path_input.clicked.connect(
            lambda: browse_open_file_into(
                self,
                "Select file to convert",
                ui.line_edit_csv_conversion_path_input,
                CONVERT_FILTER,
            )
        )
        ui.line_edit_csv_conversion_path_input.textChanged.connect(self._conversion_input_changed)
        ui.button_csv_conversion_convert.clicked.connect(
            lambda: csv_vm.convert(
                ui.line_edit_csv_conversion_path_input.text(),
                ui.combobox_csv_conversion_output_type.currentText(),
                ui.checkbox_write_index_column.isChecked(),
                ui.combobox_csv_conversion_delimiter.currentText()
                if ui.checkbox_csv_conversion_manual_delimiter.isChecked()
                else None,
            )
        )
        ui.checkbox_csv_conversion_manual_delimiter.toggled.connect(
            ui.combobox_csv_conversion_delimiter.setEnabled
        )
        ui.button_csv_conversion_open_file.clicked.connect(self._open_converted_file)
        ui.button_csv_conversion_show_folder.clicked.connect(
            lambda: self._open_folder(
                os.path.dirname(ui.line_edit_csv_conversion_open_file_path.text())
            )
        )
        ui.checkbox_write_index_column.toggled.connect(
            lambda on: ui.text_edit_csv_output.setText(_INDEX_ON_HELP if on else _INDEX_OFF_HELP)
        )
        ui.button_profile_cleanup_browse_csv_file_path.clicked.connect(
            lambda: browse_open_file_into(
                self,
                "Select csv file",
                ui.line_edit_profile_cleanup_csv_file_path,
                "CSV File (*.csv)",
            )
        )
        ui.button_profile_cleanup_browse_folder_path.clicked.connect(
            lambda: browse_folder_into(
                self,
                "Select directory that contains XML files",
                ui.line_edit_profile_cleanup_folder_path,
            )
        )
        ui.button_profile_cleanup_cleanup_start.clicked.connect(
            lambda: csv_vm.plan_cleanup(
                ui.line_edit_profile_cleanup_csv_file_path.text(),
                ui.line_edit_profile_cleanup_folder_path.text(),
            )
        )
        ui.line_edit_hexadecimal.textChanged.connect(self._hex_to_decimal)
        ui.button_load_csv.clicked.connect(self._load_table)
        ui.button_clear_table.clicked.connect(self._clear_table)
        ui.line_edit_filter_table.textChanged.connect(table.set_filter)

        for vm in (csv_vm, self.vms.transforms):
            vm.log_appended.connect(ui.text_edit_csv_output.append)
            vm.log_replaced.connect(ui.text_edit_csv_output.setText)
        csv_vm.conversion_running_changed.connect(self._set_converting)
        csv_vm.converted_file_changed.connect(self._show_converted_file)
        csv_vm.cleanup_confirmation_requested.connect(self._confirm_cleanup)
        csv_vm.cleanup_running_changed.connect(self._set_cleaning_up)
        table.has_table_changed.connect(self._table_state)
        table.loading_changed.connect(ui.button_load_csv.setDisabled)
        table.loading_changed.connect(
            lambda busy: self._set_table_status("Loading…") if busy else self._update_table_rows()
        )
        table.filtering_changed.connect(lambda _busy: self._update_table_rows())
        for signal in (table.model.modelReset, table.model.layoutChanged):
            signal.connect(self._update_table_rows)
        self._update_table_rows()
        self._csv_transforms = CsvTransformsView(self, self.vms.transforms)
        self._xml_tools = XmlToolsView(self, self.vms.xml_tools)
        self.vms.xml_tools.log_appended.connect(ui.text_edit_xml_tools_output.append)
        self.vms.xml_tools.log_replaced.connect(ui.text_edit_xml_tools_output.setText)

    def _conversion_input_changed(self, path: str) -> None:
        """Excel, HTML, JSON and Markdown files convert to CSV; CSV files to the others."""
        combo = self.ui.combobox_csv_conversion_output_type
        suggested = self.vms.csv_tools.suggested_output_type(path, combo.currentText())
        if suggested is not None:
            combo.setCurrentText(suggested)

    def _open_converted_file(self) -> None:
        path = self.ui.line_edit_csv_conversion_open_file_path.text()
        if not open_path(path):
            self.ui.text_edit_program_output.setText(
                f"Invalid or missing path: Could not open file: {path}"
            )

    def _confirm_cleanup(self, plan: CleanupPlan) -> None:
        names = "\n".join(p.name for p in plan.delete[:15])
        more = f"\n... and {len(plan.delete) - 15} more" if len(plan.delete) > 15 else ""
        confirmed = ask_yes_no(
            self,
            "Delete profile files?",
            f"{len(plan.delete)} of {plan.files_in_folder} XML files in\n{plan.folder}\n"
            f"are not listed in the CSV file and will be permanently deleted:\n\n{names}{more}"
            "\n\nDo you want to continue?",
        )
        self.vms.csv_tools.confirm_cleanup(plan, confirmed)

    # Each tool shows its own busy bar and disables its own action while it runs.

    def _set_converting(self, running: bool) -> None:
        ui = self.ui
        ui.busy_bar_conversion.set_running(running)
        ui.button_csv_conversion_convert.setDisabled(running)
        ui.button_browse_csv_conversion_path_input.setDisabled(running)
        if running:
            ui.frame_conversion_result.hide()

    def _show_converted_file(self, path: str) -> None:
        self.ui.line_edit_csv_conversion_open_file_path.setText(path)
        self.ui.line_edit_csv_conversion_open_file_path.setCursorPosition(0)
        self.ui.frame_conversion_result.setVisible(bool(path))

    def _set_cleaning_up(self, running: bool) -> None:
        self.ui.busy_bar_cleanup.set_running(running)
        self.ui.button_profile_cleanup_cleanup_start.setDisabled(running)

    def _hex_to_decimal(self, text: str) -> None:
        ui = self.ui
        try:
            value = parse_hex(text)
        except ValueError:
            ui.line_edit_decimal.clear()
            ui.label_hex_error.setText("Not a hexadecimal number: use the digits 0–9 and A–F.")
            ui.label_hex_error.show()
            return
        ui.label_hex_error.hide()
        ui.line_edit_decimal.setText("" if value is None else str(value))

    def _load_table(self) -> None:
        file_path = browse_open_file(self, "Select CSV file to display", "CSV File (*.csv)")
        if file_path:
            self.vms.table.load(file_path)

    def _clear_table(self) -> None:
        self.ui.line_edit_filter_table.clear()
        self.vms.table.clear()

    def _table_state(self, has_table: bool) -> None:
        self.ui.button_clear_table.setDisabled(not has_table)
        self.ui.line_edit_filter_table.setDisabled(not has_table)
        if has_table:
            self.ui.table_csv_data.resizeColumnsToContents()  # only fetched rows are measured
        self._update_table_rows()

    def _set_table_status(self, text: str) -> None:
        self.ui.label_table_rows.setText(text)

    def _update_table_rows(self) -> None:
        model = self.vms.table.model
        total = model.data_store.row_count
        if total == 0 and model.columnCount() == 0:
            self._set_table_status("")
        elif model.total_rows == total:
            self._set_table_status(f"{total:,} rows")
        else:
            self._set_table_status(f"{model.total_rows:,} of {total:,} rows")

    # ------------------------------------------------------------------ menus

    def _bind_menus(self) -> None:
        ui = self.ui
        ui.exit_action.triggered.connect(self.close)
        ui.open_input_action.triggered.connect(
            lambda: self._open_folder(ui.line_edit_xml_folder_path_input.text())
        )
        ui.open_output_action.triggered.connect(
            lambda: self._open_parent_folder(
                ui.line_edit_csv_output_path.text(),
                "Missing output path: Could not open output directory, please set a valid "
                "output path first.",
            )
        )
        ui.open_csv_conversion_input_action.triggered.connect(
            lambda: self._open_parent_folder(
                ui.line_edit_csv_conversion_path_input.text(),
                "Missing input path: Could not open CSV conversion input directory, please set "
                "a valid input path first.",
            )
        )
        ui.open_paths_manager.triggered.connect(self._open_paths_manager)
        ui.open_pre_built_xpaths_manager_action.triggered.connect(self._open_presets_manager)
        ui.clear_recent_xpath_expressions_action.triggered.connect(self._clear_recent)
        ui.xpath_help_action.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl(XPATH_HELP_URL))
        )
        ui.prompt_on_exit_action.toggled.connect(self.vms.settings.set_prompt_on_exit)

        self._preview_limit_action = QAction("XML Preview Size Limit...", self)
        self._preview_limit_action.setStatusTip(
            "Largest XML file whose full text is shown in the XML output"
        )
        self._preview_limit_action.triggered.connect(self._ask_preview_limit)
        ui.settings_menu.addSeparator()
        ui.settings_menu.addAction(self._preview_limit_action)

        self._build_theme_menu()
        self.vms.presets.changed.connect(self._build_config_menus)
        self.vms.settings.theme_changed.connect(self._apply_theme)
        self._build_config_menus()

    def _build_theme_menu(self) -> None:
        menu = self.ui.theme_menu
        menu.clear()
        for key in THEMES:
            action = menu.addAction(theme_label(key))
            action.triggered.connect(lambda _c=False, k=key: self.vms.settings.set_theme(k))
            if key == "light_theme_default":
                menu.addSeparator()

    def _build_config_menus(self) -> None:
        paths_menu = self.ui.paths_menu
        paths_menu.clear()
        for name, path in self.vms.presets.custom_paths().items():
            action = paths_menu.addAction(name)
            action.setStatusTip(f"Open {name}")
            action.triggered.connect(
                lambda _c=False, p=path: self.ui.line_edit_xml_folder_path_input.setText(p)
            )
        autofill_menu = self.ui.menu_autofill
        autofill_menu.clear()
        for preset in self.vms.presets.presets():
            action = autofill_menu.addAction(preset.name)
            action.triggered.connect(lambda _c=False, p=preset: self.vms.workspace.apply_preset(p))

    def _open_folder(self, folder: str) -> None:
        if not open_path(folder):
            self.ui.text_edit_program_output.setText(
                f"Invalid or missing path: Could not open directory: {folder}"
            )

    def _open_parent_folder(self, file_path: str, missing_message: str) -> None:
        if not file_path:
            self.ui.text_edit_program_output.setText(missing_message)
            return
        self._open_folder(os.path.dirname(file_path))

    def _clear_recent(self) -> None:
        if ask_yes_no(
            self,
            "Clear Recent XPath Expressions?",
            "Are you sure you want to clear all recent XPath expressions?",
        ):
            self.vms.workspace.clear_recent()

    def _ask_preview_limit(self) -> None:
        value, ok = QInputDialog.getInt(
            self,
            "XML Preview Size Limit",
            "Show the full, formatted text of XML files up to this size (MB).\n"
            "Larger files show only their beginning; tag and attribute lists\n"
            "always cover the whole file.",
            self.vms.settings.preview_limit_mb,
            1,
            MAX_PREVIEW_LIMIT_MB,
        )
        if ok:
            self.vms.settings.set_preview_limit_mb(value)

    def _open_manager(self, key: str, factory: Callable[[PresetsViewModel], QWidget]) -> None:
        window = self._managers.get(key)
        if window is None:
            window = factory(self.vms.new_presets_vm())
            window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            window.destroyed.connect(lambda _obj=None, k=key: self._managers.pop(k, None))
            self._managers[key] = window
        window.show()
        window.raise_()
        window.activateWindow()

    def _open_paths_manager(self) -> None:
        self._open_manager("paths", lambda vm: CustomPathsManager(vm, self.config_dir))

    def _open_presets_manager(self) -> None:
        self._open_manager("presets", lambda vm: PreBuiltXPathsManager(vm, self.config_dir))

    # ------------------------------------------------------------------ context menus

    def _bind_context_menus(self) -> None:
        ui = self.ui
        ui.list_widget_main_xpath_expressions.customContextMenuRequested.connect(
            self._xpath_list_menu
        )
        ui.text_edit_xml_output.customContextMenuRequested.connect(self._xml_output_menu)
        ui.text_edit_program_output.customContextMenuRequested.connect(
            lambda pos: self._text_menu(ui.text_edit_program_output, pos)
        )
        ui.text_edit_csv_output.customContextMenuRequested.connect(
            lambda pos: self._text_menu(ui.text_edit_csv_output, pos)
        )
        ui.text_edit_xml_tools_output.customContextMenuRequested.connect(
            lambda pos: self._text_menu(ui.text_edit_xml_tools_output, pos)
        )

    def _run_menu(
        self, widget: QWidget, pos: QPoint, entries: list[tuple[str, Callable[[], object]] | None]
    ) -> None:
        menu = QMenu(self)
        actions: dict[QAction, Callable[[], object]] = {}
        for entry in entries:
            if entry is None:
                menu.addSeparator()
            else:
                actions[menu.addAction(entry[0])] = entry[1]
        chosen = menu.exec(widget.mapToGlobal(pos))
        menu.deleteLater()
        if chosen in actions:
            actions[chosen]()

    def _xpath_list_menu(self, pos: QPoint) -> None:
        widget = self.ui.list_widget_main_xpath_expressions
        self._run_menu(
            widget,
            pos,
            [
                ("Remove Selected", lambda: self.vms.workspace.remove_at(widget.currentRow())),
                ("Remove All", self.vms.workspace.remove_all),
            ],
        )

    def _xml_output_menu(self, pos: QPoint) -> None:
        widget = self.ui.text_edit_xml_output
        self._run_menu(
            widget,
            pos,
            [
                ("Copy", widget.copy),
                ("Select All", widget.selectAll),
                None,
                ("Find\tCtrl+F", self._toggle_find),
            ],
        )

    def _text_menu(self, widget: QTextEdit | QPlainTextEdit, pos: QPoint) -> None:
        self._run_menu(
            widget,
            pos,
            [
                ("Copy", widget.copy),
                ("Select All", widget.selectAll),
                None,
                ("Clear", widget.clear),
            ],
        )

    # ------------------------------------------------------------------ messages

    def _bind_messages(self) -> None:
        vms = self.vms
        connect_notifications(
            self,
            vms.settings,
            vms.workspace,
            vms.inspector,
            vms.export,
            vms.csv_tools,
            vms.transforms,
            vms.xml_tools,
            vms.table,
            vms.presets,
        )
        output = self.ui.text_edit_program_output
        for vm in (vms.settings, vms.workspace, vms.inspector, vms.export, vms.table):
            vm.log_appended.connect(output.append)
            vm.log_replaced.connect(output.setText)
        if vms.presets.load_warning:
            warning = vms.presets.load_warning
            QTimer.singleShot(0, lambda: QMessageBox.warning(self, "Load config warning", warning))

    # ------------------------------------------------------------------ window state / exit

    def _restore_window_state(self) -> None:
        geometry, state = self.vms.settings.window_state()
        if geometry:
            self.restoreGeometry(geometry)
        if state:
            self.restoreState(state)
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        frame = self.frameGeometry()
        if not available.contains(frame, proper=False):
            self.resize(
                min(frame.width(), available.width()), min(frame.height(), available.height())
            )
            self.move(
                max(available.left(), min(frame.left(), available.right() - self.width())),
                max(available.top(), min(frame.top(), available.bottom() - self.height())),
            )

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.ui.prompt_on_exit_action.isChecked():
            dialog = ExitDialog(self)
            if dialog.exec() == QDialog.DialogCode.Rejected:
                event.ignore()
                return
            if dialog.dont_ask_again:
                self.ui.prompt_on_exit_action.setChecked(False)
        self.vms.settings.save_window_state(self.saveGeometry(), self.saveState())
        for window in list(self._managers.values()):
            window.close()
        self.runner.shutdown()
        super().closeEvent(event)
