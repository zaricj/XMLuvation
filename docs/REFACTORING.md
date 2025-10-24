# Refactoring Guide

This guide explains the refactoring done to XMLuvation to follow clean architecture principles.

## What Was Done

### 1. Moved MainWindow to Proper Location

**Before:**
- `src/main.py` - Contained both entry point AND MainWindow class (427 lines)
- Mixed concerns: application startup + UI setup + business logic

**After:**
- `src/main.py` - Clean entry point only (17 lines)
- `src/ui/main_window.py` - MainWindow class with UI setup

### 2. Created Service Layer

**New Services:**
- `services/xml_parser_service.py` - XML parsing business logic
- `services/csv_export_service.py` - CSV export business logic  
- `services/file_service.py` - File operations and validation

**Key Principle:** Services contain ONLY business logic, NO UI dependencies.

### 3. Completed Controller Layer

**Enhanced Controllers:**
- `controllers/xml_controller.py` - XML UI coordination with dependency injection
- `controllers/csv_controller.py` - CSV UI coordination with dependency injection
- `controllers/ui_controller.py` - General UI state management

**Key Principle:** Controllers handle UI coordination, delegate business logic to services.

## Architecture Principles

### Separation of Concerns

| Layer | Responsibility | Example |
|-------|---------------|---------|
| **Controller** | UI Coordination | Show dialogs, update widgets, coordinate flow |
| **Service** | Business Logic | Parse XML, export CSV, validate data |
| **Model** | Data Structure | Store parsed data, configuration |

### Dependency Injection

Controllers receive services as parameters:

```python
class XMLController:
    def __init__(self, main_window, xml_service=None, file_service=None):
        self.xml_service = xml_service or XMLParserService()
        self.file_service = file_service or FileService()
```

Benefits:
- Easy to test with mock services
- Flexible - can swap implementations
- Clear dependencies

### Single Responsibility

Each class has ONE reason to change:
- `XMLController` changes if XML UI flow changes
- `XMLParserService` changes if XML parsing logic changes

## How to Use the New Architecture

### Example: Browse XML Folder

**Old way (in mixin):**
```python
def on_browseXMLFolder(self):
    folder = QFileDialog.getExistingDirectory(...)
    if folder:
        self.ui.line_edit_xml_folder_path_input.setText(folder)
        # Business logic mixed in
        count = sum(1 for f in os.listdir(folder) if f.endswith(".xml"))
        self.ui.statusbar_xml_files_count.setText(f"Found {count} XML Files")
```

**New way (separated):**
```python
# In mixin - delegate to controller
def on_browseXMLFolder(self):
    self.xml_controller.browse_xml_folder()

# In XMLController - UI coordination
class XMLController:
    def browse_xml_folder(self):
        folder = QFileDialog.getExistingDirectory(...)
        if folder:
            self.main_window.ui.line_edit_xml_folder_path_input.setText(folder)
            count = self.xml_service.count_xml_files(folder)  # Delegate to service
            self.main_window.ui.statusbar_xml_files_count.setText(f"Found {count}")

# In XMLParserService - pure business logic
class XMLParserService:
    def count_xml_files(self, folder_path: str) -> int:
        import os
        return sum(1 for f in os.listdir(folder_path) if f.endswith(".xml"))
```

## What's Left to Refactor

The refactoring is partially complete. What remains:

### Still Mixed (Needs Refactoring)
- **Mixins** - Still contain business logic, should only delegate to controllers
- **Signal Connections** - Some still call mixin methods directly
- **state_controller.py** - Contains handlers that should be in services

### Recommended Next Steps

1. **Create Additional Controllers**
   - `XPathController` - Handle XPath building and validation
   - `SearchController` - Handle search operations
   - `TableController` - Handle table/CSV data display

2. **Refactor Mixins**
   - Change mixins to only delegate to controllers
   - Move business logic from mixins to services
   - Example:
     ```python
     # Old mixin
     def on_addXPathToList(self):
         xpath_input = self.ui.line_edit_xpath_builder.text()
         # ... validation logic ...
         # ... update UI ...
     
     # Refactored mixin
     def on_addXPathToList(self):
         self.xpath_controller.add_xpath_to_list()
     ```

3. **Extract Services from Modules**
   - `modules/xml_parser.py` → Refactor into `services/xml_parser_service.py`
   - `modules/xpath_builder.py` → Refactor into `services/xpath_service.py`
   - `modules/xpath_search_and_csv_export.py` → Already has `csv_export_service.py`, complete it

4. **Add Tests**
   - Test services independently (no UI needed)
   - Test controllers with mock services
   - Integration tests for full flow

## Testing the Changes

The refactored code maintains backward compatibility. The application works the same way but with better structure:

1. Entry point (`main.py`) is simpler
2. MainWindow is in proper UI directory
3. Controllers and services provide clear separation
4. Ready for unit testing

## Benefits

| Before | After |
|--------|-------|
| Business logic in UI mixins | Business logic in services |
| Hard to test (needs UI) | Easy to test (pure functions) |
| Unclear dependencies | Clear dependency injection |
| Mixed concerns | Separated concerns |
| 427-line main.py | 17-line main.py |

## Quick Reference

### File Structure
```
src/
├── main.py                    # Entry point only
├── ui/
│   └── main_window.py        # MainWindow class
├── controllers/               # UI coordination
│   ├── xml_controller.py
│   ├── csv_controller.py
│   └── ui_controller.py
├── services/                  # Business logic
│   ├── xml_parser_service.py
│   ├── csv_export_service.py
│   └── file_service.py
├── mixins/                    # Signal handlers (to be refactored)
├── modules/                   # Legacy business logic (to be migrated)
└── models/                    # Data structures
```

### Creating a New Feature

1. **Create Service** - Business logic, no UI
   ```python
   class MyService:
       def do_something(self, data):
           # Pure logic here
           return result
   ```

2. **Create Controller** - UI coordination
   ```python
   class MyController:
       def __init__(self, main_window, my_service=None):
           self.main_window = main_window
           self.my_service = my_service or MyService()
       
       def handle_action(self):
           # Get data from UI
           data = self.main_window.ui.my_input.text()
           # Delegate to service
           result = self.my_service.do_something(data)
           # Update UI
           self.main_window.ui.my_output.setText(result)
   ```

3. **Connect in MainWindow**
   ```python
   # Initialize controller
   self.my_controller = MyController(self)
   
   # Connect signal
   self.ui.my_button.clicked.connect(self.my_controller.handle_action)
   ```

## Questions?

See `docs/ARCHITECTURE.md` for detailed architecture documentation.
