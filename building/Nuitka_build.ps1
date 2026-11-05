uv run python -m nuitka `
    --standalone `
    --enable-plugin=pyside6 `
    --windows-console-mode=disable `
    --lto=yes `
    --assume-yes-for-downloads `
    --output-dir=build `
    .\src\main.pyw