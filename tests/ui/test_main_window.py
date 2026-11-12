"""Smoke and regression tests for the main window (offscreen)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QPlainTextEdit

from xmluvation.infrastructure.settings_store import SettingsStore
from xmluvation.presentation.views.main_window import PAGE_CSV_TOOLS, PAGE_TABLE, PAGE_XML_TOOLS


def test_window_builds_with_theme_and_initial_state(window) -> None:
    ui = window.ui
    assert len(QApplication.instance().styleSheet()) > 1000
    assert ui.button_abort_csv_export.isHidden() and ui.progressbar_main.isHidden()
    assert not ui.button_clear_table.isEnabled() and not ui.line_edit_filter_table.isEnabled()
    assert isinstance(ui.text_edit_xml_output, QPlainTextEdit)
    assert [a.text() for a in ui.theme_menu.actions() if a.text()][0] == "Dark Theme Default"


def test_recent_menu_works_after_adding_expression(window) -> None:
    window.vms.workspace.add_expressions("//a/@id")
    actions = window.ui.recent_xpath_expressions_menu.actions()
    assert [a.text() for a in actions] == ["//a/@id"]
    actions[0].trigger()
    assert window.ui.line_edit_xpath_builder.text() == "//a/@id"


def test_table_filter_no_longer_crashes(qtbot, window, tmp_path: Path) -> None:
    csv_file = tmp_path / "t.csv"
    csv_file.write_text("A,B\nx,1\ny,2\n", encoding="utf-8")
    window.vms.table.load(str(csv_file))
    qtbot.waitUntil(window.ui.line_edit_filter_table.isEnabled, timeout=5000)
    window.ui.line_edit_filter_table.setText("y")
    qtbot.waitUntil(lambda: window.ui.table_csv_data.model().rowCount() == 1, timeout=5000)


def test_prompt_on_exit_is_saved_immediately(window, settings: SettingsStore) -> None:
    window.ui.prompt_on_exit_action.setChecked(True)
    assert settings.prompt_on_exit is True
    window.ui.prompt_on_exit_action.setChecked(False)
    assert settings.prompt_on_exit is False


def test_manager_windows_do_not_close_each_other(qtbot, window) -> None:
    window._open_paths_manager()
    window._open_presets_manager()
    paths, presets = window._managers["paths"], window._managers["presets"]
    assert paths.isVisible() and presets.isVisible()
    window._open_paths_manager()
    assert window._managers["paths"] is paths  # reused, not duplicated


def test_config_changes_refresh_menus(window) -> None:
    window.vms.presets.save_custom_path("Exports", "C:/Exports")
    window.vms.presets.save_preset("Preset", ["//a/@id"], ["ID"])
    assert [a.text() for a in window.ui.paths_menu.actions()] == ["Exports"]
    window.ui.menu_autofill.actions()[0].trigger()
    assert window.vms.workspace.expressions == ["//a/@id"]
    assert window.ui.line_edit_csv_headers_input.text() == "ID"


def test_comboboxes_follow_selected_tag(qtbot, window, xml_dir: Path) -> None:
    window.vms.inspector.load(str(xml_dir / "simple.xml"))
    qtbot.waitUntil(lambda: window.ui.combobox_tag_names.count() > 0, timeout=5000)
    ui = window.ui
    ui.combobox_tag_names.setCurrentText("book")
    attributes = [
        ui.combobox_attribute_names.itemText(i) for i in range(ui.combobox_attribute_names.count())
    ]
    assert attributes == ["id", "lang"]
    ui.combobox_tag_names.setCurrentText("title")
    assert ui.combobox_attribute_names.count() == 0 and not ui.combobox_attribute_names.isEnabled()
    assert "<library>" in ui.text_edit_xml_output.toPlainText()


def test_settings_persist_with_legacy_keys(tmp_path: Path) -> None:
    raw = QSettings(str(tmp_path / "s.ini"), QSettings.Format.IniFormat)
    raw.setValue("app_theme", "dark_theme_peach")
    raw.setValue("recent_xpath_expressions", ["//x"])
    store = SettingsStore(raw)
    assert store.theme == "dark_theme_peach" and store.recent_xpath_expressions == ["//x"]
    store.xml_preview_limit_mb = 0
    assert store.xml_preview_limit_mb == 1


def test_column_editor_reorders_renames_and_drops(qtbot, window, tmp_path: Path) -> None:
    from PySide6.QtCore import Qt

    csv_file = tmp_path / "c.csv"
    csv_file.write_text("A,B,C\n1,2,3\n", encoding="utf-8")
    ui = window.ui
    ui.line_edit_columns_csv_file_path.setText(str(csv_file))
    qtbot.waitUntil(lambda: ui.list_widget_columns.count() == 3, timeout=5000)
    assert ui.label_columns_status.text() == "Keeping 3 of 3 columns."

    ui.list_widget_columns.item(1).setCheckState(Qt.CheckState.Unchecked)  # drop B
    ui.list_widget_columns.item(2).setText("Gamma")  # rename C
    ui.list_widget_columns.setCurrentRow(2)
    ui.button_columns_up.click()
    ui.button_columns_up.click()  # C first
    assert ui.label_columns_status.text() == "Keeping 2 of 3 columns, 1 renamed, order changed."

    ui.button_columns_save.click()
    qtbot.waitUntil(lambda: not ui.frame_columns_result.isHidden(), timeout=5000)
    edited = tmp_path / "c_edited.csv"
    assert ui.line_edit_columns_result_path.text() == str(edited)
    assert edited.read_bytes() == b"Gamma,A\r\n3,1\r\n"


def test_csv_compare_shows_both_files_side_by_side(qtbot, window, tmp_path: Path) -> None:
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    old.write_text("K,V\n1,a\n2,b\n", encoding="utf-8")
    new.write_text("K,V\n1,a\n2,c\n3,d\n", encoding="utf-8")
    ui = window.ui
    assert ui.card_compare_diff.isHidden()
    ui.line_edit_compare_old_csv_file_path.setText(str(old))
    ui.line_edit_compare_new_csv_file_path.setText(str(new))
    qtbot.waitUntil(lambda: ui.combobox_compare_key.count() == 3, timeout=5000)
    assert ui.combobox_compare_key.currentText() == "K"  # "no key" is the last entry
    ui.button_compare_start.click()
    qtbot.waitUntil(lambda: not ui.frame_compare_result.isHidden(), timeout=5000)
    assert "1 added, 1 changed rows (1 changed cells)" in ui.label_compare_summary.text()
    assert not ui.card_compare_diff.isHidden()
    assert ui.diff_view_csv_compare.pane_texts() == ("K,V\n1,a\n2,b\n", "K,V\n1,a\n2,c\n3,d")
    assert ui.diff_view_csv_compare.position_text() == "Change 1 of 1"
    assert ui.stacked_pages.currentIndex() != PAGE_TABLE

    ui.combobox_compare_key.setCurrentIndex(2)  # no key
    ui.button_compare_start.click()
    qtbot.waitUntil(lambda: not ui.frame_compare_result.isHidden(), timeout=5000)
    assert "paired by their position" in ui.label_compare_summary.text()


def test_conversion_input_selects_a_fitting_output_type(window) -> None:
    ui = window.ui
    combo = ui.combobox_csv_conversion_output_type
    assert combo.currentText() == "EXCEL"
    ui.line_edit_csv_conversion_path_input.setText(r"C:\data\report.xlsx")
    assert combo.currentText() == "CSV"
    ui.line_edit_csv_conversion_path_input.setText(r"C:\data\report.csv")
    assert combo.currentText() == "EXCEL"
    combo.setCurrentText("JSON")
    ui.line_edit_csv_conversion_path_input.setText(r"C:\data\other.csv")
    assert combo.currentText() == "JSON"  # still fits, kept


def test_xml_tools_page_validates_and_compares(qtbot, window, tmp_path: Path) -> None:
    xsd = tmp_path / "s.xsd"
    xsd.write_text(
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">'
        '<xs:element name="n" type="xs:int"/></xs:schema>',
        encoding="utf-8",
    )
    old, new = tmp_path / "old.xml", tmp_path / "new.xml"
    old.write_text("<n>1</n>", encoding="utf-8")
    new.write_text("<n>x</n>", encoding="utf-8")
    ui = window.ui
    ui.list_widget_navigation.setCurrentRow(PAGE_XML_TOOLS)
    assert ui.stacked_pages.currentWidget() is ui.page_xml_tools
    assert ui.tab_widget_output.currentWidget() is ui.tab_output_xml

    ui.line_edit_validate_schema_path.setText(str(xsd))
    ui.line_edit_validate_xml_path.setText(str(old))
    ui.button_validate_start.click()
    qtbot.waitUntil(lambda: not ui.frame_validate_result.isHidden(), timeout=5000)
    assert ui.label_validate_summary.text().startswith("Valid")
    assert ui.button_validate_open_report.isHidden()  # nothing to report
    assert ui.text_edit_validate_problems.isHidden()

    # Problems are listed in the card itself, not in the table viewer.
    ui.line_edit_validate_xml_path.setText(str(new))
    ui.button_validate_start.click()
    qtbot.waitUntil(lambda: not ui.text_edit_validate_problems.isHidden(), timeout=5000)
    problems = ui.text_edit_validate_problems.toPlainText()
    assert problems.startswith("new.xml:1:") and ": error: " in problems
    assert not ui.button_validate_open_report.isHidden()
    assert ui.stacked_pages.currentWidget() is ui.page_xml_tools

    assert ui.card_xml_compare_diff.isHidden()
    ui.line_edit_xml_compare_old_path.setText(str(old))
    ui.line_edit_xml_compare_new_path.setText(str(new))
    ui.button_xml_compare_start.click()
    qtbot.waitUntil(lambda: not ui.frame_xml_compare_result.isHidden(), timeout=5000)
    assert "1 difference(s): 1 changed" in ui.label_xml_compare_summary.text()
    assert "Report saved" in ui.text_edit_xml_tools_output.toPlainText()
    assert not ui.card_xml_compare_diff.isHidden()
    assert ui.diff_view_xml_compare.pane_texts() == ("<n>1</n>", "<n>x</n>")
    assert ui.diff_view_xml_compare.position_text() == "Change 1 of 1"
    assert not hasattr(ui, "button_xml_compare_view_report")  # reports open externally
    assert ui.stacked_pages.currentIndex() != PAGE_TABLE


def test_table_viewer_page_tools(qtbot, window, tmp_path: Path) -> None:
    from PySide6.QtCore import QItemSelectionModel
    from PySide6.QtGui import QGuiApplication

    from xmluvation.presentation.views.main_window import PAGE_CSV_TOOLS

    ui, page = window.ui, window._table_viewer
    csv_file = tmp_path / "people.csv"
    csv_file.write_text("ID,Name,City\n1,Anna,Berlin\n2,Bob,Ulm\n2,Carl,Bonn\n", encoding="utf-8")
    assert not page.button_send.isEnabled() and not page.button_export.isEnabled()
    ui.table_csv_data.files_dropped.emit([str(tmp_path / "notes.txt"), str(csv_file)])
    qtbot.waitUntil(ui.line_edit_filter_table.isEnabled, timeout=5000)
    assert ui.label_table_rows.text() == "people.csv: 3 rows"
    assert page.button_send.isEnabled()

    table = ui.table_csv_data
    table.set_frozen_columns(1)
    assert not table.frozen_view().isHidden()
    assert not table.frozen_view().isColumnHidden(0) and table.frozen_view().isColumnHidden(1)
    table.horizontalHeader().moveSection(2, 0)  # City first
    assert page._visible_columns() == [2, 0, 1]
    assert table.frozen_view().isColumnHidden(0) and not table.frozen_view().isColumnHidden(2)
    page._set_hidden(1, True)
    assert page._visible_columns() == [2, 0]

    model = table.model()
    selection = table.selectionModel()
    flags = QItemSelectionModel.SelectionFlag.Select
    for row in (0, 1):
        for column in (0, 1, 2):
            selection.select(model.index(row, column), flags)
    page._copy(headers=True)
    assert QGuiApplication.clipboard().text() == "City\tID\r\nBerlin\t1\r\nUlm\t2"

    page.edit_go_to.setText("3")
    page.edit_go_to.returnPressed.emit()
    assert table.currentIndex().row() == 2
    page.edit_go_to.setText("7")
    page.edit_go_to.returnPressed.emit()
    assert "no row 7" in page.label_message.text()

    page._highlight_duplicates(0, True)
    assert "2 rows have a duplicated" in page.label_message.text()

    compare_old = next(a for a in page.menu_send.actions() if "old" in a.text())
    compare_old.trigger()
    assert ui.line_edit_compare_old_csv_file_path.text() == str(csv_file)
    assert ui.stacked_pages.currentIndex() == PAGE_CSV_TOOLS
    assert ui.tab_widget_csv_tools.currentWidget() is ui.tab_tool_compare

    # A new file starts with all columns, in order, nothing frozen or highlighted.
    js = tmp_path / "t.json"
    js.write_text('[{"A": "1"}]', encoding="utf-8")
    page.load(str(js))
    qtbot.waitUntil(lambda: ui.label_table_rows.text() == "t.json: 1 rows", timeout=5000)
    assert table.frozen_columns == 0 and window.vms.table.model.duplicate_column is None
    assert not page.button_send.isEnabled()  # only CSV files go to the CSV tools


def test_spin_box_number_is_inside_its_border_in_every_theme(qtbot, window) -> None:
    """Qt 6.12 drew the rows-per-file number under the spin box's left border (and in a
    1 px wide field with NoButtons); it must line up with the text of a line edit."""
    from PySide6.QtWidgets import QInputDialog, QLineEdit, QSpinBox

    from xmluvation.presentation.themes import THEMES

    ui = window.ui
    ui.list_widget_navigation.setCurrentRow(PAGE_CSV_TOOLS)
    ui.tab_widget_csv_tools.setCurrentWidget(ui.tab_tool_split)
    spin, line = ui.spin_box_split_rows, ui.line_edit_split_csv_file_path
    line.setText("1048575")
    dialog = QInputDialog(window)  # e.g. the XML preview limit
    dialog.setInputMode(QInputDialog.InputMode.IntInput)
    dialog.show()
    qtbot.addWidget(dialog)

    def text_x(box: QSpinBox) -> int:
        editor = box.findChild(QLineEdit, "qt_spinbox_lineedit")
        editor.setCursorPosition(0)
        return editor.mapTo(box, editor.cursorRect().center()).x()

    for key in [*THEMES, "dark_theme_default"]:
        window.vms.settings.set_theme(key)
        QApplication.processEvents()
        editor = spin.findChild(QLineEdit, "qt_spinbox_lineedit")
        assert editor.width() > spin.width() // 2, key  # not collapsed
        assert editor.fontMetrics().horizontalAdvance(spin.text()) < editor.width(), key
        line.setCursorPosition(0)
        assert abs(text_x(spin) - line.cursorRect().center().x()) <= 1, key
        assert text_x(dialog.findChild(QSpinBox)) == text_x(spin), key
