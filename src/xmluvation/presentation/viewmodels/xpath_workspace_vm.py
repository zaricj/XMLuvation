"""The list of XPath expressions, their CSV headers and the recent-expressions history."""

from __future__ import annotations

from PySide6.QtCore import Signal

from ...application.xml_inspection import validate_xpath
from ...domain.errors import InvalidXPathError
from ...domain.models import BuildCriteria, XPathPreset
from ...domain.xpath_build import build_xpath
from ...domain.xpath_text import generate_header, parse_headers, smart_split
from ...infrastructure.settings_store import MAX_RECENT_EXPRESSIONS, SettingsStore
from .base import ViewModel


class XPathWorkspaceViewModel(ViewModel):
    expressions_changed = Signal(list)
    headers_text_changed = Signal(str)
    expression_input_changed = Signal(str)
    recent_changed = Signal(list)

    def __init__(self, settings: SettingsStore) -> None:
        super().__init__()
        self._settings = settings
        self._expressions: list[str] = []
        self._headers_text = ""
        self._recent = settings.recent_xpath_expressions

    # -- state ------------------------------------------------------------------------

    @property
    def expressions(self) -> list[str]:
        return list(self._expressions)

    @property
    def headers_text(self) -> str:
        return self._headers_text

    @property
    def recent(self) -> list[str]:
        return list(self._recent)

    def set_headers_text(self, text: str) -> None:
        """Called by the view when the user edits the header field (no echo signal)."""
        self._headers_text = text

    def _set_expressions(self, expressions: list[str]) -> None:
        self._expressions = expressions
        self.expressions_changed.emit(list(expressions))

    def _set_headers(self, text: str) -> None:
        self._headers_text = text
        self.headers_text_changed.emit(text)

    # -- commands -----------------------------------------------------------------------

    def build_expression(self, criteria: BuildCriteria) -> str:
        xpath = build_xpath(criteria)
        if xpath:
            self.log_appended.emit(f"Built XPath: {xpath}")
        else:
            self.log_appended.emit("No XPath expression built, select at least a tag name.")
        self.expression_input_changed.emit(xpath)
        return xpath

    def add_expressions(self, text: str, criteria: BuildCriteria | None = None) -> bool:
        """Validate and add one or more comma-separated expressions; all or nothing."""
        candidates = smart_split(text)
        if not candidates:
            self.info("Empty XPath", "Please enter a XPath expression.")
            return False
        duplicates = [c for c in candidates if c in self._expressions]
        duplicates += [c for i, c in enumerate(candidates) if c in candidates[:i]]
        if duplicates:
            self.info(
                "Duplicate XPath Expression",
                "Cannot add duplicate XPath expression:\n" + "\n".join(dict.fromkeys(duplicates)),
            )
            return False
        for candidate in candidates:
            try:
                validate_xpath(candidate)
            except InvalidXPathError as exc:
                self.log_appended.emit("XPath syntax is invalid")
                self.warning(exc.title, exc.message)
                return False

        existing = parse_headers(self._headers_text)
        use_criteria = criteria if len(candidates) == 1 else None
        new_headers: list[str] = []
        for candidate in candidates:
            new_headers.append(generate_header(candidate, use_criteria, existing + new_headers))
            self._add_recent(candidate)
        self._set_expressions(self._expressions + candidates)
        current = self._headers_text
        self._set_headers(
            f"{current}, {', '.join(new_headers)}" if current else ", ".join(new_headers)
        )
        self.expression_input_changed.emit("")
        return True

    def remove_at(self, row: int) -> None:
        if not 0 <= row < len(self._expressions):
            self.log_appended.emit("No item selected to delete.")
            return
        removed = self._expressions[row]
        self._set_expressions(self._expressions[:row] + self._expressions[row + 1 :])
        self.log_appended.emit(f"Removed item: {removed} at row {row}")

    def remove_all(self) -> None:
        if not self._expressions:
            self.log_replaced.emit("No items to delete in list.")
            return
        self._set_expressions([])
        self.log_replaced.emit("Deleted all items from the list.")
        if len(self._headers_text) > 1:
            self._set_headers("")

    def apply_preset(self, preset: XPathPreset) -> None:
        self._set_expressions(list(preset.xpaths))
        self._set_headers(", ".join(preset.headers))

    def use_recent(self, expression: str) -> None:
        self.expression_input_changed.emit(expression)

    def clear_recent(self) -> None:
        self._recent = []
        self._settings.recent_xpath_expressions = []
        self.recent_changed.emit([])
        self.log_replaced.emit("Cleared recent XPath expressions.")

    def _add_recent(self, expression: str) -> None:
        if expression in self._recent:
            return
        self._recent = [expression, *self._recent][:MAX_RECENT_EXPRESSIONS]
        self._settings.recent_xpath_expressions = self._recent
        self.recent_changed.emit(list(self._recent))
