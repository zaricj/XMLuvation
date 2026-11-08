from __future__ import annotations

from pathlib import Path

import pytest

from xmluvation.application.xml_inspection import count_xml_files
from xmluvation.domain.errors import InvalidXPathError, XmlParseError
from xmluvation.infrastructure.xml_engine import inspect_file, validate_xpath


def test_inspect_builds_per_tag_index(xml_dir: Path) -> None:
    index = inspect_file(xml_dir / "simple.xml", 10_000_000)
    assert index.root_tag == "library"
    assert index.encoding == "UTF-8"
    assert "book" in index.tags and "b" in index.tags
    assert index.tag_to_attributes["book"] == ("id", "lang")
    assert index.tag_attr_to_values[("book", "lang")] == ("de", "en")
    assert index.tag_to_values["title"] == ("Größe", "Mixed", "XML Basics")
    assert "empty" not in index.tag_to_values
    assert not index.preview_truncated
    assert "<library>" in index.preview_text
    assert index.element_count == 12  # 11 elements plus the comment, as in 1.3.x


def test_streaming_mode_gives_same_index_and_truncated_preview(xml_dir: Path) -> None:
    full = inspect_file(xml_dir / "simple.xml", 10_000_000)
    streamed = inspect_file(xml_dir / "simple.xml", 100)
    assert streamed.preview_truncated
    assert len(streamed.preview_text.encode()) <= 100
    for attr in ("root_tag", "tags", "tag_to_values", "tag_to_attributes", "tag_attr_to_values"):
        assert getattr(streamed, attr) == getattr(full, attr), attr
    assert streamed.element_count == full.element_count


def test_namespaced_tags_use_clark_notation(xml_dir: Path) -> None:
    index = inspect_file(xml_dir / "default_ns.xml", 10_000_000)
    assert index.namespaces == ("urn:books", "urn:extra")
    assert "{urn:books}book" in index.tags


def test_malformed_raises_parse_error(xml_dir: Path) -> None:
    with pytest.raises(XmlParseError):
        inspect_file(xml_dir / "malformed.xml", 10_000_000)


def test_external_entities_are_not_resolved(tmp_path: Path) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("TOPSECRET", encoding="utf-8")
    doc = tmp_path / "xxe.xml"
    doc.write_text(
        f'<!DOCTYPE r [<!ENTITY x SYSTEM "{secret.as_uri()}">]><r>&x;</r>', encoding="utf-8"
    )
    try:
        index = inspect_file(doc, 10_000_000)
    except XmlParseError:
        return
    assert "TOPSECRET" not in index.preview_text


def test_validate_xpath() -> None:
    validate_xpath("//a[@b='c']")
    with pytest.raises(InvalidXPathError):
        validate_xpath("//a[")


def test_count_xml_files_is_case_insensitive(tmp_path: Path) -> None:
    (tmp_path / "a.xml").touch()
    (tmp_path / "b.XML").touch()
    (tmp_path / "c.txt").touch()
    assert count_xml_files(str(tmp_path)) == 2
    assert count_xml_files(str(tmp_path / "nope")) is None
    assert count_xml_files("") is None
