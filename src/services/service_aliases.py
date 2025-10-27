# File: services/service_aliases.py
"""
Type aliases and documentation for service classes.

This module provides clear documentation about the role of each "Handler" class
in the codebase. While the classes retain their original names for backward
compatibility, this module clarifies their actual architectural roles.

Service Orchestrators (Create and manage worker threads):
- SearchAndExportToCSVHandler: Orchestrates CSV export operations
- ParseXMLFileHandler: Orchestrates XML parsing operations  
- CSVConversionHandler: Orchestrates CSV file conversion
- LobsterProfileExportCleanupHandler: Orchestrates profile cleanup
- CSVColumnDropHandler: Orchestrates CSV column removal

Controllers (Manage UI state and logic):
- ComboboxStateHandler: Controls combobox state based on XML data
- SearchXMLOutputTextHandler: Controls text search in XML output

Action Handlers (Execute specific actions):
- XPathBuildHandler: Builds XPath expressions
- AddXPathExpressionToListHandler: Adds XPath to list widget
- GenerateCSVHeaderHandler: Generates CSV headers

Note: Future refactoring may rename these classes to better reflect their roles,
but current names are maintained for backward compatibility.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.modules_controller import (
        SearchAndExportToCSVHandler,
        ParseXMLFileHandler,
        CSVConversionHandler,
        LobsterProfileExportCleanupHandler,
        CSVColumnDropHandler,
        ComboboxStateHandler,
        SearchXMLOutputTextHandler,
        XPathBuildHandler,
        AddXPathExpressionToListHandler,
        GenerateCSVHeaderHandler,
    )

# Type aliases with clearer names for documentation
CSVExportService = 'SearchAndExportToCSVHandler'
XMLParserService = 'ParseXMLFileHandler'
CSVConversionService = 'CSVConversionHandler'
ProfileCleanupService = 'LobsterProfileExportCleanupHandler'
ColumnDropService = 'CSVColumnDropHandler'

# Controllers
ComboboxController = 'ComboboxStateHandler'
SearchController = 'SearchXMLOutputTextHandler'

# Action handlers remain as-is
XPathBuilder = 'XPathBuildHandler'
XPathListManager = 'AddXPathExpressionToListHandler'
CSVHeaderGenerator = 'GenerateCSVHeaderHandler'
