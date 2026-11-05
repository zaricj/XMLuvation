"""Enforce the dependency direction between layers by inspecting imports."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2] / "src" / "xmluvation"


def _imports(path: Path) -> set[str]:
    """Absolute module names imported by ``path`` (relative imports resolved)."""
    # The package containing this module: for a/b/c.py and a/b/__init__.py it is "a.b".
    package = list(path.relative_to(PACKAGE.parent).parent.parts)
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package[: len(package) - (node.level - 1)]
                names.add(".".join(base + ([node.module] if node.module else [])))
            else:
                names.add(node.module or "")
    return names


def _matches(name: str, prefixes: tuple[str, ...]) -> bool:
    return any(name == p or name.startswith(p + ".") for p in prefixes)


def _files(layer: str) -> list[Path]:
    return sorted((PACKAGE / layer).rglob("*.py"))


RULES = {
    # layer: forbidden import prefixes
    "domain": (
        "PySide6",
        "lxml",
        "pandas",
        "xmluvation.application",
        "xmluvation.infrastructure",
        "xmluvation.presentation",
        "xmluvation.app",
    ),
    "application": ("PySide6", "xmluvation.presentation", "xmluvation.app"),
    "infrastructure": (
        "PySide6.QtWidgets",
        "PySide6.QtGui",
        "xmluvation.application",
        "xmluvation.presentation",
        "xmluvation.app",
    ),
    "presentation/viewmodels": (
        "PySide6.QtWidgets",
        "PySide6.QtGui",
        "xmluvation.presentation.views",
        "xmluvation.infrastructure.xml_engine",
        "xmluvation.infrastructure.csv_io",
        "xmluvation.infrastructure.config_store",
    ),
}


@pytest.mark.parametrize("layer", list(RULES))
def test_layer_dependencies(layer: str) -> None:
    violations = [
        f"{path.relative_to(PACKAGE)} imports {name}"
        for path in _files(layer)
        for name in _imports(path)
        if _matches(name, RULES[layer])
    ]
    assert not violations, "\n".join(violations)


def test_rule_detection_works() -> None:
    """Guard against the scanner silently resolving nothing."""
    imports = _imports(PACKAGE / "presentation" / "viewmodels" / "export_vm.py")
    assert "xmluvation.application.export_xpath_csv" in imports
    assert "PySide6.QtCore" in imports
