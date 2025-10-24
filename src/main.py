# main.py
"""
XMLuvation - XML Parser and XPath Searcher with CSV Export
Entry point for the application.
"""
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

