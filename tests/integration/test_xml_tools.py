from __future__ import annotations

import csv
from pathlib import Path

import pytest

from xmluvation.application.cancellation import CancellationToken, NullReporter
from xmluvation.application.xml_tools import (
    compare_summary,
    compare_xml,
    validate_against_schema,
    validation_summary,
)
from xmluvation.domain.errors import Cancelled, ValidationError, XmlParseError
from xmluvation.domain.xml_checks import Change, NodeKind
from xmluvation.infrastructure.xml_diff import diff_files

SCHEMA = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root"><xs:complexType><xs:sequence>
    <xs:element name="n" type="xs:int" maxOccurs="unbounded"/>
  </xs:sequence></xs:complexType></xs:element>
</xs:schema>"""


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _validate(schema: Path, target: Path):
    return validate_against_schema(str(schema), str(target), NullReporter(), CancellationToken())


# ---------------------------------------------------------------- validation


def test_folder_validation_reports_schema_errors_and_broken_files(tmp_path: Path) -> None:
    schema = _write(tmp_path / "profile.xsd", SCHEMA)
    folder = tmp_path / "xml"
    folder.mkdir()
    _write(folder / "ok.xml", "<root><n>1</n></root>")
    _write(folder / "bad.xml", "<root><n>x</n><m/></root>")
    _write(folder / "broken.xml", "<root><n>1</root>")
    _write(folder / "ignored.txt", "<root/>")

    result = _validate(schema, folder)

    assert result.files == 3 and result.valid_files == 1
    assert result.invalid_files == ["bad.xml", "broken.xml"]
    assert result.report == folder / "profile_validation.csv"
    rows = _rows(result.report)
    assert [(r["File"], r["Level"], r["Path"]) for r in rows] == [
        ("bad.xml", "error", "/root/n"),
        ("bad.xml", "error", "/root/m"),
        ("broken.xml", "not well-formed", ""),
    ]
    assert "2 of 3 file(s) are not valid" in validation_summary(result)[0]


def test_single_valid_file_writes_no_report(tmp_path: Path) -> None:
    schema = _write(tmp_path / "s.xsd", SCHEMA)
    result = _validate(schema, _write(tmp_path / "a.xml", "<root><n>7</n></root>"))
    assert result.all_valid and result.report is None
    assert validation_summary(result) == ["Valid: the file is valid against s.xsd."]


def test_schema_with_relative_include_is_resolved(tmp_path: Path) -> None:
    _write(
        tmp_path / "types.xsd",
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">'
        '<xs:simpleType name="code"><xs:restriction base="xs:string">'
        '<xs:length value="2"/></xs:restriction></xs:simpleType></xs:schema>',
    )
    schema = _write(
        tmp_path / "main.xsd",
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">'
        '<xs:include schemaLocation="types.xsd"/>'
        '<xs:element name="c" type="code"/></xs:schema>',
    )
    assert _validate(schema, _write(tmp_path / "ok.xml", "<c>DE</c>")).all_valid
    assert not _validate(schema, _write(tmp_path / "bad.xml", "<c>DEU</c>")).all_valid


def test_invalid_schema_and_missing_inputs(tmp_path: Path) -> None:
    xml = _write(tmp_path / "a.xml", "<root/>")
    with pytest.raises(XmlParseError, match="not a valid XSD"):
        _validate(_write(tmp_path / "x.xsd", "<root/>"), xml)
    with pytest.raises(ValidationError, match="XSD schema"):
        _validate(tmp_path / "missing.xsd", xml)
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ValidationError, match="no .xml files"):
        _validate(_write(tmp_path / "s.xsd", SCHEMA), empty)


# ---------------------------------------------------------------- compare


def _diff(tmp_path: Path, old: str, new: str, **kwargs):
    return diff_files(
        _write(tmp_path / "old.xml", old), _write(tmp_path / "new.xml", new), **kwargs
    )


def test_inserted_sibling_does_not_shift_the_others(tmp_path: Path) -> None:
    items = "".join(f"<item id='{i}'>v{i}</item>" for i in range(50))
    inserted = items.replace("<item id='25'>", "<item id='new'>x</item><item id='25'>")
    outcome = _diff(tmp_path, f"<r>{items}</r>", f"<r>{inserted}</r>")
    assert [(d.change, d.kind, d.path) for d in outcome.differences] == [
        (Change.ADDED, NodeKind.ELEMENT, "/r/item[26]")
    ]


def test_attribute_text_and_element_changes_in_document_order(tmp_path: Path) -> None:
    outcome = _diff(
        tmp_path,
        '<p:r xmlns:p="urn:x" a="1"><s t="1">x</s><old/></p:r>',
        '<p:r xmlns:p="urn:x" a="2" b="3">\n<s t="1">y</s><new/></p:r>',
    )
    assert [(d.change, d.kind, d.path, d.old_value, d.new_value) for d in outcome.differences] == [
        (Change.CHANGED, NodeKind.ATTRIBUTE, "/p:r/@a", "1", "2"),
        (Change.ADDED, NodeKind.ATTRIBUTE, "/p:r/@b", "", "3"),
        (Change.CHANGED, NodeKind.TEXT, "/p:r/s", "x", "y"),
        (Change.REMOVED, NodeKind.ELEMENT, "/p:r/old", "<old>", ""),
        (Change.ADDED, NodeKind.ELEMENT, "/p:r/new", "", "<new>"),
    ]
    assert outcome.differences[2].new_line == 2  # line numbers come from the files


def test_whitespace_option_and_ignored_comments(tmp_path: Path) -> None:
    old = "<r><a>x  y</a><!-- note --><b/></r>"
    new = "<r>\n  <a>x y</a>\n  <b/>\n</r>"
    assert _diff(tmp_path, old, new, ignore_whitespace=True).differences == []
    strict = _diff(tmp_path, old, new, ignore_whitespace=False).differences
    assert {d.kind for d in strict} == {NodeKind.TEXT, NodeKind.TAIL}


def test_different_root_and_limit(tmp_path: Path) -> None:
    outcome = _diff(tmp_path, "<a/>", "<b/>")
    assert [(d.change, d.path) for d in outcome.differences] == [
        (Change.REMOVED, "/a"),
        (Change.ADDED, "/b"),
    ]
    many = _diff(
        tmp_path,
        "<r>" + "<x/>" * 20 + "</r>",
        "<r>" + "<y/>" * 20 + "</r>",
        limit=5,
    )
    assert many.truncated and len(many.differences) == 5


def test_large_lists_of_identical_siblings_stay_fast(tmp_path: Path) -> None:
    old = "<r>" + "<x>1</x>" * 3000 + "</r>"
    new = "<r>" + "<x>1</x>" * 1500 + "<x>2</x>" + "<x>1</x>" * 1499 + "</r>"
    outcome = _diff(tmp_path, old, new)
    assert [(d.change, d.kind) for d in outcome.differences] == [(Change.CHANGED, NodeKind.TEXT)]


def test_compare_xml_writes_report_and_summary(tmp_path: Path) -> None:
    old = _write(tmp_path / "v1.xml", "<r><a>1</a></r>")
    new = _write(tmp_path / "v2.xml", "<r><a>2</a><b/></r>")
    result = compare_xml(str(old), str(new), True, NullReporter(), CancellationToken())
    assert result.report == tmp_path / "v2_vs_v1_xmldiff.csv"
    rows = _rows(result.report)
    assert [(r["Change"], r["Node"], r["Path"], r["Old value"], r["New value"]) for r in rows] == [
        ("changed", "text", "/r/a", "1", "2"),
        ("added", "element", "/r/b", "", "<b>"),
    ]
    assert compare_summary(result)[0] == "2 difference(s): 1 added, 1 changed."

    same = compare_xml(str(old), str(old), True, NullReporter(), CancellationToken())
    assert same.identical and same.report is None


def test_compare_rejects_broken_xml_and_can_be_cancelled(tmp_path: Path) -> None:
    good = _write(tmp_path / "good.xml", "<r/>")
    broken = _write(tmp_path / "broken.xml", "<r>")
    with pytest.raises(XmlParseError, match="not well-formed"):
        compare_xml(str(good), str(broken), True, NullReporter(), CancellationToken())
    token = CancellationToken()
    token.cancel()
    with pytest.raises(Cancelled):
        compare_xml(str(good), str(good), True, NullReporter(), token)
