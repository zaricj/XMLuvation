from __future__ import annotations

from pathlib import Path

import pytest

from xmluvation.application.cancellation import CancellationToken, NullReporter
from xmluvation.application.profile_cleanup import apply_cleanup, describe_plan, plan_cleanup
from xmluvation.domain.errors import ValidationError


@pytest.fixture
def export_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "export"
    folder.mkdir()
    for name in ("Keep.xml", "keep_case.XML", "Orphan.xml", "Prof_FB.xml", "readme.txt"):
        (folder / name).write_text("<r/>", encoding="utf-8")
    return folder


def test_plan_and_apply_only_touch_unlisted_xml(tmp_path: Path, export_folder: Path) -> None:
    csv_file = tmp_path / "profiles.csv"
    csv_file.write_text("Profile\nKeep\nKEEP_CASE\nProf_*FB*\n0042\n", encoding="utf-8")

    plan = plan_cleanup(str(csv_file), str(export_folder))
    assert [p.name for p in plan.delete] == ["Orphan.xml"]
    assert plan.files_in_folder == 4  # readme.txt is never considered
    assert plan.case_mismatches == ("keep_case.XML",)
    assert "Files to keep: 3, Files to delete: 1" in describe_plan(plan)

    result = apply_cleanup(plan, NullReporter(), CancellationToken())
    assert result.deleted == ["Orphan.xml"]
    remaining = sorted(p.name for p in export_folder.iterdir())
    assert remaining == ["Keep.xml", "Prof_FB.xml", "keep_case.XML", "readme.txt"]


def test_empty_csv_refuses_to_delete_everything(tmp_path: Path, export_folder: Path) -> None:
    csv_file = tmp_path / "profiles.csv"
    csv_file.write_text("Profile\n", encoding="utf-8")
    with pytest.raises(ValidationError, match="Nothing was changed"):
        plan_cleanup(str(csv_file), str(export_folder))
    assert len(list(export_folder.iterdir())) == 5


@pytest.mark.parametrize(("csv_text", "folder_text"), [("", "x"), ("x", "")])
def test_missing_inputs(csv_text: str, folder_text: str) -> None:
    with pytest.raises(ValidationError):
        plan_cleanup(csv_text, folder_text)
