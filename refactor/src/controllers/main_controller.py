# src/controllers/main_controller.py
from PySide6.QtCore import QObject, Slot, QThreadPool
from refactor.src.models.config_model import XMLuvationConfig
from src.views.main_window import MainWindow
from src.core.csv_conversion_worker import CSVConversionWorker


class MainController(QObject):
    def __init__(self, model: XMLuvationConfig, view: MainWindow) -> None:
        super().__init__()
        self.model = model
        self.view = view
        self.thread_pool = QThreadPool.globalInstance()

        self._connect_signals()
        self._hydrate_ui_from_model()

    def _connect_signals(self) -> None:
        """Connect signals coming out of the specialized sub-views."""
        self.view.xml_xpath_tab.search_execution_requested.connect(self.run_search_engine)
        self.view.csv_profile_tab.conversion_requested.connect(self.run_csv_conversion)

    def _hydrate_ui_from_model(self) -> None:
        """Pushes data coordinates onto corresponding layout form sheets."""
        self.view.xml_xpath_tab.populate_fields(
            folder=self.model.xml_folder_path,
            csv=self.model.csv_output_path,
            xpaths=self.model.xpath_expressions,
        )
        # Hydrate the CSV conversion tab fields if your view supports it
        if hasattr(self.view.csv_profile_tab, "populate_fields"):
            self.view.csv_profile_tab.populate_fields(
                input_file=self.model.csv_file_to_convert_input
            )

    @Slot(dict)
    def run_search_engine(self, search_parameters: dict) -> None:
        """Updates configurations and schedules background XPath searching operations."""
        self.model.xml_folder_path = search_parameters["folder"]
        self.model.csv_output_path = search_parameters["output"]
        self.model.xpath_expressions = search_parameters["expressions"]
        self.model.group_matches = search_parameters["group_matches"]

        # Pre-flight guard checks
        if not self.model.xml_folder_path or not self.model.xpath_expressions:
            self.view.show_warning("Validation Error", "Required search inputs are missing.")
            return

        self.view.set_global_loading_state(True)
        # (Instantiate MultiXmlXPathWorker here similar to CSV below)

    @Slot(dict)
    def run_csv_conversion(self, conversion_parameters: dict) -> None:
        """
        Extracts parameters from View, runs pre-flight business checks,
        and hands off the task to the QThreadPool.
        
        Expected payload layout matching view state:
        {
            "input_file": "/path/to/input.csv",
            "extension_type": "EXCEL",
            "write_index": True
        }
        """
        # Update the Model Layer (Triggers auto QSettings saving)
        self.model.csv_file_to_convert_input = conversion_parameters.get("input_file", "")
        
        # Pre-flight checks (Business rules live in Controller/Model)
        if not self.model.csv_file_to_convert_input:
            self.view.csv_profile_tab.show_warning(
                "Missing File Input", 
                "Please select a target CSV file before beginning conversion processes."
            )
            return

        # Spin up Worker Context
        worker = CSVConversionWorker(
            csv_file_to_convert=self.model.csv_file_to_convert_input,
            extension_type=conversion_parameters.get("extension_type", "EXCEL"),
            write_index=conversion_parameters.get("write_index", False)
        )

        # Connect Worker Pipelines back to the View Layer via Controller Slots
        worker.signals.started.connect(lambda: self.view.set_global_loading_state(True))
        worker.signals.finished.connect(lambda: self.view.set_global_loading_state(False))
        
        worker.signals.log_message.connect(self.view.csv_profile_tab.append_output_log)
        worker.signals.file_converted.connect(self.view.csv_profile_tab.set_completed_file_path)
        
        worker.signals.error_occurred.connect(
            lambda msg: self.view.show_error_messagebox("Conversion Error", msg)
        )
        worker.signals.warning_occurred.connect(
            lambda msg: self.view.show_warning_messagebox("Conversion Warning", msg)
        )

        # Offload thread directly onto underlying CPU system cycles
        self.thread_pool.start(worker)