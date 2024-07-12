import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QGroupBox, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QRadioButton, 
                             QListWidget, QTextEdit, QProgressBar, QStatusBar,
                             QMenuBar, QCheckBox,QMenu)
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XMLuvation v1.0 © 2024 by Jovan Zaric")
        self.setWindowIcon(QIcon("path_to_icon.png"))  # Replace with actual path
        self.setGeometry(100, 100, 1200, 800)

        # Set the font
        font = QFont("Calibri", 10)
        self.setFont(font)

        # Set the color scheme
        self.set_dark_theme()

        # Create the menu bar
        self.create_menu_bar()

        # Create the main layout
        main_layout = QVBoxLayout()

        # Create the tab widget
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_xml_evaluation_tab(), "XML Evaluation")
        tab_widget.addTab(self.create_csv_conversion_tab(), "CSV Conversion")

        main_layout.addWidget(tab_widget)

        # Create a central widget to hold the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(49, 54, 59))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 47, 51))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 58, 63))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 58, 63))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(dark_palette)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("File")
        open_menu = menu_bar.addMenu("Open")
        paths_menu = menu_bar.addMenu("Paths")
        help_menu = menu_bar.addMenu("Help")

    def create_xml_evaluation_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()

        # Left column
        left_column = QVBoxLayout()
        left_column.addWidget(self.create_xml_eval_group())
        left_column.addWidget(self.create_matching_filter_group())
        left_column.addWidget(self.create_export_evaluation_group())
        left_column.addWidget(self.create_program_output_group())

        # Right column
        right_column = QVBoxLayout()
        right_column.addWidget(self.create_xml_output_group())

        layout.addLayout(left_column, 1)
        layout.addLayout(right_column, 1)
        tab.setLayout(layout)
        return tab

    def create_xml_eval_group(self):
        group = QGroupBox("XML folder selection and XPath builder")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Choose a Folder that contains XML Files"))
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLineEdit())
        folder_layout.addWidget(QPushButton("Browse"))
        folder_layout.addWidget(QPushButton("Read XML"))
        layout.addLayout(folder_layout)

        layout.addWidget(QLabel("Get XML Tag and Attribute Names/Values for XPath generation"))

        tag_layout = QHBoxLayout()
        tag_layout.addWidget(QLabel("Tag name:"))
        tag_layout.addWidget(QComboBox())
        tag_layout.addWidget(QLabel("Tag Value:"))
        tag_layout.addWidget(QComboBox())
        layout.addLayout(tag_layout)

        att_layout = QHBoxLayout()
        att_layout.addWidget(QLabel("Att name:"))
        att_layout.addWidget(QComboBox())
        att_layout.addWidget(QLabel("Att Value:"))
        att_layout.addWidget(QComboBox())
        layout.addLayout(att_layout)

        function_layout = QHBoxLayout()
        function_layout.addWidget(QLabel("Function:"))
        function_layout.addWidget(QRadioButton("Equals"))
        function_layout.addWidget(QRadioButton("Contains"))
        function_layout.addWidget(QRadioButton("Starts-with"))
        function_layout.addWidget(QRadioButton("Greater"))
        function_layout.addWidget(QRadioButton("Smaller"))
        layout.addLayout(function_layout)

        xpath_layout = QHBoxLayout()
        xpath_layout.addWidget(QLabel("XPath Expression:"))
        xpath_layout.addWidget(QLineEdit())
        xpath_layout.addWidget(QPushButton("Build XPath"))
        layout.addLayout(xpath_layout)

        group.setLayout(layout)
        return group

    def create_matching_filter_group(self):
        group = QGroupBox("List of filters to match in XML files")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Add XPath Expressions to list to look for in XML Files:"))
        header_layout.addWidget(QPushButton("Add XPath Filter"))
        layout.addLayout(header_layout)

        layout.addWidget(QListWidget())

        group.setLayout(layout)
        return group

    def create_export_evaluation_group(self):
        group = QGroupBox("Export evaluation result as a CSV File")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Choose a folder where you want to save the XML Evaluation"))
        
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLineEdit())
        export_layout.addWidget(QPushButton("Save as"))
        export_layout.addWidget(QPushButton("Export"))
        layout.addLayout(export_layout)

        group.setLayout(layout)
        return group

    def create_program_output_group(self):
        group = QGroupBox("Program Output")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        layout.addWidget(QTextEdit())

        group.setLayout(layout)
        return group

    def create_xml_output_group(self):
        group = QGroupBox("XML Output")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        layout.addWidget(QTextEdit())
        
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("0%"))
        progress_layout.addWidget(QProgressBar())
        layout.addLayout(progress_layout)

        group.setLayout(layout)
        return group
    
    def create_csv_conversion_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()

        # Left column
        left_column = QVBoxLayout()
        left_column.addWidget(self.create_csv_conversion_group())

        # Right column
        right_column = QVBoxLayout()
        right_column.addWidget(self.create_csv_output_group())

        layout.addLayout(left_column, 1)
        layout.addLayout(right_column, 1)
        tab.setLayout(layout)
        return tab

    def create_csv_conversion_group(self):
        group = QGroupBox("CSV Conversion to different file type")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("CSV Converter")
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #FFC857;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel("Convert CSV File to a different file type with the Pandas module.\nSupported output file types: Excel, Markdown, HTML and JSON")
        layout.addWidget(desc_label)

        layout.addWidget(QLabel("Choose a CSV file for conversion:"))
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLineEdit())
        input_layout.addWidget(QPushButton("Browse"))
        input_layout.addWidget(QPushButton("Read CSV"))
        layout.addLayout(input_layout)

        layout.addWidget(QLabel("Choose where to save output of CSV file"))
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLineEdit())
        output_layout.addWidget(QPushButton("Save as"))
        output_layout.addWidget(QPushButton("Convert"))
        layout.addLayout(output_layout)

        layout.addWidget(QCheckBox("Write Index Column?"))

        # Add logo (placeholder)
        logo_label = QLabel()
        pixmap = QPixmap("_internal/images/logo.png")  # Replace with actual path
        logo_label.setPixmap(pixmap)
        layout.addWidget(logo_label)

        layout.addStretch()  # This will push everything up and fill the empty space at the bottom

        group.setLayout(layout)
        return group

    def create_csv_output_group(self):
        group = QGroupBox("CSV Conversion Output")
        group.setStyleSheet("QGroupBox { color: #FFC857; }")
        layout = QVBoxLayout()

        layout.addWidget(QTextEdit())

        group.setLayout(layout)
        return group
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())