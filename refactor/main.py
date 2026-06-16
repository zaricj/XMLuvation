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
    STYLES_DIR = ASSETS_DIR / "styles"

    # Initialize the root graphical loop runner instance context
    app = QApplication(sys.argv)

    # Establish Global Layout Theme Skin Configurations
    default_style = STYLES_DIR / "dark" / "dark_theme_default.qss"

    if default_style.is_file and default_style.exists():
        with open(default_style, "r", encoding="utf-8") as stream:
            app.setStyleSheet(stream.read())

    # MVC Component Construction & Dependency Injection
    model = XMLuvationConfig()  # Passive model structure
    view = MainWindow()  # Graphics engine representation layer

    # Controller accepts model and view instances to tie their pipelines together
    controller = MainController(model=model, view=view)

    # 4. Display Window and enter main event loop
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
