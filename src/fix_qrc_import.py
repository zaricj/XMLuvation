from pathlib import Path

def fix_qrc_import():
    """
    Fix the import error that appears after every ui file changed in Qt Designer.
    
    This opens the ui file and replaces the line with 'import resources.qrc.xmluvation_resources_rc' 
    """
    cwd = Path(__file__).parent
    print(cwd)
    
    main_ui_file_path = cwd / "ui" / "main" / "XMLuvation_ui.py"
    widgets_ui_file_path = cwd / "ui" / "widgets" / "CustomPathsManager_ui.py"
    widgets_ui_file_path_2 = cwd / "ui" / "widgets" / "PreBuiltXPathsManager_ui.py"
    
    print(f"Main UI File Path: {main_ui_file_path}")
    print(f"Settings UI File Path: {widgets_ui_file_path}")
    
    main_path = main_ui_file_path
    widgets_path = widgets_ui_file_path
    widgets_path_2 = widgets_ui_file_path_2
    
    path_list = [main_path, widgets_path, widgets_path_2]
    
    for path  in path_list:
        with open(path, "r") as file:
            lines = file.readlines()

        modified = False
        for i, line in enumerate(lines):
            if "import xmluvation_resources_rc" in line and "import resources.qrc.xmluvation_resources_rc" not in line:
                lines[i] = line.replace(
                    "import xmluvation_resources_rc",
                    "import resources.qrc.xmluvation_resources_rc"
                )
                print(f"Replaced import for {path}!")
                modified = True
                break
            
        if modified:
            with open(path, "w") as file:
                file.writelines(lines)

fix_qrc_import()