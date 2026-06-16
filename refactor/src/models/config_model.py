# src/models/config_model.py
from dataclasses import dataclass, field
from typing import List
from PySide6.QtCore import QSettings


@dataclass
class XMLuvationConfig:
    """
    The Single Source of Truth for XMLuvation.
    Tracks persistent app configurations, current search paths, and UI options.
    Modifying any property instantly writes it to QSettings.
    """

    # App setting
    prompt_on_exit: bool = True

    # Active Search / Workflow States (formerly 'search_model')
    xml_folder_path: str = ""
    csv_output_path: str = ""
    xpath_expressions: List[str] = field(default_factory=list)
    group_matches: bool = False

    # Advanced / Utility States (formerly 'config_model')
    csv_file_to_convert_input: str = "" # Holds the filepath which is used for the conversion to a different filetype
    target_file_to_convert_output: str = "" 
    
    profile_cleanup_csv_path: str = ""
    current_theme: str = "dark_theme_default"
    max_threads: int = 8

    # Registry keys for OS storage
    _org: str = "Jovan"
    _app: str = "XMLuvation"

    def __post_init__(self) -> None:
        """Hydrate the dataclass attributes straight from disk upon launch."""
        self.load_all()

    def load_all(self) -> None:
        """Reads all persisted session state options from QSettings."""
        settings = QSettings(self._org, self._app)

        # Bypassing __setattr__ loop via super() during initialization

        to_prompt = str(settings.value("prompt_on_exit", "true")).lower() == "false"
        super().__setattr__("prompt_on_exit", to_prompt)

        super().__setattr__("xml_folder_path", str(settings.value("xml_folder_path", "")))
        super().__setattr__("csv_output_path", str(settings.value("csv_output_path", "")))
        super().__setattr__("csv_file_to_convert_input", str(settings.value("csv_file_to_convert_input", "")))
        super().__setattr__("target_file_to_convert_output", str(settings.value("target_file_to_convert_output", "")))
        super().__setattr__("profile_cleanup_csv_path",str(settings.value("profile_cleanup_csv_path", "")))
        super().__setattr__("current_theme", str(settings.value("current_theme", "dark_theme_default")))
        super().__setattr__("max_threads", int(settings.value("max_threads", 8)))

        # Explicit type parsing safeguards
        is_grouped = str(settings.value("group_matches", "false")).lower() == "true"
        super().__setattr__("group_matches", is_grouped)

        saved_xpaths = settings.value("xpath_expressions", [])
        super().__setattr__(
            "xpath_expressions", list(saved_xpaths) if saved_xpaths else []
        )

    def __setattr__(self, key: str, value: any) -> None:
        """Intercepts all value changes to keep system configurations perfectly synced."""
        super().__setattr__(key, value)

        # Exclude internal orchestrators or private properties from disk serialization
        if not key.startswith("_"):
            settings = QSettings(self._org, self._app)
            settings.setValue(key, value)
