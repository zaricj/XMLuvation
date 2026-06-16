import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from src.models.config_model import XMLuvationConfig
from src.views.main_window import MainWindow
from src.controllers.main_controller import MainController

def main() -> None:
    
    # Constants
    ROOT_DIR = Path(__file__).parent
    ASSETS_DIR = ROOT_DIR / "assets"
    print(ROOT_DIR)
    
    # Initialize the root graphical loop runner instance context
    app = QApplication(sys.argv)

    # Establish Global Layout Theme Skin Configurations
    style_asset = ASSETS_DIR / "stylesheet.qss"
    
    if style_asset.is_file and style_asset.exists():
        with open(style_asset, "r", encoding="utf-8") as stream:
            app.setStyleSheet(stream.read())

    # MVC Component Construction & Dependency Injection
    model = XMLuvationConfig()  # Passive model structure
    view = MainWindow()    # Graphics engine representation layer
    
    # Controller accepts model and view instances to tie their pipelines together
    controller = MainController(model=model, view=view)

    # 4. Display Window and enter main event loop
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()