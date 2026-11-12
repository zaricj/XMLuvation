# Changelog

All notable changes to XMLuvation are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [1.5.0] - 2026-11-10

This release adds an XML tools page, rebuilds the CSV compare around a side-by-side
view, and turns the table viewer into a tool for working with tabular files.

### Added

#### XML tools page

A new page in the sidebar (Ctrl+2) with two tools:

- **Validate**: checks one XML file, or every `.xml` file in a folder, against an XSD
  schema. Problems are listed in the tool as `file:line:column: level: message`, and
  saved to `<schema>_validation.csv` next to the XML files. Schemas that include or
  import other local schema files are supported; the network is never used.
- **Compare**: compares two XML documents element by element (elements, attributes and
  text) and lists every added, removed and changed node with a readable path and the
  line numbers in both files. Whitespace differences in text can be ignored; comments
  and processing instructions are not compared.
- **Side-by-side view** for Compare: the old file on the left, the new file on the
  right, removed and changed lines in red, added and changed lines in green, with the
  changed characters marked. F7 and Shift+F7 jump to the next and previous change.
  Files larger than 16 MB are compared and reported, but not shown side by side.

#### Convert

- Excel (`.xlsx`, `.xlsm`), HTML, JSON and Markdown tables can be converted back to
  CSV. Every cell is read as text, so values such as `007` or `1.50` stay unchanged.
- The output type switches to a fitting one when you choose the input file.
- The delimiter can be set manually: for a CSV input when it was detected wrong, and
  for a CSV output (a comma otherwise). A CSV output never overwrites an existing file.

#### Table viewer

- Opens Excel, HTML, JSON and Markdown tables as well as CSV files.
- Files can be dropped on the table, and a **Recent** menu lists the last 10 files.
- The quick filter can be a regular expression and can match case.
- **Column filters**: filter by one column with contains, does not contain, equals,
  does not equal, starts with, ends with, matches regex, is empty, is not empty,
  is duplicated or is unique. Several filters can be combined; all must match.
- **Columns**: hide and show columns, drag column headers to reorder them, resize
  columns to their contents, and freeze the first columns so they stay in view while
  scrolling sideways. Right-click a column header for all column tools.
- **Column statistics**: number of empty, distinct and duplicated values, minimum and
  maximum (as numbers when every value is a number), and the most frequent values.
- **Highlight duplicate values** of a column.
- **Copy**: Ctrl+C copies the selected cells as tab-separated text that pastes into
  Excel as cells. "Copy with headers" includes the column names.
- **Export view**: saves the rows and columns currently shown (filtered, sorted, hidden
  columns left out) as CSV or Excel.
- **Go to row**: jumps to a row by its number in the file.
- **Send to**: uses the open CSV file in Split, Compare or Columns.

### Changed

- **CSV Compare** now works like the XML Compare:
  - Rows are aligned by their content, so inserted or deleted rows no longer shift the
    rest of the file, and are then paired by the key column.
  - The key column is optional: "no key" pairs changed rows by their position.
  - With a key column, rows found at another position are reported as moved.
  - Both files are shown side by side, one row per line, with the changed cells marked.
  - The report has "Old row" and "New row" columns (the header counts as row 1, as in
    a spreadsheet) and is only written when the files differ.
- **Compare reports** (CSV and XML) now replace the report of the previous compare of the
  same two files instead of adding `(2)`, `(3)`, ... copies. When the files no longer
  differ, the old report is removed. Copy a report elsewhere to keep it.
- The table viewer only reads tabular files. The compare tools no longer open their
  reports there; "Open" shows a report in its default program, for example Excel.
- The row header of the table viewer shows each row's number in the file (1 = first
  data row), also after sorting and filtering. It used to show a count starting at 0.
- The table viewer selects cells instead of whole rows, so blocks of cells can be
  copied. Click a row number to select the whole row.
- Delimiter detection reads quoted cells correctly, so delimiters inside quoted text
  (for example `||` in SQL or multi-line values) no longer lead to a wrong guess.
- The yellow theme has been redesigned to match the default dark theme, with yellow
  accents. Text, check marks and radio button dots on yellow are dark for readability.

### Removed

- The "View in table" buttons of CSV Compare and XML Compare. Reports open with "Open"
  in their default program instead.

### Fixed

- The number in "Rows per file" (Split) was hidden behind the field's border with Qt
  6.12 and is visible again. Number fields in dialogs, such as the XML preview size
  limit, had their text too close to the border; they are aligned with the other input
  fields now.

### Requirements

- New dependency: `openpyxl` (reading Excel files). When running from source, update the
  environment with `uv sync`.

## Earlier versions

Earlier releases are tagged in the repository (`xmluvation-1.4.0`, `xmluvation-1.3.2`,
`xmluvation-1.1.0`, `xmluvation-1.0.4`).

[1.5.0]: https://github.com/zaricj/XMLuvation/compare/xmluvation-1.4.0...HEAD
