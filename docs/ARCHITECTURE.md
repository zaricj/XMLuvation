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
* The export use case runs a bounded `ThreadPoolExecutor` and writes rows itself, in
  file-name order. There is no writer thread or queue. Files in flight are limited to
  `2 × workers` **and** to `INFLIGHT_BYTES_BUDGET` (256 MiB) of source XML, so a
  multi-gigabyte file is parsed alone instead of next to 31 others.
* Table loading and filtering, and XML inspection, take the task's cancellation token.
* Closing the window cancels all tasks and waits up to 5 s (`TaskRunner.shutdown`).

## XML handling

* Parsers never use the network or load DTDs. Only internal entities are expanded.
* Export uses `recover=True, huge_tree=True` (as in 1.3.x). Unparsable files are listed in
  the export summary instead of being skipped silently.
* XPaths are compiled once per worker thread with `smart_strings=False`.
* Export parses each file completely: arbitrary XPath 1.0 (ancestors, siblings,
  `count()`, predicates) needs the whole tree, so `iterparse` is not an option there.
  The tree is released before rows are assembled, and `gc.collect()` runs at the end of
  every export, after failed or cancelled inspections and table loads, and when a table
  is closed.
* "Read XML" pretty-prints files up to the **XML Preview Size Limit** (Settings menu,
  default 20 MB). Larger files are indexed with `iterparse` (low memory) and only the
  beginning of the raw text is shown. Measured on a 22 MB file: about 440 MB peak working
  set for the full parse vs. about 49 MB streaming. Streaming uses `huge_tree=True`, checks
  for cancellation every 10,000 events, and keeps at most `MAX_DISTINCT_VALUES` (1,000)
  values per tag and attribute for the builder's comboboxes (`XmlIndex.values_capped`).

## Table viewer

* `presentation/models/table_model.py` holds the CSV as one numpy array of `str` per
  column (`TableData`, built on the worker thread). The CSV is read as text in 100,000-row
  chunks, which are collected in a list and concatenated once.
* `TableModel` exposes rows to the view in batches of 2,000 (`canFetchMore`/`fetchMore`).
  Sorting (stable, as text) and filtering (any column, case-insensitive, literal) are
  vectorized and produce a row permutation; there is no `QSortFilterProxyModel`.
  Filtering runs on a worker thread, debounced by 200 ms, and superseded results are
  dropped.

## UI structure and themes

* The main window is a sidebar (`list_widget_navigation`) driving `stacked_pages`
  (Extract, XML tools, CSV tools, Table viewer), with a bottom `dock_output` holding one
  log per tool page. Ctrl+1–4 switch pages; Ctrl+J toggles the output dock.
* Sections are `QFrame` cards. Widgets carry a dynamic `role` property (`card`,
  `card-title`, `hint`, `field-label`, `primary`, `accent`, `danger`, `flat`, `nav`, …)
  that the style sheets select on, so the `.ui` files contain no inline styles or fonts.
* CSV tools: Convert turns a CSV file into Excel, HTML, JSON or Markdown
  (`infrastructure/tabular_export.py`) and those back into CSV
  (`infrastructure/tabular_import.py`: first worksheet via openpyxl, first `<table>`,
  JSON records/rows/columns, first pipe table; every cell read as text). A CSV result is
  written like the reports (UTF-8 with BOM, CRLF, comma unless a delimiter is set) and
  never overwrites an existing file. Split (`application/csv_split.py`), Compare
  (`application/csv_compare.py`), Columns (`save_column_edits` in `csv_tools.py`),
  Profile clean-up and Hex → decimal. Split and Columns stream rows through
  `csv_io.csv_rows` and keep each cell's exact text plus the delimiter, encoding and BOM.
  No tool overwrites an existing file unless asked to (`application/output_paths.py`);
  Split removes its new folder if it fails or is cancelled.
  `presentation/views/csv_transforms_view.py` binds Split, Compare and Columns;
  `HeaderReader` loads a file's column names in the background.
* CSV Compare (`infrastructure/csv_diff.py`, `application/csv_compare.py`) works like
  XML Compare, with rows in place of child elements: every data row is fingerprinted
  (its values in the columns both files have), rows are aligned by fingerprint with the
  patience diff of `domain/text_diff.py` (`patience_opcodes`; a CSV file is one long
  list, so plain `difflib` would not scale), and the rows of each differing region are
  paired by the key column, or by position when "no key" is chosen. With a key, rows
  paired out of order or across regions are reported as *moved*. Only each row's text
  (re-written as one CSV record) and fingerprint are kept; paired rows are parsed again,
  so memory stays near the files' size (300,000 rows / 12.6 MB: about 1.5 s). The result
  is shown in the same `DiffView` as XML Compare: one record per line, header first,
  numbered like spreadsheet rows, changed cells marked, `↵` for line breaks inside a
  cell. Files over 16 MB are compared and reported but not shown side by side. The
  report (`<new>_vs_<old>_diff.csv`, only written when the files differ) is opened in
  the default application; the table viewer is only for reading tabular files.
* XML tools (`application/xml_tools.py`, bound by `presentation/views/xml_tools_view.py`):
  * Validate checks one file, or every `*.xml` directly in a folder, against an XSD 1.0
    schema (`infrastructure/xml_validation.py`, libxml2). Local `xs:include`/`xs:import`
    files are resolved relative to the schema; the network is never used. The problems
    are listed in the card (`file:line:column: level: message`, up to 5,000), and up to
    1,000 problems per file go to `<schema>_validation.csv` next to the XML files.
  * Compare (`infrastructure/xml_diff.py`) fingerprints every subtree bottom-up, aligns
    child lists by fingerprint and then by tag (`difflib`, with common start/end trimmed
    and positional pairing for very long sibling lists), and lists added, removed and
    changed elements, attributes and text with a readable XPath and line numbers in
    `<new>_vs_<old>_xmldiff.csv`. Comments and processing instructions are ignored;
    whitespace in text is normalized unless the option is turned off. The report stops
    at 100,000 differences; "Open" shows it in the default application.
  * Compare also shows both files side by side (`presentation/widgets/diff_view.py`,
    a promoted widget): old left, new right, removed/changed lines red, added/changed
    lines green, changed characters marked, filler rows keep both sides aligned, an
    overview strip and F7 / Shift+F7 navigate. The line diff is `domain/text_diff.py`: a
    patience diff (anchors on lines unique to both sides, recursing into the gaps, plain
    `difflib` only for small gaps without such lines), because `difflib` alone is
    quadratic on XML's repeated closing tags. The files are decoded by BOM or XML
    declaration (`xml_diff.read_text`); files over 16 MB are not shown side by side.
    Backgrounds are painted per visible row, so large files stay responsive. Colors
    come from `qproperty-*` in the theme, like `BusyBar`.
* The CSV and XML tools pages are segmented `QTabWidget`s with one card per tool. Each tool's
  action row holds a `BusyBar` (`presentation/widgets/busy_bar.py`, a promoted widget
  in the `.ui`): an indeterminate striped bar that keeps its place in the layout, paints
  nothing while idle, and takes its colors from `qproperty-trackColor`/`stripeColor`.
* `dark_theme.qss` and `light_theme.qss` share one structure and differ only in color
  values; change both together. The themes under `styles/other/` predate the roles and
  only style generic widgets.
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
.\building\Nuitka_build.ps1               # standalone build -> dist\XMLuvation-<version>\ (-OneFile, -Zip, -CheckOnly)
```
