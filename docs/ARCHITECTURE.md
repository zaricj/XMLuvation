# XMLuvation Architecture Guide

This document describes the refactored architecture following the Separation of Concerns principle.

## Architecture Overview

```
app/
├── main.py                          # Entry point only
├── ui/
│   ├── main_window.py              # MainWindow class (UI setup only)
│   └── dialogs/                    # Dialog classes
├── controllers/
│   ├── xml_controller.py           # Handles XML-related UI coordination
│   ├── csv_controller.py           # Handles CSV-related UI coordination
│   ├── ui_controller.py            # Handles UI state changes
│   └── xpath_controller.py         # Handles XPath operations
├── services/
│   ├── xml_parser_service.py       # XML parsing business logic
│   ├── csv_export_service.py       # CSV export business logic
│   └── file_service.py             # File operations
├── workers/                         # QRunnable workers for threading
├── models/                          # Data models
└── utils/                           # Helper functions
```

## Key Principles

### 1. Separation of Concerns

#### Controller (UI Coordination)
- Handles user interactions
- Coordinates between UI and services
- Updates UI based on results
- **NO business logic**

Example:
```python
class XMLController:
    def browse_xml_folder(self):
        # Get folder from user (UI)
        folder = QFileDialog.getExistingDirectory(...)
        
        # Update UI
        self.main_window.ui.line_edit_xml_folder_path_input.setText(folder)
        
        # Delegate business logic to service
        count = self.xml_service.count_xml_files(folder)
        
        # Update UI with result
        self.main_window.ui.statusbar_xml_files_count.setText(f"Found {count} XML Files")
```

#### Service (Business Logic)
- Pure business logic
- No UI dependencies
- Testable without UI
- Returns data, not UI updates

Example:
```python
class XMLParserService:
    def count_xml_files(self, folder_path: str) -> int:
        """Pure business logic - no UI"""
        import os
        return sum(1 for f in os.listdir(folder_path) if f.endswith(".xml"))
```

#### Model (Data)
- Plain data structures
- No logic beyond data validation
- Easily serializable

### 2. Single Responsibility

Each class should have ONE reason to change:

- **XMLController** changes only if XML UI flow changes
- **XMLParserService** changes only if XML parsing logic changes
- **XMLState** (model) changes only if XML data structure changes

### 3. Dependency Injection

Controllers receive dependencies, don't create them:

```python
class XMLController:
    def __init__(self, main_window, xml_service=None, file_service=None):
        """Dependencies are injected, allowing easy testing and flexibility"""
        self.main_window = main_window
        self.xml_service = xml_service or XMLParserService()
        self.file_service = file_service or FileService()
```

Benefits:
- Easy to test with mock services
- Can swap implementations
- Clear dependencies

## Component Responsibilities

### Controllers

#### XMLController
- Browse XML folders and files
- Trigger XML parsing
- Update UI with parse results
- Manage XML-related UI state

#### CSVController
- Browse CSV output paths
- Start/stop CSV export
- Handle export progress
- Update UI with export status

#### UIController
- Theme management
- Progress indicators
- Message boxes
- General UI state

### Services

#### XMLParserService
- Parse XML files
- Count XML files
- Create parser workers
- Pure XML logic

#### CSVExportService
- Create CSV export workers
- Validate export configuration
- Pure CSV export logic

#### FileService
- Validate file paths
- Ensure directories exist
- File system operations

## Migration from Old Architecture

The old architecture had business logic mixed with UI in mixins:

**Old (Mixins with Business Logic):**
```python
class ButtonActionsMixin:
    def on_browseXMLFolder(self):
        folder = QFileDialog.getExistingDirectory(...)  # UI
        if folder:
            self.ui.line_edit_xml_folder_path_input.setText(folder)  # UI
            count = sum(1 for f in os.listdir(folder) if f.endswith(".xml"))  # BUSINESS LOGIC
            self.ui.statusbar_xml_files_count.setText(f"Found {count} XML Files")  # UI
```

**New (Separated):**
```python
# Controller - UI coordination only
class XMLController:
    def browse_xml_folder(self):
        folder = QFileDialog.getExistingDirectory(...)  # UI
        if folder:
            self.main_window.ui.line_edit_xml_folder_path_input.setText(folder)  # UI
            count = self.xml_service.count_xml_files(folder)  # Delegate to service
            self.main_window.ui.statusbar_xml_files_count.setText(f"Found {count}")  # UI

# Service - Business logic only
class XMLParserService:
    def count_xml_files(self, folder_path: str) -> int:
        import os
        return sum(1 for f in os.listdir(folder_path) if f.endswith(".xml"))
```

## Testing Strategy

With the new architecture, components can be tested independently:

### Testing Services (No UI needed)
```python
def test_count_xml_files():
    service = XMLParserService()
    count = service.count_xml_files("/path/to/folder")
    assert count == 5
```

### Testing Controllers (Mock services)
```python
def test_browse_xml_folder():
    mock_service = Mock(XMLParserService)
    mock_service.count_xml_files.return_value = 5
    
    controller = XMLController(main_window, xml_service=mock_service)
    controller.browse_xml_folder()
    
    assert mock_service.count_xml_files.called
```

## Future Refactoring

The following components still need refactoring:

1. **Mixins** - Currently contain business logic, should only coordinate with controllers
2. **Signal Connections** - Should route through controllers
3. **State Management** - Extract to dedicated state classes/models
4. **Workers** - Should be created by services, not modules

### Recommended Next Steps

1. Create more controller classes (XPathController, SearchController)
2. Refactor mixins to delegate to controllers
3. Extract business logic from `modules/` to `services/`
4. Create proper model classes for data structures
5. Add unit tests for services and controllers

## Benefits of This Architecture

1. **Testability**: Services can be tested without UI
2. **Maintainability**: Clear separation makes code easier to understand and modify
3. **Reusability**: Services can be used in different contexts (CLI, API, GUI)
4. **Flexibility**: Easy to swap implementations via dependency injection
5. **Scalability**: Clear structure makes it easier to add features

## Example Usage

### Creating a Controller with Dependency Injection

```python
# In main_window.py
def initialize_controllers(self):
    # Create services (can be shared)
    xml_service = XMLParserService()
    csv_service = CSVExportService()
    file_service = FileService()
    
    # Inject services into controllers
    self.xml_controller = XMLController(self, xml_service, file_service)
    self.csv_controller = CSVController(self, csv_service, file_service)
    self.ui_controller = UIController(self)
```

### Using Controllers

```python
# In mixins or signal handlers
def on_browseXMLFolder(self):
    # Delegate to controller
    self.xml_controller.browse_xml_folder()
```

## References

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Separation of Concerns](https://en.wikipedia.org/wiki/Separation_of_concerns)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
