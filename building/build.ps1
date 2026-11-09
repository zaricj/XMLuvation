# Standalone Nuitka build with Zig (no Visual Studio). Output: build\main.dist\XMLuvation.exe
Set-Location (Split-Path -Parent $PSScriptRoot)
uv run --isolated --no-dev --with nuitka python -m nuitka src\main.pyw `
    --standalone --zig --assume-yes-for-downloads --output-dir=build `
    --output-filename=XMLuvation.exe --windows-console-mode=disable `
    --windows-icon-from-ico=src\xmluvation\resources\icons\xml_256px.ico `
    --enable-plugin=pyside6 --noinclude-qt-translations `
    --include-package=xlsxwriter --include-module=tabulate `
    --include-data-files=src\config\config.json=config\config.json
