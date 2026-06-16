# src/views/xml_xpath_view.py
from PySide6.QtWidgets import QWidget, QFileDialog, QListWidgetItem
from PySide6.QtCore import Signal

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.main import MainWindow


class TabXMLSearchView(QWidget):
    """Encapsulates execution operations bounded to the primary XML selection layout space."""

    parse_tags_requested = Signal(str)
    search_execution_requested = Signal(dict)

    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()
        self.window = main_window
        self.ui = main_window.ui
        self._wire_widget_events()

    def _wire_widget_events(self) -> None:
        self.ui.button_browse_xml_folder.clicked.connect(self._on_browse_folder)
        self.ui.button_read_xml.clicked.connect(self._on_read_xml)
        self.ui.button_add_xpath_to_list.clicked.connect(self._add_xpath_to_list)
        # self.ui.button_remove_xpath.clicked.connect(self._remove_xpath_from_list)
        
        self.ui.button_start_csv_export.clicked.connect(self._on_start_search)

    def _on_browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self.window, "Select XML Directory")
        if folder:
            self.ui.line_edit_xml_folder_path_input.setText(folder)

    def _on_read_xml(self) -> None:
        path, _ = QFileDialog.getOpenFileName(parent=self.window, caption="Read a XML file", filter="XML File (*.xml)")
        if path:
            self.parse_tags_requested.emit(path)

    def _add_xpath_to_list(self) -> None:
        expr = self.ui.line_edit_xpath_builder.text().strip()
        if expr:
            items = [
                self.ui.list_widget_main_xpath_expressions.item(i).text()
                for i in range(self.ui.list_widget_main_xpath_expressions.count())
            ]
            if expr not in items:
                self.ui.list_widget_main_xpath_expressions.addItem(
                    QListWidgetItem(expr)
                )
                self.ui.line_edit_xpath_builder.clear()

    def _remove_xpath_from_list(self) -> None:
        current = self.ui.list_widget_main_xpath_expressions.currentItem()
        if current:
            row = self.ui.list_widget_main_xpath_expressions.row(current)
            self.ui.list_widget_main_xpath_expressions.takeItem(row)

    def _on_start_search(self) -> None:
        xpaths = [
            self.ui.list_widget_main_xpath_expressions.item(i).text()
            for i in range(self.ui.list_widget_main_xpath_expressions.count())
        ]

        self.search_execution_requested.emit(
            {
                "folder": self.ui.line_edit_xml_folder_path_input.text().strip(),
                "output": self.ui.line_edit_csv_output_path.text().strip(),
                "expressions": xpaths,
                "group_matches": self.ui.checkbox_group_matches.isChecked(),
            }
        )

    def populate_fields(self, folder: str, csv: str, xpaths: list) -> None:
        self.ui.line_edit_xml_folder_path_input.setText(folder)
        self.ui.line_edit_csv_output_path.setText(csv)
        self.ui.list_widget_main_xpath_expressions.clear()
        for item in xpaths:
            self.ui.list_widget_main_xpath_expressions.addItem(QListWidgetItem(item))
