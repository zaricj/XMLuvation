"""ViewModel tests: no widgets are created."""

from __future__ import annotations

import shutil
from pathlib import Path

from xmluvation.domain.models import BuildCriteria, Operator, XPathPreset
from xmluvation.infrastructure.settings_store import SettingsStore
from xmluvation.presentation.viewmodels.csv_tools_vm import CsvToolsViewModel
from xmluvation.presentation.viewmodels.export_vm import ExportViewModel
from xmluvation.presentation.viewmodels.table_viewer_vm import TableViewerViewModel
from xmluvation.presentation.viewmodels.xml_inspector_vm import XmlInspectorViewModel
from xmluvation.presentation.viewmodels.xpath_workspace_vm import XPathWorkspaceViewModel


def _collect(signal) -> list:
    received: list = []
    signal.connect(lambda *args: received.append(args if len(args) != 1 else args[0]))
    return received


# ---------------------------------------------------------------- workspace


def test_add_expression_generates_header_and_recent(settings: SettingsStore) -> None:
    vm = XPathWorkspaceViewModel(settings)
    inputs = _collect(vm.expression_input_changed)
    criteria = BuildCriteria("filter", "", "id", "", Operator.EQUALS)
    assert vm.add_expressions("//filter[@id]/@id", criteria)
    assert vm.expressions == ["//filter[@id]/@id"]
    assert vm.headers_text == "filter @id"
    assert vm.recent == ["//filter[@id]/@id"]
    assert settings.recent_xpath_expressions == ["//filter[@id]/@id"]
    assert inputs[-1] == ""  # input cleared


def test_duplicate_and_invalid_are_rejected(settings: SettingsStore) -> None:
    vm = XPathWorkspaceViewModel(settings)
    notes = _collect(vm.notify)
    vm.add_expressions("//a/@id")
    assert not vm.add_expressions("//a/@id")
    assert notes[-1][1] == "Duplicate XPath Expression"
    assert not vm.add_expressions("//a[")
    assert notes[-1][1] == "XPathSyntaxError"
    assert vm.expressions == ["//a/@id"]


def test_comma_input_is_all_or_nothing(settings: SettingsStore) -> None:
    vm = XPathWorkspaceViewModel(settings)
    assert not vm.add_expressions("//a/@x, //b[")
    assert vm.expressions == []
    assert vm.add_expressions("//a/@x, //b/@y, concat(//c, 'd,e')")
    assert vm.expressions == ["//a/@x", "//b/@y", "concat(//c, 'd,e')"]
    assert vm.headers_text == "a @x, b @y, c 'd e')"
    assert len(vm.headers_text.split(",")) == len(vm.expressions)


def test_header_text_keeps_user_edits_and_never_appends_none(settings: SettingsStore) -> None:
    vm = XPathWorkspaceViewModel(settings)
    vm.set_headers_text("My Header")
    vm.add_expressions("//x/@y")
    vm.add_expressions("//other/x/@y")
    assert vm.headers_text == "My Header, x @y, x @y (2)"
    assert "None" not in vm.headers_text


def test_remove_and_presets(settings: SettingsStore) -> None:
    vm = XPathWorkspaceViewModel(settings)
    logs = _collect(vm.log_appended)
    vm.apply_preset(XPathPreset("P", ("//a/@x", "//b/@y"), ("A", "B")))
    assert vm.headers_text == "A, B"
    vm.remove_at(0)
    assert vm.expressions == ["//b/@y"] and logs[-1] == "Removed item: //a/@x at row 0"
    vm.remove_at(-1)
    assert logs[-1] == "No item selected to delete."
    vm.remove_all()
    assert vm.expressions == [] and vm.headers_text == ""


def test_recent_keeps_ten_newest(settings: SettingsStore) -> None:
    vm = XPathWorkspaceViewModel(settings)
    for i in range(12):
        vm.add_expressions(f"//e{i}/@x")
    assert len(vm.recent) == 10 and vm.recent[0] == "//e11/@x"
    vm.clear_recent()
    assert settings.recent_xpath_expressions == []


def test_build_expression_logs(settings: SettingsStore) -> None:
    vm = XPathWorkspaceViewModel(settings)
    logs = _collect(vm.log_appended)
    assert vm.build_expression(BuildCriteria("a")) == "//a/text()"
    assert logs[-1] == "Built XPath: //a/text()"
    vm.build_expression(BuildCriteria())
    assert logs[-1].startswith("No XPath expression built")


# ---------------------------------------------------------------- export


def test_export_vm_runs_and_reports(qtbot, runner, profiles_dir: Path, tmp_path: Path) -> None:
    vm = ExportViewModel(runner)
    replaced = _collect(vm.log_replaced)
    running = _collect(vm.running_changed)
    out = tmp_path / "out.csv"
    vm.start(str(profiles_dir), str(out), "ID", ["//field/filter/@id"], False)
    qtbot.waitUntil(lambda: running[-1:] == [False], timeout=10000)
    assert running == [True, False]
    assert "CSV export completed successfully!" in replaced[-1]
    assert out.exists()


def test_export_vm_validation_warns_without_starting(runner, tmp_path: Path) -> None:
    vm = ExportViewModel(runner)
    notes = _collect(vm.notify)
    running = _collect(vm.running_changed)
    vm.start(str(tmp_path), "", "A", ["//a"], False)
    assert notes[-1][:2] == ("warning", "Invalid CSV Output")
    assert running == []


def test_folder_count_is_debounced(qtbot, runner, profiles_dir: Path) -> None:
    vm = ExportViewModel(runner)
    counts = _collect(vm.folder_count_changed)
    for partial in ("C", "C:/x", str(profiles_dir)):
        vm.folder_changed(partial)
    qtbot.waitUntil(lambda: bool(counts), timeout=5000)
    assert counts == ["Found 4 XML Files"]


# ---------------------------------------------------------------- inspector


def test_inspector_derives_lists_from_selected_tag(qtbot, runner, xml_dir: Path) -> None:
    vm = XmlInspectorViewModel(runner, lambda: 20)
    tags = _collect(vm.tags_changed)
    attrs = _collect(vm.attributes_changed)
    values = _collect(vm.attribute_values_changed)
    vm.load(str(xml_dir / "simple.xml"))
    qtbot.waitUntil(lambda: bool(tags), timeout=5000)
    vm.select_tag("book")
    vm.select_attribute("book", "lang")
    assert attrs[-1] == ["id", "lang"] and values[-1] == ["de", "en"]
    vm.select_tag("title")
    assert attrs[-1] == []


def test_inspector_reports_parse_errors(qtbot, runner, xml_dir: Path) -> None:
    vm = XmlInspectorViewModel(runner, lambda: 20)
    notes = _collect(vm.notify)
    loading = _collect(vm.loading_changed)
    vm.load(str(xml_dir / "malformed.xml"))
    qtbot.waitUntil(lambda: loading[-1:] == [False], timeout=5000)
    assert notes[-1][0] == "critical"


# ---------------------------------------------------------------- CSV tools / table


def test_cleanup_requires_confirmation(qtbot, runner, profiles_dir: Path, tmp_path: Path) -> None:
    folder = tmp_path / "profiles"
    shutil.copytree(profiles_dir, folder)
    listing = tmp_path / "list.csv"
    listing.write_text("Profile\nProfile_Alpha\n", encoding="utf-8")
    vm = CsvToolsViewModel(runner)
    plans = _collect(vm.cleanup_confirmation_requested)
    running = _collect(vm.cleanup_running_changed)

    vm.plan_cleanup(str(listing), str(folder))
    qtbot.waitUntil(lambda: bool(plans), timeout=5000)
    vm.confirm_cleanup(plans[-1], False)
    assert len(list(folder.glob("*.xml"))) == 4  # nothing deleted when declined

    vm.plan_cleanup(str(listing), str(folder))
    qtbot.waitUntil(lambda: len(plans) == 2, timeout=5000)
    vm.confirm_cleanup(plans[-1], True)
    qtbot.waitUntil(lambda: running[-1:] == [False], timeout=5000)
    assert sorted(p.name for p in folder.iterdir()) == ["Profile_Alpha.xml", "notes.txt"]


def test_csv_headers_are_replaced_not_accumulated(qtbot, runner, tmp_path: Path) -> None:
    csv_file = tmp_path / "h.csv"
    csv_file.write_text("A,B\n1,2\n", encoding="utf-8")
    vm = CsvToolsViewModel(runner)
    headers = _collect(vm.headers_changed)
    vm.csv_path_changed(str(csv_file))
    qtbot.waitUntil(lambda: bool(headers), timeout=5000)
    vm.csv_path_changed(str(csv_file))
    qtbot.waitUntil(lambda: len(headers) == 2, timeout=5000)
    assert headers == [["A", "B"], ["A", "B"]]


def test_table_filter_matches_any_column_case_insensitive(qtbot, runner, tmp_path: Path) -> None:
    csv_file = tmp_path / "t.csv"
    csv_file.write_text("Name,City\nAnna,Berlin\nBob,Köln\nCarl,BERLIN-Mitte\n", encoding="utf-8")
    vm = TableViewerViewModel(runner)
    loaded = _collect(vm.has_table_changed)
    vm.load(str(csv_file))
    qtbot.waitUntil(lambda: bool(loaded), timeout=5000)
    assert vm.model.rowCount() == 3
    vm.set_filter("berlin")
    assert vm.model.rowCount() == 2
    vm.set_filter("bob")
    assert vm.model.rowCount() == 1
    vm.clear()
    assert vm.model.rowCount() == 0 and loaded[-1] is False
