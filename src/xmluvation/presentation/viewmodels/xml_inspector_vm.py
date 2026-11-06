"""State of the XPath builder's comboboxes, derived from one inspected XML file."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Signal

from ...application.xml_inspection import inspect_xml_file
from ...domain.models import XmlIndex
from ..tasks import TaskRunner
from .base import ViewModel


class XmlInspectorViewModel(ViewModel):
    loading_changed = Signal(bool)
    document_loaded = Signal(object)  # XmlIndex
    tags_changed = Signal(list)
    tag_values_changed = Signal(list)
    attributes_changed = Signal(list)
    attribute_values_changed = Signal(list)

    def __init__(self, runner: TaskRunner, preview_limit_mb: Callable[[], int]) -> None:
        super().__init__()
        self._runner = runner
        self._preview_limit_mb = preview_limit_mb
        self._index: XmlIndex | None = None
        self._loading = False

    @property
    def index(self) -> XmlIndex | None:
        return self._index

    @property
    def loading(self) -> bool:
        return self._loading

    def load(self, file_path: str) -> None:
        if self._loading or not file_path:
            return
        path = Path(file_path)
        limit = int(self._preview_limit_mb())
        self._set_loading(True)
        self._runner.start(
            lambda _ctx: inspect_xml_file(path, limit),
            on_success=self._loaded,
            on_error=lambda e: self.report_error(e, "Exception on parsing xml file"),
            on_finished=lambda: self._set_loading(False),
        )

    def _set_loading(self, value: bool) -> None:
        self._loading = value
        self.loading_changed.emit(value)

    def _loaded(self, index: XmlIndex) -> None:
        self._index = index
        self.document_loaded.emit(index)
        self.tags_changed.emit(list(index.tags))
        lines = [
            f"File: {index.file_path}",
            f"Root element: {index.root_tag}",
            f"Total elements: {index.element_count}",
            f"Unique tags: {len(index.tags)}",
            f"Encoding: {index.encoding}",
        ]
        if index.preview_truncated:
            lines.append(
                f"Preview truncated: the file is {index.size_bytes / 1_048_576:.1f} MB, larger "
                f"than the preview limit of {self._preview_limit_mb()} MB. Tag and attribute "
                "lists cover the whole file. Change the limit under Settings."
            )
        self.log_appended.emit("\n".join(lines))

    # -- selection-derived lists ----------------------------------------------------

    def select_tag(self, tag: str) -> None:
        if self._index is None or not tag:
            return
        self.attributes_changed.emit(list(self._index.tag_to_attributes.get(tag, ())))
        self.tag_values_changed.emit(list(self._index.tag_to_values.get(tag, ())))

    def select_attribute(self, tag: str, attribute: str) -> None:
        if self._index is None or not tag or not attribute:
            self.attribute_values_changed.emit([])
            return
        values = self._index.tag_attr_to_values.get((tag, attribute), ())
        self.attribute_values_changed.emit(list(values))
