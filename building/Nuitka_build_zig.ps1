# Standalone Nuitka build with Zig (no Visual Studio). Output: dist\XMLuvation.exe
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    uv run --isolated --no-dev --with nuitka python -m nuitka src\main.pyw `
        --standalone --zig --assume-yes-for-downloads --output-dir=build `
        --output-filename=XMLuvation.exe --windows-console-mode=disable `
        --windows-icon-from-ico=src\xmluvation\resources\icons\xml_256px.ico `
        --enable-plugin=pyside6 --noinclude-qt-translations `
        --include-package=xlsxwriter --include-module=tabulate --include-package=openpyxl `
        --include-data-files=src\config\config.json=config\config.json
    if ($LASTEXITCODE -ne 0) { throw "Nuitka failed with exit code $LASTEXITCODE." }

    # Move build\main.dist to dist\ and remove Nuitka's intermediate output.
    if (Test-Path dist) { Remove-Item dist -Recurse -Force }
    Move-Item build\main.dist dist
    Remove-Item build\main.build -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Done: $(Resolve-Path dist\XMLuvation.exe)"
} finally {
    Pop-Location
}