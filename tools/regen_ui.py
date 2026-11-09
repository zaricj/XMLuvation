"""Regenerate Python code from Qt Designer ``.ui`` files and the ``.qrc`` resource file.

Run after editing anything in ``src/xmluvation/resources/ui`` or the ``.qrc`` file::

    uv run python tools/regen_ui.py

Generated modules go to ``src/xmluvation/presentation/generated`` and use relative
imports for the resource module (``--from-imports``), so no post-processing is needed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "src" / "xmluvation"
UI_DIR = PACKAGE / "resources" / "ui"
QRC_FILE = PACKAGE / "resources" / "qrc" / "xmluvation_resources.qrc"
OUT_DIR = PACKAGE / "presentation" / "generated"

# .ui file name -> generated module name
UI_FILES = {
    "XMLuvation.ui": "main_window_ui.py",
    "CustomPathsManager.ui": "custom_paths_manager_ui.py",
    "PreBuiltXPathsManager.ui": "prebuilt_xpaths_manager_ui.py",
    "ExitDialogBox.ui": "exit_dialog_ui.py",
}


def _tool(name: str) -> str:
    scripts = Path(sys.executable).parent
    candidate = scripts / (name + (".exe" if sys.platform == "win32" else ""))
    return str(candidate) if candidate.exists() else name


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "__init__.py").touch()
    subprocess.run(
        [_tool("pyside6-rcc"), str(QRC_FILE), "-o", str(OUT_DIR / "xmluvation_resources_rc.py")],
        check=True,
    )
    for ui_name, module_name in UI_FILES.items():
        subprocess.run(
            [
                _tool("pyside6-uic"),
                "--from-imports",
                str(UI_DIR / ui_name),
                "-o",
                str(OUT_DIR / module_name),
            ],
            check=True,
        )
        print(f"generated {module_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
