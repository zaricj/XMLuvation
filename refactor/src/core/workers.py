import os
import csv
from lxml import etree
from PySide6.QtCore import QRunnable, Signal, QObject, Slot

class WorkerSignals(QObject):
    """Encapsulates asynchronous cross-thread data updates using Qt Signals."""
    progress = Signal(int, int)          # current_index, total_count
    match_found = Signal(str, str, str)  # filename, expression, content
    finished = Signal(str)               # generated_csv_path
    error = Signal(str)                  # exception_details_string

class MultiXmlXPathWorker(QRunnable):
    """Executes heavy disk and XPath parsing calculations across background thread structures."""
    def __init__(self, target_folder: str, expressions: list, output_csv: str):
        super().__init__()
        self.target_folder = target_folder
        self.expressions = expressions
        self.output_csv = output_csv
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            files = [os.path.join(self.target_folder, f) for f in os.listdir(self.target_folder) if f.lower().endswith('.xml')]
            total_count = len(files)
            extracted_records = []
            
            # Use recover=True to handle malformed structures gracefully without crashing
            xml_parser = etree.XMLParser(recover=True, remove_blank_text=True)

            for index, file_path in enumerate(files, start=1):
                base_name = os.path.basename(file_path)
                try:
                    tree = etree.parse(file_path, parser=xml_parser)
                    for expr in self.expressions:
                        hits = tree.xpath(expr)
                        for hit in hits:
                            value = hit.text if hasattr(hit, 'text') else str(hit)
                            if value:
                                value = value.strip()
                                extracted_records.append([base_name, expr, value])
                                self.signals.match_found.emit(base_name, expr, value)
                except etree.XMLSyntaxError:
                    self.signals.match_found.emit(base_name, "N/A", "[CRITICAL: Invalid XML Content Structure]")
                
                self.signals.progress.emit(index, total_count)

            if extracted_records:
                with open(self.output_csv, mode='w', newline='', encoding='utf-8') as stream:
                    writer = csv.writer(stream)
                    writer.writerow(['File Target Name', 'XPath Query Expression', 'Parsed Value Result'])
                    writer.writerows(extracted_records)
                self.signals.finished.emit(self.output_csv)
            else:
                self.signals.finished.emit("")

        except Exception as system_fault:
            self.signals.error.emit(str(system_fault))