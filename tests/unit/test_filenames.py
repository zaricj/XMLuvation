from __future__ import annotations

import pytest

from xmluvation.domain.filenames import profile_file_name, sanitize_filename_for_windows


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Profile_*FB*.xml", "Profile_FB.xml"),  # '*' is a forbidden character
        ("Profile_*FB*", "Profile_FB"),
        ('a<b>c:"d|e?f*g', "abcdefg"),
        ("Normal.xml", "Normal.xml"),
    ],
)
def test_sanitize(name: str, expected: str) -> None:
    assert sanitize_filename_for_windows(name) == expected


def test_profile_file_name_adds_extension_once() -> None:
    assert profile_file_name(" P1 ") == "P1.xml"
    assert profile_file_name("P2.XML") == "P2.XML"
