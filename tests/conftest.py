from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

TESTS = Path(__file__).parent
FIXTURES = TESTS / "fixtures"
GOLDEN = TESTS / "golden"


@pytest.fixture
def profiles_dir() -> Path:
    return FIXTURES / "profiles"


@pytest.fixture
def xml_dir() -> Path:
    return FIXTURES / "xml"


@pytest.fixture(scope="session")
def golden_cases() -> dict:
    return json.loads((GOLDEN / "cases.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def builder_golden() -> dict:
    return json.loads((GOLDEN / "builder.json").read_text(encoding="utf-8"))
