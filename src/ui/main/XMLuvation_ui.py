# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'XMLuvationoaJult.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QProgressBar,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QSplitter, QTabWidget, QTextEdit, QVBoxLayout,
    QWidget)
import resources.qrc.xmluvation_resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1086, 813)
        font = QFont()
        font.setFamilies([u"Calibri"])
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        MainWindow.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet(u"")
        MainWindow.setIconSize(QSize(256, 256))
        self.clear_recent_xpath_expressions_action = QAction(MainWindow)
        self.clear_recent_xpath_expressions_action.setObjectName(u"clear_recent_xpath_expressions_action")
        self.clear_action = QAction(MainWindow)
        self.clear_action.setObjectName(u"clear_action")
        self.exit_action = QAction(MainWindow)
        self.exit_action.setObjectName(u"exit_action")
        self.open_input_action = QAction(MainWindow)
        self.open_input_action.setObjectName(u"open_input_action")
        self.open_output_action = QAction(MainWindow)
        self.open_output_action.setObjectName(u"open_output_action")
        self.open_csv_conversion_input_action = QAction(MainWindow)
        self.open_csv_conversion_input_action.setObjectName(u"open_csv_conversion_input_action")
        self.add_custom_path_action = QAction(MainWindow)
        self.add_custom_path_action.setObjectName(u"add_custom_path_action")
        self.open_paths_manager = QAction(MainWindow)
        self.open_paths_manager.setObjectName(u"open_paths_manager")
        self.xpath_help_action = QAction(MainWindow)
        self.xpath_help_action.setObjectName(u"xpath_help_action")
        self.actionx = QAction(MainWindow)
        self.actionx.setObjectName(u"actionx")
        self.open_pre_built_xpaths_manager_action = QAction(MainWindow)
        self.open_pre_built_xpaths_manager_action.setObjectName(u"open_pre_built_xpaths_manager_action")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        font1 = QFont()
        font1.setFamilies([u"Microsoft YaHei UI"])
        font1.setPointSize(10)
        font1.setBold(False)
        font1.setItalic(False)
        font1.setUnderline(False)
        self.centralwidget.setFont(font1)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        font2 = QFont()
        font2.setFamilies([u"Microsoft YaHei UI"])
        font2.setPointSize(10)
        font2.setBold(True)
        font2.setItalic(True)
        font2.setUnderline(False)
        font2.setStrikeOut(False)
        self.tabWidget.setFont(font2)
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget.setUsesScrollButtons(False)
        self.tab_xml_evaluation = QWidget()
        self.tab_xml_evaluation.setObjectName(u"tab_xml_evaluation")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_xml_evaluation.sizePolicy().hasHeightForWidth())
        self.tab_xml_evaluation.setSizePolicy(sizePolicy)
        font3 = QFont()
        font3.setFamilies([u"Microsoft YaHei UI"])
        font3.setPointSize(10)
        font3.setBold(False)
        font3.setItalic(False)
        font3.setUnderline(False)
        font3.setStrikeOut(False)
        self.tab_xml_evaluation.setFont(font3)
        self.verticalLayout_4 = QVBoxLayout(self.tab_xml_evaluation)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.splitter = QSplitter(self.tab_xml_evaluation)
        self.splitter.setObjectName(u"splitter")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy1)
        self.splitter.setMinimumSize(QSize(0, 0))
        self.splitter.setMaximumSize(QSize(16777215, 16777215))
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.layoutWidget_2 = QWidget(self.splitter)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.vert_layout_main = QVBoxLayout(self.layoutWidget_2)
        self.vert_layout_main.setObjectName(u"vert_layout_main")
        self.vert_layout_main.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.vert_layout_main.setContentsMargins(0, 0, 0, 0)
        self.group_box_xml_input_xpath_builder = QGroupBox(self.layoutWidget_2)
        self.group_box_xml_input_xpath_builder.setObjectName(u"group_box_xml_input_xpath_builder")
        sizePolicy1.setHeightForWidth(self.group_box_xml_input_xpath_builder.sizePolicy().hasHeightForWidth())
        self.group_box_xml_input_xpath_builder.setSizePolicy(sizePolicy1)
        font4 = QFont()
        font4.setFamilies([u"Microsoft YaHei UI"])
        font4.setPointSize(10)
        font4.setBold(True)
        font4.setItalic(False)
        font4.setUnderline(False)
        font4.setStrikeOut(False)
        self.group_box_xml_input_xpath_builder.setFont(font4)
        self.verticalLayout_7 = QVBoxLayout(self.group_box_xml_input_xpath_builder)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.statusbar_xml_files_count = QLabel(self.group_box_xml_input_xpath_builder)
        self.statusbar_xml_files_count.setObjectName(u"statusbar_xml_files_count")
        sizePolicy.setHeightForWidth(self.statusbar_xml_files_count.sizePolicy().hasHeightForWidth())
        self.statusbar_xml_files_count.setSizePolicy(sizePolicy)
        self.statusbar_xml_files_count.setStyleSheet(u"color: rgb(78, 132, 240);\n"
"font: bold;")

        self.verticalLayout_7.addWidget(self.statusbar_xml_files_count)

        self.horizontalLayout_one = QHBoxLayout()
        self.horizontalLayout_one.setObjectName(u"horizontalLayout_one")
        self.line_edit_xml_folder_path_input = QLineEdit(self.group_box_xml_input_xpath_builder)
        self.line_edit_xml_folder_path_input.setObjectName(u"line_edit_xml_folder_path_input")
        self.line_edit_xml_folder_path_input.setFont(font3)
        self.line_edit_xml_folder_path_input.setClearButtonEnabled(True)

        self.horizontalLayout_one.addWidget(self.line_edit_xml_folder_path_input)

        self.button_browse_xml_folder = QPushButton(self.group_box_xml_input_xpath_builder)
        self.button_browse_xml_folder.setObjectName(u"button_browse_xml_folder")
        self.button_browse_xml_folder.setFont(font3)

        self.horizontalLayout_one.addWidget(self.button_browse_xml_folder)

        self.button_read_xml = QPushButton(self.group_box_xml_input_xpath_builder)
        self.button_read_xml.setObjectName(u"button_read_xml")
        self.button_read_xml.setFont(font3)

        self.horizontalLayout_one.addWidget(self.button_read_xml)


        self.verticalLayout_7.addLayout(self.horizontalLayout_one)

        self.horizontalLayout_two = QHBoxLayout()
        self.horizontalLayout_two.setObjectName(u"horizontalLayout_two")
        self.horizontalLayout_two.setContentsMargins(-1, 3, -1, 3)
        self.label_xpath_builder = QLabel(self.group_box_xml_input_xpath_builder)
        self.label_xpath_builder.setObjectName(u"label_xpath_builder")
        sizePolicy.setHeightForWidth(self.label_xpath_builder.sizePolicy().hasHeightForWidth())
        self.label_xpath_builder.setSizePolicy(sizePolicy)
        self.label_xpath_builder.setFont(font3)

        self.horizontalLayout_two.addWidget(self.label_xpath_builder)


        self.verticalLayout_7.addLayout(self.horizontalLayout_two)

        self.horizontalLayout_three = QHBoxLayout()
        self.horizontalLayout_three.setObjectName(u"horizontalLayout_three")
        self.horizontalLayout_three.setContentsMargins(-1, 1, -1, 1)
        self.label_tag_names = QLabel(self.group_box_xml_input_xpath_builder)
        self.label_tag_names.setObjectName(u"label_tag_names")
        sizePolicy.setHeightForWidth(self.label_tag_names.sizePolicy().hasHeightForWidth())
        self.label_tag_names.setSizePolicy(sizePolicy)
        self.label_tag_names.setMaximumSize(QSize(72, 16777215))
        font5 = QFont()
        font5.setFamilies([u"Microsoft YaHei UI"])
        font5.setPointSize(9)
        font5.setBold(True)
        font5.setItalic(False)
        font5.setUnderline(False)
        font5.setStrikeOut(False)
        self.label_tag_names.setFont(font5)

        self.horizontalLayout_three.addWidget(self.label_tag_names)

        self.combobox_tag_names = QComboBox(self.group_box_xml_input_xpath_builder)
        self.combobox_tag_names.setObjectName(u"combobox_tag_names")
        self.combobox_tag_names.setEnabled(False)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.combobox_tag_names.sizePolicy().hasHeightForWidth())
        self.combobox_tag_names.setSizePolicy(sizePolicy2)
        self.combobox_tag_names.setFont(font4)
        self.combobox_tag_names.setEditable(True)

        self.horizontalLayout_three.addWidget(self.combobox_tag_names)

        self.label_tag_values = QLabel(self.group_box_xml_input_xpath_builder)
        self.label_tag_values.setObjectName(u"label_tag_values")
        sizePolicy.setHeightForWidth(self.label_tag_values.sizePolicy().hasHeightForWidth())
        self.label_tag_values.setSizePolicy(sizePolicy)
        self.label_tag_values.setMaximumSize(QSize(72, 16777215))
        self.label_tag_values.setFont(font5)

        self.horizontalLayout_three.addWidget(self.label_tag_values)

        self.combobox_tag_values = QComboBox(self.group_box_xml_input_xpath_builder)
        self.combobox_tag_values.setObjectName(u"combobox_tag_values")
        self.combobox_tag_values.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.combobox_tag_values.sizePolicy().hasHeightForWidth())
        self.combobox_tag_values.setSizePolicy(sizePolicy2)
        self.combobox_tag_values.setFont(font4)
        self.combobox_tag_values.setEditable(True)

        self.horizontalLayout_three.addWidget(self.combobox_tag_values)


        self.verticalLayout_7.addLayout(self.horizontalLayout_three)

        self.horizontalLayout_four = QHBoxLayout()
        self.horizontalLayout_four.setSpacing(6)
        self.horizontalLayout_four.setObjectName(u"horizontalLayout_four")
        self.horizontalLayout_four.setContentsMargins(-1, 1, -1, 1)
        self.label_attribute_names = QLabel(self.group_box_xml_input_xpath_builder)
        self.label_attribute_names.setObjectName(u"label_attribute_names")
        sizePolicy.setHeightForWidth(self.label_attribute_names.sizePolicy().hasHeightForWidth())
        self.label_attribute_names.setSizePolicy(sizePolicy)
        self.label_attribute_names.setMaximumSize(QSize(72, 16777215))
        self.label_attribute_names.setFont(font5)

        self.horizontalLayout_four.addWidget(self.label_attribute_names)

        self.combobox_attribute_names = QComboBox(self.group_box_xml_input_xpath_builder)
        self.combobox_attribute_names.setObjectName(u"combobox_attribute_names")
        self.combobox_attribute_names.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.combobox_attribute_names.sizePolicy().hasHeightForWidth())
        self.combobox_attribute_names.setSizePolicy(sizePolicy2)
        self.combobox_attribute_names.setFont(font4)
        self.combobox_attribute_names.setEditable(True)

        self.horizontalLayout_four.addWidget(self.combobox_attribute_names)

        self.label_attribute_values = QLabel(self.group_box_xml_input_xpath_builder)
        self.label_attribute_values.setObjectName(u"label_attribute_values")
        sizePolicy.setHeightForWidth(self.label_attribute_values.sizePolicy().hasHeightForWidth())
        self.label_attribute_values.setSizePolicy(sizePolicy)
        self.label_attribute_values.setMaximumSize(QSize(72, 16777215))
        self.label_attribute_values.setFont(font5)

        self.horizontalLayout_four.addWidget(self.label_attribute_values)

        self.combobox_attribute_values = QComboBox(self.group_box_xml_input_xpath_builder)
        self.combobox_attribute_values.setObjectName(u"combobox_attribute_values")
        self.combobox_attribute_values.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.combobox_attribute_values.sizePolicy().hasHeightForWidth())
        self.combobox_attribute_values.setSizePolicy(sizePolicy2)
        self.combobox_attribute_values.setFont(font4)
        self.combobox_attribute_values.setEditable(True)

        self.horizontalLayout_four.addWidget(self.combobox_attribute_values)


        self.verticalLayout_7.addLayout(self.horizontalLayout_four)

        self.horizontalLayout_five = QHBoxLayout()
        self.horizontalLayout_five.setSpacing(20)
        self.horizontalLayout_five.setObjectName(u"horizontalLayout_five")
        self.horizontalLayout_five.setContentsMargins(-1, 7, -1, 7)
        self.label_function = QLabel(self.group_box_xml_input_xpath_builder)
        self.label_function.setObjectName(u"label_function")
        sizePolicy.setHeightForWidth(self.label_function.sizePolicy().hasHeightForWidth())
        self.label_function.setSizePolicy(sizePolicy)
        self.label_function.setFont(font4)

        self.horizontalLayout_five.addWidget(self.label_function)

        self.radio_button_equals = QRadioButton(self.group_box_xml_input_xpath_builder)
        self.radio_button_equals.setObjectName(u"radio_button_equals")
        self.radio_button_equals.setFont(font4)
        self.radio_button_equals.setChecked(True)

        self.horizontalLayout_five.addWidget(self.radio_button_equals)

        self.radio_button_contains = QRadioButton(self.group_box_xml_input_xpath_builder)
        self.radio_button_contains.setObjectName(u"radio_button_contains")
        self.radio_button_contains.setFont(font4)
        self.radio_button_contains.setStyleSheet(u"")

        self.horizontalLayout_five.addWidget(self.radio_button_contains)

        self.radio_button_starts_with = QRadioButton(self.group_box_xml_input_xpath_builder)
        self.radio_button_starts_with.setObjectName(u"radio_button_starts_with")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.radio_button_starts_with.sizePolicy().hasHeightForWidth())
        self.radio_button_starts_with.setSizePolicy(sizePolicy3)
        self.radio_button_starts_with.setFont(font4)

        self.horizontalLayout_five.addWidget(self.radio_button_starts_with)

        self.radio_button_greater = QRadioButton(self.group_box_xml_input_xpath_builder)
        self.radio_button_greater.setObjectName(u"radio_button_greater")
        self.radio_button_greater.setFont(font4)

        self.horizontalLayout_five.addWidget(self.radio_button_greater)

        self.radio_button_smaller = QRadioButton(self.group_box_xml_input_xpath_builder)
        self.radio_button_smaller.setObjectName(u"radio_button_smaller")
        self.radio_button_smaller.setFont(font4)

        self.horizontalLayout_five.addWidget(self.radio_button_smaller)


        self.verticalLayout_7.addLayout(self.horizontalLayout_five)

        self.horizontalLayout_six = QHBoxLayout()
        self.horizontalLayout_six.setObjectName(u"horizontalLayout_six")
        self.line_edit_xpath_builder = QLineEdit(self.group_box_xml_input_xpath_builder)
        self.line_edit_xpath_builder.setObjectName(u"line_edit_xpath_builder")
        self.line_edit_xpath_builder.setFont(font3)
        self.line_edit_xpath_builder.setClearButtonEnabled(True)

        self.horizontalLayout_six.addWidget(self.line_edit_xpath_builder)

        self.button_build_xpath = QPushButton(self.group_box_xml_input_xpath_builder)
        self.button_build_xpath.setObjectName(u"button_build_xpath")
        self.button_build_xpath.setFont(font3)

        self.horizontalLayout_six.addWidget(self.button_build_xpath)


        self.verticalLayout_7.addLayout(self.horizontalLayout_six)

        self.button_add_xpath_to_list = QPushButton(self.group_box_xml_input_xpath_builder)
        self.button_add_xpath_to_list.setObjectName(u"button_add_xpath_to_list")
        self.button_add_xpath_to_list.setFont(font3)

        self.verticalLayout_7.addWidget(self.button_add_xpath_to_list)


        self.vert_layout_main.addWidget(self.group_box_xml_input_xpath_builder)

        self.group_box_xpath_expressions_list = QGroupBox(self.layoutWidget_2)
        self.group_box_xpath_expressions_list.setObjectName(u"group_box_xpath_expressions_list")
        sizePolicy1.setHeightForWidth(self.group_box_xpath_expressions_list.sizePolicy().hasHeightForWidth())
        self.group_box_xpath_expressions_list.setSizePolicy(sizePolicy1)
        self.group_box_xpath_expressions_list.setFont(font4)
        self.verticalLayout_8 = QVBoxLayout(self.group_box_xpath_expressions_list)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.list_widget_main_xpath_expressions = QListWidget(self.group_box_xpath_expressions_list)
        self.list_widget_main_xpath_expressions.setObjectName(u"list_widget_main_xpath_expressions")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.list_widget_main_xpath_expressions.sizePolicy().hasHeightForWidth())
        self.list_widget_main_xpath_expressions.setSizePolicy(sizePolicy4)
        self.list_widget_main_xpath_expressions.setFont(font3)
        self.list_widget_main_xpath_expressions.setTabKeyNavigation(False)
        self.list_widget_main_xpath_expressions.setDragEnabled(True)
        self.list_widget_main_xpath_expressions.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget_main_xpath_expressions.setAlternatingRowColors(True)
        self.list_widget_main_xpath_expressions.setMovement(QListView.Movement.Snap)
        self.list_widget_main_xpath_expressions.setSortingEnabled(False)

        self.verticalLayout_8.addWidget(self.list_widget_main_xpath_expressions)

        self.statusbar_xpath_expressions = QLabel(self.group_box_xpath_expressions_list)
        self.statusbar_xpath_expressions.setObjectName(u"statusbar_xpath_expressions")
        sizePolicy.setHeightForWidth(self.statusbar_xpath_expressions.sizePolicy().hasHeightForWidth())
        self.statusbar_xpath_expressions.setSizePolicy(sizePolicy)
        self.statusbar_xpath_expressions.setFont(font4)
        self.statusbar_xpath_expressions.setStyleSheet(u"color: rgb(78, 132, 240);\n"
"font: bold;")

        self.verticalLayout_8.addWidget(self.statusbar_xpath_expressions)


        self.vert_layout_main.addWidget(self.group_box_xpath_expressions_list)

        self.group_box_export_to_csv = QGroupBox(self.layoutWidget_2)
        self.group_box_export_to_csv.setObjectName(u"group_box_export_to_csv")
        sizePolicy1.setHeightForWidth(self.group_box_export_to_csv.sizePolicy().hasHeightForWidth())
        self.group_box_export_to_csv.setSizePolicy(sizePolicy1)
        self.group_box_export_to_csv.setFont(font4)
        self.verticalLayout_11 = QVBoxLayout(self.group_box_export_to_csv)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.label_csv_headers_info = QLabel(self.group_box_export_to_csv)
        self.label_csv_headers_info.setObjectName(u"label_csv_headers_info")
        sizePolicy.setHeightForWidth(self.label_csv_headers_info.sizePolicy().hasHeightForWidth())
        self.label_csv_headers_info.setSizePolicy(sizePolicy)
        self.label_csv_headers_info.setFont(font3)

        self.verticalLayout_11.addWidget(self.label_csv_headers_info)

        self.hor_layout_csv_headers = QHBoxLayout()
        self.hor_layout_csv_headers.setObjectName(u"hor_layout_csv_headers")
        self.line_edit_csv_headers_input = QLineEdit(self.group_box_export_to_csv)
        self.line_edit_csv_headers_input.setObjectName(u"line_edit_csv_headers_input")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.line_edit_csv_headers_input.sizePolicy().hasHeightForWidth())
        self.line_edit_csv_headers_input.setSizePolicy(sizePolicy5)
        self.line_edit_csv_headers_input.setFont(font3)
        self.line_edit_csv_headers_input.setClearButtonEnabled(True)

        self.hor_layout_csv_headers.addWidget(self.line_edit_csv_headers_input)


        self.verticalLayout_11.addLayout(self.hor_layout_csv_headers)

        self.label_csv_export_input = QLabel(self.group_box_export_to_csv)
        self.label_csv_export_input.setObjectName(u"label_csv_export_input")
        sizePolicy.setHeightForWidth(self.label_csv_export_input.sizePolicy().hasHeightForWidth())
        self.label_csv_export_input.setSizePolicy(sizePolicy)
        self.label_csv_export_input.setFont(font3)

        self.verticalLayout_11.addWidget(self.label_csv_export_input)

        self.hor_layout_csv_input_and_export = QHBoxLayout()
        self.hor_layout_csv_input_and_export.setObjectName(u"hor_layout_csv_input_and_export")
        self.line_edit_csv_output_path = QLineEdit(self.group_box_export_to_csv)
        self.line_edit_csv_output_path.setObjectName(u"line_edit_csv_output_path")
        self.line_edit_csv_output_path.setFont(font3)
        self.line_edit_csv_output_path.setClearButtonEnabled(True)

        self.hor_layout_csv_input_and_export.addWidget(self.line_edit_csv_output_path)

        self.button_browse_csv = QPushButton(self.group_box_export_to_csv)
        self.button_browse_csv.setObjectName(u"button_browse_csv")
        self.button_browse_csv.setFont(font3)

        self.hor_layout_csv_input_and_export.addWidget(self.button_browse_csv)


        self.verticalLayout_11.addLayout(self.hor_layout_csv_input_and_export)

        self.hor_layout_button_export_and_abort = QHBoxLayout()
        self.hor_layout_button_export_and_abort.setObjectName(u"hor_layout_button_export_and_abort")
        self.button_abort_csv_export = QPushButton(self.group_box_export_to_csv)
        self.button_abort_csv_export.setObjectName(u"button_abort_csv_export")
        self.button_abort_csv_export.setEnabled(True)
        self.button_abort_csv_export.setFont(font3)
        self.button_abort_csv_export.setFlat(False)

        self.hor_layout_button_export_and_abort.addWidget(self.button_abort_csv_export)

        self.button_start_csv_export = QPushButton(self.group_box_export_to_csv)
        self.button_start_csv_export.setObjectName(u"button_start_csv_export")
        self.button_start_csv_export.setFont(font3)

        self.hor_layout_button_export_and_abort.addWidget(self.button_start_csv_export)


        self.verticalLayout_11.addLayout(self.hor_layout_button_export_and_abort)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_options = QLabel(self.group_box_export_to_csv)
        self.label_options.setObjectName(u"label_options")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.label_options.sizePolicy().hasHeightForWidth())
        self.label_options.setSizePolicy(sizePolicy6)
        self.label_options.setFont(font4)

        self.horizontalLayout_2.addWidget(self.label_options)

        self.checkbox_group_matches = QCheckBox(self.group_box_export_to_csv)
        self.checkbox_group_matches.setObjectName(u"checkbox_group_matches")
        sizePolicy2.setHeightForWidth(self.checkbox_group_matches.sizePolicy().hasHeightForWidth())
        self.checkbox_group_matches.setSizePolicy(sizePolicy2)
        self.checkbox_group_matches.setFont(font3)
        self.checkbox_group_matches.setChecked(False)

        self.horizontalLayout_2.addWidget(self.checkbox_group_matches)

        self.button_pass_csv_to_converter = QLabel(self.group_box_export_to_csv)
        self.button_pass_csv_to_converter.setObjectName(u"button_pass_csv_to_converter")
        self.button_pass_csv_to_converter.setFont(font3)
        self.button_pass_csv_to_converter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.button_pass_csv_to_converter.setStyleSheet(u"")
        self.button_pass_csv_to_converter.setFrameShape(QFrame.Shape.NoFrame)
        self.button_pass_csv_to_converter.setFrameShadow(QFrame.Shadow.Plain)
        self.button_pass_csv_to_converter.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.button_pass_csv_to_converter)


        self.verticalLayout_11.addLayout(self.horizontalLayout_2)


        self.vert_layout_main.addWidget(self.group_box_export_to_csv)

        self.group_box_program_output = QGroupBox(self.layoutWidget_2)
        self.group_box_program_output.setObjectName(u"group_box_program_output")
        sizePolicy1.setHeightForWidth(self.group_box_program_output.sizePolicy().hasHeightForWidth())
        self.group_box_program_output.setSizePolicy(sizePolicy1)
        self.group_box_program_output.setFont(font4)
        self.verticalLayout_12 = QVBoxLayout(self.group_box_program_output)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.text_edit_program_output = QTextEdit(self.group_box_program_output)
        self.text_edit_program_output.setObjectName(u"text_edit_program_output")
        sizePolicy4.setHeightForWidth(self.text_edit_program_output.sizePolicy().hasHeightForWidth())
        self.text_edit_program_output.setSizePolicy(sizePolicy4)
        self.text_edit_program_output.setFont(font3)
        self.text_edit_program_output.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.text_edit_program_output.setReadOnly(True)

        self.verticalLayout_12.addWidget(self.text_edit_program_output)


        self.vert_layout_main.addWidget(self.group_box_program_output)

        self.splitter.addWidget(self.layoutWidget_2)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.vert_layout_xml_output = QVBoxLayout(self.layoutWidget)
        self.vert_layout_xml_output.setObjectName(u"vert_layout_xml_output")
        self.vert_layout_xml_output.setContentsMargins(0, 0, 0, 0)
        self.group_box_xml_output = QGroupBox(self.layoutWidget)
        self.group_box_xml_output.setObjectName(u"group_box_xml_output")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.group_box_xml_output.sizePolicy().hasHeightForWidth())
        self.group_box_xml_output.setSizePolicy(sizePolicy7)
        self.group_box_xml_output.setMinimumSize(QSize(450, 0))
        self.group_box_xml_output.setFont(font4)
        self.verticalLayout_6 = QVBoxLayout(self.group_box_xml_output)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.text_edit_xml_output = QTextEdit(self.group_box_xml_output)
        self.text_edit_xml_output.setObjectName(u"text_edit_xml_output")
        sizePolicy4.setHeightForWidth(self.text_edit_xml_output.sizePolicy().hasHeightForWidth())
        self.text_edit_xml_output.setSizePolicy(sizePolicy4)
        self.text_edit_xml_output.setMinimumSize(QSize(0, 0))
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        brush1 = QBrush(QColor(255, 200, 87, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        brush2 = QBrush(QColor(54, 54, 54, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush2)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush)
        brush3 = QBrush(QColor(255, 255, 127, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush3)
        brush4 = QBrush(QColor(0, 0, 0, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush4)
        brush5 = QBrush(QColor(49, 51, 56, 255))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush5)
        brush6 = QBrush(QColor(35, 36, 40, 255))
        brush6.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush6)
        brush7 = QBrush(QColor(211, 162, 72, 255))
        brush7.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, brush7)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, brush4)
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Accent, brush1)
#endif
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush2)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush3)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush4)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush5)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, brush7)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, brush4)
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Accent, brush1)
#endif
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush6)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush6)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, brush4)
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Accent, brush1)
#endif
        self.text_edit_xml_output.setPalette(palette)
        self.text_edit_xml_output.setFont(font3)
        self.text_edit_xml_output.setReadOnly(True)

        self.verticalLayout_6.addWidget(self.text_edit_xml_output)

        self.hor_layout_find_functionality = QHBoxLayout()
        self.hor_layout_find_functionality.setObjectName(u"hor_layout_find_functionality")
        self.line_edit_xml_output_find_text = QLineEdit(self.group_box_xml_output)
        self.line_edit_xml_output_find_text.setObjectName(u"line_edit_xml_output_find_text")
        self.line_edit_xml_output_find_text.setFont(font3)

        self.hor_layout_find_functionality.addWidget(self.line_edit_xml_output_find_text)

        self.button_find_next = QPushButton(self.group_box_xml_output)
        self.button_find_next.setObjectName(u"button_find_next")
        self.button_find_next.setFont(font3)

        self.hor_layout_find_functionality.addWidget(self.button_find_next)

        self.button_find_previous = QPushButton(self.group_box_xml_output)
        self.button_find_previous.setObjectName(u"button_find_previous")
        self.button_find_previous.setFont(font3)

        self.hor_layout_find_functionality.addWidget(self.button_find_previous)


        self.verticalLayout_6.addLayout(self.hor_layout_find_functionality)

        self.progressbar_main = QProgressBar(self.group_box_xml_output)
        self.progressbar_main.setObjectName(u"progressbar_main")
        self.progressbar_main.setFont(font3)
        self.progressbar_main.setValue(0)

        self.verticalLayout_6.addWidget(self.progressbar_main)

        self.label_file_processing = QLabel(self.group_box_xml_output)
        self.label_file_processing.setObjectName(u"label_file_processing")
        sizePolicy1.setHeightForWidth(self.label_file_processing.sizePolicy().hasHeightForWidth())
        self.label_file_processing.setSizePolicy(sizePolicy1)
        self.label_file_processing.setFont(font4)
        self.label_file_processing.setStyleSheet(u"color: rgb(78, 132, 240);\n"
"font: bold;")

        self.verticalLayout_6.addWidget(self.label_file_processing)


        self.vert_layout_xml_output.addWidget(self.group_box_xml_output)

        self.splitter.addWidget(self.layoutWidget)

        self.verticalLayout_4.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab_xml_evaluation, "")
        self.tab_csv_conversion = QWidget()
        self.tab_csv_conversion.setObjectName(u"tab_csv_conversion")
        self.tab_csv_conversion.setFont(font3)
        self.horizontalLayout_4 = QHBoxLayout(self.tab_csv_conversion)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.main_layout_csv_conversion_and_cleanup_tab = QHBoxLayout()
        self.main_layout_csv_conversion_and_cleanup_tab.setObjectName(u"main_layout_csv_conversion_and_cleanup_tab")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupbox_csv_conversion = QGroupBox(self.tab_csv_conversion)
        self.groupbox_csv_conversion.setObjectName(u"groupbox_csv_conversion")
        self.groupbox_csv_conversion.setMaximumSize(QSize(16777215, 16777215))
        self.groupbox_csv_conversion.setFont(font4)
        self.verticalLayout_13 = QVBoxLayout(self.groupbox_csv_conversion)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_csv_conversion_title = QLabel(self.groupbox_csv_conversion)
        self.label_csv_conversion_title.setObjectName(u"label_csv_conversion_title")
        sizePolicy1.setHeightForWidth(self.label_csv_conversion_title.sizePolicy().hasHeightForWidth())
        self.label_csv_conversion_title.setSizePolicy(sizePolicy1)
        self.label_csv_conversion_title.setMaximumSize(QSize(16777215, 60))
        font6 = QFont()
        font6.setFamilies([u"Microsoft YaHei UI"])
        font6.setPointSize(32)
        font6.setBold(True)
        font6.setItalic(False)
        font6.setUnderline(False)
        font6.setStrikeOut(False)
        font6.setKerning(True)
        self.label_csv_conversion_title.setFont(font6)
        self.label_csv_conversion_title.setStyleSheet(u"color: rgb(255, 200, 87);")

        self.verticalLayout_13.addWidget(self.label_csv_conversion_title)

        self.label_csv_conversion_desc = QLabel(self.groupbox_csv_conversion)
        self.label_csv_conversion_desc.setObjectName(u"label_csv_conversion_desc")
        self.label_csv_conversion_desc.setMaximumSize(QSize(16777215, 60))
        self.label_csv_conversion_desc.setFont(font3)

        self.verticalLayout_13.addWidget(self.label_csv_conversion_desc)

        self.hor_layout_csv_path_input = QHBoxLayout()
        self.hor_layout_csv_path_input.setObjectName(u"hor_layout_csv_path_input")
        self.hor_layout_csv_path_input.setContentsMargins(0, 0, -1, -1)
        self.line_edit_csv_conversion_path_input = QLineEdit(self.groupbox_csv_conversion)
        self.line_edit_csv_conversion_path_input.setObjectName(u"line_edit_csv_conversion_path_input")
        self.line_edit_csv_conversion_path_input.setFont(font3)
        self.line_edit_csv_conversion_path_input.setClearButtonEnabled(True)

        self.hor_layout_csv_path_input.addWidget(self.line_edit_csv_conversion_path_input)

        self.button_browse_csv_conversion_path_input = QPushButton(self.groupbox_csv_conversion)
        self.button_browse_csv_conversion_path_input.setObjectName(u"button_browse_csv_conversion_path_input")
        self.button_browse_csv_conversion_path_input.setFont(font3)

        self.hor_layout_csv_path_input.addWidget(self.button_browse_csv_conversion_path_input)


        self.verticalLayout_13.addLayout(self.hor_layout_csv_path_input)

        self.hor_layout_csv_conversion_path_output = QHBoxLayout()
        self.hor_layout_csv_conversion_path_output.setObjectName(u"hor_layout_csv_conversion_path_output")
        self.label_csv_conversion_output_type = QLabel(self.groupbox_csv_conversion)
        self.label_csv_conversion_output_type.setObjectName(u"label_csv_conversion_output_type")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.label_csv_conversion_output_type.sizePolicy().hasHeightForWidth())
        self.label_csv_conversion_output_type.setSizePolicy(sizePolicy8)

        self.hor_layout_csv_conversion_path_output.addWidget(self.label_csv_conversion_output_type)

        self.combobox_csv_conversion_output_type = QComboBox(self.groupbox_csv_conversion)
        self.combobox_csv_conversion_output_type.addItem("")
        self.combobox_csv_conversion_output_type.addItem("")
        self.combobox_csv_conversion_output_type.addItem("")
        self.combobox_csv_conversion_output_type.addItem("")
        self.combobox_csv_conversion_output_type.setObjectName(u"combobox_csv_conversion_output_type")
        sizePolicy2.setHeightForWidth(self.combobox_csv_conversion_output_type.sizePolicy().hasHeightForWidth())
        self.combobox_csv_conversion_output_type.setSizePolicy(sizePolicy2)

        self.hor_layout_csv_conversion_path_output.addWidget(self.combobox_csv_conversion_output_type)

        self.checkbox_write_index_column = QCheckBox(self.groupbox_csv_conversion)
        self.checkbox_write_index_column.setObjectName(u"checkbox_write_index_column")
        sizePolicy8.setHeightForWidth(self.checkbox_write_index_column.sizePolicy().hasHeightForWidth())
        self.checkbox_write_index_column.setSizePolicy(sizePolicy8)
        self.checkbox_write_index_column.setFont(font3)

        self.hor_layout_csv_conversion_path_output.addWidget(self.checkbox_write_index_column)


        self.verticalLayout_13.addLayout(self.hor_layout_csv_conversion_path_output)

        self.button_csv_conversion_convert = QPushButton(self.groupbox_csv_conversion)
        self.button_csv_conversion_convert.setObjectName(u"button_csv_conversion_convert")
        self.button_csv_conversion_convert.setFont(font3)

        self.verticalLayout_13.addWidget(self.button_csv_conversion_convert)


        self.verticalLayout.addWidget(self.groupbox_csv_conversion)

        self.line = QFrame(self.tab_csv_conversion)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.groupbox_lobster_profiles_cleanup = QGroupBox(self.tab_csv_conversion)
        self.groupbox_lobster_profiles_cleanup.setObjectName(u"groupbox_lobster_profiles_cleanup")
        self.groupbox_lobster_profiles_cleanup.setFont(font4)
        self.verticalLayout_10 = QVBoxLayout(self.groupbox_lobster_profiles_cleanup)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_title_profile_cleanup = QLabel(self.groupbox_lobster_profiles_cleanup)
        self.label_title_profile_cleanup.setObjectName(u"label_title_profile_cleanup")
        sizePolicy9 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.label_title_profile_cleanup.sizePolicy().hasHeightForWidth())
        self.label_title_profile_cleanup.setSizePolicy(sizePolicy9)
        font7 = QFont()
        font7.setFamilies([u"Microsoft YaHei UI"])
        font7.setPointSize(32)
        font7.setBold(True)
        font7.setItalic(False)
        font7.setUnderline(False)
        font7.setStrikeOut(False)
        self.label_title_profile_cleanup.setFont(font7)
        self.label_title_profile_cleanup.setStyleSheet(u"color: rgb(255, 200, 87);")

        self.verticalLayout_10.addWidget(self.label_title_profile_cleanup)

        self.label_2 = QLabel(self.groupbox_lobster_profiles_cleanup)
        self.label_2.setObjectName(u"label_2")
        sizePolicy9.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy9)
        self.label_2.setFont(font3)

        self.verticalLayout_10.addWidget(self.label_2)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.line_edit_profile_cleanup_csv_file_path = QLineEdit(self.groupbox_lobster_profiles_cleanup)
        self.line_edit_profile_cleanup_csv_file_path.setObjectName(u"line_edit_profile_cleanup_csv_file_path")
        self.line_edit_profile_cleanup_csv_file_path.setFont(font3)
        self.line_edit_profile_cleanup_csv_file_path.setClearButtonEnabled(True)

        self.horizontalLayout_5.addWidget(self.line_edit_profile_cleanup_csv_file_path)

        self.button_profile_cleanup_browse_csv_file_path = QPushButton(self.groupbox_lobster_profiles_cleanup)
        self.button_profile_cleanup_browse_csv_file_path.setObjectName(u"button_profile_cleanup_browse_csv_file_path")
        self.button_profile_cleanup_browse_csv_file_path.setMinimumSize(QSize(0, 0))
        self.button_profile_cleanup_browse_csv_file_path.setMaximumSize(QSize(16777215, 16777215))
        self.button_profile_cleanup_browse_csv_file_path.setFont(font3)

        self.horizontalLayout_5.addWidget(self.button_profile_cleanup_browse_csv_file_path)


        self.verticalLayout_5.addLayout(self.horizontalLayout_5)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.line_edit_profile_cleanup_folder_path = QLineEdit(self.groupbox_lobster_profiles_cleanup)
        self.line_edit_profile_cleanup_folder_path.setObjectName(u"line_edit_profile_cleanup_folder_path")
        self.line_edit_profile_cleanup_folder_path.setFont(font3)
        self.line_edit_profile_cleanup_folder_path.setClearButtonEnabled(True)

        self.horizontalLayout_6.addWidget(self.line_edit_profile_cleanup_folder_path)

        self.button_profile_cleanup_browse_folder_path = QPushButton(self.groupbox_lobster_profiles_cleanup)
        self.button_profile_cleanup_browse_folder_path.setObjectName(u"button_profile_cleanup_browse_folder_path")
        self.button_profile_cleanup_browse_folder_path.setFont(font3)

        self.horizontalLayout_6.addWidget(self.button_profile_cleanup_browse_folder_path)


        self.verticalLayout_9.addLayout(self.horizontalLayout_6)


        self.verticalLayout_5.addLayout(self.verticalLayout_9)

        self.button_profile_cleanup_cleanup_start = QPushButton(self.groupbox_lobster_profiles_cleanup)
        self.button_profile_cleanup_cleanup_start.setObjectName(u"button_profile_cleanup_cleanup_start")
        self.button_profile_cleanup_cleanup_start.setFont(font3)

        self.verticalLayout_5.addWidget(self.button_profile_cleanup_cleanup_start)


        self.verticalLayout_10.addLayout(self.verticalLayout_5)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_csv_headers_combobox = QLabel(self.groupbox_lobster_profiles_cleanup)
        self.label_csv_headers_combobox.setObjectName(u"label_csv_headers_combobox")
        sizePolicy10 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.label_csv_headers_combobox.sizePolicy().hasHeightForWidth())
        self.label_csv_headers_combobox.setSizePolicy(sizePolicy10)
        self.label_csv_headers_combobox.setFont(font3)

        self.horizontalLayout_7.addWidget(self.label_csv_headers_combobox)

        self.combobox_csv_headers = QComboBox(self.groupbox_lobster_profiles_cleanup)
        self.combobox_csv_headers.setObjectName(u"combobox_csv_headers")
        self.combobox_csv_headers.setEnabled(False)
        sizePolicy9.setHeightForWidth(self.combobox_csv_headers.sizePolicy().hasHeightForWidth())
        self.combobox_csv_headers.setSizePolicy(sizePolicy9)

        self.horizontalLayout_7.addWidget(self.combobox_csv_headers)

        self.button_drop_csv_header = QPushButton(self.groupbox_lobster_profiles_cleanup)
        self.button_drop_csv_header.setObjectName(u"button_drop_csv_header")
        self.button_drop_csv_header.setEnabled(False)
        sizePolicy10.setHeightForWidth(self.button_drop_csv_header.sizePolicy().hasHeightForWidth())
        self.button_drop_csv_header.setSizePolicy(sizePolicy10)
        self.button_drop_csv_header.setFont(font3)

        self.horizontalLayout_7.addWidget(self.button_drop_csv_header)


        self.verticalLayout_10.addLayout(self.horizontalLayout_7)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer)


        self.verticalLayout.addWidget(self.groupbox_lobster_profiles_cleanup)


        self.main_layout_csv_conversion_and_cleanup_tab.addLayout(self.verticalLayout)

        self.group_box_tab2_program_output = QGroupBox(self.tab_csv_conversion)
        self.group_box_tab2_program_output.setObjectName(u"group_box_tab2_program_output")
        self.group_box_tab2_program_output.setFont(font4)
        self.horizontalLayout_8 = QHBoxLayout(self.group_box_tab2_program_output)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.text_edit_csv_output = QTextEdit(self.group_box_tab2_program_output)
        self.text_edit_csv_output.setObjectName(u"text_edit_csv_output")
        self.text_edit_csv_output.setFont(font3)
        self.text_edit_csv_output.setReadOnly(True)

        self.horizontalLayout_8.addWidget(self.text_edit_csv_output)


        self.main_layout_csv_conversion_and_cleanup_tab.addWidget(self.group_box_tab2_program_output)


        self.horizontalLayout_4.addLayout(self.main_layout_csv_conversion_and_cleanup_tab)

        self.tabWidget.addTab(self.tab_csv_conversion, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menu_bar = QMenuBar(MainWindow)
        self.menu_bar.setObjectName(u"menu_bar")
        self.menu_bar.setGeometry(QRect(0, 0, 1086, 33))
        self.file_menu = QMenu(self.menu_bar)
        self.file_menu.setObjectName(u"file_menu")
        self.recent_xpath_expressions_menu = QMenu(self.file_menu)
        self.recent_xpath_expressions_menu.setObjectName(u"recent_xpath_expressions_menu")
        self.open_menu = QMenu(self.menu_bar)
        self.open_menu.setObjectName(u"open_menu")
        self.paths_menu = QMenu(self.menu_bar)
        self.paths_menu.setObjectName(u"paths_menu")
        self.settings_menu = QMenu(self.menu_bar)
        self.settings_menu.setObjectName(u"settings_menu")
        self.help_menu = QMenu(self.menu_bar)
        self.help_menu.setObjectName(u"help_menu")
        self.menu_autofill = QMenu(self.menu_bar)
        self.menu_autofill.setObjectName(u"menu_autofill")
        MainWindow.setMenuBar(self.menu_bar)

        self.menu_bar.addAction(self.file_menu.menuAction())
        self.menu_bar.addAction(self.open_menu.menuAction())
        self.menu_bar.addAction(self.paths_menu.menuAction())
        self.menu_bar.addAction(self.menu_autofill.menuAction())
        self.menu_bar.addAction(self.settings_menu.menuAction())
        self.menu_bar.addAction(self.help_menu.menuAction())
        self.file_menu.addAction(self.recent_xpath_expressions_menu.menuAction())
        self.file_menu.addAction(self.clear_recent_xpath_expressions_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        self.open_menu.addAction(self.open_input_action)
        self.open_menu.addAction(self.open_output_action)
        self.open_menu.addSeparator()
        self.open_menu.addAction(self.open_csv_conversion_input_action)
        self.paths_menu.addAction(self.add_custom_path_action)
        self.settings_menu.addAction(self.open_paths_manager)
        self.settings_menu.addAction(self.open_pre_built_xpaths_manager_action)
        self.help_menu.addAction(self.xpath_help_action)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.combobox_tag_names.setCurrentIndex(-1)
        self.combobox_tag_values.setCurrentIndex(-1)
        self.combobox_attribute_names.setCurrentIndex(-1)
        self.combobox_attribute_values.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"XMLuvation", None))
        self.clear_recent_xpath_expressions_action.setText(QCoreApplication.translate("MainWindow", u"Clear recent XPath expressions", None))
        self.clear_action.setText(QCoreApplication.translate("MainWindow", u"Clear all outputs", None))
        self.exit_action.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.open_input_action.setText(QCoreApplication.translate("MainWindow", u"Open input XML folder", None))
        self.open_output_action.setText(QCoreApplication.translate("MainWindow", u"Open output CSV folder", None))
        self.open_csv_conversion_input_action.setText(QCoreApplication.translate("MainWindow", u"Open output CSV converted folder", None))
        self.add_custom_path_action.setText(QCoreApplication.translate("MainWindow", u"Add custom path", None))
        self.open_paths_manager.setText(QCoreApplication.translate("MainWindow", u"Open Custom Path Manager", None))
        self.xpath_help_action.setText(QCoreApplication.translate("MainWindow", u"Regex Help", None))
        self.actionx.setText(QCoreApplication.translate("MainWindow", u"x", None))
        self.open_pre_built_xpaths_manager_action.setText(QCoreApplication.translate("MainWindow", u"Open pre-built XPaths Manager", None))
        self.group_box_xml_input_xpath_builder.setTitle(QCoreApplication.translate("MainWindow", u"XML FOLDER SELECTION AND XPATH BUILDER", None))
        self.statusbar_xml_files_count.setText("")
        self.line_edit_xml_folder_path_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Choose a folder that contains XML files...", None))
#if QT_CONFIG(tooltip)
        self.button_browse_xml_folder.setToolTip(QCoreApplication.translate("MainWindow", u"Browse for the folder containing your XML files.", None))
#endif // QT_CONFIG(tooltip)
        self.button_browse_xml_folder.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
#if QT_CONFIG(tooltip)
        self.button_read_xml.setToolTip(QCoreApplication.translate("MainWindow", u"Load data from an XML file into the Combo Boxes and display the XML content.", None))
#endif // QT_CONFIG(tooltip)
        self.button_read_xml.setText(QCoreApplication.translate("MainWindow", u"Read XML", None))
        self.label_xpath_builder.setText(QCoreApplication.translate("MainWindow", u"Get the names and values of XML tags and attributes for XPath generation:", None))
        self.label_tag_names.setText(QCoreApplication.translate("MainWindow", u"Tag Names:", None))
        self.combobox_tag_names.setCurrentText("")
        self.combobox_tag_names.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select Tag Name...", None))
        self.label_tag_values.setText(QCoreApplication.translate("MainWindow", u"Tag Values:", None))
        self.combobox_tag_values.setCurrentText("")
        self.combobox_tag_values.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select Tag Value...", None))
        self.label_attribute_names.setText(QCoreApplication.translate("MainWindow", u"Attr Names:", None))
        self.combobox_attribute_names.setCurrentText("")
        self.combobox_attribute_names.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select Attribute Name...", None))
        self.label_attribute_values.setText(QCoreApplication.translate("MainWindow", u"Attr Values:", None))
        self.combobox_attribute_values.setCurrentText("")
        self.combobox_attribute_values.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select Attribute Value...", None))
        self.label_function.setText(QCoreApplication.translate("MainWindow", u"Function:", None))
#if QT_CONFIG(tooltip)
        self.radio_button_equals.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.radio_button_equals.setText(QCoreApplication.translate("MainWindow", u"Equals", None))
        self.radio_button_contains.setText(QCoreApplication.translate("MainWindow", u"Contains", None))
        self.radio_button_starts_with.setText(QCoreApplication.translate("MainWindow", u"Starts-with", None))
        self.radio_button_greater.setText(QCoreApplication.translate("MainWindow", u"Greater", None))
        self.radio_button_smaller.setText(QCoreApplication.translate("MainWindow", u"Smaller", None))
        self.line_edit_xpath_builder.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter a XPath expression or build one...", None))
#if QT_CONFIG(tooltip)
        self.button_build_xpath.setToolTip(QCoreApplication.translate("MainWindow", u"Create an XPath expression based on the current Combo Box values.", None))
#endif // QT_CONFIG(tooltip)
        self.button_build_xpath.setText(QCoreApplication.translate("MainWindow", u"Build XPath", None))
#if QT_CONFIG(tooltip)
        self.button_add_xpath_to_list.setToolTip(QCoreApplication.translate("MainWindow", u"Add the entered or generated XPath expression to the list below.", None))
#endif // QT_CONFIG(tooltip)
        self.button_add_xpath_to_list.setText(QCoreApplication.translate("MainWindow", u"Add XPath expression to list", None))
        self.group_box_xpath_expressions_list.setTitle(QCoreApplication.translate("MainWindow", u"LIST OF XPATH FILTERS TO SEARCH AND MATCH IN XML FILES", None))
        self.statusbar_xpath_expressions.setText("")
        self.group_box_export_to_csv.setTitle(QCoreApplication.translate("MainWindow", u"EXPORT SEARCH RESULT TO CSV FILE", None))
        self.label_csv_headers_info.setText(QCoreApplication.translate("MainWindow", u"Enter CSV headers for each XPath expression (comma-separated):", None))
        self.line_edit_csv_headers_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter CSV header names... (comma-separated)", None))
        self.label_csv_export_input.setText(QCoreApplication.translate("MainWindow", u"Browse file path where to save the csv result:", None))
        self.line_edit_csv_output_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Choose a folder where to save the CSV evaluation...", None))
#if QT_CONFIG(tooltip)
        self.button_browse_csv.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the folder and filename where the results CSV will be saved.", None))
#endif // QT_CONFIG(tooltip)
        self.button_browse_csv.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
#if QT_CONFIG(tooltip)
        self.button_abort_csv_export.setToolTip(QCoreApplication.translate("MainWindow", u"Stop the current operation.", None))
#endif // QT_CONFIG(tooltip)
        self.button_abort_csv_export.setText(QCoreApplication.translate("MainWindow", u"Abort", None))
#if QT_CONFIG(tooltip)
        self.button_start_csv_export.setToolTip(QCoreApplication.translate("MainWindow", u"Search the XML files and export the results to the CSV file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_start_csv_export.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.label_options.setText(QCoreApplication.translate("MainWindow", u"Option:", None))
#if QT_CONFIG(tooltip)
        self.checkbox_group_matches.setToolTip(QCoreApplication.translate("MainWindow", u"Group matches in the CSV using semicolons; if unchecked, each match is written to a separate row.", None))
#endif // QT_CONFIG(tooltip)
        self.checkbox_group_matches.setText(QCoreApplication.translate("MainWindow", u"Group matches", None))
        self.button_pass_csv_to_converter.setText(QCoreApplication.translate("MainWindow", u"<a href=\"#\" style=\"color: #ffc857\">Pass CSV Path to Converter</a>", None))
        self.group_box_program_output.setTitle(QCoreApplication.translate("MainWindow", u"PROGRAM OUTPUT", None))
        self.group_box_xml_output.setTitle(QCoreApplication.translate("MainWindow", u"XML OUTPUT", None))
        self.line_edit_xml_output_find_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Find text in summary...", None))
#if QT_CONFIG(tooltip)
        self.button_find_next.setToolTip(QCoreApplication.translate("MainWindow", u"Search next term.", None))
#endif // QT_CONFIG(tooltip)
        self.button_find_next.setText(QCoreApplication.translate("MainWindow", u"Next", None))
#if QT_CONFIG(tooltip)
        self.button_find_previous.setToolTip(QCoreApplication.translate("MainWindow", u"Search previous term.", None))
#endif // QT_CONFIG(tooltip)
        self.button_find_previous.setText(QCoreApplication.translate("MainWindow", u"Previous", None))
        self.progressbar_main.setFormat(QCoreApplication.translate("MainWindow", u"%p%", None))
        self.label_file_processing.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_xml_evaluation), QCoreApplication.translate("MainWindow", u"XML Evaluation", None))
        self.groupbox_csv_conversion.setTitle(QCoreApplication.translate("MainWindow", u"CSV CONVERSION", None))
        self.label_csv_conversion_title.setText(QCoreApplication.translate("MainWindow", u"CSV Conversion", None))
        self.label_csv_conversion_desc.setText(QCoreApplication.translate("MainWindow", u"Convert CSV File to a different file type with the Pandas module\n"
"Supported output file types: Excel, Markdown, HTML and JSON", None))
        self.line_edit_csv_conversion_path_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select the CSV file which you want to connvert...", None))
#if QT_CONFIG(tooltip)
        self.button_browse_csv_conversion_path_input.setToolTip(QCoreApplication.translate("MainWindow", u"Browse for the CSV file which will be used for the conversion.", None))
#endif // QT_CONFIG(tooltip)
        self.button_browse_csv_conversion_path_input.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.label_csv_conversion_output_type.setText(QCoreApplication.translate("MainWindow", u"Select output file format:", None))
        self.combobox_csv_conversion_output_type.setItemText(0, QCoreApplication.translate("MainWindow", u"EXCEL", None))
        self.combobox_csv_conversion_output_type.setItemText(1, QCoreApplication.translate("MainWindow", u"HTML", None))
        self.combobox_csv_conversion_output_type.setItemText(2, QCoreApplication.translate("MainWindow", u"JSON", None))
        self.combobox_csv_conversion_output_type.setItemText(3, QCoreApplication.translate("MainWindow", u"MARKDOWN", None))

#if QT_CONFIG(tooltip)
        self.checkbox_write_index_column.setToolTip(QCoreApplication.translate("MainWindow", u"Write an index colum starting at 1 for the supported output file formats.", None))
#endif // QT_CONFIG(tooltip)
        self.checkbox_write_index_column.setText(QCoreApplication.translate("MainWindow", u"Write index column?", None))
#if QT_CONFIG(tooltip)
        self.button_csv_conversion_convert.setToolTip(QCoreApplication.translate("MainWindow", u"Convert the CSV file to the selected file type.", None))
#endif // QT_CONFIG(tooltip)
        self.button_csv_conversion_convert.setText(QCoreApplication.translate("MainWindow", u"Convert CSV File", None))
        self.groupbox_lobster_profiles_cleanup.setTitle(QCoreApplication.translate("MainWindow", u"PROFILE EXPORT CLEAN UP", None))
        self.label_title_profile_cleanup.setText(QCoreApplication.translate("MainWindow", u"CSV File Clean Up", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Mainly used for Lobster profiles that have been exported as a CSV file.", None))
        self.line_edit_profile_cleanup_csv_file_path.setText("")
        self.line_edit_profile_cleanup_csv_file_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select the exported CSV file containing all lobster profiles...", None))
#if QT_CONFIG(tooltip)
        self.button_profile_cleanup_browse_csv_file_path.setToolTip(QCoreApplication.translate("MainWindow", u"Browse for the CSV file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_profile_cleanup_browse_csv_file_path.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.line_edit_profile_cleanup_folder_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select the folder path that contains all Lobster profiles as XML files...", None))
#if QT_CONFIG(tooltip)
        self.button_profile_cleanup_browse_folder_path.setToolTip(QCoreApplication.translate("MainWindow", u"Browse for the folder path which contains XML files.", None))
#endif // QT_CONFIG(tooltip)
        self.button_profile_cleanup_browse_folder_path.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
#if QT_CONFIG(tooltip)
        self.button_profile_cleanup_cleanup_start.setToolTip(QCoreApplication.translate("MainWindow", u"Perform cleanup operations on the XML files.", None))
#endif // QT_CONFIG(tooltip)
        self.button_profile_cleanup_cleanup_start.setText(QCoreApplication.translate("MainWindow", u"Clean up XML files", None))
        self.label_csv_headers_combobox.setText(QCoreApplication.translate("MainWindow", u"Current CSV file headers:", None))
#if QT_CONFIG(tooltip)
        self.button_drop_csv_header.setToolTip(QCoreApplication.translate("MainWindow", u"Delete the selected header from the CSV file and save changes.", None))
#endif // QT_CONFIG(tooltip)
        self.button_drop_csv_header.setText(QCoreApplication.translate("MainWindow", u"Drop Header", None))
        self.group_box_tab2_program_output.setTitle(QCoreApplication.translate("MainWindow", u"CSV OUTPUT", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_csv_conversion), QCoreApplication.translate("MainWindow", u"CSV Conversion and Cleanup", None))
        self.file_menu.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.recent_xpath_expressions_menu.setTitle(QCoreApplication.translate("MainWindow", u"Recent XPath expressions", None))
        self.open_menu.setTitle(QCoreApplication.translate("MainWindow", u"Open", None))
        self.paths_menu.setTitle(QCoreApplication.translate("MainWindow", u"Paths", None))
        self.settings_menu.setTitle(QCoreApplication.translate("MainWindow", u"Manage", None))
        self.help_menu.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menu_autofill.setTitle(QCoreApplication.translate("MainWindow", u"Autofill", None))
    # retranslateUi

