"""Smoke and regression tests for the main window (offscreen)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QPlainTextEdit

from xmluvation.infrastructure.settings_store import SettingsStore


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


def test_compare_report_opens_in_table_viewer(qtbot, window, tmp_path: Path) -> None:
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    old.write_text("K,V\n1,a\n2,b\n", encoding="utf-8")
    new.write_text("K,V\n1,a\n2,c\n3,d\n", encoding="utf-8")
    ui = window.ui
    ui.line_edit_compare_old_csv_file_path.setText(str(old))
    ui.line_edit_compare_new_csv_file_path.setText(str(new))
    qtbot.waitUntil(lambda: ui.combobox_compare_key.count() == 2, timeout=5000)
    ui.button_compare_start.click()
    qtbot.waitUntil(lambda: not ui.frame_compare_result.isHidden(), timeout=5000)
    assert "1 added, 1 changed rows (1 cells)" in ui.label_compare_summary.text()
    ui.button_compare_view_report.click()
    qtbot.waitUntil(lambda: window.vms.table.model.rowCount() == 2, timeout=5000)
    assert ui.stacked_pages.currentIndex() == 2
