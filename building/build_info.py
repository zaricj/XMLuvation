"""Print build metadata as JSON for Nuitka_build.ps1 (keeps quoting out of PowerShell).

Reads the app version from ``src/xmluvation/__init__.py`` and the requirements from
``pyproject.toml``: runtime dependencies plus the build/test tools from the ``dev`` group.
"""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_TOOLS = ("nuitka", "pytest", "pytest-qt")


def _name(requirement: str) -> str:
    return re.split(r"[<>=!~;\[ ]", requirement, maxsplit=1)[0].strip().lower()


def main() -> int:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    init = (ROOT / "src" / "xmluvation" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init)
    if match is None:
        print("No __version__ in src/xmluvation/__init__.py", file=sys.stderr)
        return 1
    version = match.group(1)
    numbers = [int(n) for n in re.findall(r"\d+", version)[:4]]
    dev = project.get("dependency-groups", {}).get("dev", [])
    info = {
        "version": version,
        "windows_version": ".".join(str(n) for n in (numbers + [0, 0, 0, 0])[:4]),
        "requires_python": project["project"].get("requires-python", ""),
        "python": "{}.{}.{}".format(*sys.version_info[:3]),
        "requirements": [
            *project["project"]["dependencies"],
            *(r for r in dev if _name(r) in BUILD_TOOLS),
        ],
    }
    print(json.dumps(info))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
