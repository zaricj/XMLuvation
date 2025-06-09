# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'XMLuvation.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QProgressBar, QPushButton,
    QRadioButton, QSizePolicy, QTabWidget, QTextEdit,
    QVBoxLayout, QWidget, QStatusBar)
from gui.resources.qrc import xmluvation_resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1305, 1000)
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        MainWindow.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(u"QWidget {\n"
"    background-color: #232428;\n"
"    color: #ffffff;\n"
"    font-family: Arial, sans-serif;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"QMenuBar {\n"
"    background-color: #232428;\n"
"    padding: 4px;\n"
"}\n"
"\n"
"QMenuBar::item:selected {\n"
"    background-color: #ffc857;\n"
"    border-radius: 4px;\n"
"    color: #1e1e1e;\n"
"}\n"
"\n"
"QMenu {\n"
"    background-color: #232428;\n"
"    border: 1px solid #313338;\n"
"    border-radius: 2px;\n"
"}\n"
"\n"
"QMenu::item:selected {\n"
"    background-color: #ffc857;\n"
"    color: #1e1e1e;\n"
"}\n"
"\n"
"QPushButton {\n"
"    background-color: #ffc857;\n"
"    color: #000000;\n"
"    border: none;\n"
"    padding: 8px 14px;\n"
"    border-radius: 6px;\n"
"    font: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #a3803c;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #313338;\n"
"    color: #ffffff;\n"
"    padding-left: 9px; /* Creates a \"pressed\" effect */\n"
"    padding-top: 8px;\n"
"}\n"
"\n"
"QLine"
                        "Edit, QComboBox, QTextEdit, QStatusBar {\n"
"    background-color: #313338;\n"
"    border: 1px solid #4a4a4a;\n"
"    padding: 6px;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"QListWidget {\n"
"    background-color: #313338;\n"
"}\n"
"\n"
"QListWidget::item {\n"
"    height: 26px;\n"
"}\n"
"\n"
"QListWidget::item:selected {\n"
"    background-color: #ffc857;\n"
"    color: #000000;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    border: none;\n"
"    background-color: #ffc857;\n"
"    width: 20px;\n"
"    border-top-right-radius: 6px;\n"
"    border-bottom-right-radius: 6px;\n"
"    image: url(:/images/drpdwn_arrow.png)\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"    background-color: #808080;\n"
"}\n"
"\n"
"QComboBox:disabled {\n"
"    background-color: #808080;    \n"
"}\n"
"\n"
"QComboBox::drop-down:disabled {\n"
"    border: none;\n"
"    background-color: #3d3d3d;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border: 1px solid #313338;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    background-c"
                        "olor: #232428;\n"
"    border: 1px solid #313338;\n"
"    padding: 8px 14px;\n"
"    border-radius: 6px;\n"
"    margin: 0 2px;\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    background-color: #ffc857;\n"
"    color: #000000;\n"
"}\n"
"\n"
"QTableView {\n"
"    background-color: #313338;\n"
"}\n"
"\n"
"QGroupBox {\n"
"    border: 1px solid #313338;\n"
"    border-radius: 6px;\n"
"    margin-top: 10px;\n"
"    padding: 10px;\n"
"    font: bold;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position: top left;\n"
"    left: 12px;\n"
"    padding: 0 6px;\n"
"}\n"
"\n"
"QRadioButton::indicator {\n"
"    width: 16px;\n"
"    height: 16px;\n"
"}\n"
"\n"
"\n"
"QRadioButton:disabled {\n"
"    color: #808080; \n"
"}\n"
"\n"
"\n"
"QScrollBar:vertical {\n"
"    border: none;\n"
"    background: #232428;\n"
"    width: 12px;\n"
"    margin: 4px;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: #313338;\n"
"    min-height: 20px;\n"
"    b"
                        "order-radius: 6px;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {\n"
"    height: 0px;\n"
"}\n"
"\n"
"/* Progress Bar */\n"
"QProgressBar {\n"
"    background-color: #313338;\n"
"    border: 1px solid #4a4a4a;\n"
"    border-radius: 6px;\n"
"    text-align: center;\n"
"    color: #ffffff;\n"
"    padding: 2px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #ffc857;\n"
"}\n"
"/* CheckBox */\n"
"QCheckBox {\n"
"    spacing: 6px;\n"
"}\n"
"\n"
"QCheckBox::indicator {\n"
"    width: 16px;\n"
"    height: 16px;\n"
"    border-radius: 4px;\n"
"    background-color: #313338;\n"
"    border: 1px solid #4a4a4a;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background-color: #ffc857;\n"
"    border: 1px solid #ec971f;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked {\n"
"    background-color: #313338;\n"
"    border: 1px solid #4a4a4a;\n"
"}\n"
"")
        MainWindow.setIconSize(QSize(256, 256))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(10)
        font1.setBold(False)
        self.tabWidget.setFont(font1)
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget.setUsesScrollButtons(False)
        self.tab_xml_evaluation = QWidget()
        self.tab_xml_evaluation.setObjectName(u"tab_xml_evaluation")
        self.horizontalLayout_2 = QHBoxLayout(self.tab_xml_evaluation)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.vert_layout_main = QVBoxLayout()
        self.vert_layout_main.setObjectName(u"vert_layout_main")
        self.group_box_xml_input_xpath_builder = QGroupBox(self.tab_xml_evaluation)
        self.group_box_xml_input_xpath_builder.setObjectName(u"group_box_xml_input_xpath_builder")
        self.statusbar_xml_files_count = QStatusBar(self.group_box_xml_input_xpath_builder)
        self.statusbar_xml_files_count.setSizeGripEnabled(False)
        self.statusbar_xml_files_count.setObjectName(u"statusbar_xml_files_count")
        self.verticalLayout_4 = QVBoxLayout(self.group_box_xml_input_xpath_builder)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.addWidget(self.statusbar_xml_files_count)
        self.horizontalLayout_one = QHBoxLayout()
        self.horizontalLayout_one.setObjectName(u"horizontalLayout_one")
        self.line_edit_xml_folder_path_input = QLineEdit(self.group_box_xml_input_xpath_builder)
        self.line_edit_xml_folder_path_input.setObjectName(u"line_edit_xml_folder_path_input")

        self.horizontalLayout_one.addWidget(self.line_edit_xml_folder_path_input)

        self.button_browse_xml_folder = QPushButton(self.group_box_xml_input_xpath_builder)
        self.button_browse_xml_folder.setObjectName(u"button_browse_xml_folder")

        self.horizontalLayout_one.addWidget(self.button_browse_xml_folder)

        self.button_read_xml = QPushButton(self.group_box_xml_input_xpath_builder)
        self.button_read_xml.setObjectName(u"button_read_xml")

        self.horizontalLayout_one.addWidget(self.button_read_xml)


        self.verticalLayout_4.addLayout(self.horizontalLayout_one)

        self.horizontalLayout_two = QHBoxLayout()
        self.horizontalLayout_two.setObjectName(u"horizontalLayout_two")
        self.label_xpath_builder = QLabel(self.group_box_xml_input_xpath_builder)
        self.label_xpath_builder.setObjectName(u"label_xpath_builder")

        self.horizontalLayout_two.addWidget(self.label_xpath_builder)


        self.verticalLayout_4.addLayout(self.horizontalLayout_two)

        self.horizontalLayout_three = QHBoxLayout()
        self.horizontalLayout_three.setObjectName(u"horizontalLayout_three")
        self.combobox_tag_names = QComboBox(self.group_box_xml_input_xpath_builder)
        self.combobox_tag_names.setObjectName(u"combobox_tag_names")
        self.combobox_tag_names.setEditable(False)

        self.horizontalLayout_three.addWidget(self.combobox_tag_names)

        self.combobox_tag_values = QComboBox(self.group_box_xml_input_xpath_builder)
        self.combobox_tag_values.setObjectName(u"combobox_tag_values")
        self.combobox_tag_values.setEditable(False)

        self.horizontalLayout_three.addWidget(self.combobox_tag_values)


        self.verticalLayout_4.addLayout(self.horizontalLayout_three)

        self.horizontalLayout_four = QHBoxLayout()
        self.horizontalLayout_four.setObjectName(u"horizontalLayout_four")
        self.combobox_attribute_names = QComboBox(self.group_box_xml_input_xpath_builder)
        self.combobox_attribute_names.setObjectName(u"combobox_attribute_names")
        self.combobox_attribute_names.setEditable(False)

        self.horizontalLayout_four.addWidget(self.combobox_attribute_names)

        self.combobox_attribute_values = QComboBox(self.group_box_xml_input_xpath_builder)
        self.combobox_attribute_values.setObjectName(u"combobox_attribute_values")
        self.combobox_attribute_values.setEditable(False)

        self.horizontalLayout_four.addWidget(self.combobox_attribute_values)


        self.verticalLayout_4.addLayout(self.horizontalLayout_four)

        self.horizontalLayout_five = QHBoxLayout()
        self.horizontalLayout_five.setObjectName(u"horizontalLayout_five")
        self.label_function = QLabel(self.group_box_xml_input_xpath_builder)
        self.label_function.setObjectName(u"label_function")

        self.horizontalLayout_five.addWidget(self.label_function)

        self.radio_button_equals = QRadioButton(self.group_box_xml_input_xpath_builder)
        self.radio_button_equals.setObjectName(u"radio_button_equals")
        self.radio_button_equals.setChecked(True)

        self.horizontalLayout_five.addWidget(self.radio_button_equals)

        self.radio_button_contains = QRadioButton(self.group_box_xml_input_xpath_builder)
        self.radio_button_contains.setObjectName(u"radio_button_contains")

        self.horizontalLayout_five.addWidget(self.radio_button_contains)

        self.radio_button_starts_with = QRadioButton(self.group_box_xml_input_xpath_builder)
        self.radio_button_starts_with.setObjectName(u"radio_button_starts_with")

        self.horizontalLayout_five.addWidget(self.radio_button_starts_with)

        self.radio_button_greater = QRadioButton(self.group_box_xml_input_xpath_builder)
        self.radio_button_greater.setObjectName(u"radio_button_greater")

        self.horizontalLayout_five.addWidget(self.radio_button_greater)

        self.radio_button_smaller = QRadioButton(self.group_box_xml_input_xpath_builder)
        self.radio_button_smaller.setObjectName(u"radio_button_smaller")

        self.horizontalLayout_five.addWidget(self.radio_button_smaller)


        self.verticalLayout_4.addLayout(self.horizontalLayout_five)

        self.horizontalLayout_six = QHBoxLayout()
        self.horizontalLayout_six.setObjectName(u"horizontalLayout_six")
        self.line_edit_xpath_builder = QLineEdit(self.group_box_xml_input_xpath_builder)
        self.line_edit_xpath_builder.setObjectName(u"line_edit_xpath_builder")

        self.horizontalLayout_six.addWidget(self.line_edit_xpath_builder)

        self.button_build_xpath = QPushButton(self.group_box_xml_input_xpath_builder)
        self.button_build_xpath.setObjectName(u"button_build_xpath")

        self.horizontalLayout_six.addWidget(self.button_build_xpath)


        self.verticalLayout_4.addLayout(self.horizontalLayout_six)

        self.button_add_xpath_to_list = QPushButton(self.group_box_xml_input_xpath_builder)
        self.button_add_xpath_to_list.setObjectName(u"button_add_xpath_to_list")

        self.verticalLayout_4.addWidget(self.button_add_xpath_to_list)


        self.vert_layout_main.addWidget(self.group_box_xml_input_xpath_builder)

        self.group_box_xpath_expressions_list = QGroupBox(self.tab_xml_evaluation)
        self.group_box_xpath_expressions_list.setObjectName(u"group_box_xpath_expressions_list")
        self.verticalLayout_7 = QVBoxLayout(self.group_box_xpath_expressions_list)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.list_widget_xpath_expressions = QListWidget(self.group_box_xpath_expressions_list)
        self.list_widget_xpath_expressions.setObjectName(u"list_widget_xpath_expressions")
        self.statusbar_xpath_expressions = QStatusBar(self.group_box_xpath_expressions_list)
        self.statusbar_xpath_expressions.setSizeGripEnabled(False)
        self.statusbar_xpath_expressions.setObjectName(u"statusbar_xpath_expressions")
        self.verticalLayout_7.addWidget(self.list_widget_xpath_expressions)
        self.verticalLayout_7.addWidget(self.statusbar_xpath_expressions)

        self.vert_layout_main.addWidget(self.group_box_xpath_expressions_list)

        self.group_box_export_to_csv = QGroupBox(self.tab_xml_evaluation)
        self.group_box_export_to_csv.setObjectName(u"group_box_export_to_csv")
        self.horizontalLayout = QHBoxLayout(self.group_box_export_to_csv)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.line_edit_csv_output_path = QLineEdit(self.group_box_export_to_csv)
        self.line_edit_csv_output_path.setObjectName(u"line_edit_csv_output_path")

        self.horizontalLayout.addWidget(self.line_edit_csv_output_path)

        self.button_browse_csv = QPushButton(self.group_box_export_to_csv)
        self.button_browse_csv.setObjectName(u"button_browse_csv")

        self.horizontalLayout.addWidget(self.button_browse_csv)

        self.button_export_csv = QPushButton(self.group_box_export_to_csv)
        self.button_export_csv.setObjectName(u"button_export_csv")

        self.horizontalLayout.addWidget(self.button_export_csv)

        self.button_abort_csv_export = QPushButton(self.group_box_export_to_csv)
        self.button_abort_csv_export.setObjectName(u"button_abort_csv_export")
        self.button_abort_csv_export.setVisible(False)

        self.horizontalLayout.addWidget(self.button_abort_csv_export)

        self.vert_layout_main.addWidget(self.group_box_export_to_csv)

        self.group_box_program_output = QGroupBox(self.tab_xml_evaluation)
        self.group_box_program_output.setObjectName(u"group_box_program_output")
        self.verticalLayout_6 = QVBoxLayout(self.group_box_program_output)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.text_edit_program_output = QTextEdit(self.group_box_program_output)
        self.text_edit_program_output.setObjectName(u"text_edit_program_output")
        self.text_edit_program_output.setReadOnly(True)

        self.verticalLayout_6.addWidget(self.text_edit_program_output)


        self.vert_layout_main.addWidget(self.group_box_program_output)


        self.horizontalLayout_2.addLayout(self.vert_layout_main)

        self.vert_layout_xml_output = QVBoxLayout()
        self.vert_layout_xml_output.setObjectName(u"vert_layout_xml_output")
        self.group_box_xml_output = QGroupBox(self.tab_xml_evaluation)
        self.group_box_xml_output.setObjectName(u"group_box_xml_output")
        self.verticalLayout_5 = QVBoxLayout(self.group_box_xml_output)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.text_edit_xml_output = QTextEdit(self.group_box_xml_output)
        self.text_edit_xml_output.setObjectName(u"text_edit_xml_output")

        self.verticalLayout_5.addWidget(self.text_edit_xml_output)

        self.progressbar_main = QProgressBar(self.group_box_xml_output)
        self.progressbar_main.setObjectName(u"progressbar_main")
        self.progressbar_main.setValue(0)

        self.verticalLayout_5.addWidget(self.progressbar_main)


        self.vert_layout_xml_output.addWidget(self.group_box_xml_output)


        self.horizontalLayout_2.addLayout(self.vert_layout_xml_output)

        self.tabWidget.addTab(self.tab_xml_evaluation, "")
        self.tab_csv_conversion = QWidget()
        self.tab_csv_conversion.setObjectName(u"tab_csv_conversion")
        self.verticalLayout_3 = QVBoxLayout(self.tab_csv_conversion)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupbox_csv_conversion = QGroupBox(self.tab_csv_conversion)
        self.groupbox_csv_conversion.setObjectName(u"groupbox_csv_conversion")
        self.groupbox_csv_conversion.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.groupbox_csv_conversion)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_csv_conversion_title = QLabel(self.groupbox_csv_conversion)
        self.label_csv_conversion_title.setObjectName(u"label_csv_conversion_title")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_csv_conversion_title.sizePolicy().hasHeightForWidth())
        self.label_csv_conversion_title.setSizePolicy(sizePolicy)
        self.label_csv_conversion_title.setMaximumSize(QSize(16777215, 60))
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(32)
        self.label_csv_conversion_title.setFont(font2)

        self.verticalLayout_2.addWidget(self.label_csv_conversion_title)

        self.label_csv_conversion_desc = QLabel(self.groupbox_csv_conversion)
        self.label_csv_conversion_desc.setObjectName(u"label_csv_conversion_desc")
        self.label_csv_conversion_desc.setMaximumSize(QSize(16777215, 60))
        self.label_csv_conversion_desc.setFont(font)

        self.verticalLayout_2.addWidget(self.label_csv_conversion_desc)

        self.hor_layout_csv_path_input = QHBoxLayout()
        self.hor_layout_csv_path_input.setObjectName(u"hor_layout_csv_path_input")
        self.hor_layout_csv_path_input.setContentsMargins(0, 0, -1, -1)
        self.line_edit_csv_conversion_path_input = QLineEdit(self.groupbox_csv_conversion)
        self.line_edit_csv_conversion_path_input.setObjectName(u"line_edit_csv_conversion_path_input")

        self.hor_layout_csv_path_input.addWidget(self.line_edit_csv_conversion_path_input)

        self.button_browse_csv_conversion_path_input = QPushButton(self.groupbox_csv_conversion)
        self.button_browse_csv_conversion_path_input.setObjectName(u"button_browse_csv_conversion_path_input")

        self.hor_layout_csv_path_input.addWidget(self.button_browse_csv_conversion_path_input)


        self.verticalLayout_2.addLayout(self.hor_layout_csv_path_input)

        self.hor_layout_csv_conversion_path_output = QHBoxLayout()
        self.hor_layout_csv_conversion_path_output.setObjectName(u"hor_layout_csv_conversion_path_output")
        self.line_edit_csv_conversion_path_output = QLineEdit(self.groupbox_csv_conversion)
        self.line_edit_csv_conversion_path_output.setObjectName(u"line_edit_csv_conversion_path_output")

        self.hor_layout_csv_conversion_path_output.addWidget(self.line_edit_csv_conversion_path_output)

        self.button_browse_csv_conversion_path_output = QPushButton(self.groupbox_csv_conversion)
        self.button_browse_csv_conversion_path_output.setObjectName(u"button_browse_csv_conversion_path_output")

        self.hor_layout_csv_conversion_path_output.addWidget(self.button_browse_csv_conversion_path_output)


        self.verticalLayout_2.addLayout(self.hor_layout_csv_conversion_path_output)

        self.button_csv_conversion_convert = QPushButton(self.groupbox_csv_conversion)
        self.button_csv_conversion_convert.setObjectName(u"button_csv_conversion_convert")

        self.verticalLayout_2.addWidget(self.button_csv_conversion_convert)

        self.checkbox_write_index_column = QCheckBox(self.groupbox_csv_conversion)
        self.checkbox_write_index_column.setObjectName(u"checkbox_write_index_column")

        self.verticalLayout_2.addWidget(self.checkbox_write_index_column)

        self.text_edit_csv_conversion_output = QTextEdit(self.groupbox_csv_conversion)
        self.text_edit_csv_conversion_output.setObjectName(u"text_edit_csv_conversion_output")
        self.text_edit_csv_conversion_output.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.text_edit_csv_conversion_output)


        self.verticalLayout_3.addWidget(self.groupbox_csv_conversion)

        self.tabWidget.addTab(self.tab_csv_conversion, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"XMLuvation", None))
        self.group_box_xml_input_xpath_builder.setTitle(QCoreApplication.translate("MainWindow", u"XML FOLDER SELECTION AND XPATH BUILDER", None))
        self.line_edit_xml_folder_path_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Choose a folder that contains XML files...", None))
        self.button_browse_xml_folder.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.button_read_xml.setText(QCoreApplication.translate("MainWindow", u"Read XML", None))
        self.label_xpath_builder.setText(QCoreApplication.translate("MainWindow", u"Get names and values of XML tags and Attributes for XPath generation:", None))
        self.combobox_tag_names.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select Tag Name...", None))
        self.combobox_tag_values.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select Tag Value...", None))
        self.combobox_attribute_names.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select Attribute Name...", None))
        self.combobox_attribute_values.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select Attribute Value...", None))
        self.label_function.setText(QCoreApplication.translate("MainWindow", u"Function:", None))
        self.radio_button_equals.setText(QCoreApplication.translate("MainWindow", u"Equals", None))
        self.radio_button_contains.setText(QCoreApplication.translate("MainWindow", u"Contains", None))
        self.radio_button_starts_with.setText(QCoreApplication.translate("MainWindow", u"Starts-with", None))
        self.radio_button_greater.setText(QCoreApplication.translate("MainWindow", u"Greater", None))
        self.radio_button_smaller.setText(QCoreApplication.translate("MainWindow", u"Smaller", None))
        self.line_edit_xpath_builder.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter a XPath expression or build one...", None))
        self.button_build_xpath.setText(QCoreApplication.translate("MainWindow", u"Build XPath", None))
        self.button_add_xpath_to_list.setText(QCoreApplication.translate("MainWindow", u"Add XPath Expression to list", None))
        self.group_box_xpath_expressions_list.setTitle(QCoreApplication.translate("MainWindow", u"LIST OF XPATH FILTERS TO SEARCH AND MATCH IN XML FILES", None))
        self.group_box_export_to_csv.setTitle(QCoreApplication.translate("MainWindow", u"EXPORT SEARCH RESULT TO CSV FILE", None))
        self.line_edit_csv_output_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Choose a folder where to save the CSV evaluation...", None))
        self.button_browse_csv.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.button_export_csv.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.button_abort_csv_export.setText(QCoreApplication.translate("MainWindow", u"Abort", None))
        self.group_box_program_output.setTitle(QCoreApplication.translate("MainWindow", u"PROGRAM OUTPUT", None))
        self.group_box_xml_output.setTitle(QCoreApplication.translate("MainWindow", u"XML OUTPUT", None))
        self.progressbar_main.setFormat(QCoreApplication.translate("MainWindow", u"%p%", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_xml_evaluation), QCoreApplication.translate("MainWindow", u"XML Evaluation", None))
        self.groupbox_csv_conversion.setTitle(QCoreApplication.translate("MainWindow", u"CSV Conversion", None))
        self.label_csv_conversion_title.setText(QCoreApplication.translate("MainWindow", u"CSV Conversion", None))
        self.label_csv_conversion_desc.setText(QCoreApplication.translate("MainWindow", u"Convert CSV File to a different file type with the Pandas module\n"
"Supported output file types: Excel, Markdown, HTML and JSON", None))
        self.line_edit_csv_conversion_path_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Choose a CSV file for conversion...", None))
        self.button_browse_csv_conversion_path_input.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.line_edit_csv_conversion_path_output.setText("")
        self.line_edit_csv_conversion_path_output.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Choose where to save the converted CSV file..", None))
        self.button_browse_csv_conversion_path_output.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.button_csv_conversion_convert.setText(QCoreApplication.translate("MainWindow", u"Convert CSV File", None))
        self.checkbox_write_index_column.setText(QCoreApplication.translate("MainWindow", u"Write Index Column?", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_csv_conversion), QCoreApplication.translate("MainWindow", u"CSV Conversion and Display", None))
    # retranslateUi

