"""Windowed launcher (double-click on Windows, and Nuitka's build entry point).

Equivalent to ``python -m xmluvation``.
"""

from xmluvation.app.bootstrap import main

if __name__ == "__main__":
    raise SystemExit(main())
