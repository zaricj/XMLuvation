# File: modules/state_controller.py
# This file maintains backward compatibility by re-exporting handlers from their new locations
# Import handlers from their new modular locations
from controllers.combobox_state_handler import ComboboxStateHandler
from controllers.xml_output_search_handler import SearchXMLOutputTextHandler
from controllers.xpath_handlers import (
    AddXPathExpressionToListHandler,
    XPathBuildHandler,
    GenerateCSVHeaderHandler
)
from services.csv_service_handlers import (
    CSVConversionHandler,
    SearchAndExportToCSVHandler,
    LobsterProfileExportCleanupHandler,
    CSVColumnDropHandler
)
from services.xml_service_handlers import ParseXMLFileHandler

# Re-export all classes for backward compatibility
__all__ = [
    'ComboboxStateHandler',
    'CSVConversionHandler',
    'AddXPathExpressionToListHandler',
    'SearchAndExportToCSVHandler',
    'LobsterProfileExportCleanupHandler',
    'CSVColumnDropHandler',
    'ParseXMLFileHandler',
    'XPathBuildHandler',
    'GenerateCSVHeaderHandler',
    'SearchXMLOutputTextHandler',
]
