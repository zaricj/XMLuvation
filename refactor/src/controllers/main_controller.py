# src/controllers/main_controller.py
from PySide6.QtCore import QObject, Slot
from src.models.config_model import XMLuvationConfig
from src.views.main_window import MainWindow

class MainController(QObject):
    def __init__(self, model: XMLuvationConfig, view: MainWindow) -> None:
        super().__init__()
        self.model = model
        self.view = view

        # Connect signals coming out of the specialized sub-views
        self.view.xml_xpath_tab.search_execution_requested.connect(self.run_search_engine)
        
        self._hydrate_ui_from_model()

    def _hydrate_ui_from_model(self) -> None:
        """Pushes values from the self-persisted model straight into the sub-views."""
        self.view.xml_xpath_tab.populate_fields(
            folder=self.model.xml_folder_path,
            csv=self.model.csv_output_path,
            xpaths=self.model.xpath_expressions
        )

    @Slot(dict)
    def run_search_engine(self, search_parameters: dict) -> None:
        """Updates the persistent configuration and schedules background execution tasks."""
        # Mutating these updates values on disk inside QSettings completely automatically!
        self.model.xml_folder_path = search_parameters["folder"]
        self.model.csv_output_path = search_parameters["output"]
        self.model.xpath_expressions = search_parameters["expressions"]
        self.model.group_matches = search_parameters["group_matches"]

        # Proceed with file validation and background QRunnable thread pool dispatching...
        self.view.set_global_loading_state(True)