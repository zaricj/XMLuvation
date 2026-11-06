"""Characterisation tests: the new export pipeline must reproduce the legacy CSV output.

Golden files in ``tests/golden`` were produced by the 1.3.5 engine (rows normalised to
file-name order, which is now the guaranteed order).
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from tests.conftest import GOLDEN
from xmluvation.application.cancellation import CancellationToken, NullReporter
from xmluvation.application.export_xpath_csv import make_spec, run_export, summary_text
from xmluvation.domain.errors import InvalidXPathError, OutputFileError, ValidationError


def _spec(folder: Path, out: Path, xpaths: list[str], headers: list[str], group: bool):
    return make_spec(str(folder), xpaths, ", ".join(headers), str(out), group, 4)


@pytest.mark.parametrize("group", [False, True])
@pytest.mark.parametrize(
    "case_name",
    ["all_filters", "anchored_units", "profile_overview", "element_counts", "conf_usage"],
)
def test_export_matches_legacy_golden(
    tmp_path: Path, profiles_dir: Path, golden_cases: dict, case_name: str, group: bool
) -> None:
    case = golden_cases["export"][case_name]
    out = tmp_path / "out.csv"
    result = run_export(
        _spec(profiles_dir, out, case["xpaths"], case["headers"], group),
        NullReporter(),
        CancellationToken(),
    )
    golden = GOLDEN / f"{case_name}__group_{str(group).lower()}.csv"
    assert out.read_text(encoding="utf-8") == golden.read_text(encoding="utf-8")
    assert result.total_files == 4
    assert result.processed_files == 4
    assert not result.cancelled


def test_row_order_is_deterministic(tmp_path: Path, profiles_dir: Path, golden_cases: dict) -> None:
    case = golden_cases["export"]["all_filters"]
    outputs = []
    for i in range(3):
        out = tmp_path / f"o{i}.csv"
        run_export(
            _spec(profiles_dir, out, case["xpaths"], case["headers"], False),
            NullReporter(),
            CancellationToken(),
        )
        outputs.append(out.read_bytes())
    assert outputs[0] == outputs[1] == outputs[2]


def test_unparsable_file_is_reported_not_silent(tmp_path: Path) -> None:
    (tmp_path / "good.xml").write_text("<r><a id='1'/></r>", encoding="utf-8")
    (tmp_path / "empty.xml").write_text("", encoding="utf-8")
    out = tmp_path / "out.csv"
    result = run_export(
        _spec(tmp_path, out, ["//a/@id"], ["ID"], False), NullReporter(), CancellationToken()
    )
    assert [e.file_name for e in result.errors] == ["empty.xml"]
    assert result.rows_written == 1
    assert "Errors encountered: 1" in summary_text(result)


def test_count_function_is_supported(tmp_path: Path) -> None:
    (tmp_path / "a.xml").write_text("<r><a/><a/><a/></r>", encoding="utf-8")
    out = tmp_path / "out.csv"
    result = run_export(
        _spec(tmp_path, out, ["count(//a)"], ["As"], False), NullReporter(), CancellationToken()
    )
    assert out.read_text(encoding="utf-8").splitlines() == ["Filename,As Match Count", "a,3"]
    assert not result.errors


def test_locked_output_raises_instead_of_hanging(tmp_path: Path, profiles_dir: Path) -> None:
    out = tmp_path / "locked.csv"
    out.write_text("", encoding="utf-8")
    os.chmod(out, stat.S_IREAD)
    try:
        with pytest.raises(OutputFileError):
            run_export(
                _spec(profiles_dir, out, ["//field/@name"], ["F"], False),
                NullReporter(),
                CancellationToken(),
            )
    finally:
        os.chmod(out, stat.S_IWRITE | stat.S_IREAD)


def test_cancel_stops_early(tmp_path: Path) -> None:
    for i in range(200):
        (tmp_path / f"f{i:03}.xml").write_text(f"<r><a id='{i}'/></r>", encoding="utf-8")
    token = CancellationToken()

    class CancelAfterFirst(NullReporter):
        def progress(self, done: int, total: int, text: str = "") -> None:
            token.cancel()

    out = tmp_path / "out.csv"
    result = run_export(_spec(tmp_path, out, ["//a/@id"], ["ID"], False), CancelAfterFirst(), token)
    assert result.cancelled
    assert result.processed_files < 200
    assert "aborted" in summary_text(result)


@pytest.mark.parametrize(
    ("xpaths", "headers", "output", "title"),
    [
        (["//a/@id"], "ID", "", "Invalid CSV Output"),
        (["//a/@id"], "ID", "out.txt", "CSV Output Path is Invalid"),
        ([], "", "out.csv", "No XPath Expressions"),
        (["//a/@id", "//b/@id"], "ID", "out.csv", "Header/XPath Length Mismatch"),
        (["//a/@id", "//b/@id"], "ID, ID", "out.csv", "Duplicate CSV Headers"),
    ],
)
def test_validation(
    tmp_path: Path, xpaths: list[str], headers: str, output: str, title: str
) -> None:
    out = str(tmp_path / output) if output else ""
    with pytest.raises(ValidationError) as info:
        make_spec(str(tmp_path), xpaths, headers, out, False)
    assert info.value.title == title


def test_validation_rejects_missing_folder(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="valid XML folder"):
        make_spec(str(tmp_path / "missing"), ["//a"], "A", str(tmp_path / "o.csv"), False)


def test_validation_rejects_invalid_xpath(tmp_path: Path) -> None:
    with pytest.raises(InvalidXPathError):
        make_spec(str(tmp_path), ["//a[@"], "A", str(tmp_path / "o.csv"), False)
