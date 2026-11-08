# XMLuvation architecture

## Layers and dependency direction

```text
presentation ──► application ──► domain
     │                │            ▲
     │                └──► infrastructure
     └── app/bootstrap.py (composition root) wires everything
```

| Layer | Package | May import | Must not import |
|---|---|---|---|
| Domain | `xmluvation.domain` | stdlib only | Qt, lxml, pandas, any other layer |
| Application (use cases) | `xmluvation.application` | domain, infrastructure | Qt, presentation |
| Infrastructure | `xmluvation.infrastructure` | domain, lxml, pandas, `QtCore.QSettings` | QtWidgets/QtGui, application, presentation |
| ViewModels | `xmluvation.presentation.viewmodels` | application, domain, `QtCore` | `QtWidgets`, `QtGui`, views, low-level infrastructure |
| Views | `xmluvation.presentation.views` | ViewModels, generated UI, Qt widgets | business rules, file I/O |

`tests/unit/test_architecture.py` enforces these rules on every test run.

Use cases call infrastructure functions directly instead of going through abstract
"ports": this is a desktop application with one XML engine and one storage format, so
the extra indirection would add code without adding testability (infrastructure is
tested against real files in temporary directories).

## Packages

```text
src/
  main.pyw                     windowed launcher / Nuitka entry point
  config/config.json           custom paths and XPath presets (user data)
  xmluvation/
    __main__.py                python -m xmluvation
    app/                       bootstrap (composition root, logging, excepthook), paths
    domain/                    models, errors, XPath building/escaping, header rules, row assembly
    application/               export, XML inspection, CSV tools, profile cleanup, presets
    infrastructure/            lxml engine, CSV I/O, Excel/HTML/JSON/MD writers, config + settings stores
    presentation/
      tasks.py                 TaskRunner: background work with cancel/progress/shutdown
      themes.py                theme registry (style sheets are compiled into the QRC)
      viewmodels/              UI state and commands (QtCore only)
      models/                  DataFrame table model + filter proxy
      views/                   main window, managers, exit dialog
      generated/               pyside6-uic / pyside6-rcc output - do not edit
    resources/                 .ui, .qrc, styles, icons, images, gif
tests/
  unit/ integration/ ui/       pytest (+ pytest-qt, offscreen)
  golden/                      CSV output captured from the 1.3.5 engine
  perf/bench_export.py         manual benchmark on real data
tools/regen_ui.py              regenerate presentation/generated after editing .ui/.qrc
```

## Threading

* All long-running work goes through `TaskRunner.start(fn, on_success=..., ...)`. `fn` runs
  on a `QThreadPool` thread and gets a `TaskContext` (progress, messages, cancellation
  token). Callbacks are delivered on the GUI thread through queued signals of a QObject
  owned by the runner. Worker code never touches widgets.
* The export use case runs a bounded `ThreadPoolExecutor` (at most `2 × workers` files in
  flight) and writes rows itself, in file-name order. There is no writer thread or queue.
* Closing the window cancels all tasks and waits up to 5 s (`TaskRunner.shutdown`).

## XML handling

* Parsers never use the network or load DTDs. Only internal entities are expanded.
* Export uses `recover=True, huge_tree=True` (as in 1.3.x). Unparsable files are listed in
  the export summary instead of being skipped silently.
* XPaths are compiled once per worker thread with `smart_strings=False`.
* "Read XML" pretty-prints files up to the **XML Preview Size Limit** (Settings menu,
  default 20 MB). Larger files are indexed with `iterparse` (low memory) and only the
  beginning of the raw text is shown. Measured on a 22 MB file: about 440 MB peak working
  set for the full parse vs. about 49 MB streaming.
* XPath 1.0 only (lxml). Namespaced documents are not handled specially yet: tags appear
  in Clark notation `{uri}name` and expressions are evaluated without a namespace map.

## Development

```powershell
uv sync                                   # Python 3.15, runtime + dev dependencies
uv run python -m xmluvation               # run the app
$env:QT_QPA_PLATFORM="offscreen"; uv run pytest -q
uv run ruff check src tests tools; uv run ruff format --check src tests tools
uv run mypy                               # strict, domain + application
uv run python tools/regen_ui.py           # after editing .ui or .qrc files
```
