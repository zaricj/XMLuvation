# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'XMLuvation.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractSpinBox, QApplication, QCheckBox,
    QComboBox, QDockWidget, QFormLayout, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMenu, QMenuBar, QPlainTextEdit, QProgressBar,
    QPushButton, QRadioButton, QScrollArea, QSizePolicy,
    QSpacerItem, QSpinBox, QSplitter, QStackedWidget,
    QStatusBar, QTabWidget, QTextEdit, QVBoxLayout,
    QWidget)

from xmluvation.presentation.widgets.busy_bar import BusyBar
from xmluvation.presentation.widgets.data_table import DataTableView
from xmluvation.presentation.widgets.diff_view import DiffView
from . import xmluvation_resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1369, 952)
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setDockNestingEnabled(False)
        self.open_input_action = QAction(MainWindow)
        self.open_input_action.setObjectName(u"open_input_action")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.FolderOpen))
        self.open_input_action.setIcon(icon1)
        self.open_output_action = QAction(MainWindow)
        self.open_output_action.setObjectName(u"open_output_action")
        self.open_output_action.setIcon(icon1)
        self.open_csv_conversion_input_action = QAction(MainWindow)
        self.open_csv_conversion_input_action.setObjectName(u"open_csv_conversion_input_action")
        self.open_csv_conversion_input_action.setIcon(icon1)
        self.clear_recent_xpath_expressions_action = QAction(MainWindow)
        self.clear_recent_xpath_expressions_action.setObjectName(u"clear_recent_xpath_expressions_action")
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditClear))
        self.clear_recent_xpath_expressions_action.setIcon(icon2)
        self.prompt_on_exit_action = QAction(MainWindow)
        self.prompt_on_exit_action.setObjectName(u"prompt_on_exit_action")
        self.prompt_on_exit_action.setCheckable(True)
        self.prompt_on_exit_action.setChecked(True)
        self.exit_action = QAction(MainWindow)
        self.exit_action.setObjectName(u"exit_action")
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit))
        self.exit_action.setIcon(icon3)
        self.open_paths_manager = QAction(MainWindow)
        self.open_paths_manager.setObjectName(u"open_paths_manager")
        self.open_pre_built_xpaths_manager_action = QAction(MainWindow)
        self.open_pre_built_xpaths_manager_action.setObjectName(u"open_pre_built_xpaths_manager_action")
        self.xpath_help_action = QAction(MainWindow)
        self.xpath_help_action.setObjectName(u"xpath_help_action")
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        self.xpath_help_action.setIcon(icon4)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.layout_central = QHBoxLayout(self.centralwidget)
        self.layout_central.setSpacing(0)
        self.layout_central.setObjectName(u"layout_central")
        self.layout_central.setContentsMargins(0, 0, 0, 0)
        self.frame_sidebar = QFrame(self.centralwidget)
        self.frame_sidebar.setObjectName(u"frame_sidebar")
        self.frame_sidebar.setMinimumSize(QSize(200, 0))
        self.frame_sidebar.setMaximumSize(QSize(200, 16777215))
        self.layout_sidebar = QVBoxLayout(self.frame_sidebar)
        self.layout_sidebar.setSpacing(4)
        self.layout_sidebar.setObjectName(u"layout_sidebar")
        self.layout_sidebar.setContentsMargins(14, 20, 14, 16)
        self.label_app_title = QLabel(self.frame_sidebar)
        self.label_app_title.setObjectName(u"label_app_title")

        self.layout_sidebar.addWidget(self.label_app_title)

        self.label_app_subtitle = QLabel(self.frame_sidebar)
        self.label_app_subtitle.setObjectName(u"label_app_subtitle")
        self.label_app_subtitle.setWordWrap(True)

        self.layout_sidebar.addWidget(self.label_app_subtitle)

        self.spacer_1 = QSpacerItem(0, 16, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.layout_sidebar.addItem(self.spacer_1)

        self.list_widget_navigation = QListWidget(self.frame_sidebar)
        icon5 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditFind))
        __qlistwidgetitem = QListWidgetItem(self.list_widget_navigation)
        __qlistwidgetitem.setIcon(icon5)
        QListWidgetItem(self.list_widget_navigation)
        icon6 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        __qlistwidgetitem1 = QListWidgetItem(self.list_widget_navigation)
        __qlistwidgetitem1.setIcon(icon6)
        QListWidgetItem(self.list_widget_navigation)
        self.list_widget_navigation.setObjectName(u"list_widget_navigation")
        self.list_widget_navigation.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.list_widget_navigation.setFrameShape(QFrame.Shape.NoFrame)
        self.list_widget_navigation.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget_navigation.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget_navigation.setIconSize(QSize(18, 18))
        self.list_widget_navigation.setUniformItemSizes(True)

        self.layout_sidebar.addWidget(self.list_widget_navigation)

        self.label_sidebar_shortcuts = QLabel(self.frame_sidebar)
        self.label_sidebar_shortcuts.setObjectName(u"label_sidebar_shortcuts")
        self.label_sidebar_shortcuts.setWordWrap(True)

        self.layout_sidebar.addWidget(self.label_sidebar_shortcuts)

        self.layout_sidebar.setStretch(3, 1)

        self.layout_central.addWidget(self.frame_sidebar)

        self.stacked_pages = QStackedWidget(self.centralwidget)
        self.stacked_pages.setObjectName(u"stacked_pages")
        self.page_extract = QWidget()
        self.page_extract.setObjectName(u"page_extract")
        self.layout_page_extract = QVBoxLayout(self.page_extract)
        self.layout_page_extract.setSpacing(12)
        self.layout_page_extract.setObjectName(u"layout_page_extract")
        self.layout_page_extract.setContentsMargins(28, 24, 28, 20)
        self.label_page_extract_title = QLabel(self.page_extract)
        self.label_page_extract_title.setObjectName(u"label_page_extract_title")

        self.layout_page_extract.addWidget(self.label_page_extract_title)

        self.label_page_extract_hint = QLabel(self.page_extract)
        self.label_page_extract_hint.setObjectName(u"label_page_extract_hint")
        self.label_page_extract_hint.setWordWrap(True)

        self.layout_page_extract.addWidget(self.label_page_extract_hint)

        self.splitter_extract = QSplitter(self.page_extract)
        self.splitter_extract.setObjectName(u"splitter_extract")
        self.splitter_extract.setOrientation(Qt.Orientation.Horizontal)
        self.splitter_extract.setHandleWidth(12)
        self.splitter_extract.setChildrenCollapsible(False)
        self.scroll_extract = QScrollArea(self.splitter_extract)
        self.scroll_extract.setObjectName(u"scroll_extract")
        self.scroll_extract.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_extract.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_extract.setWidgetResizable(True)
        self.scroll_extract_contents = QWidget()
        self.scroll_extract_contents.setObjectName(u"scroll_extract_contents")
        self.scroll_extract_contents.setGeometry(QRect(0, 0, 701, 914))
        self.layout_scroll_extract_contents = QVBoxLayout(self.scroll_extract_contents)
        self.layout_scroll_extract_contents.setSpacing(14)
        self.layout_scroll_extract_contents.setObjectName(u"layout_scroll_extract_contents")
        self.layout_scroll_extract_contents.setContentsMargins(0, 0, 10, 0)
        self.card_source = QFrame(self.scroll_extract_contents)
        self.card_source.setObjectName(u"card_source")
        self.card_source.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_source = QVBoxLayout(self.card_source)
        self.layout_card_source.setSpacing(10)
        self.layout_card_source.setObjectName(u"layout_card_source")
        self.layout_card_source.setContentsMargins(18, 16, 18, 18)
        self.label_card_source_title = QLabel(self.card_source)
        self.label_card_source_title.setObjectName(u"label_card_source_title")

        self.layout_card_source.addWidget(self.label_card_source_title)

        self.layout_source_path = QHBoxLayout()
        self.layout_source_path.setSpacing(8)
        self.layout_source_path.setObjectName(u"layout_source_path")
        self.layout_source_path.setContentsMargins(0, 0, 0, 0)
        self.line_edit_xml_folder_path_input = QLineEdit(self.card_source)
        self.line_edit_xml_folder_path_input.setObjectName(u"line_edit_xml_folder_path_input")
        self.line_edit_xml_folder_path_input.setClearButtonEnabled(True)

        self.layout_source_path.addWidget(self.line_edit_xml_folder_path_input)

        self.button_browse_xml_folder = QPushButton(self.card_source)
        self.button_browse_xml_folder.setObjectName(u"button_browse_xml_folder")

        self.layout_source_path.addWidget(self.button_browse_xml_folder)


        self.layout_card_source.addLayout(self.layout_source_path)

        self.statusbar_xml_files_count = QLabel(self.card_source)
        self.statusbar_xml_files_count.setObjectName(u"statusbar_xml_files_count")

        self.layout_card_source.addWidget(self.statusbar_xml_files_count)


        self.layout_scroll_extract_contents.addWidget(self.card_source)

        self.card_builder = QFrame(self.scroll_extract_contents)
        self.card_builder.setObjectName(u"card_builder")
        self.card_builder.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_builder = QVBoxLayout(self.card_builder)
        self.layout_card_builder.setSpacing(10)
        self.layout_card_builder.setObjectName(u"layout_card_builder")
        self.layout_card_builder.setContentsMargins(18, 16, 18, 18)
        self.label_card_builder_title = QLabel(self.card_builder)
        self.label_card_builder_title.setObjectName(u"label_card_builder_title")

        self.layout_card_builder.addWidget(self.label_card_builder_title)

        self.label_xpath_builder = QLabel(self.card_builder)
        self.label_xpath_builder.setObjectName(u"label_xpath_builder")
        self.label_xpath_builder.setWordWrap(True)

        self.layout_card_builder.addWidget(self.label_xpath_builder)

        self.layout_builder_grid = QGridLayout()
        self.layout_builder_grid.setSpacing(10)
        self.layout_builder_grid.setObjectName(u"layout_builder_grid")
        self.layout_builder_grid.setContentsMargins(0, 4, 0, 4)
        self.label_tag_names = QLabel(self.card_builder)
        self.label_tag_names.setObjectName(u"label_tag_names")

        self.layout_builder_grid.addWidget(self.label_tag_names, 0, 0, 1, 1)

        self.combobox_tag_names = QComboBox(self.card_builder)
        self.combobox_tag_names.setObjectName(u"combobox_tag_names")
        self.combobox_tag_names.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combobox_tag_names.setMinimumContentsLength(12)

        self.layout_builder_grid.addWidget(self.combobox_tag_names, 0, 1, 1, 1)

        self.label_tag_values = QLabel(self.card_builder)
        self.label_tag_values.setObjectName(u"label_tag_values")

        self.layout_builder_grid.addWidget(self.label_tag_values, 0, 2, 1, 1)

        self.combobox_tag_values = QComboBox(self.card_builder)
        self.combobox_tag_values.setObjectName(u"combobox_tag_values")
        self.combobox_tag_values.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combobox_tag_values.setMinimumContentsLength(12)

        self.layout_builder_grid.addWidget(self.combobox_tag_values, 0, 3, 1, 1)

        self.label_attribute_names = QLabel(self.card_builder)
        self.label_attribute_names.setObjectName(u"label_attribute_names")

        self.layout_builder_grid.addWidget(self.label_attribute_names, 1, 0, 1, 1)

        self.combobox_attribute_names = QComboBox(self.card_builder)
        self.combobox_attribute_names.setObjectName(u"combobox_attribute_names")
        self.combobox_attribute_names.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combobox_attribute_names.setMinimumContentsLength(12)

        self.layout_builder_grid.addWidget(self.combobox_attribute_names, 1, 1, 1, 1)

        self.label_attribute_values = QLabel(self.card_builder)
        self.label_attribute_values.setObjectName(u"label_attribute_values")

        self.layout_builder_grid.addWidget(self.label_attribute_values, 1, 2, 1, 1)

        self.combobox_attribute_values = QComboBox(self.card_builder)
        self.combobox_attribute_values.setObjectName(u"combobox_attribute_values")
        self.combobox_attribute_values.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combobox_attribute_values.setMinimumContentsLength(12)

        self.layout_builder_grid.addWidget(self.combobox_attribute_values, 1, 3, 1, 1)

        self.label_function = QLabel(self.card_builder)
        self.label_function.setObjectName(u"label_function")

        self.layout_builder_grid.addWidget(self.label_function, 2, 0, 1, 1)

        self.layout_match_function = QHBoxLayout()
        self.layout_match_function.setSpacing(16)
        self.layout_match_function.setObjectName(u"layout_match_function")
        self.layout_match_function.setContentsMargins(0, 0, 0, 0)
        self.radio_button_equals = QRadioButton(self.card_builder)
        self.radio_button_equals.setObjectName(u"radio_button_equals")
        self.radio_button_equals.setChecked(True)

        self.layout_match_function.addWidget(self.radio_button_equals)

        self.radio_button_contains = QRadioButton(self.card_builder)
        self.radio_button_contains.setObjectName(u"radio_button_contains")

        self.layout_match_function.addWidget(self.radio_button_contains)

        self.radio_button_starts_with = QRadioButton(self.card_builder)
        self.radio_button_starts_with.setObjectName(u"radio_button_starts_with")

        self.layout_match_function.addWidget(self.radio_button_starts_with)

        self.radio_button_greater = QRadioButton(self.card_builder)
        self.radio_button_greater.setObjectName(u"radio_button_greater")

        self.layout_match_function.addWidget(self.radio_button_greater)

        self.radio_button_smaller = QRadioButton(self.card_builder)
        self.radio_button_smaller.setObjectName(u"radio_button_smaller")

        self.layout_match_function.addWidget(self.radio_button_smaller)

        self.spacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_match_function.addItem(self.spacer_3)


        self.layout_builder_grid.addLayout(self.layout_match_function, 2, 1, 1, 3)

        self.layout_builder_grid.setColumnStretch(1, 1)
        self.layout_builder_grid.setColumnStretch(3, 1)

        self.layout_card_builder.addLayout(self.layout_builder_grid)

        self.layout_builder_expression = QHBoxLayout()
        self.layout_builder_expression.setSpacing(8)
        self.layout_builder_expression.setObjectName(u"layout_builder_expression")
        self.layout_builder_expression.setContentsMargins(0, 0, 0, 0)
        self.line_edit_xpath_builder = QLineEdit(self.card_builder)
        self.line_edit_xpath_builder.setObjectName(u"line_edit_xpath_builder")
        self.line_edit_xpath_builder.setClearButtonEnabled(True)

        self.layout_builder_expression.addWidget(self.line_edit_xpath_builder)

        self.button_build_xpath = QPushButton(self.card_builder)
        self.button_build_xpath.setObjectName(u"button_build_xpath")

        self.layout_builder_expression.addWidget(self.button_build_xpath)

        self.button_add_xpath_to_list = QPushButton(self.card_builder)
        self.button_add_xpath_to_list.setObjectName(u"button_add_xpath_to_list")

        self.layout_builder_expression.addWidget(self.button_add_xpath_to_list)


        self.layout_card_builder.addLayout(self.layout_builder_expression)


        self.layout_scroll_extract_contents.addWidget(self.card_builder)

        self.card_expressions = QFrame(self.scroll_extract_contents)
        self.card_expressions.setObjectName(u"card_expressions")
        self.card_expressions.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_expressions = QVBoxLayout(self.card_expressions)
        self.layout_card_expressions.setSpacing(10)
        self.layout_card_expressions.setObjectName(u"layout_card_expressions")
        self.layout_card_expressions.setContentsMargins(18, 16, 18, 18)
        self.label_card_expressions_title = QLabel(self.card_expressions)
        self.label_card_expressions_title.setObjectName(u"label_card_expressions_title")

        self.layout_card_expressions.addWidget(self.label_card_expressions_title)

        self.label_card_expressions_hint = QLabel(self.card_expressions)
        self.label_card_expressions_hint.setObjectName(u"label_card_expressions_hint")
        self.label_card_expressions_hint.setWordWrap(True)

        self.layout_card_expressions.addWidget(self.label_card_expressions_hint)

        self.list_widget_main_xpath_expressions = QListWidget(self.card_expressions)
        self.list_widget_main_xpath_expressions.setObjectName(u"list_widget_main_xpath_expressions")
        self.list_widget_main_xpath_expressions.setMinimumSize(QSize(0, 140))
        self.list_widget_main_xpath_expressions.setAlternatingRowColors(True)
        self.list_widget_main_xpath_expressions.setUniformItemSizes(True)
        self.list_widget_main_xpath_expressions.setSortingEnabled(False)

        self.layout_card_expressions.addWidget(self.list_widget_main_xpath_expressions)


        self.layout_scroll_extract_contents.addWidget(self.card_expressions)

        self.card_export = QFrame(self.scroll_extract_contents)
        self.card_export.setObjectName(u"card_export")
        self.card_export.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_export = QVBoxLayout(self.card_export)
        self.layout_card_export.setSpacing(10)
        self.layout_card_export.setObjectName(u"layout_card_export")
        self.layout_card_export.setContentsMargins(18, 16, 18, 18)
        self.label_card_export_title = QLabel(self.card_export)
        self.label_card_export_title.setObjectName(u"label_card_export_title")

        self.layout_card_export.addWidget(self.label_card_export_title)

        self.layout_export_form = QFormLayout()
        self.layout_export_form.setObjectName(u"layout_export_form")
        self.layout_export_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_export_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.layout_export_form.setHorizontalSpacing(10)
        self.layout_export_form.setVerticalSpacing(10)
        self.layout_export_form.setContentsMargins(0, 4, 0, 4)
        self.label_csv_headers_info = QLabel(self.card_export)
        self.label_csv_headers_info.setObjectName(u"label_csv_headers_info")

        self.layout_export_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_csv_headers_info)

        self.line_edit_csv_headers_input = QLineEdit(self.card_export)
        self.line_edit_csv_headers_input.setObjectName(u"line_edit_csv_headers_input")
        self.line_edit_csv_headers_input.setClearButtonEnabled(True)

        self.layout_export_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.line_edit_csv_headers_input)

        self.label_csv_output = QLabel(self.card_export)
        self.label_csv_output.setObjectName(u"label_csv_output")

        self.layout_export_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_csv_output)

        self.layout_csv_output = QHBoxLayout()
        self.layout_csv_output.setSpacing(8)
        self.layout_csv_output.setObjectName(u"layout_csv_output")
        self.layout_csv_output.setContentsMargins(0, 0, 0, 0)
        self.line_edit_csv_output_path = QLineEdit(self.card_export)
        self.line_edit_csv_output_path.setObjectName(u"line_edit_csv_output_path")
        self.line_edit_csv_output_path.setClearButtonEnabled(True)

        self.layout_csv_output.addWidget(self.line_edit_csv_output_path)

        self.button_browse_csv = QPushButton(self.card_export)
        self.button_browse_csv.setObjectName(u"button_browse_csv")

        self.layout_csv_output.addWidget(self.button_browse_csv)


        self.layout_export_form.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_csv_output)

        self.label_options = QLabel(self.card_export)
        self.label_options.setObjectName(u"label_options")

        self.layout_export_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_options)

        self.layout_export_options = QHBoxLayout()
        self.layout_export_options.setSpacing(8)
        self.layout_export_options.setObjectName(u"layout_export_options")
        self.layout_export_options.setContentsMargins(0, 0, 0, 0)
        self.checkbox_group_matches = QCheckBox(self.card_export)
        self.checkbox_group_matches.setObjectName(u"checkbox_group_matches")

        self.layout_export_options.addWidget(self.checkbox_group_matches)

        self.spacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_export_options.addItem(self.spacer_4)

        self.button_pass_csv_to_converter = QLabel(self.card_export)
        self.button_pass_csv_to_converter.setObjectName(u"button_pass_csv_to_converter")
        self.button_pass_csv_to_converter.setTextFormat(Qt.TextFormat.RichText)

        self.layout_export_options.addWidget(self.button_pass_csv_to_converter)


        self.layout_export_form.setLayout(2, QFormLayout.ItemRole.FieldRole, self.layout_export_options)


        self.layout_card_export.addLayout(self.layout_export_form)

        self.layout_export_actions = QHBoxLayout()
        self.layout_export_actions.setSpacing(12)
        self.layout_export_actions.setObjectName(u"layout_export_actions")
        self.layout_export_actions.setContentsMargins(0, 0, 0, 0)
        self.label_file_processing = QLabel(self.card_export)
        self.label_file_processing.setObjectName(u"label_file_processing")

        self.layout_export_actions.addWidget(self.label_file_processing)

        self.progressbar_main = QProgressBar(self.card_export)
        self.progressbar_main.setObjectName(u"progressbar_main")
        self.progressbar_main.setMaximumSize(QSize(16777215, 8))
        self.progressbar_main.setValue(0)
        self.progressbar_main.setTextVisible(False)

        self.layout_export_actions.addWidget(self.progressbar_main)

        self.spacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_export_actions.addItem(self.spacer_5)

        self.button_abort_csv_export = QPushButton(self.card_export)
        self.button_abort_csv_export.setObjectName(u"button_abort_csv_export")

        self.layout_export_actions.addWidget(self.button_abort_csv_export)

        self.button_start_csv_export = QPushButton(self.card_export)
        self.button_start_csv_export.setObjectName(u"button_start_csv_export")

        self.layout_export_actions.addWidget(self.button_start_csv_export)


        self.layout_card_export.addLayout(self.layout_export_actions)


        self.layout_scroll_extract_contents.addWidget(self.card_export)

        self.spacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_scroll_extract_contents.addItem(self.spacer_6)

        self.scroll_extract.setWidget(self.scroll_extract_contents)
        self.splitter_extract.addWidget(self.scroll_extract)
        self.card_preview = QFrame(self.splitter_extract)
        self.card_preview.setObjectName(u"card_preview")
        self.card_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_preview = QVBoxLayout(self.card_preview)
        self.layout_card_preview.setSpacing(10)
        self.layout_card_preview.setObjectName(u"layout_card_preview")
        self.layout_card_preview.setContentsMargins(18, 16, 18, 18)
        self.layout_preview_header = QHBoxLayout()
        self.layout_preview_header.setSpacing(8)
        self.layout_preview_header.setObjectName(u"layout_preview_header")
        self.layout_preview_header.setContentsMargins(0, 0, 0, 0)
        self.label_card_preview_title = QLabel(self.card_preview)
        self.label_card_preview_title.setObjectName(u"label_card_preview_title")

        self.layout_preview_header.addWidget(self.label_card_preview_title)

        self.spacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_preview_header.addItem(self.spacer_7)

        self.label_preview_shortcut = QLabel(self.card_preview)
        self.label_preview_shortcut.setObjectName(u"label_preview_shortcut")
        self.label_preview_shortcut.setWordWrap(True)

        self.layout_preview_header.addWidget(self.label_preview_shortcut)


        self.layout_card_preview.addLayout(self.layout_preview_header)

        self.text_edit_xml_output = QPlainTextEdit(self.card_preview)
        self.text_edit_xml_output.setObjectName(u"text_edit_xml_output")
        self.text_edit_xml_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.text_edit_xml_output.setReadOnly(True)

        self.layout_card_preview.addWidget(self.text_edit_xml_output)

        self.button_read_xml = QPushButton(self.card_preview)
        self.button_read_xml.setObjectName(u"button_read_xml")

        self.layout_card_preview.addWidget(self.button_read_xml)

        self.layout_preview_find = QHBoxLayout()
        self.layout_preview_find.setSpacing(8)
        self.layout_preview_find.setObjectName(u"layout_preview_find")
        self.layout_preview_find.setContentsMargins(0, 0, 0, 0)
        self.line_edit_xml_output_find_text = QLineEdit(self.card_preview)
        self.line_edit_xml_output_find_text.setObjectName(u"line_edit_xml_output_find_text")
        self.line_edit_xml_output_find_text.setClearButtonEnabled(True)

        self.layout_preview_find.addWidget(self.line_edit_xml_output_find_text)

        self.button_find_previous = QPushButton(self.card_preview)
        self.button_find_previous.setObjectName(u"button_find_previous")

        self.layout_preview_find.addWidget(self.button_find_previous)

        self.button_find_next = QPushButton(self.card_preview)
        self.button_find_next.setObjectName(u"button_find_next")

        self.layout_preview_find.addWidget(self.button_find_next)


        self.layout_card_preview.addLayout(self.layout_preview_find)

        self.splitter_extract.addWidget(self.card_preview)

        self.layout_page_extract.addWidget(self.splitter_extract)

        self.layout_page_extract.setStretch(2, 1)
        self.stacked_pages.addWidget(self.page_extract)
        self.page_xml_tools = QWidget()
        self.page_xml_tools.setObjectName(u"page_xml_tools")
        self.layout_page_xml_tools = QVBoxLayout(self.page_xml_tools)
        self.layout_page_xml_tools.setSpacing(12)
        self.layout_page_xml_tools.setObjectName(u"layout_page_xml_tools")
        self.layout_page_xml_tools.setContentsMargins(28, 24, 28, 20)
        self.label_page_xml_tools_title = QLabel(self.page_xml_tools)
        self.label_page_xml_tools_title.setObjectName(u"label_page_xml_tools_title")

        self.layout_page_xml_tools.addWidget(self.label_page_xml_tools_title)

        self.label_page_xml_tools_hint = QLabel(self.page_xml_tools)
        self.label_page_xml_tools_hint.setObjectName(u"label_page_xml_tools_hint")
        self.label_page_xml_tools_hint.setWordWrap(True)

        self.layout_page_xml_tools.addWidget(self.label_page_xml_tools_hint)

        self.tab_widget_xml_tools = QTabWidget(self.page_xml_tools)
        self.tab_widget_xml_tools.setObjectName(u"tab_widget_xml_tools")
        self.tab_widget_xml_tools.setUsesScrollButtons(True)
        self.tab_widget_xml_tools.setDocumentMode(True)
        self.tab_xml_validate = QWidget()
        self.tab_xml_validate.setObjectName(u"tab_xml_validate")
        self.layout_tab_xml_validate = QVBoxLayout(self.tab_xml_validate)
        self.layout_tab_xml_validate.setSpacing(0)
        self.layout_tab_xml_validate.setObjectName(u"layout_tab_xml_validate")
        self.layout_tab_xml_validate.setContentsMargins(0, 16, 0, 0)
        self.scroll_tab_xml_validate = QScrollArea(self.tab_xml_validate)
        self.scroll_tab_xml_validate.setObjectName(u"scroll_tab_xml_validate")
        self.scroll_tab_xml_validate.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_tab_xml_validate.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_tab_xml_validate.setWidgetResizable(True)
        self.scroll_tab_xml_validate_contents = QWidget()
        self.scroll_tab_xml_validate_contents.setObjectName(u"scroll_tab_xml_validate_contents")
        self.layout_scroll_tab_xml_validate_contents = QVBoxLayout(self.scroll_tab_xml_validate_contents)
        self.layout_scroll_tab_xml_validate_contents.setSpacing(14)
        self.layout_scroll_tab_xml_validate_contents.setObjectName(u"layout_scroll_tab_xml_validate_contents")
        self.layout_scroll_tab_xml_validate_contents.setContentsMargins(0, 0, 10, 0)
        self.card_validate = QFrame(self.scroll_tab_xml_validate_contents)
        self.card_validate.setObjectName(u"card_validate")
        self.card_validate.setMaximumSize(QSize(860, 16777215))
        self.card_validate.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_validate = QVBoxLayout(self.card_validate)
        self.layout_card_validate.setSpacing(10)
        self.layout_card_validate.setObjectName(u"layout_card_validate")
        self.layout_card_validate.setContentsMargins(18, 16, 18, 18)
        self.label_card_validate_title = QLabel(self.card_validate)
        self.label_card_validate_title.setObjectName(u"label_card_validate_title")

        self.layout_card_validate.addWidget(self.label_card_validate_title)

        self.label_card_validate_hint = QLabel(self.card_validate)
        self.label_card_validate_hint.setObjectName(u"label_card_validate_hint")
        self.label_card_validate_hint.setWordWrap(True)

        self.layout_card_validate.addWidget(self.label_card_validate_hint)

        self.layout_validate_form = QFormLayout()
        self.layout_validate_form.setObjectName(u"layout_validate_form")
        self.layout_validate_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_validate_form.setHorizontalSpacing(10)
        self.layout_validate_form.setVerticalSpacing(10)
        self.layout_validate_form.setContentsMargins(0, 4, 0, 4)
        self.label_validate_schema = QLabel(self.card_validate)
        self.label_validate_schema.setObjectName(u"label_validate_schema")

        self.layout_validate_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_validate_schema)

        self.layout_validate_schema = QHBoxLayout()
        self.layout_validate_schema.setSpacing(8)
        self.layout_validate_schema.setObjectName(u"layout_validate_schema")
        self.layout_validate_schema.setContentsMargins(0, 0, 0, 0)
        self.line_edit_validate_schema_path = QLineEdit(self.card_validate)
        self.line_edit_validate_schema_path.setObjectName(u"line_edit_validate_schema_path")
        self.line_edit_validate_schema_path.setClearButtonEnabled(True)

        self.layout_validate_schema.addWidget(self.line_edit_validate_schema_path)

        self.button_validate_browse_schema = QPushButton(self.card_validate)
        self.button_validate_browse_schema.setObjectName(u"button_validate_browse_schema")

        self.layout_validate_schema.addWidget(self.button_validate_browse_schema)


        self.layout_validate_form.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layout_validate_schema)

        self.label_validate_xml = QLabel(self.card_validate)
        self.label_validate_xml.setObjectName(u"label_validate_xml")

        self.layout_validate_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_validate_xml)

        self.layout_validate_xml = QHBoxLayout()
        self.layout_validate_xml.setSpacing(8)
        self.layout_validate_xml.setObjectName(u"layout_validate_xml")
        self.layout_validate_xml.setContentsMargins(0, 0, 0, 0)
        self.line_edit_validate_xml_path = QLineEdit(self.card_validate)
        self.line_edit_validate_xml_path.setObjectName(u"line_edit_validate_xml_path")
        self.line_edit_validate_xml_path.setClearButtonEnabled(True)

        self.layout_validate_xml.addWidget(self.line_edit_validate_xml_path)

        self.button_validate_browse_file = QPushButton(self.card_validate)
        self.button_validate_browse_file.setObjectName(u"button_validate_browse_file")

        self.layout_validate_xml.addWidget(self.button_validate_browse_file)

        self.button_validate_browse_folder = QPushButton(self.card_validate)
        self.button_validate_browse_folder.setObjectName(u"button_validate_browse_folder")

        self.layout_validate_xml.addWidget(self.button_validate_browse_folder)


        self.layout_validate_form.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_validate_xml)


        self.layout_card_validate.addLayout(self.layout_validate_form)

        self.layout_validate_actions = QHBoxLayout()
        self.layout_validate_actions.setSpacing(12)
        self.layout_validate_actions.setObjectName(u"layout_validate_actions")
        self.layout_validate_actions.setContentsMargins(0, 0, 0, 0)
        self.busy_bar_validate = BusyBar(self.card_validate)
        self.busy_bar_validate.setObjectName(u"busy_bar_validate")
        self.busy_bar_validate.setMinimumSize(QSize(120, 6))
        self.busy_bar_validate.setMaximumSize(QSize(16777215, 6))

        self.layout_validate_actions.addWidget(self.busy_bar_validate)

        self.label_validate_progress = QLabel(self.card_validate)
        self.label_validate_progress.setObjectName(u"label_validate_progress")

        self.layout_validate_actions.addWidget(self.label_validate_progress)

        self.button_validate_cancel = QPushButton(self.card_validate)
        self.button_validate_cancel.setObjectName(u"button_validate_cancel")

        self.layout_validate_actions.addWidget(self.button_validate_cancel)

        self.button_validate_start = QPushButton(self.card_validate)
        self.button_validate_start.setObjectName(u"button_validate_start")
        self.button_validate_start.setMinimumSize(QSize(120, 0))

        self.layout_validate_actions.addWidget(self.button_validate_start)

        self.layout_validate_actions.setStretch(0, 1)

        self.layout_card_validate.addLayout(self.layout_validate_actions)

        self.frame_validate_result = QFrame(self.card_validate)
        self.frame_validate_result.setObjectName(u"frame_validate_result")
        self.frame_validate_result.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_validate_result = QVBoxLayout(self.frame_validate_result)
        self.layout_validate_result.setSpacing(6)
        self.layout_validate_result.setObjectName(u"layout_validate_result")
        self.layout_validate_result.setContentsMargins(14, 8, 8, 8)
        self.label_validate_summary = QLabel(self.frame_validate_result)
        self.label_validate_summary.setObjectName(u"label_validate_summary")
        self.label_validate_summary.setWordWrap(True)

        self.layout_validate_result.addWidget(self.label_validate_summary)

        self.text_edit_validate_problems = QPlainTextEdit(self.frame_validate_result)
        self.text_edit_validate_problems.setObjectName(u"text_edit_validate_problems")
        self.text_edit_validate_problems.setMinimumSize(QSize(0, 240))
        self.text_edit_validate_problems.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.text_edit_validate_problems.setReadOnly(True)

        self.layout_validate_result.addWidget(self.text_edit_validate_problems)

        self.layout_validate_result_path = QHBoxLayout()
        self.layout_validate_result_path.setSpacing(10)
        self.layout_validate_result_path.setObjectName(u"layout_validate_result_path")
        self.layout_validate_result_path.setContentsMargins(0, 0, 0, 0)
        self.label_validate_result = QLabel(self.frame_validate_result)
        self.label_validate_result.setObjectName(u"label_validate_result")

        self.layout_validate_result_path.addWidget(self.label_validate_result)

        self.line_edit_validate_result_path = QLineEdit(self.frame_validate_result)
        self.line_edit_validate_result_path.setObjectName(u"line_edit_validate_result_path")
        self.line_edit_validate_result_path.setFrame(False)
        self.line_edit_validate_result_path.setReadOnly(True)

        self.layout_validate_result_path.addWidget(self.line_edit_validate_result_path)

        self.button_validate_open_report = QPushButton(self.frame_validate_result)
        self.button_validate_open_report.setObjectName(u"button_validate_open_report")

        self.layout_validate_result_path.addWidget(self.button_validate_open_report)


        self.layout_validate_result.addLayout(self.layout_validate_result_path)


        self.layout_card_validate.addWidget(self.frame_validate_result)


        self.layout_scroll_tab_xml_validate_contents.addWidget(self.card_validate)

        self.spacer_xml_101 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_scroll_tab_xml_validate_contents.addItem(self.spacer_xml_101)

        self.scroll_tab_xml_validate.setWidget(self.scroll_tab_xml_validate_contents)

        self.layout_tab_xml_validate.addWidget(self.scroll_tab_xml_validate)

        self.tab_widget_xml_tools.addTab(self.tab_xml_validate, "")
        self.tab_xml_compare = QWidget()
        self.tab_xml_compare.setObjectName(u"tab_xml_compare")
        self.layout_tab_xml_compare = QVBoxLayout(self.tab_xml_compare)
        self.layout_tab_xml_compare.setSpacing(0)
        self.layout_tab_xml_compare.setObjectName(u"layout_tab_xml_compare")
        self.layout_tab_xml_compare.setContentsMargins(0, 16, 0, 0)
        self.scroll_tab_xml_compare = QScrollArea(self.tab_xml_compare)
        self.scroll_tab_xml_compare.setObjectName(u"scroll_tab_xml_compare")
        self.scroll_tab_xml_compare.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_tab_xml_compare.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_tab_xml_compare.setWidgetResizable(True)
        self.scroll_tab_xml_compare_contents = QWidget()
        self.scroll_tab_xml_compare_contents.setObjectName(u"scroll_tab_xml_compare_contents")
        self.layout_scroll_tab_xml_compare_contents = QVBoxLayout(self.scroll_tab_xml_compare_contents)
        self.layout_scroll_tab_xml_compare_contents.setSpacing(14)
        self.layout_scroll_tab_xml_compare_contents.setObjectName(u"layout_scroll_tab_xml_compare_contents")
        self.layout_scroll_tab_xml_compare_contents.setContentsMargins(0, 0, 10, 0)
        self.card_xml_compare = QFrame(self.scroll_tab_xml_compare_contents)
        self.card_xml_compare.setObjectName(u"card_xml_compare")
        self.card_xml_compare.setMaximumSize(QSize(860, 16777215))
        self.card_xml_compare.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_xml_compare = QVBoxLayout(self.card_xml_compare)
        self.layout_card_xml_compare.setSpacing(10)
        self.layout_card_xml_compare.setObjectName(u"layout_card_xml_compare")
        self.layout_card_xml_compare.setContentsMargins(18, 16, 18, 18)
        self.label_card_xml_compare_title = QLabel(self.card_xml_compare)
        self.label_card_xml_compare_title.setObjectName(u"label_card_xml_compare_title")

        self.layout_card_xml_compare.addWidget(self.label_card_xml_compare_title)

        self.label_card_xml_compare_hint = QLabel(self.card_xml_compare)
        self.label_card_xml_compare_hint.setObjectName(u"label_card_xml_compare_hint")
        self.label_card_xml_compare_hint.setWordWrap(True)

        self.layout_card_xml_compare.addWidget(self.label_card_xml_compare_hint)

        self.layout_xml_compare_form = QFormLayout()
        self.layout_xml_compare_form.setObjectName(u"layout_xml_compare_form")
        self.layout_xml_compare_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_xml_compare_form.setHorizontalSpacing(10)
        self.layout_xml_compare_form.setVerticalSpacing(10)
        self.layout_xml_compare_form.setContentsMargins(0, 4, 0, 4)
        self.label_xml_compare_old = QLabel(self.card_xml_compare)
        self.label_xml_compare_old.setObjectName(u"label_xml_compare_old")

        self.layout_xml_compare_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_xml_compare_old)

        self.layout_xml_compare_old = QHBoxLayout()
        self.layout_xml_compare_old.setSpacing(8)
        self.layout_xml_compare_old.setObjectName(u"layout_xml_compare_old")
        self.layout_xml_compare_old.setContentsMargins(0, 0, 0, 0)
        self.line_edit_xml_compare_old_path = QLineEdit(self.card_xml_compare)
        self.line_edit_xml_compare_old_path.setObjectName(u"line_edit_xml_compare_old_path")
        self.line_edit_xml_compare_old_path.setClearButtonEnabled(True)

        self.layout_xml_compare_old.addWidget(self.line_edit_xml_compare_old_path)

        self.button_xml_compare_old_browse = QPushButton(self.card_xml_compare)
        self.button_xml_compare_old_browse.setObjectName(u"button_xml_compare_old_browse")

        self.layout_xml_compare_old.addWidget(self.button_xml_compare_old_browse)


        self.layout_xml_compare_form.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layout_xml_compare_old)

        self.label_xml_compare_new = QLabel(self.card_xml_compare)
        self.label_xml_compare_new.setObjectName(u"label_xml_compare_new")

        self.layout_xml_compare_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_xml_compare_new)

        self.layout_xml_compare_new = QHBoxLayout()
        self.layout_xml_compare_new.setSpacing(8)
        self.layout_xml_compare_new.setObjectName(u"layout_xml_compare_new")
        self.layout_xml_compare_new.setContentsMargins(0, 0, 0, 0)
        self.line_edit_xml_compare_new_path = QLineEdit(self.card_xml_compare)
        self.line_edit_xml_compare_new_path.setObjectName(u"line_edit_xml_compare_new_path")
        self.line_edit_xml_compare_new_path.setClearButtonEnabled(True)

        self.layout_xml_compare_new.addWidget(self.line_edit_xml_compare_new_path)

        self.button_xml_compare_new_browse = QPushButton(self.card_xml_compare)
        self.button_xml_compare_new_browse.setObjectName(u"button_xml_compare_new_browse")

        self.layout_xml_compare_new.addWidget(self.button_xml_compare_new_browse)


        self.layout_xml_compare_form.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_xml_compare_new)

        self.label_xml_compare_options = QLabel(self.card_xml_compare)
        self.label_xml_compare_options.setObjectName(u"label_xml_compare_options")

        self.layout_xml_compare_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_xml_compare_options)

        self.checkbox_xml_compare_ignore_whitespace = QCheckBox(self.card_xml_compare)
        self.checkbox_xml_compare_ignore_whitespace.setObjectName(u"checkbox_xml_compare_ignore_whitespace")
        self.checkbox_xml_compare_ignore_whitespace.setChecked(True)

        self.layout_xml_compare_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.checkbox_xml_compare_ignore_whitespace)


        self.layout_card_xml_compare.addLayout(self.layout_xml_compare_form)

        self.layout_xml_compare_actions = QHBoxLayout()
        self.layout_xml_compare_actions.setSpacing(12)
        self.layout_xml_compare_actions.setObjectName(u"layout_xml_compare_actions")
        self.layout_xml_compare_actions.setContentsMargins(0, 0, 0, 0)
        self.busy_bar_xml_compare = BusyBar(self.card_xml_compare)
        self.busy_bar_xml_compare.setObjectName(u"busy_bar_xml_compare")
        self.busy_bar_xml_compare.setMinimumSize(QSize(120, 6))
        self.busy_bar_xml_compare.setMaximumSize(QSize(16777215, 6))

        self.layout_xml_compare_actions.addWidget(self.busy_bar_xml_compare)

        self.button_xml_compare_cancel = QPushButton(self.card_xml_compare)
        self.button_xml_compare_cancel.setObjectName(u"button_xml_compare_cancel")

        self.layout_xml_compare_actions.addWidget(self.button_xml_compare_cancel)

        self.button_xml_compare_start = QPushButton(self.card_xml_compare)
        self.button_xml_compare_start.setObjectName(u"button_xml_compare_start")
        self.button_xml_compare_start.setMinimumSize(QSize(120, 0))

        self.layout_xml_compare_actions.addWidget(self.button_xml_compare_start)

        self.layout_xml_compare_actions.setStretch(0, 1)

        self.layout_card_xml_compare.addLayout(self.layout_xml_compare_actions)

        self.frame_xml_compare_result = QFrame(self.card_xml_compare)
        self.frame_xml_compare_result.setObjectName(u"frame_xml_compare_result")
        self.frame_xml_compare_result.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_xml_compare_result = QVBoxLayout(self.frame_xml_compare_result)
        self.layout_xml_compare_result.setSpacing(6)
        self.layout_xml_compare_result.setObjectName(u"layout_xml_compare_result")
        self.layout_xml_compare_result.setContentsMargins(14, 8, 8, 8)
        self.label_xml_compare_summary = QLabel(self.frame_xml_compare_result)
        self.label_xml_compare_summary.setObjectName(u"label_xml_compare_summary")
        self.label_xml_compare_summary.setWordWrap(True)

        self.layout_xml_compare_result.addWidget(self.label_xml_compare_summary)

        self.layout_xml_compare_result_path = QHBoxLayout()
        self.layout_xml_compare_result_path.setSpacing(10)
        self.layout_xml_compare_result_path.setObjectName(u"layout_xml_compare_result_path")
        self.layout_xml_compare_result_path.setContentsMargins(0, 0, 0, 0)
        self.label_xml_compare_result = QLabel(self.frame_xml_compare_result)
        self.label_xml_compare_result.setObjectName(u"label_xml_compare_result")

        self.layout_xml_compare_result_path.addWidget(self.label_xml_compare_result)

        self.line_edit_xml_compare_result_path = QLineEdit(self.frame_xml_compare_result)
        self.line_edit_xml_compare_result_path.setObjectName(u"line_edit_xml_compare_result_path")
        self.line_edit_xml_compare_result_path.setFrame(False)
        self.line_edit_xml_compare_result_path.setReadOnly(True)

        self.layout_xml_compare_result_path.addWidget(self.line_edit_xml_compare_result_path)

        self.button_xml_compare_open_report = QPushButton(self.frame_xml_compare_result)
        self.button_xml_compare_open_report.setObjectName(u"button_xml_compare_open_report")

        self.layout_xml_compare_result_path.addWidget(self.button_xml_compare_open_report)


        self.layout_xml_compare_result.addLayout(self.layout_xml_compare_result_path)


        self.layout_card_xml_compare.addWidget(self.frame_xml_compare_result)


        self.layout_scroll_tab_xml_compare_contents.addWidget(self.card_xml_compare)

        self.card_xml_compare_diff = QFrame(self.scroll_tab_xml_compare_contents)
        self.card_xml_compare_diff.setObjectName(u"card_xml_compare_diff")
        self.card_xml_compare_diff.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_xml_compare_diff = QVBoxLayout(self.card_xml_compare_diff)
        self.layout_card_xml_compare_diff.setSpacing(10)
        self.layout_card_xml_compare_diff.setObjectName(u"layout_card_xml_compare_diff")
        self.layout_card_xml_compare_diff.setContentsMargins(18, 16, 18, 18)
        self.label_card_xml_compare_diff_title = QLabel(self.card_xml_compare_diff)
        self.label_card_xml_compare_diff_title.setObjectName(u"label_card_xml_compare_diff_title")

        self.layout_card_xml_compare_diff.addWidget(self.label_card_xml_compare_diff_title)

        self.label_card_xml_compare_diff_hint = QLabel(self.card_xml_compare_diff)
        self.label_card_xml_compare_diff_hint.setObjectName(u"label_card_xml_compare_diff_hint")
        self.label_card_xml_compare_diff_hint.setWordWrap(True)

        self.layout_card_xml_compare_diff.addWidget(self.label_card_xml_compare_diff_hint)

        self.diff_view_xml_compare = DiffView(self.card_xml_compare_diff)
        self.diff_view_xml_compare.setObjectName(u"diff_view_xml_compare")
        self.diff_view_xml_compare.setMinimumSize(QSize(0, 460))

        self.layout_card_xml_compare_diff.addWidget(self.diff_view_xml_compare)


        self.layout_scroll_tab_xml_compare_contents.addWidget(self.card_xml_compare_diff)

        self.spacer_xml_102 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_scroll_tab_xml_compare_contents.addItem(self.spacer_xml_102)

        self.scroll_tab_xml_compare.setWidget(self.scroll_tab_xml_compare_contents)

        self.layout_tab_xml_compare.addWidget(self.scroll_tab_xml_compare)

        self.tab_widget_xml_tools.addTab(self.tab_xml_compare, "")

        self.layout_page_xml_tools.addWidget(self.tab_widget_xml_tools)

        self.layout_page_xml_tools.setStretch(2, 1)
        self.stacked_pages.addWidget(self.page_xml_tools)
        self.page_csv_tools = QWidget()
        self.page_csv_tools.setObjectName(u"page_csv_tools")
        self.layout_page_csv_tools = QVBoxLayout(self.page_csv_tools)
        self.layout_page_csv_tools.setSpacing(12)
        self.layout_page_csv_tools.setObjectName(u"layout_page_csv_tools")
        self.layout_page_csv_tools.setContentsMargins(28, 24, 28, 20)
        self.label_page_csv_tools_title = QLabel(self.page_csv_tools)
        self.label_page_csv_tools_title.setObjectName(u"label_page_csv_tools_title")

        self.layout_page_csv_tools.addWidget(self.label_page_csv_tools_title)

        self.label_page_csv_tools_hint = QLabel(self.page_csv_tools)
        self.label_page_csv_tools_hint.setObjectName(u"label_page_csv_tools_hint")
        self.label_page_csv_tools_hint.setWordWrap(True)

        self.layout_page_csv_tools.addWidget(self.label_page_csv_tools_hint)

        self.tab_widget_csv_tools = QTabWidget(self.page_csv_tools)
        self.tab_widget_csv_tools.setObjectName(u"tab_widget_csv_tools")
        self.tab_widget_csv_tools.setUsesScrollButtons(True)
        self.tab_widget_csv_tools.setDocumentMode(True)
        self.tab_tool_convert = QWidget()
        self.tab_tool_convert.setObjectName(u"tab_tool_convert")
        self.layout_tab_tool_convert = QVBoxLayout(self.tab_tool_convert)
        self.layout_tab_tool_convert.setSpacing(0)
        self.layout_tab_tool_convert.setObjectName(u"layout_tab_tool_convert")
        self.layout_tab_tool_convert.setContentsMargins(0, 16, 0, 0)
        self.scroll_tab_tool_convert = QScrollArea(self.tab_tool_convert)
        self.scroll_tab_tool_convert.setObjectName(u"scroll_tab_tool_convert")
        self.scroll_tab_tool_convert.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_tab_tool_convert.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_tab_tool_convert.setWidgetResizable(True)
        self.scroll_tab_tool_convert_contents = QWidget()
        self.scroll_tab_tool_convert_contents.setObjectName(u"scroll_tab_tool_convert_contents")
        self.scroll_tab_tool_convert_contents.setGeometry(QRect(0, 0, 439, 368))
        self.layout_scroll_tab_tool_convert_contents = QVBoxLayout(self.scroll_tab_tool_convert_contents)
        self.layout_scroll_tab_tool_convert_contents.setSpacing(14)
        self.layout_scroll_tab_tool_convert_contents.setObjectName(u"layout_scroll_tab_tool_convert_contents")
        self.layout_scroll_tab_tool_convert_contents.setContentsMargins(0, 0, 10, 0)
        self.groupbox_csv_conversion = QFrame(self.scroll_tab_tool_convert_contents)
        self.groupbox_csv_conversion.setObjectName(u"groupbox_csv_conversion")
        self.groupbox_csv_conversion.setMaximumSize(QSize(860, 16777215))
        self.groupbox_csv_conversion.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_groupbox_csv_conversion = QVBoxLayout(self.groupbox_csv_conversion)
        self.layout_groupbox_csv_conversion.setSpacing(10)
        self.layout_groupbox_csv_conversion.setObjectName(u"layout_groupbox_csv_conversion")
        self.layout_groupbox_csv_conversion.setContentsMargins(18, 16, 18, 18)
        self.label_groupbox_csv_conversion_title = QLabel(self.groupbox_csv_conversion)
        self.label_groupbox_csv_conversion_title.setObjectName(u"label_groupbox_csv_conversion_title")

        self.layout_groupbox_csv_conversion.addWidget(self.label_groupbox_csv_conversion_title)

        self.label_csv_conversion_desc = QLabel(self.groupbox_csv_conversion)
        self.label_csv_conversion_desc.setObjectName(u"label_csv_conversion_desc")
        self.label_csv_conversion_desc.setWordWrap(True)

        self.layout_groupbox_csv_conversion.addWidget(self.label_csv_conversion_desc)

        self.layout_conversion_form = QFormLayout()
        self.layout_conversion_form.setObjectName(u"layout_conversion_form")
        self.layout_conversion_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_conversion_form.setHorizontalSpacing(10)
        self.layout_conversion_form.setVerticalSpacing(10)
        self.layout_conversion_form.setContentsMargins(0, 4, 0, 4)
        self.label_conversion_input = QLabel(self.groupbox_csv_conversion)
        self.label_conversion_input.setObjectName(u"label_conversion_input")

        self.layout_conversion_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_conversion_input)

        self.layout_conversion_input = QHBoxLayout()
        self.layout_conversion_input.setSpacing(8)
        self.layout_conversion_input.setObjectName(u"layout_conversion_input")
        self.layout_conversion_input.setContentsMargins(0, 0, 0, 0)
        self.line_edit_csv_conversion_path_input = QLineEdit(self.groupbox_csv_conversion)
        self.line_edit_csv_conversion_path_input.setObjectName(u"line_edit_csv_conversion_path_input")
        self.line_edit_csv_conversion_path_input.setClearButtonEnabled(True)

        self.layout_conversion_input.addWidget(self.line_edit_csv_conversion_path_input)

        self.button_browse_csv_conversion_path_input = QPushButton(self.groupbox_csv_conversion)
        self.button_browse_csv_conversion_path_input.setObjectName(u"button_browse_csv_conversion_path_input")

        self.layout_conversion_input.addWidget(self.button_browse_csv_conversion_path_input)


        self.layout_conversion_form.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layout_conversion_input)

        self.label_csv_conversion_output_type = QLabel(self.groupbox_csv_conversion)
        self.label_csv_conversion_output_type.setObjectName(u"label_csv_conversion_output_type")

        self.layout_conversion_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_csv_conversion_output_type)

        self.layout_conversion_format = QHBoxLayout()
        self.layout_conversion_format.setSpacing(16)
        self.layout_conversion_format.setObjectName(u"layout_conversion_format")
        self.layout_conversion_format.setContentsMargins(0, 0, 0, 0)
        self.combobox_csv_conversion_output_type = QComboBox(self.groupbox_csv_conversion)
        self.combobox_csv_conversion_output_type.addItem("")
        self.combobox_csv_conversion_output_type.addItem("")
        self.combobox_csv_conversion_output_type.addItem("")
        self.combobox_csv_conversion_output_type.addItem("")
        self.combobox_csv_conversion_output_type.addItem("")
        self.combobox_csv_conversion_output_type.setObjectName(u"combobox_csv_conversion_output_type")
        self.combobox_csv_conversion_output_type.setMinimumSize(QSize(160, 0))

        self.layout_conversion_format.addWidget(self.combobox_csv_conversion_output_type)

        self.checkbox_write_index_column = QCheckBox(self.groupbox_csv_conversion)
        self.checkbox_write_index_column.setObjectName(u"checkbox_write_index_column")

        self.layout_conversion_format.addWidget(self.checkbox_write_index_column)

        self.spacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_conversion_format.addItem(self.spacer_8)


        self.layout_conversion_form.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_conversion_format)

        self.label_csv_conversion_delimiter = QLabel(self.groupbox_csv_conversion)
        self.label_csv_conversion_delimiter.setObjectName(u"label_csv_conversion_delimiter")

        self.layout_conversion_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_csv_conversion_delimiter)

        self.layout_conversion_delimiter = QHBoxLayout()
        self.layout_conversion_delimiter.setSpacing(16)
        self.layout_conversion_delimiter.setObjectName(u"layout_conversion_delimiter")
        self.layout_conversion_delimiter.setContentsMargins(0, 0, 0, 0)
        self.checkbox_csv_conversion_manual_delimiter = QCheckBox(self.groupbox_csv_conversion)
        self.checkbox_csv_conversion_manual_delimiter.setObjectName(u"checkbox_csv_conversion_manual_delimiter")

        self.layout_conversion_delimiter.addWidget(self.checkbox_csv_conversion_manual_delimiter)

        self.combobox_csv_conversion_delimiter = QComboBox(self.groupbox_csv_conversion)
        self.combobox_csv_conversion_delimiter.addItem("")
        self.combobox_csv_conversion_delimiter.addItem("")
        self.combobox_csv_conversion_delimiter.addItem("")
        self.combobox_csv_conversion_delimiter.addItem("")
        self.combobox_csv_conversion_delimiter.setObjectName(u"combobox_csv_conversion_delimiter")
        self.combobox_csv_conversion_delimiter.setEnabled(False)
        self.combobox_csv_conversion_delimiter.setMinimumSize(QSize(160, 0))
        self.combobox_csv_conversion_delimiter.setEditable(True)
        self.combobox_csv_conversion_delimiter.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.layout_conversion_delimiter.addWidget(self.combobox_csv_conversion_delimiter)

        self.spacer_20 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_conversion_delimiter.addItem(self.spacer_20)


        self.layout_conversion_form.setLayout(2, QFormLayout.ItemRole.FieldRole, self.layout_conversion_delimiter)


        self.layout_groupbox_csv_conversion.addLayout(self.layout_conversion_form)

        self.layout_conversion_actions = QHBoxLayout()
        self.layout_conversion_actions.setSpacing(12)
        self.layout_conversion_actions.setObjectName(u"layout_conversion_actions")
        self.layout_conversion_actions.setContentsMargins(0, 0, 0, 0)
        self.busy_bar_conversion = BusyBar(self.groupbox_csv_conversion)
        self.busy_bar_conversion.setObjectName(u"busy_bar_conversion")
        self.busy_bar_conversion.setMinimumSize(QSize(120, 6))
        self.busy_bar_conversion.setMaximumSize(QSize(16777215, 6))

        self.layout_conversion_actions.addWidget(self.busy_bar_conversion)

        self.button_csv_conversion_convert = QPushButton(self.groupbox_csv_conversion)
        self.button_csv_conversion_convert.setObjectName(u"button_csv_conversion_convert")
        self.button_csv_conversion_convert.setMinimumSize(QSize(120, 0))

        self.layout_conversion_actions.addWidget(self.button_csv_conversion_convert)

        self.layout_conversion_actions.setStretch(0, 1)

        self.layout_groupbox_csv_conversion.addLayout(self.layout_conversion_actions)

        self.frame_conversion_result = QFrame(self.groupbox_csv_conversion)
        self.frame_conversion_result.setObjectName(u"frame_conversion_result")
        self.frame_conversion_result.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_conversion_result = QVBoxLayout(self.frame_conversion_result)
        self.layout_conversion_result.setSpacing(6)
        self.layout_conversion_result.setObjectName(u"layout_conversion_result")
        self.layout_conversion_result.setContentsMargins(14, 8, 8, 8)
        self.layout_conversion_result_path = QHBoxLayout()
        self.layout_conversion_result_path.setSpacing(10)
        self.layout_conversion_result_path.setObjectName(u"layout_conversion_result_path")
        self.layout_conversion_result_path.setContentsMargins(0, 0, 0, 0)
        self.label_conversion_result = QLabel(self.frame_conversion_result)
        self.label_conversion_result.setObjectName(u"label_conversion_result")

        self.layout_conversion_result_path.addWidget(self.label_conversion_result)

        self.line_edit_csv_conversion_open_file_path = QLineEdit(self.frame_conversion_result)
        self.line_edit_csv_conversion_open_file_path.setObjectName(u"line_edit_csv_conversion_open_file_path")
        self.line_edit_csv_conversion_open_file_path.setFrame(False)
        self.line_edit_csv_conversion_open_file_path.setReadOnly(True)
        self.line_edit_csv_conversion_open_file_path.setClearButtonEnabled(False)

        self.layout_conversion_result_path.addWidget(self.line_edit_csv_conversion_open_file_path)

        self.button_csv_conversion_open_file = QPushButton(self.frame_conversion_result)
        self.button_csv_conversion_open_file.setObjectName(u"button_csv_conversion_open_file")

        self.layout_conversion_result_path.addWidget(self.button_csv_conversion_open_file)

        self.button_csv_conversion_show_folder = QPushButton(self.frame_conversion_result)
        self.button_csv_conversion_show_folder.setObjectName(u"button_csv_conversion_show_folder")

        self.layout_conversion_result_path.addWidget(self.button_csv_conversion_show_folder)


        self.layout_conversion_result.addLayout(self.layout_conversion_result_path)


        self.layout_groupbox_csv_conversion.addWidget(self.frame_conversion_result)


        self.layout_scroll_tab_tool_convert_contents.addWidget(self.groupbox_csv_conversion)

        self.spacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_scroll_tab_tool_convert_contents.addItem(self.spacer_9)

        self.scroll_tab_tool_convert.setWidget(self.scroll_tab_tool_convert_contents)

        self.layout_tab_tool_convert.addWidget(self.scroll_tab_tool_convert)

        self.tab_widget_csv_tools.addTab(self.tab_tool_convert, "")
        self.tab_tool_split = QWidget()
        self.tab_tool_split.setObjectName(u"tab_tool_split")
        self.layout_tab_tool_split = QVBoxLayout(self.tab_tool_split)
        self.layout_tab_tool_split.setSpacing(0)
        self.layout_tab_tool_split.setObjectName(u"layout_tab_tool_split")
        self.layout_tab_tool_split.setContentsMargins(0, 16, 0, 0)
        self.scroll_tab_tool_split = QScrollArea(self.tab_tool_split)
        self.scroll_tab_tool_split.setObjectName(u"scroll_tab_tool_split")
        self.scroll_tab_tool_split.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_tab_tool_split.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_tab_tool_split.setWidgetResizable(True)
        self.scroll_tab_tool_split_contents = QWidget()
        self.scroll_tab_tool_split_contents.setObjectName(u"scroll_tab_tool_split_contents")
        self.scroll_tab_tool_split_contents.setGeometry(QRect(0, 0, 497, 368))
        self.layout_scroll_tab_tool_split_contents = QVBoxLayout(self.scroll_tab_tool_split_contents)
        self.layout_scroll_tab_tool_split_contents.setSpacing(14)
        self.layout_scroll_tab_tool_split_contents.setObjectName(u"layout_scroll_tab_tool_split_contents")
        self.layout_scroll_tab_tool_split_contents.setContentsMargins(0, 0, 10, 0)
        self.card_split = QFrame(self.scroll_tab_tool_split_contents)
        self.card_split.setObjectName(u"card_split")
        self.card_split.setMaximumSize(QSize(860, 16777215))
        self.card_split.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_split = QVBoxLayout(self.card_split)
        self.layout_card_split.setSpacing(10)
        self.layout_card_split.setObjectName(u"layout_card_split")
        self.layout_card_split.setContentsMargins(18, 16, 18, 18)
        self.label_card_split_title = QLabel(self.card_split)
        self.label_card_split_title.setObjectName(u"label_card_split_title")

        self.layout_card_split.addWidget(self.label_card_split_title)

        self.label_card_split_hint = QLabel(self.card_split)
        self.label_card_split_hint.setObjectName(u"label_card_split_hint")
        self.label_card_split_hint.setWordWrap(True)

        self.layout_card_split.addWidget(self.label_card_split_hint)

        self.layout_split_form = QFormLayout()
        self.layout_split_form.setObjectName(u"layout_split_form")
        self.layout_split_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_split_form.setHorizontalSpacing(10)
        self.layout_split_form.setVerticalSpacing(10)
        self.layout_split_form.setContentsMargins(0, 4, 0, 4)
        self.label_split_csv = QLabel(self.card_split)
        self.label_split_csv.setObjectName(u"label_split_csv")

        self.layout_split_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_split_csv)

        self.layout_split_csv = QHBoxLayout()
        self.layout_split_csv.setSpacing(8)
        self.layout_split_csv.setObjectName(u"layout_split_csv")
        self.layout_split_csv.setContentsMargins(0, 0, 0, 0)
        self.line_edit_split_csv_file_path = QLineEdit(self.card_split)
        self.line_edit_split_csv_file_path.setObjectName(u"line_edit_split_csv_file_path")
        self.line_edit_split_csv_file_path.setClearButtonEnabled(True)

        self.layout_split_csv.addWidget(self.line_edit_split_csv_file_path)

        self.button_split_browse_csv_file_path = QPushButton(self.card_split)
        self.button_split_browse_csv_file_path.setObjectName(u"button_split_browse_csv_file_path")

        self.layout_split_csv.addWidget(self.button_split_browse_csv_file_path)


        self.layout_split_form.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layout_split_csv)

        self.label_split_by = QLabel(self.card_split)
        self.label_split_by.setObjectName(u"label_split_by")

        self.layout_split_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_split_by)

        self.layout_split_by = QVBoxLayout()
        self.layout_split_by.setSpacing(8)
        self.layout_split_by.setObjectName(u"layout_split_by")
        self.layout_split_by.setContentsMargins(0, 0, 0, 0)
        self.layout_split_rows = QHBoxLayout()
        self.layout_split_rows.setSpacing(10)
        self.layout_split_rows.setObjectName(u"layout_split_rows")
        self.layout_split_rows.setContentsMargins(0, 0, 0, 0)
        self.radio_split_by_rows = QRadioButton(self.card_split)
        self.radio_split_by_rows.setObjectName(u"radio_split_by_rows")
        self.radio_split_by_rows.setMinimumSize(QSize(130, 0))
        self.radio_split_by_rows.setChecked(True)

        self.layout_split_rows.addWidget(self.radio_split_by_rows)

        self.spin_box_split_rows = QSpinBox(self.card_split)
        self.spin_box_split_rows.setObjectName(u"spin_box_split_rows")
        self.spin_box_split_rows.setMinimumSize(QSize(150, 0))
        self.spin_box_split_rows.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spin_box_split_rows.setMinimum(1)
        self.spin_box_split_rows.setMaximum(100000000)
        self.spin_box_split_rows.setValue(1048575)
        self.spin_box_split_rows.setProperty(u"groupSeparatorShown", True)

        self.layout_split_rows.addWidget(self.spin_box_split_rows)

        self.button_split_excel_rows = QPushButton(self.card_split)
        self.button_split_excel_rows.setObjectName(u"button_split_excel_rows")

        self.layout_split_rows.addWidget(self.button_split_excel_rows)

        self.spacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_split_rows.addItem(self.spacer_10)


        self.layout_split_by.addLayout(self.layout_split_rows)

        self.layout_split_column = QHBoxLayout()
        self.layout_split_column.setSpacing(10)
        self.layout_split_column.setObjectName(u"layout_split_column")
        self.layout_split_column.setContentsMargins(0, 0, 0, 0)
        self.radio_split_by_column = QRadioButton(self.card_split)
        self.radio_split_by_column.setObjectName(u"radio_split_by_column")
        self.radio_split_by_column.setMinimumSize(QSize(130, 0))

        self.layout_split_column.addWidget(self.radio_split_by_column)

        self.combobox_split_column = QComboBox(self.card_split)
        self.combobox_split_column.setObjectName(u"combobox_split_column")
        self.combobox_split_column.setMinimumSize(QSize(220, 0))

        self.layout_split_column.addWidget(self.combobox_split_column)

        self.spacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_split_column.addItem(self.spacer_11)


        self.layout_split_by.addLayout(self.layout_split_column)


        self.layout_split_form.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_split_by)


        self.layout_card_split.addLayout(self.layout_split_form)

        self.layout_split_actions = QHBoxLayout()
        self.layout_split_actions.setSpacing(12)
        self.layout_split_actions.setObjectName(u"layout_split_actions")
        self.layout_split_actions.setContentsMargins(0, 0, 0, 0)
        self.busy_bar_split = BusyBar(self.card_split)
        self.busy_bar_split.setObjectName(u"busy_bar_split")
        self.busy_bar_split.setMinimumSize(QSize(120, 6))
        self.busy_bar_split.setMaximumSize(QSize(16777215, 6))

        self.layout_split_actions.addWidget(self.busy_bar_split)

        self.button_split_cancel = QPushButton(self.card_split)
        self.button_split_cancel.setObjectName(u"button_split_cancel")

        self.layout_split_actions.addWidget(self.button_split_cancel)

        self.button_split_start = QPushButton(self.card_split)
        self.button_split_start.setObjectName(u"button_split_start")
        self.button_split_start.setMinimumSize(QSize(120, 0))

        self.layout_split_actions.addWidget(self.button_split_start)

        self.layout_split_actions.setStretch(0, 1)

        self.layout_card_split.addLayout(self.layout_split_actions)

        self.frame_split_result = QFrame(self.card_split)
        self.frame_split_result.setObjectName(u"frame_split_result")
        self.frame_split_result.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_split_result = QVBoxLayout(self.frame_split_result)
        self.layout_split_result.setSpacing(6)
        self.layout_split_result.setObjectName(u"layout_split_result")
        self.layout_split_result.setContentsMargins(14, 8, 8, 8)
        self.layout_split_result_path = QHBoxLayout()
        self.layout_split_result_path.setSpacing(10)
        self.layout_split_result_path.setObjectName(u"layout_split_result_path")
        self.layout_split_result_path.setContentsMargins(0, 0, 0, 0)
        self.label_split_result = QLabel(self.frame_split_result)
        self.label_split_result.setObjectName(u"label_split_result")

        self.layout_split_result_path.addWidget(self.label_split_result)

        self.line_edit_split_result_path = QLineEdit(self.frame_split_result)
        self.line_edit_split_result_path.setObjectName(u"line_edit_split_result_path")
        self.line_edit_split_result_path.setFrame(False)
        self.line_edit_split_result_path.setReadOnly(True)
        self.line_edit_split_result_path.setClearButtonEnabled(False)

        self.layout_split_result_path.addWidget(self.line_edit_split_result_path)

        self.button_split_show_folder = QPushButton(self.frame_split_result)
        self.button_split_show_folder.setObjectName(u"button_split_show_folder")

        self.layout_split_result_path.addWidget(self.button_split_show_folder)


        self.layout_split_result.addLayout(self.layout_split_result_path)


        self.layout_card_split.addWidget(self.frame_split_result)


        self.layout_scroll_tab_tool_split_contents.addWidget(self.card_split)

        self.spacer_12 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_scroll_tab_tool_split_contents.addItem(self.spacer_12)

        self.scroll_tab_tool_split.setWidget(self.scroll_tab_tool_split_contents)

        self.layout_tab_tool_split.addWidget(self.scroll_tab_tool_split)

        self.tab_widget_csv_tools.addTab(self.tab_tool_split, "")
        self.tab_tool_compare = QWidget()
        self.tab_tool_compare.setObjectName(u"tab_tool_compare")
        self.layout_tab_tool_compare = QVBoxLayout(self.tab_tool_compare)
        self.layout_tab_tool_compare.setSpacing(0)
        self.layout_tab_tool_compare.setObjectName(u"layout_tab_tool_compare")
        self.layout_tab_tool_compare.setContentsMargins(0, 16, 0, 0)
        self.scroll_tab_tool_compare = QScrollArea(self.tab_tool_compare)
        self.scroll_tab_tool_compare.setObjectName(u"scroll_tab_tool_compare")
        self.scroll_tab_tool_compare.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_tab_tool_compare.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_tab_tool_compare.setWidgetResizable(True)
        self.scroll_tab_tool_compare_contents = QWidget()
        self.scroll_tab_tool_compare_contents.setObjectName(u"scroll_tab_tool_compare_contents")
        self.scroll_tab_tool_compare_contents.setGeometry(QRect(0, 0, 438, 424))
        self.layout_scroll_tab_tool_compare_contents = QVBoxLayout(self.scroll_tab_tool_compare_contents)
        self.layout_scroll_tab_tool_compare_contents.setSpacing(14)
        self.layout_scroll_tab_tool_compare_contents.setObjectName(u"layout_scroll_tab_tool_compare_contents")
        self.layout_scroll_tab_tool_compare_contents.setContentsMargins(0, 0, 10, 0)
        self.card_compare = QFrame(self.scroll_tab_tool_compare_contents)
        self.card_compare.setObjectName(u"card_compare")
        self.card_compare.setMaximumSize(QSize(860, 16777215))
        self.card_compare.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_compare = QVBoxLayout(self.card_compare)
        self.layout_card_compare.setSpacing(10)
        self.layout_card_compare.setObjectName(u"layout_card_compare")
        self.layout_card_compare.setContentsMargins(18, 16, 18, 18)
        self.label_card_compare_title = QLabel(self.card_compare)
        self.label_card_compare_title.setObjectName(u"label_card_compare_title")

        self.layout_card_compare.addWidget(self.label_card_compare_title)

        self.label_card_compare_hint = QLabel(self.card_compare)
        self.label_card_compare_hint.setObjectName(u"label_card_compare_hint")
        self.label_card_compare_hint.setWordWrap(True)

        self.layout_card_compare.addWidget(self.label_card_compare_hint)

        self.layout_compare_form = QFormLayout()
        self.layout_compare_form.setObjectName(u"layout_compare_form")
        self.layout_compare_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_compare_form.setHorizontalSpacing(10)
        self.layout_compare_form.setVerticalSpacing(10)
        self.layout_compare_form.setContentsMargins(0, 4, 0, 4)
        self.label_compare_old = QLabel(self.card_compare)
        self.label_compare_old.setObjectName(u"label_compare_old")

        self.layout_compare_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_compare_old)

        self.layout_compare_old_csv = QHBoxLayout()
        self.layout_compare_old_csv.setSpacing(8)
        self.layout_compare_old_csv.setObjectName(u"layout_compare_old_csv")
        self.layout_compare_old_csv.setContentsMargins(0, 0, 0, 0)
        self.line_edit_compare_old_csv_file_path = QLineEdit(self.card_compare)
        self.line_edit_compare_old_csv_file_path.setObjectName(u"line_edit_compare_old_csv_file_path")
        self.line_edit_compare_old_csv_file_path.setClearButtonEnabled(True)

        self.layout_compare_old_csv.addWidget(self.line_edit_compare_old_csv_file_path)

        self.button_compare_old_browse_csv_file_path = QPushButton(self.card_compare)
        self.button_compare_old_browse_csv_file_path.setObjectName(u"button_compare_old_browse_csv_file_path")

        self.layout_compare_old_csv.addWidget(self.button_compare_old_browse_csv_file_path)


        self.layout_compare_form.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layout_compare_old_csv)

        self.label_compare_new = QLabel(self.card_compare)
        self.label_compare_new.setObjectName(u"label_compare_new")

        self.layout_compare_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_compare_new)

        self.layout_compare_new_csv = QHBoxLayout()
        self.layout_compare_new_csv.setSpacing(8)
        self.layout_compare_new_csv.setObjectName(u"layout_compare_new_csv")
        self.layout_compare_new_csv.setContentsMargins(0, 0, 0, 0)
        self.line_edit_compare_new_csv_file_path = QLineEdit(self.card_compare)
        self.line_edit_compare_new_csv_file_path.setObjectName(u"line_edit_compare_new_csv_file_path")
        self.line_edit_compare_new_csv_file_path.setClearButtonEnabled(True)

        self.layout_compare_new_csv.addWidget(self.line_edit_compare_new_csv_file_path)

        self.button_compare_new_browse_csv_file_path = QPushButton(self.card_compare)
        self.button_compare_new_browse_csv_file_path.setObjectName(u"button_compare_new_browse_csv_file_path")

        self.layout_compare_new_csv.addWidget(self.button_compare_new_browse_csv_file_path)


        self.layout_compare_form.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_compare_new_csv)

        self.label_compare_key = QLabel(self.card_compare)
        self.label_compare_key.setObjectName(u"label_compare_key")

        self.layout_compare_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_compare_key)

        self.layout_compare_key = QHBoxLayout()
        self.layout_compare_key.setSpacing(8)
        self.layout_compare_key.setObjectName(u"layout_compare_key")
        self.layout_compare_key.setContentsMargins(0, 0, 0, 0)
        self.combobox_compare_key = QComboBox(self.card_compare)
        self.combobox_compare_key.setObjectName(u"combobox_compare_key")
        self.combobox_compare_key.setMinimumSize(QSize(220, 0))

        self.layout_compare_key.addWidget(self.combobox_compare_key)

        self.spacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_compare_key.addItem(self.spacer_13)


        self.layout_compare_form.setLayout(2, QFormLayout.ItemRole.FieldRole, self.layout_compare_key)

        self.label_compare_options = QLabel(self.card_compare)
        self.label_compare_options.setObjectName(u"label_compare_options")

        self.layout_compare_form.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_compare_options)

        self.checkbox_compare_loose = QCheckBox(self.card_compare)
        self.checkbox_compare_loose.setObjectName(u"checkbox_compare_loose")

        self.layout_compare_form.setWidget(3, QFormLayout.ItemRole.FieldRole, self.checkbox_compare_loose)


        self.layout_card_compare.addLayout(self.layout_compare_form)

        self.layout_compare_actions = QHBoxLayout()
        self.layout_compare_actions.setSpacing(12)
        self.layout_compare_actions.setObjectName(u"layout_compare_actions")
        self.layout_compare_actions.setContentsMargins(0, 0, 0, 0)
        self.busy_bar_compare = BusyBar(self.card_compare)
        self.busy_bar_compare.setObjectName(u"busy_bar_compare")
        self.busy_bar_compare.setMinimumSize(QSize(120, 6))
        self.busy_bar_compare.setMaximumSize(QSize(16777215, 6))

        self.layout_compare_actions.addWidget(self.busy_bar_compare)

        self.button_compare_cancel = QPushButton(self.card_compare)
        self.button_compare_cancel.setObjectName(u"button_compare_cancel")

        self.layout_compare_actions.addWidget(self.button_compare_cancel)

        self.button_compare_start = QPushButton(self.card_compare)
        self.button_compare_start.setObjectName(u"button_compare_start")
        self.button_compare_start.setMinimumSize(QSize(120, 0))

        self.layout_compare_actions.addWidget(self.button_compare_start)

        self.layout_compare_actions.setStretch(0, 1)

        self.layout_card_compare.addLayout(self.layout_compare_actions)

        self.frame_compare_result = QFrame(self.card_compare)
        self.frame_compare_result.setObjectName(u"frame_compare_result")
        self.frame_compare_result.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_compare_result = QVBoxLayout(self.frame_compare_result)
        self.layout_compare_result.setSpacing(6)
        self.layout_compare_result.setObjectName(u"layout_compare_result")
        self.layout_compare_result.setContentsMargins(14, 8, 8, 8)
        self.label_compare_summary = QLabel(self.frame_compare_result)
        self.label_compare_summary.setObjectName(u"label_compare_summary")
        self.label_compare_summary.setWordWrap(True)

        self.layout_compare_result.addWidget(self.label_compare_summary)

        self.layout_compare_result_path = QHBoxLayout()
        self.layout_compare_result_path.setSpacing(10)
        self.layout_compare_result_path.setObjectName(u"layout_compare_result_path")
        self.layout_compare_result_path.setContentsMargins(0, 0, 0, 0)
        self.label_compare_result = QLabel(self.frame_compare_result)
        self.label_compare_result.setObjectName(u"label_compare_result")

        self.layout_compare_result_path.addWidget(self.label_compare_result)

        self.line_edit_compare_result_path = QLineEdit(self.frame_compare_result)
        self.line_edit_compare_result_path.setObjectName(u"line_edit_compare_result_path")
        self.line_edit_compare_result_path.setFrame(False)
        self.line_edit_compare_result_path.setReadOnly(True)
        self.line_edit_compare_result_path.setClearButtonEnabled(False)

        self.layout_compare_result_path.addWidget(self.line_edit_compare_result_path)

        self.button_compare_open_report = QPushButton(self.frame_compare_result)
        self.button_compare_open_report.setObjectName(u"button_compare_open_report")

        self.layout_compare_result_path.addWidget(self.button_compare_open_report)


        self.layout_compare_result.addLayout(self.layout_compare_result_path)


        self.layout_card_compare.addWidget(self.frame_compare_result)


        self.layout_scroll_tab_tool_compare_contents.addWidget(self.card_compare)

        self.card_compare_diff = QFrame(self.scroll_tab_tool_compare_contents)
        self.card_compare_diff.setObjectName(u"card_compare_diff")
        self.card_compare_diff.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_compare_diff = QVBoxLayout(self.card_compare_diff)
        self.layout_card_compare_diff.setSpacing(10)
        self.layout_card_compare_diff.setObjectName(u"layout_card_compare_diff")
        self.layout_card_compare_diff.setContentsMargins(18, 16, 18, 18)
        self.label_card_compare_diff_title = QLabel(self.card_compare_diff)
        self.label_card_compare_diff_title.setObjectName(u"label_card_compare_diff_title")

        self.layout_card_compare_diff.addWidget(self.label_card_compare_diff_title)

        self.label_card_compare_diff_hint = QLabel(self.card_compare_diff)
        self.label_card_compare_diff_hint.setObjectName(u"label_card_compare_diff_hint")
        self.label_card_compare_diff_hint.setWordWrap(True)

        self.layout_card_compare_diff.addWidget(self.label_card_compare_diff_hint)

        self.diff_view_csv_compare = DiffView(self.card_compare_diff)
        self.diff_view_csv_compare.setObjectName(u"diff_view_csv_compare")
        self.diff_view_csv_compare.setMinimumSize(QSize(0, 460))

        self.layout_card_compare_diff.addWidget(self.diff_view_csv_compare)


        self.layout_scroll_tab_tool_compare_contents.addWidget(self.card_compare_diff)

        self.spacer_14 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_scroll_tab_tool_compare_contents.addItem(self.spacer_14)

        self.scroll_tab_tool_compare.setWidget(self.scroll_tab_tool_compare_contents)

        self.layout_tab_tool_compare.addWidget(self.scroll_tab_tool_compare)

        self.tab_widget_csv_tools.addTab(self.tab_tool_compare, "")
        self.tab_tool_columns = QWidget()
        self.tab_tool_columns.setObjectName(u"tab_tool_columns")
        self.layout_tab_tool_columns = QVBoxLayout(self.tab_tool_columns)
        self.layout_tab_tool_columns.setSpacing(0)
        self.layout_tab_tool_columns.setObjectName(u"layout_tab_tool_columns")
        self.layout_tab_tool_columns.setContentsMargins(0, 16, 0, 0)
        self.scroll_tab_tool_columns = QScrollArea(self.tab_tool_columns)
        self.scroll_tab_tool_columns.setObjectName(u"scroll_tab_tool_columns")
        self.scroll_tab_tool_columns.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_tab_tool_columns.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_tab_tool_columns.setWidgetResizable(True)
        self.scroll_tab_tool_columns_contents = QWidget()
        self.scroll_tab_tool_columns_contents.setObjectName(u"scroll_tab_tool_columns_contents")
        self.scroll_tab_tool_columns_contents.setGeometry(QRect(0, 0, 354, 620))
        self.layout_scroll_tab_tool_columns_contents = QVBoxLayout(self.scroll_tab_tool_columns_contents)
        self.layout_scroll_tab_tool_columns_contents.setSpacing(14)
        self.layout_scroll_tab_tool_columns_contents.setObjectName(u"layout_scroll_tab_tool_columns_contents")
        self.layout_scroll_tab_tool_columns_contents.setContentsMargins(0, 0, 10, 0)
        self.card_columns = QFrame(self.scroll_tab_tool_columns_contents)
        self.card_columns.setObjectName(u"card_columns")
        self.card_columns.setMaximumSize(QSize(860, 16777215))
        self.card_columns.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_card_columns = QVBoxLayout(self.card_columns)
        self.layout_card_columns.setSpacing(10)
        self.layout_card_columns.setObjectName(u"layout_card_columns")
        self.layout_card_columns.setContentsMargins(18, 16, 18, 18)
        self.label_card_columns_title = QLabel(self.card_columns)
        self.label_card_columns_title.setObjectName(u"label_card_columns_title")

        self.layout_card_columns.addWidget(self.label_card_columns_title)

        self.label_card_columns_hint = QLabel(self.card_columns)
        self.label_card_columns_hint.setObjectName(u"label_card_columns_hint")
        self.label_card_columns_hint.setWordWrap(True)

        self.layout_card_columns.addWidget(self.label_card_columns_hint)

        self.layout_columns_form = QFormLayout()
        self.layout_columns_form.setObjectName(u"layout_columns_form")
        self.layout_columns_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_columns_form.setHorizontalSpacing(10)
        self.layout_columns_form.setVerticalSpacing(10)
        self.layout_columns_form.setContentsMargins(0, 4, 0, 4)
        self.label_columns_csv = QLabel(self.card_columns)
        self.label_columns_csv.setObjectName(u"label_columns_csv")

        self.layout_columns_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_columns_csv)

        self.layout_columns_csv = QHBoxLayout()
        self.layout_columns_csv.setSpacing(8)
        self.layout_columns_csv.setObjectName(u"layout_columns_csv")
        self.layout_columns_csv.setContentsMargins(0, 0, 0, 0)
        self.line_edit_columns_csv_file_path = QLineEdit(self.card_columns)
        self.line_edit_columns_csv_file_path.setObjectName(u"line_edit_columns_csv_file_path")
        self.line_edit_columns_csv_file_path.setClearButtonEnabled(True)

        self.layout_columns_csv.addWidget(self.line_edit_columns_csv_file_path)

        self.button_columns_browse_csv_file_path = QPushButton(self.card_columns)
        self.button_columns_browse_csv_file_path.setObjectName(u"button_columns_browse_csv_file_path")

        self.layout_columns_csv.addWidget(self.button_columns_browse_csv_file_path)


        self.layout_columns_form.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layout_columns_csv)


        self.layout_card_columns.addLayout(self.layout_columns_form)

        self.layout_columns_editor = QHBoxLayout()
        self.layout_columns_editor.setSpacing(12)
        self.layout_columns_editor.setObjectName(u"layout_columns_editor")
        self.layout_columns_editor.setContentsMargins(0, 0, 0, 0)
        self.list_widget_columns = QListWidget(self.card_columns)
        self.list_widget_columns.setObjectName(u"list_widget_columns")
        self.list_widget_columns.setMinimumSize(QSize(0, 240))
        self.list_widget_columns.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.list_widget_columns.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget_columns.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget_columns.setAlternatingRowColors(True)
        self.list_widget_columns.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.layout_columns_editor.addWidget(self.list_widget_columns)

        self.layout_columns_buttons = QVBoxLayout()
        self.layout_columns_buttons.setSpacing(6)
        self.layout_columns_buttons.setObjectName(u"layout_columns_buttons")
        self.layout_columns_buttons.setContentsMargins(0, 0, 0, 0)
        self.button_columns_up = QPushButton(self.card_columns)
        self.button_columns_up.setObjectName(u"button_columns_up")

        self.layout_columns_buttons.addWidget(self.button_columns_up)

        self.button_columns_down = QPushButton(self.card_columns)
        self.button_columns_down.setObjectName(u"button_columns_down")

        self.layout_columns_buttons.addWidget(self.button_columns_down)

        self.spacer_15 = QSpacerItem(0, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.layout_columns_buttons.addItem(self.spacer_15)

        self.button_columns_all = QPushButton(self.card_columns)
        self.button_columns_all.setObjectName(u"button_columns_all")

        self.layout_columns_buttons.addWidget(self.button_columns_all)

        self.button_columns_none = QPushButton(self.card_columns)
        self.button_columns_none.setObjectName(u"button_columns_none")

        self.layout_columns_buttons.addWidget(self.button_columns_none)

        self.spacer_16 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_columns_buttons.addItem(self.spacer_16)

        self.button_columns_reset = QPushButton(self.card_columns)
        self.button_columns_reset.setObjectName(u"button_columns_reset")

        self.layout_columns_buttons.addWidget(self.button_columns_reset)


        self.layout_columns_editor.addLayout(self.layout_columns_buttons)

        self.layout_columns_editor.setStretch(0, 1)

        self.layout_card_columns.addLayout(self.layout_columns_editor)

        self.label_columns_status = QLabel(self.card_columns)
        self.label_columns_status.setObjectName(u"label_columns_status")
        self.label_columns_status.setWordWrap(True)

        self.layout_card_columns.addWidget(self.label_columns_status)

        self.checkbox_columns_overwrite = QCheckBox(self.card_columns)
        self.checkbox_columns_overwrite.setObjectName(u"checkbox_columns_overwrite")

        self.layout_card_columns.addWidget(self.checkbox_columns_overwrite)

        self.layout_columns_actions = QHBoxLayout()
        self.layout_columns_actions.setSpacing(12)
        self.layout_columns_actions.setObjectName(u"layout_columns_actions")
        self.layout_columns_actions.setContentsMargins(0, 0, 0, 0)
        self.busy_bar_columns = BusyBar(self.card_columns)
        self.busy_bar_columns.setObjectName(u"busy_bar_columns")
        self.busy_bar_columns.setMinimumSize(QSize(120, 6))
        self.busy_bar_columns.setMaximumSize(QSize(16777215, 6))

        self.layout_columns_actions.addWidget(self.busy_bar_columns)

        self.button_columns_save = QPushButton(self.card_columns)
        self.button_columns_save.setObjectName(u"button_columns_save")
        self.button_columns_save.setMinimumSize(QSize(120, 0))

        self.layout_columns_actions.addWidget(self.button_columns_save)

        self.layout_columns_actions.setStretch(0, 1)

        self.layout_card_columns.addLayout(self.layout_columns_actions)

        self.frame_columns_result = QFrame(self.card_columns)
        self.frame_columns_result.setObjectName(u"frame_columns_result")
        self.frame_columns_result.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_columns_result = QVBoxLayout(self.frame_columns_result)
        self.layout_columns_result.setSpacing(6)
        self.layout_columns_result.setObjectName(u"layout_columns_result")
        self.layout_columns_result.setContentsMargins(14, 8, 8, 8)
        self.layout_columns_result_path = QHBoxLayout()
        self.layout_columns_result_path.setSpacing(10)
        self.layout_columns_result_path.setObjectName(u"layout_columns_result_path")
        self.layout_columns_result_path.setContentsMargins(0, 0, 0, 0)
        self.label_columns_result = QLabel(self.frame_columns_result)
        self.label_columns_result.setObjectName(u"label_columns_result")

        self.layout_columns_result_path.addWidget(self.label_columns_result)

        self.line_edit_columns_result_path = QLineEdit(self.frame_columns_result)
        self.line_edit_columns_result_path.setObjectName(u"line_edit_columns_result_path")
        self.line_edit_columns_result_path.setFrame(False)
        self.line_edit_columns_result_path.setReadOnly(True)
        self.line_edit_columns_result_path.setClearButtonEnabled(False)

        self.layout_columns_result_path.addWidget(self.line_edit_columns_result_path)

        self.button_columns_open_result = QPushButton(self.frame_columns_result)
        self.button_columns_open_result.setObjectName(u"button_columns_open_result")

        self.layout_columns_result_path.addWidget(self.button_columns_open_result)

        self.button_columns_show_folder = QPushButton(self.frame_columns_result)
        self.button_columns_show_folder.setObjectName(u"button_columns_show_folder")

        self.layout_columns_result_path.addWidget(self.button_columns_show_folder)


        self.layout_columns_result.addLayout(self.layout_columns_result_path)


        self.layout_card_columns.addWidget(self.frame_columns_result)


        self.layout_scroll_tab_tool_columns_contents.addWidget(self.card_columns)

        self.spacer_17 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_scroll_tab_tool_columns_contents.addItem(self.spacer_17)

        self.scroll_tab_tool_columns.setWidget(self.scroll_tab_tool_columns_contents)

        self.layout_tab_tool_columns.addWidget(self.scroll_tab_tool_columns)

        self.tab_widget_csv_tools.addTab(self.tab_tool_columns, "")
        self.tab_tool_cleanup = QWidget()
        self.tab_tool_cleanup.setObjectName(u"tab_tool_cleanup")
        self.layout_tab_tool_cleanup = QVBoxLayout(self.tab_tool_cleanup)
        self.layout_tab_tool_cleanup.setSpacing(0)
        self.layout_tab_tool_cleanup.setObjectName(u"layout_tab_tool_cleanup")
        self.layout_tab_tool_cleanup.setContentsMargins(0, 16, 0, 0)
        self.scroll_tab_tool_cleanup = QScrollArea(self.tab_tool_cleanup)
        self.scroll_tab_tool_cleanup.setObjectName(u"scroll_tab_tool_cleanup")
        self.scroll_tab_tool_cleanup.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_tab_tool_cleanup.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_tab_tool_cleanup.setWidgetResizable(True)
        self.scroll_tab_tool_cleanup_contents = QWidget()
        self.scroll_tab_tool_cleanup_contents.setObjectName(u"scroll_tab_tool_cleanup_contents")
        self.scroll_tab_tool_cleanup_contents.setGeometry(QRect(0, 0, 338, 288))
        self.layout_scroll_tab_tool_cleanup_contents = QVBoxLayout(self.scroll_tab_tool_cleanup_contents)
        self.layout_scroll_tab_tool_cleanup_contents.setSpacing(14)
        self.layout_scroll_tab_tool_cleanup_contents.setObjectName(u"layout_scroll_tab_tool_cleanup_contents")
        self.layout_scroll_tab_tool_cleanup_contents.setContentsMargins(0, 0, 10, 0)
        self.groupbox_lobster_profiles_cleanup = QFrame(self.scroll_tab_tool_cleanup_contents)
        self.groupbox_lobster_profiles_cleanup.setObjectName(u"groupbox_lobster_profiles_cleanup")
        self.groupbox_lobster_profiles_cleanup.setMaximumSize(QSize(860, 16777215))
        self.groupbox_lobster_profiles_cleanup.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_groupbox_lobster_profiles_cleanup = QVBoxLayout(self.groupbox_lobster_profiles_cleanup)
        self.layout_groupbox_lobster_profiles_cleanup.setSpacing(10)
        self.layout_groupbox_lobster_profiles_cleanup.setObjectName(u"layout_groupbox_lobster_profiles_cleanup")
        self.layout_groupbox_lobster_profiles_cleanup.setContentsMargins(18, 16, 18, 18)
        self.label_groupbox_lobster_profiles_cleanup_title = QLabel(self.groupbox_lobster_profiles_cleanup)
        self.label_groupbox_lobster_profiles_cleanup_title.setObjectName(u"label_groupbox_lobster_profiles_cleanup_title")

        self.layout_groupbox_lobster_profiles_cleanup.addWidget(self.label_groupbox_lobster_profiles_cleanup_title)

        self.label_2 = QLabel(self.groupbox_lobster_profiles_cleanup)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setWordWrap(True)

        self.layout_groupbox_lobster_profiles_cleanup.addWidget(self.label_2)

        self.layout_cleanup_form = QFormLayout()
        self.layout_cleanup_form.setObjectName(u"layout_cleanup_form")
        self.layout_cleanup_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_cleanup_form.setHorizontalSpacing(10)
        self.layout_cleanup_form.setVerticalSpacing(10)
        self.layout_cleanup_form.setContentsMargins(0, 4, 0, 4)
        self.label_cleanup_csv = QLabel(self.groupbox_lobster_profiles_cleanup)
        self.label_cleanup_csv.setObjectName(u"label_cleanup_csv")

        self.layout_cleanup_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_cleanup_csv)

        self.layout_cleanup_csv = QHBoxLayout()
        self.layout_cleanup_csv.setSpacing(8)
        self.layout_cleanup_csv.setObjectName(u"layout_cleanup_csv")
        self.layout_cleanup_csv.setContentsMargins(0, 0, 0, 0)
        self.line_edit_profile_cleanup_csv_file_path = QLineEdit(self.groupbox_lobster_profiles_cleanup)
        self.line_edit_profile_cleanup_csv_file_path.setObjectName(u"line_edit_profile_cleanup_csv_file_path")
        self.line_edit_profile_cleanup_csv_file_path.setClearButtonEnabled(True)

        self.layout_cleanup_csv.addWidget(self.line_edit_profile_cleanup_csv_file_path)

        self.button_profile_cleanup_browse_csv_file_path = QPushButton(self.groupbox_lobster_profiles_cleanup)
        self.button_profile_cleanup_browse_csv_file_path.setObjectName(u"button_profile_cleanup_browse_csv_file_path")

        self.layout_cleanup_csv.addWidget(self.button_profile_cleanup_browse_csv_file_path)


        self.layout_cleanup_form.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layout_cleanup_csv)

        self.label_cleanup_folder = QLabel(self.groupbox_lobster_profiles_cleanup)
        self.label_cleanup_folder.setObjectName(u"label_cleanup_folder")

        self.layout_cleanup_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_cleanup_folder)

        self.layout_cleanup_folder = QHBoxLayout()
        self.layout_cleanup_folder.setSpacing(8)
        self.layout_cleanup_folder.setObjectName(u"layout_cleanup_folder")
        self.layout_cleanup_folder.setContentsMargins(0, 0, 0, 0)
        self.line_edit_profile_cleanup_folder_path = QLineEdit(self.groupbox_lobster_profiles_cleanup)
        self.line_edit_profile_cleanup_folder_path.setObjectName(u"line_edit_profile_cleanup_folder_path")
        self.line_edit_profile_cleanup_folder_path.setClearButtonEnabled(True)

        self.layout_cleanup_folder.addWidget(self.line_edit_profile_cleanup_folder_path)

        self.button_profile_cleanup_browse_folder_path = QPushButton(self.groupbox_lobster_profiles_cleanup)
        self.button_profile_cleanup_browse_folder_path.setObjectName(u"button_profile_cleanup_browse_folder_path")

        self.layout_cleanup_folder.addWidget(self.button_profile_cleanup_browse_folder_path)


        self.layout_cleanup_form.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_cleanup_folder)


        self.layout_groupbox_lobster_profiles_cleanup.addLayout(self.layout_cleanup_form)

        self.layout_cleanup_actions = QHBoxLayout()
        self.layout_cleanup_actions.setSpacing(12)
        self.layout_cleanup_actions.setObjectName(u"layout_cleanup_actions")
        self.layout_cleanup_actions.setContentsMargins(0, 0, 0, 0)
        self.busy_bar_cleanup = BusyBar(self.groupbox_lobster_profiles_cleanup)
        self.busy_bar_cleanup.setObjectName(u"busy_bar_cleanup")
        self.busy_bar_cleanup.setMinimumSize(QSize(120, 6))
        self.busy_bar_cleanup.setMaximumSize(QSize(16777215, 6))

        self.layout_cleanup_actions.addWidget(self.busy_bar_cleanup)

        self.button_profile_cleanup_cleanup_start = QPushButton(self.groupbox_lobster_profiles_cleanup)
        self.button_profile_cleanup_cleanup_start.setObjectName(u"button_profile_cleanup_cleanup_start")

        self.layout_cleanup_actions.addWidget(self.button_profile_cleanup_cleanup_start)

        self.layout_cleanup_actions.setStretch(0, 1)

        self.layout_groupbox_lobster_profiles_cleanup.addLayout(self.layout_cleanup_actions)


        self.layout_scroll_tab_tool_cleanup_contents.addWidget(self.groupbox_lobster_profiles_cleanup)

        self.spacer_18 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_scroll_tab_tool_cleanup_contents.addItem(self.spacer_18)

        self.scroll_tab_tool_cleanup.setWidget(self.scroll_tab_tool_cleanup_contents)

        self.layout_tab_tool_cleanup.addWidget(self.scroll_tab_tool_cleanup)

        self.tab_widget_csv_tools.addTab(self.tab_tool_cleanup, "")
        self.tab_tool_hex = QWidget()
        self.tab_tool_hex.setObjectName(u"tab_tool_hex")
        self.layout_tab_tool_hex = QVBoxLayout(self.tab_tool_hex)
        self.layout_tab_tool_hex.setSpacing(0)
        self.layout_tab_tool_hex.setObjectName(u"layout_tab_tool_hex")
        self.layout_tab_tool_hex.setContentsMargins(0, 16, 0, 0)
        self.scroll_tab_tool_hex = QScrollArea(self.tab_tool_hex)
        self.scroll_tab_tool_hex.setObjectName(u"scroll_tab_tool_hex")
        self.scroll_tab_tool_hex.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_tab_tool_hex.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_tab_tool_hex.setWidgetResizable(True)
        self.scroll_tab_tool_hex_contents = QWidget()
        self.scroll_tab_tool_hex_contents.setObjectName(u"scroll_tab_tool_hex_contents")
        self.scroll_tab_tool_hex_contents.setGeometry(QRect(0, 0, 177, 288))
        self.layout_scroll_tab_tool_hex_contents = QVBoxLayout(self.scroll_tab_tool_hex_contents)
        self.layout_scroll_tab_tool_hex_contents.setSpacing(14)
        self.layout_scroll_tab_tool_hex_contents.setObjectName(u"layout_scroll_tab_tool_hex_contents")
        self.layout_scroll_tab_tool_hex_contents.setContentsMargins(0, 0, 10, 0)
        self.groupbox_hexadecimal_to_decimal = QFrame(self.scroll_tab_tool_hex_contents)
        self.groupbox_hexadecimal_to_decimal.setObjectName(u"groupbox_hexadecimal_to_decimal")
        self.groupbox_hexadecimal_to_decimal.setMaximumSize(QSize(860, 16777215))
        self.groupbox_hexadecimal_to_decimal.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_groupbox_hexadecimal_to_decimal = QVBoxLayout(self.groupbox_hexadecimal_to_decimal)
        self.layout_groupbox_hexadecimal_to_decimal.setSpacing(10)
        self.layout_groupbox_hexadecimal_to_decimal.setObjectName(u"layout_groupbox_hexadecimal_to_decimal")
        self.layout_groupbox_hexadecimal_to_decimal.setContentsMargins(18, 16, 18, 18)
        self.label_groupbox_hexadecimal_to_decimal_title = QLabel(self.groupbox_hexadecimal_to_decimal)
        self.label_groupbox_hexadecimal_to_decimal_title.setObjectName(u"label_groupbox_hexadecimal_to_decimal_title")

        self.layout_groupbox_hexadecimal_to_decimal.addWidget(self.label_groupbox_hexadecimal_to_decimal_title)

        self.label_groupbox_hexadecimal_to_decimal_hint = QLabel(self.groupbox_hexadecimal_to_decimal)
        self.label_groupbox_hexadecimal_to_decimal_hint.setObjectName(u"label_groupbox_hexadecimal_to_decimal_hint")
        self.label_groupbox_hexadecimal_to_decimal_hint.setWordWrap(True)

        self.layout_groupbox_hexadecimal_to_decimal.addWidget(self.label_groupbox_hexadecimal_to_decimal_hint)

        self.layout_hex_form = QFormLayout()
        self.layout_hex_form.setObjectName(u"layout_hex_form")
        self.layout_hex_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_hex_form.setHorizontalSpacing(10)
        self.layout_hex_form.setVerticalSpacing(10)
        self.layout_hex_form.setContentsMargins(0, 4, 0, 4)
        self.label_from_hexadecimal = QLabel(self.groupbox_hexadecimal_to_decimal)
        self.label_from_hexadecimal.setObjectName(u"label_from_hexadecimal")

        self.layout_hex_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_from_hexadecimal)

        self.line_edit_hexadecimal = QLineEdit(self.groupbox_hexadecimal_to_decimal)
        self.line_edit_hexadecimal.setObjectName(u"line_edit_hexadecimal")
        self.line_edit_hexadecimal.setClearButtonEnabled(True)

        self.layout_hex_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.line_edit_hexadecimal)

        self.label_to_decimal = QLabel(self.groupbox_hexadecimal_to_decimal)
        self.label_to_decimal.setObjectName(u"label_to_decimal")

        self.layout_hex_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_to_decimal)

        self.line_edit_decimal = QLineEdit(self.groupbox_hexadecimal_to_decimal)
        self.line_edit_decimal.setObjectName(u"line_edit_decimal")
        self.line_edit_decimal.setReadOnly(True)
        self.line_edit_decimal.setClearButtonEnabled(False)

        self.layout_hex_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.line_edit_decimal)


        self.layout_groupbox_hexadecimal_to_decimal.addLayout(self.layout_hex_form)

        self.label_hex_error = QLabel(self.groupbox_hexadecimal_to_decimal)
        self.label_hex_error.setObjectName(u"label_hex_error")

        self.layout_groupbox_hexadecimal_to_decimal.addWidget(self.label_hex_error)


        self.layout_scroll_tab_tool_hex_contents.addWidget(self.groupbox_hexadecimal_to_decimal)

        self.spacer_19 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_scroll_tab_tool_hex_contents.addItem(self.spacer_19)

        self.scroll_tab_tool_hex.setWidget(self.scroll_tab_tool_hex_contents)

        self.layout_tab_tool_hex.addWidget(self.scroll_tab_tool_hex)

        self.tab_widget_csv_tools.addTab(self.tab_tool_hex, "")

        self.layout_page_csv_tools.addWidget(self.tab_widget_csv_tools)

        self.layout_page_csv_tools.setStretch(2, 1)
        self.stacked_pages.addWidget(self.page_csv_tools)
        self.page_table = QWidget()
        self.page_table.setObjectName(u"page_table")
        self.layout_page_table = QVBoxLayout(self.page_table)
        self.layout_page_table.setSpacing(12)
        self.layout_page_table.setObjectName(u"layout_page_table")
        self.layout_page_table.setContentsMargins(28, 24, 28, 20)
        self.label_page_table_title = QLabel(self.page_table)
        self.label_page_table_title.setObjectName(u"label_page_table_title")

        self.layout_page_table.addWidget(self.label_page_table_title)

        self.label_page_table_hint = QLabel(self.page_table)
        self.label_page_table_hint.setObjectName(u"label_page_table_hint")
        self.label_page_table_hint.setWordWrap(True)

        self.layout_page_table.addWidget(self.label_page_table_hint)

        self.layout_table_toolbar = QHBoxLayout()
        self.layout_table_toolbar.setSpacing(10)
        self.layout_table_toolbar.setObjectName(u"layout_table_toolbar")
        self.layout_table_toolbar.setContentsMargins(0, 0, 0, 0)
        self.line_edit_filter_table = QLineEdit(self.page_table)
        self.line_edit_filter_table.setObjectName(u"line_edit_filter_table")
        self.line_edit_filter_table.setClearButtonEnabled(True)

        self.layout_table_toolbar.addWidget(self.line_edit_filter_table)

        self.label_table_rows = QLabel(self.page_table)
        self.label_table_rows.setObjectName(u"label_table_rows")

        self.layout_table_toolbar.addWidget(self.label_table_rows)

        self.button_load_csv = QPushButton(self.page_table)
        self.button_load_csv.setObjectName(u"button_load_csv")

        self.layout_table_toolbar.addWidget(self.button_load_csv)

        self.button_clear_table = QPushButton(self.page_table)
        self.button_clear_table.setObjectName(u"button_clear_table")

        self.layout_table_toolbar.addWidget(self.button_clear_table)


        self.layout_page_table.addLayout(self.layout_table_toolbar)

        self.table_csv_data = DataTableView(self.page_table)
        self.table_csv_data.setObjectName(u"table_csv_data")
        self.table_csv_data.setAlternatingRowColors(True)
        self.table_csv_data.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table_csv_data.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_csv_data.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_csv_data.setSortingEnabled(True)
        self.table_csv_data.setWordWrap(False)
        self.table_csv_data.setCornerButtonEnabled(False)
        self.table_csv_data.horizontalHeader().setStretchLastSection(True)

        self.layout_page_table.addWidget(self.table_csv_data)

        self.layout_page_table.setStretch(3, 1)
        self.stacked_pages.addWidget(self.page_table)

        self.layout_central.addWidget(self.stacked_pages)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menu_bar = QMenuBar(MainWindow)
        self.menu_bar.setObjectName(u"menu_bar")
        self.menu_bar.setGeometry(QRect(0, 0, 1369, 33))
        self.file_menu = QMenu(self.menu_bar)
        self.file_menu.setObjectName(u"file_menu")
        self.recent_xpath_expressions_menu = QMenu(self.file_menu)
        self.recent_xpath_expressions_menu.setObjectName(u"recent_xpath_expressions_menu")
        self.paths_menu = QMenu(self.menu_bar)
        self.paths_menu.setObjectName(u"paths_menu")
        self.menu_autofill = QMenu(self.menu_bar)
        self.menu_autofill.setObjectName(u"menu_autofill")
        self.view_menu = QMenu(self.menu_bar)
        self.view_menu.setObjectName(u"view_menu")
        self.settings_menu = QMenu(self.menu_bar)
        self.settings_menu.setObjectName(u"settings_menu")
        self.theme_menu = QMenu(self.settings_menu)
        self.theme_menu.setObjectName(u"theme_menu")
        self.help_menu = QMenu(self.menu_bar)
        self.help_menu.setObjectName(u"help_menu")
        MainWindow.setMenuBar(self.menu_bar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setSizeGripEnabled(True)
        MainWindow.setStatusBar(self.statusbar)
        self.dock_output = QDockWidget(MainWindow)
        self.dock_output.setObjectName(u"dock_output")
        self.dock_output.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable|QDockWidget.DockWidgetFeature.DockWidgetFloatable|QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.dock_output.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea|Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock_output_contents = QWidget()
        self.dock_output_contents.setObjectName(u"dock_output_contents")
        self.layout_dock_output = QVBoxLayout(self.dock_output_contents)
        self.layout_dock_output.setSpacing(8)
        self.layout_dock_output.setObjectName(u"layout_dock_output")
        self.layout_dock_output.setContentsMargins(12, 4, 12, 10)
        self.tab_widget_output = QTabWidget(self.dock_output_contents)
        self.tab_widget_output.setObjectName(u"tab_widget_output")
        self.tab_widget_output.setDocumentMode(True)
        self.tab_output_extract = QWidget()
        self.tab_output_extract.setObjectName(u"tab_output_extract")
        self.layout_tab_output_extract = QVBoxLayout(self.tab_output_extract)
        self.layout_tab_output_extract.setSpacing(8)
        self.layout_tab_output_extract.setObjectName(u"layout_tab_output_extract")
        self.layout_tab_output_extract.setContentsMargins(0, 0, 0, 0)
        self.text_edit_program_output = QTextEdit(self.tab_output_extract)
        self.text_edit_program_output.setObjectName(u"text_edit_program_output")
        self.text_edit_program_output.setReadOnly(True)

        self.layout_tab_output_extract.addWidget(self.text_edit_program_output)

        self.tab_widget_output.addTab(self.tab_output_extract, "")
        self.tab_output_csv = QWidget()
        self.tab_output_csv.setObjectName(u"tab_output_csv")
        self.layout_tab_output_csv = QVBoxLayout(self.tab_output_csv)
        self.layout_tab_output_csv.setSpacing(8)
        self.layout_tab_output_csv.setObjectName(u"layout_tab_output_csv")
        self.layout_tab_output_csv.setContentsMargins(0, 0, 0, 0)
        self.text_edit_csv_output = QTextEdit(self.tab_output_csv)
        self.text_edit_csv_output.setObjectName(u"text_edit_csv_output")
        self.text_edit_csv_output.setReadOnly(True)

        self.layout_tab_output_csv.addWidget(self.text_edit_csv_output)

        self.tab_widget_output.addTab(self.tab_output_csv, "")
        self.tab_output_xml = QWidget()
        self.tab_output_xml.setObjectName(u"tab_output_xml")
        self.layout_tab_output_xml = QVBoxLayout(self.tab_output_xml)
        self.layout_tab_output_xml.setSpacing(0)
        self.layout_tab_output_xml.setObjectName(u"layout_tab_output_xml")
        self.layout_tab_output_xml.setContentsMargins(0, 0, 0, 0)
        self.text_edit_xml_tools_output = QTextEdit(self.tab_output_xml)
        self.text_edit_xml_tools_output.setObjectName(u"text_edit_xml_tools_output")
        self.text_edit_xml_tools_output.setReadOnly(True)

        self.layout_tab_output_xml.addWidget(self.text_edit_xml_tools_output)

        self.tab_widget_output.addTab(self.tab_output_xml, "")

        self.layout_dock_output.addWidget(self.tab_widget_output)

        self.dock_output.setWidget(self.dock_output_contents)
        MainWindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_output)

        self.menu_bar.addAction(self.file_menu.menuAction())
        self.menu_bar.addAction(self.paths_menu.menuAction())
        self.menu_bar.addAction(self.menu_autofill.menuAction())
        self.menu_bar.addAction(self.view_menu.menuAction())
        self.menu_bar.addAction(self.settings_menu.menuAction())
        self.menu_bar.addAction(self.help_menu.menuAction())
        self.file_menu.addAction(self.open_input_action)
        self.file_menu.addAction(self.open_output_action)
        self.file_menu.addAction(self.open_csv_conversion_input_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.recent_xpath_expressions_menu.menuAction())
        self.file_menu.addAction(self.clear_recent_xpath_expressions_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.prompt_on_exit_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        self.settings_menu.addAction(self.open_paths_manager)
        self.settings_menu.addAction(self.open_pre_built_xpaths_manager_action)
        self.settings_menu.addSeparator()
        self.settings_menu.addAction(self.theme_menu.menuAction())
        self.help_menu.addAction(self.xpath_help_action)

        self.retranslateUi(MainWindow)

        self.list_widget_navigation.setCurrentRow(0)
        self.stacked_pages.setCurrentIndex(0)
        self.button_start_csv_export.setDefault(True)
        self.tab_widget_xml_tools.setCurrentIndex(0)
        self.tab_widget_csv_tools.setCurrentIndex(0)
        self.tab_widget_output.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"XMLuvation", None))
        self.open_input_action.setText(QCoreApplication.translate("MainWindow", u"Open XML folder", None))
        self.open_output_action.setText(QCoreApplication.translate("MainWindow", u"Open CSV output folder", None))
        self.open_csv_conversion_input_action.setText(QCoreApplication.translate("MainWindow", u"Open CSV conversion folder", None))
        self.clear_recent_xpath_expressions_action.setText(QCoreApplication.translate("MainWindow", u"Clear recent expressions", None))
        self.prompt_on_exit_action.setText(QCoreApplication.translate("MainWindow", u"Ask before exiting", None))
        self.exit_action.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
#if QT_CONFIG(shortcut)
        self.exit_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.open_paths_manager.setText(QCoreApplication.translate("MainWindow", u"Manage custom paths\u2026", None))
        self.open_pre_built_xpaths_manager_action.setText(QCoreApplication.translate("MainWindow", u"Manage XPath presets\u2026", None))
        self.xpath_help_action.setText(QCoreApplication.translate("MainWindow", u"XPath syntax reference", None))
#if QT_CONFIG(shortcut)
        self.xpath_help_action.setShortcut(QCoreApplication.translate("MainWindow", u"F1", None))
#endif // QT_CONFIG(shortcut)
        self.frame_sidebar.setProperty(u"role", QCoreApplication.translate("MainWindow", u"sidebar", None))
        self.label_app_title.setText(QCoreApplication.translate("MainWindow", u"XMLuvation", None))
        self.label_app_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"app-title", None))
        self.label_app_subtitle.setText(QCoreApplication.translate("MainWindow", u"XPath search and CSV toolkit", None))
        self.label_app_subtitle.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))

        __sortingEnabled = self.list_widget_navigation.isSortingEnabled()
        self.list_widget_navigation.setSortingEnabled(False)
        ___qlistwidgetitem = self.list_widget_navigation.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"Extract", None))
        ___qlistwidgetitem1 = self.list_widget_navigation.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"XML tools", None))
        ___qlistwidgetitem2 = self.list_widget_navigation.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("MainWindow", u"CSV tools", None))
        ___qlistwidgetitem3 = self.list_widget_navigation.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Table viewer", None))
        self.list_widget_navigation.setSortingEnabled(__sortingEnabled)

        self.list_widget_navigation.setProperty(u"role", QCoreApplication.translate("MainWindow", u"nav", None))
        self.label_sidebar_shortcuts.setText(QCoreApplication.translate("MainWindow", u"Ctrl+1\u20134 switch pages\n"
"Ctrl+J toggles output", None))
        self.label_sidebar_shortcuts.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.page_extract.setProperty(u"role", QCoreApplication.translate("MainWindow", u"page", None))
        self.label_page_extract_title.setText(QCoreApplication.translate("MainWindow", u"Extract XML to CSV", None))
        self.label_page_extract_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"page-title", None))
        self.label_page_extract_hint.setText(QCoreApplication.translate("MainWindow", u"Search a folder of XML files with XPath expressions and export every match to one CSV file.", None))
        self.label_page_extract_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.scroll_extract.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_extract_contents.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.card_source.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_source_title.setText(QCoreApplication.translate("MainWindow", u"Source folder", None))
        self.label_card_source_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.line_edit_xml_folder_path_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Folder that contains the XML files to search", None))
#if QT_CONFIG(tooltip)
        self.button_browse_xml_folder.setToolTip(QCoreApplication.translate("MainWindow", u"Browse for the folder containing your XML files.", None))
#endif // QT_CONFIG(tooltip)
        self.button_browse_xml_folder.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
        self.statusbar_xml_files_count.setText("")
        self.statusbar_xml_files_count.setProperty(u"role", QCoreApplication.translate("MainWindow", u"status", None))
        self.card_builder.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_builder_title.setText(QCoreApplication.translate("MainWindow", u"XPath builder", None))
        self.label_card_builder_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_xpath_builder.setText(QCoreApplication.translate("MainWindow", u"Inspect an XML file to fill the lists, then build an expression or type your own.", None))
        self.label_xpath_builder.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.label_tag_names.setText(QCoreApplication.translate("MainWindow", u"Tag", None))
        self.label_tag_names.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.combobox_tag_names.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select a tag", None))
        self.label_tag_values.setText(QCoreApplication.translate("MainWindow", u"Value", None))
        self.label_tag_values.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.combobox_tag_values.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Any value", None))
        self.label_attribute_names.setText(QCoreApplication.translate("MainWindow", u"Attribute", None))
        self.label_attribute_names.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.combobox_attribute_names.setPlaceholderText(QCoreApplication.translate("MainWindow", u"No attribute", None))
        self.label_attribute_values.setText(QCoreApplication.translate("MainWindow", u"Value", None))
        self.label_attribute_values.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.combobox_attribute_values.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Any value", None))
        self.label_function.setText(QCoreApplication.translate("MainWindow", u"Match", None))
        self.label_function.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.radio_button_equals.setText(QCoreApplication.translate("MainWindow", u"Equals", None))
        self.radio_button_contains.setText(QCoreApplication.translate("MainWindow", u"Contains", None))
        self.radio_button_starts_with.setText(QCoreApplication.translate("MainWindow", u"Starts with", None))
        self.radio_button_greater.setText(QCoreApplication.translate("MainWindow", u"Greater than", None))
        self.radio_button_smaller.setText(QCoreApplication.translate("MainWindow", u"Less than", None))
        self.line_edit_xpath_builder.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Type an XPath expression, or build one from the lists above", None))
#if QT_CONFIG(tooltip)
        self.button_build_xpath.setToolTip(QCoreApplication.translate("MainWindow", u"Create an XPath expression from the selected tag, attribute and match.", None))
#endif // QT_CONFIG(tooltip)
        self.button_build_xpath.setText(QCoreApplication.translate("MainWindow", u"Build", None))
#if QT_CONFIG(tooltip)
        self.button_add_xpath_to_list.setToolTip(QCoreApplication.translate("MainWindow", u"Add the expression (comma-separated for several) to the list below.", None))
#endif // QT_CONFIG(tooltip)
        self.button_add_xpath_to_list.setText(QCoreApplication.translate("MainWindow", u"Add to list", None))
        self.button_add_xpath_to_list.setProperty(u"role", QCoreApplication.translate("MainWindow", u"accent", None))
        self.card_expressions.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_expressions_title.setText(QCoreApplication.translate("MainWindow", u"Expressions to export", None))
        self.label_card_expressions_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_card_expressions_hint.setText(QCoreApplication.translate("MainWindow", u"Each expression becomes one CSV column. Right-click an entry to remove it.", None))
        self.label_card_expressions_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.card_export.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_export_title.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.label_card_export_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_csv_headers_info.setText(QCoreApplication.translate("MainWindow", u"Column headers", None))
        self.label_csv_headers_info.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_csv_headers_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"One header per expression, comma-separated", None))
        self.label_csv_output.setText(QCoreApplication.translate("MainWindow", u"Output file", None))
        self.label_csv_output.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_csv_output_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Where to save the CSV file", None))
#if QT_CONFIG(tooltip)
        self.button_browse_csv.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the folder and file name for the CSV result.", None))
#endif // QT_CONFIG(tooltip)
        self.button_browse_csv.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
        self.label_options.setText(QCoreApplication.translate("MainWindow", u"Options", None))
        self.label_options.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
#if QT_CONFIG(tooltip)
        self.checkbox_group_matches.setToolTip(QCoreApplication.translate("MainWindow", u"Join all matches of an expression with \"; \". When off, each match gets its own row.", None))
#endif // QT_CONFIG(tooltip)
        self.checkbox_group_matches.setText(QCoreApplication.translate("MainWindow", u"Group matches into one row per file", None))
        self.button_pass_csv_to_converter.setText(QCoreApplication.translate("MainWindow", u"<a href=\"#convert\">Send result to CSV tools \u2192</a>", None))
        self.button_pass_csv_to_converter.setProperty(u"role", QCoreApplication.translate("MainWindow", u"link", None))
        self.label_file_processing.setText("")
        self.label_file_processing.setProperty(u"role", QCoreApplication.translate("MainWindow", u"status", None))
#if QT_CONFIG(tooltip)
        self.button_abort_csv_export.setToolTip(QCoreApplication.translate("MainWindow", u"Stop the running export. Rows written so far are kept.", None))
#endif // QT_CONFIG(tooltip)
        self.button_abort_csv_export.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
#if QT_CONFIG(tooltip)
        self.button_start_csv_export.setToolTip(QCoreApplication.translate("MainWindow", u"Search all XML files in the folder and write the matches to the CSV file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_start_csv_export.setText(QCoreApplication.translate("MainWindow", u"Run export", None))
        self.button_start_csv_export.setProperty(u"role", QCoreApplication.translate("MainWindow", u"primary", None))
        self.card_preview.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_preview_title.setText(QCoreApplication.translate("MainWindow", u"XML preview", None))
        self.label_card_preview_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_preview_shortcut.setText(QCoreApplication.translate("MainWindow", u"Ctrl+F to search", None))
        self.label_preview_shortcut.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.text_edit_xml_output.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Inspect an XML file to see its content here.", None))
        self.text_edit_xml_output.setProperty(u"role", QCoreApplication.translate("MainWindow", u"code", None))
#if QT_CONFIG(tooltip)
        self.button_read_xml.setToolTip(QCoreApplication.translate("MainWindow", u"Open one XML file to fill the XPath builder lists and show its content in the preview.", None))
#endif // QT_CONFIG(tooltip)
        self.button_read_xml.setText(QCoreApplication.translate("MainWindow", u"Inspect XML file\u2026", None))
        self.line_edit_xml_output_find_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Find in preview", None))
#if QT_CONFIG(tooltip)
        self.button_find_previous.setToolTip(QCoreApplication.translate("MainWindow", u"Find previous match (Shift+Enter)", None))
#endif // QT_CONFIG(tooltip)
        self.button_find_previous.setText(QCoreApplication.translate("MainWindow", u"\u2191", None))
#if QT_CONFIG(tooltip)
        self.button_find_next.setToolTip(QCoreApplication.translate("MainWindow", u"Find next match (Enter)", None))
#endif // QT_CONFIG(tooltip)
        self.button_find_next.setText(QCoreApplication.translate("MainWindow", u"\u2193", None))
        self.page_xml_tools.setProperty(u"role", QCoreApplication.translate("MainWindow", u"page", None))
        self.label_page_xml_tools_title.setText(QCoreApplication.translate("MainWindow", u"XML tools", None))
        self.label_page_xml_tools_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"page-title", None))
        self.label_page_xml_tools_hint.setText(QCoreApplication.translate("MainWindow", u"Validate XML files against a schema and compare two versions of a document.", None))
        self.label_page_xml_tools_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.tab_widget_xml_tools.setProperty(u"role", QCoreApplication.translate("MainWindow", u"segmented", None))
        self.tab_xml_validate.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_xml_validate.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_xml_validate_contents.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.card_validate.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_validate_title.setText(QCoreApplication.translate("MainWindow", u"Validate against an XSD schema", None))
        self.label_card_validate_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_card_validate_hint.setText(QCoreApplication.translate("MainWindow", u"Checks XML files against an XSD 1.0 schema. Choose one XML file or a folder: every .xml file directly in it is checked. Problems are listed with line, column and XPath in a report CSV saved next to the XML files.", None))
        self.label_card_validate_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.label_validate_schema.setText(QCoreApplication.translate("MainWindow", u"Schema", None))
        self.label_validate_schema.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_validate_schema_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"XSD file, e.g. profile.xsd", None))
#if QT_CONFIG(tooltip)
        self.button_validate_browse_schema.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the XSD schema file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_validate_browse_schema.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
        self.label_validate_xml.setText(QCoreApplication.translate("MainWindow", u"XML", None))
        self.label_validate_xml.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_validate_xml_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"XML file, or a folder with XML files", None))
#if QT_CONFIG(tooltip)
        self.button_validate_browse_file.setToolTip(QCoreApplication.translate("MainWindow", u"Choose one XML file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_validate_browse_file.setText(QCoreApplication.translate("MainWindow", u"File\u2026", None))
#if QT_CONFIG(tooltip)
        self.button_validate_browse_folder.setToolTip(QCoreApplication.translate("MainWindow", u"Choose a folder: every .xml file directly in it is checked.", None))
#endif // QT_CONFIG(tooltip)
        self.button_validate_browse_folder.setText(QCoreApplication.translate("MainWindow", u"Folder\u2026", None))
        self.label_validate_progress.setText("")
        self.label_validate_progress.setProperty(u"role", QCoreApplication.translate("MainWindow", u"status", None))
#if QT_CONFIG(tooltip)
        self.button_validate_cancel.setToolTip(QCoreApplication.translate("MainWindow", u"Stop validating.", None))
#endif // QT_CONFIG(tooltip)
        self.button_validate_cancel.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
#if QT_CONFIG(tooltip)
        self.button_validate_start.setToolTip(QCoreApplication.translate("MainWindow", u"Validate the XML file(s) against the schema.", None))
#endif // QT_CONFIG(tooltip)
        self.button_validate_start.setText(QCoreApplication.translate("MainWindow", u"Validate", None))
        self.button_validate_start.setProperty(u"role", QCoreApplication.translate("MainWindow", u"primary", None))
        self.frame_validate_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result", None))
        self.label_validate_summary.setText("")
        self.text_edit_validate_problems.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Problems found during validation appear here.", None))
        self.text_edit_validate_problems.setProperty(u"role", QCoreApplication.translate("MainWindow", u"code", None))
        self.label_validate_result.setText(QCoreApplication.translate("MainWindow", u"Report", None))
        self.label_validate_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result-title", None))
#if QT_CONFIG(tooltip)
        self.button_validate_open_report.setToolTip(QCoreApplication.translate("MainWindow", u"Open the report file (CSV) in its default program.", None))
#endif // QT_CONFIG(tooltip)
        self.button_validate_open_report.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.tab_widget_xml_tools.setTabText(self.tab_widget_xml_tools.indexOf(self.tab_xml_validate), QCoreApplication.translate("MainWindow", u"Validate", None))
        self.tab_xml_compare.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_xml_compare.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_xml_compare_contents.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.card_xml_compare.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_xml_compare_title.setText(QCoreApplication.translate("MainWindow", u"Compare two XML files", None))
        self.label_card_xml_compare_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_card_xml_compare_hint.setText(QCoreApplication.translate("MainWindow", u"Compares elements, attributes and text and lists every addition, removal and change with its XPath and line numbers in a report CSV saved next to the new file. Comments and attribute order are ignored.", None))
        self.label_card_xml_compare_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.label_xml_compare_old.setText(QCoreApplication.translate("MainWindow", u"Old file", None))
        self.label_xml_compare_old.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_xml_compare_old_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Earlier version, e.g. the profile before a change", None))
#if QT_CONFIG(tooltip)
        self.button_xml_compare_old_browse.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the XML file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_xml_compare_old_browse.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
        self.label_xml_compare_new.setText(QCoreApplication.translate("MainWindow", u"New file", None))
        self.label_xml_compare_new.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_xml_compare_new_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Later version to compare against the old file", None))
#if QT_CONFIG(tooltip)
        self.button_xml_compare_new_browse.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the XML file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_xml_compare_new_browse.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
        self.label_xml_compare_options.setText(QCoreApplication.translate("MainWindow", u"Options", None))
        self.label_xml_compare_options.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
#if QT_CONFIG(tooltip)
        self.checkbox_xml_compare_ignore_whitespace.setToolTip(QCoreApplication.translate("MainWindow", u"Treat text that differs only in spaces, line breaks or indentation as equal.", None))
#endif // QT_CONFIG(tooltip)
        self.checkbox_xml_compare_ignore_whitespace.setText(QCoreApplication.translate("MainWindow", u"Ignore whitespace and indentation in text", None))
#if QT_CONFIG(tooltip)
        self.button_xml_compare_cancel.setToolTip(QCoreApplication.translate("MainWindow", u"Stop comparing.", None))
#endif // QT_CONFIG(tooltip)
        self.button_xml_compare_cancel.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
#if QT_CONFIG(tooltip)
        self.button_xml_compare_start.setToolTip(QCoreApplication.translate("MainWindow", u"Compare the files, show them side by side and write a difference report.", None))
#endif // QT_CONFIG(tooltip)
        self.button_xml_compare_start.setText(QCoreApplication.translate("MainWindow", u"Compare", None))
        self.button_xml_compare_start.setProperty(u"role", QCoreApplication.translate("MainWindow", u"primary", None))
        self.frame_xml_compare_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result", None))
        self.label_xml_compare_summary.setText("")
        self.label_xml_compare_result.setText(QCoreApplication.translate("MainWindow", u"Report", None))
        self.label_xml_compare_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result-title", None))
#if QT_CONFIG(tooltip)
        self.button_xml_compare_open_report.setToolTip(QCoreApplication.translate("MainWindow", u"Open the report file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_xml_compare_open_report.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.card_xml_compare_diff.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_xml_compare_diff_title.setText(QCoreApplication.translate("MainWindow", u"Side by side", None))
        self.label_card_xml_compare_diff_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_card_xml_compare_diff_hint.setText(QCoreApplication.translate("MainWindow", u"Both files line by line: removed and changed lines are red on the left, added and changed lines green on the right. Unlike the report, this view also shows comments and formatting. F7 / Shift+F7 jump to the next / previous change.", None))
        self.label_card_xml_compare_diff_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.tab_widget_xml_tools.setTabText(self.tab_widget_xml_tools.indexOf(self.tab_xml_compare), QCoreApplication.translate("MainWindow", u"Compare", None))
        self.page_csv_tools.setProperty(u"role", QCoreApplication.translate("MainWindow", u"page", None))
        self.label_page_csv_tools_title.setText(QCoreApplication.translate("MainWindow", u"CSV tools", None))
        self.label_page_csv_tools_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"page-title", None))
        self.label_page_csv_tools_hint.setText(QCoreApplication.translate("MainWindow", u"Convert, split, compare and edit CSV files, and clean up profile exports.", None))
        self.label_page_csv_tools_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.tab_widget_csv_tools.setProperty(u"role", QCoreApplication.translate("MainWindow", u"segmented", None))
        self.tab_tool_convert.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_convert.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_convert_contents.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.groupbox_csv_conversion.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_groupbox_csv_conversion_title.setText(QCoreApplication.translate("MainWindow", u"Convert CSV", None))
        self.label_groupbox_csv_conversion_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_csv_conversion_desc.setText(QCoreApplication.translate("MainWindow", u"Turn a CSV file into an Excel workbook, HTML table, JSON records or a Markdown table, or convert one of those back to CSV. The result is saved next to the input file.", None))
        self.label_csv_conversion_desc.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.label_conversion_input.setText(QCoreApplication.translate("MainWindow", u"Input file", None))
        self.label_conversion_input.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_csv_conversion_path_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"CSV, Excel (.xlsx), HTML, JSON or Markdown file to convert", None))
#if QT_CONFIG(tooltip)
        self.button_browse_csv_conversion_path_input.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the file to convert.", None))
#endif // QT_CONFIG(tooltip)
        self.button_browse_csv_conversion_path_input.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
        self.label_csv_conversion_output_type.setText(QCoreApplication.translate("MainWindow", u"Format", None))
        self.label_csv_conversion_output_type.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.combobox_csv_conversion_output_type.setItemText(0, QCoreApplication.translate("MainWindow", u"EXCEL", None))
        self.combobox_csv_conversion_output_type.setItemText(1, QCoreApplication.translate("MainWindow", u"HTML", None))
        self.combobox_csv_conversion_output_type.setItemText(2, QCoreApplication.translate("MainWindow", u"JSON", None))
        self.combobox_csv_conversion_output_type.setItemText(3, QCoreApplication.translate("MainWindow", u"MARKDOWN", None))
        self.combobox_csv_conversion_output_type.setItemText(4, QCoreApplication.translate("MainWindow", u"CSV", None))

#if QT_CONFIG(tooltip)
        self.checkbox_write_index_column.setToolTip(QCoreApplication.translate("MainWindow", u"Add an index column starting at 1 (Excel, HTML, Markdown and CSV).", None))
#endif // QT_CONFIG(tooltip)
        self.checkbox_write_index_column.setText(QCoreApplication.translate("MainWindow", u"Write index column", None))
        self.label_csv_conversion_delimiter.setText(QCoreApplication.translate("MainWindow", u"Delimiter", None))
        self.label_csv_conversion_delimiter.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
#if QT_CONFIG(tooltip)
        self.checkbox_csv_conversion_manual_delimiter.setToolTip(QCoreApplication.translate("MainWindow", u"Reading a CSV file: the delimiter is detected automatically; tick this if it was detected wrong and choose or type it yourself. Converting to CSV: the file is written with this delimiter (a comma if not ticked).", None))
#endif // QT_CONFIG(tooltip)
        self.checkbox_csv_conversion_manual_delimiter.setText(QCoreApplication.translate("MainWindow", u"Set manually", None))
        self.combobox_csv_conversion_delimiter.setItemText(0, QCoreApplication.translate("MainWindow", u",", None))
        self.combobox_csv_conversion_delimiter.setItemText(1, QCoreApplication.translate("MainWindow", u";", None))
        self.combobox_csv_conversion_delimiter.setItemText(2, QCoreApplication.translate("MainWindow", u"|", None))
        self.combobox_csv_conversion_delimiter.setItemText(3, QCoreApplication.translate("MainWindow", u"Tab", None))

#if QT_CONFIG(tooltip)
        self.combobox_csv_conversion_delimiter.setToolTip(QCoreApplication.translate("MainWindow", u"One character, e.g. , ; or |. Type Tab for a tab.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.button_csv_conversion_convert.setToolTip(QCoreApplication.translate("MainWindow", u"Convert the CSV file to the selected format.", None))
#endif // QT_CONFIG(tooltip)
        self.button_csv_conversion_convert.setText(QCoreApplication.translate("MainWindow", u"Convert", None))
        self.button_csv_conversion_convert.setProperty(u"role", QCoreApplication.translate("MainWindow", u"primary", None))
        self.frame_conversion_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result", None))
        self.label_conversion_result.setText(QCoreApplication.translate("MainWindow", u"Saved as", None))
        self.label_conversion_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result-title", None))
        self.line_edit_csv_conversion_open_file_path.setPlaceholderText("")
#if QT_CONFIG(tooltip)
        self.button_csv_conversion_open_file.setToolTip(QCoreApplication.translate("MainWindow", u"Open the converted file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_csv_conversion_open_file.setText(QCoreApplication.translate("MainWindow", u"Open", None))
#if QT_CONFIG(tooltip)
        self.button_csv_conversion_show_folder.setToolTip(QCoreApplication.translate("MainWindow", u"Open the folder that contains the converted file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_csv_conversion_show_folder.setText(QCoreApplication.translate("MainWindow", u"Show in folder", None))
        self.button_csv_conversion_show_folder.setProperty(u"role", QCoreApplication.translate("MainWindow", u"flat", None))
        self.tab_widget_csv_tools.setTabText(self.tab_widget_csv_tools.indexOf(self.tab_tool_convert), QCoreApplication.translate("MainWindow", u"Convert", None))
        self.tab_tool_split.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_split.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_split_contents.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.card_split.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_split_title.setText(QCoreApplication.translate("MainWindow", u"Split CSV", None))
        self.label_card_split_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_card_split_hint.setText(QCoreApplication.translate("MainWindow", u"Every part keeps the header row, the delimiter and the encoding. Parts are saved in a new folder next to the CSV file; splitting by a column writes one file per value.", None))
        self.label_card_split_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.label_split_csv.setText(QCoreApplication.translate("MainWindow", u"CSV file", None))
        self.label_split_csv.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_split_csv_file_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"CSV file to split", None))
#if QT_CONFIG(tooltip)
        self.button_split_browse_csv_file_path.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the CSV file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_split_browse_csv_file_path.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
        self.label_split_by.setText(QCoreApplication.translate("MainWindow", u"Split by", None))
        self.label_split_by.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.radio_split_by_rows.setText(QCoreApplication.translate("MainWindow", u"Rows per file", None))
#if QT_CONFIG(tooltip)
        self.spin_box_split_rows.setToolTip(QCoreApplication.translate("MainWindow", u"1,048,575 data rows fill exactly one Excel sheet.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.button_split_excel_rows.setToolTip(QCoreApplication.translate("MainWindow", u"Use 1,048,575 rows per file, the most one Excel sheet can hold.", None))
#endif // QT_CONFIG(tooltip)
        self.button_split_excel_rows.setText(QCoreApplication.translate("MainWindow", u"Excel limit", None))
        self.button_split_excel_rows.setProperty(u"role", QCoreApplication.translate("MainWindow", u"flat", None))
        self.radio_split_by_column.setText(QCoreApplication.translate("MainWindow", u"Column value", None))
        self.combobox_split_column.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select a CSV file first", None))
#if QT_CONFIG(tooltip)
        self.button_split_cancel.setToolTip(QCoreApplication.translate("MainWindow", u"Stop splitting. Files written so far are removed.", None))
#endif // QT_CONFIG(tooltip)
        self.button_split_cancel.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
#if QT_CONFIG(tooltip)
        self.button_split_start.setToolTip(QCoreApplication.translate("MainWindow", u"Split the CSV file into several files.", None))
#endif // QT_CONFIG(tooltip)
        self.button_split_start.setText(QCoreApplication.translate("MainWindow", u"Split", None))
        self.button_split_start.setProperty(u"role", QCoreApplication.translate("MainWindow", u"primary", None))
        self.frame_split_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result", None))
        self.label_split_result.setText(QCoreApplication.translate("MainWindow", u"Saved in", None))
        self.label_split_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result-title", None))
        self.line_edit_split_result_path.setPlaceholderText("")
#if QT_CONFIG(tooltip)
        self.button_split_show_folder.setToolTip(QCoreApplication.translate("MainWindow", u"Open the folder with the parts.", None))
#endif // QT_CONFIG(tooltip)
        self.button_split_show_folder.setText(QCoreApplication.translate("MainWindow", u"Show folder", None))
        self.tab_widget_csv_tools.setTabText(self.tab_widget_csv_tools.indexOf(self.tab_tool_split), QCoreApplication.translate("MainWindow", u"Split", None))
        self.tab_tool_compare.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_compare.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_compare_contents.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.card_compare.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_compare_title.setText(QCoreApplication.translate("MainWindow", u"Compare two CSV files", None))
        self.label_card_compare_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_card_compare_hint.setText(QCoreApplication.translate("MainWindow", u"Aligns the rows of both files, pairs them by a key column and shows removed, added, moved and changed rows side by side. Every difference is also listed in a report CSV saved next to the new file.", None))
        self.label_card_compare_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.label_compare_old.setText(QCoreApplication.translate("MainWindow", u"Old file", None))
        self.label_compare_old.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_compare_old_csv_file_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Earlier version, e.g. last month's export", None))
#if QT_CONFIG(tooltip)
        self.button_compare_old_browse_csv_file_path.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the CSV file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_compare_old_browse_csv_file_path.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
        self.label_compare_new.setText(QCoreApplication.translate("MainWindow", u"New file", None))
        self.label_compare_new.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_compare_new_csv_file_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Later version to compare against the old file", None))
#if QT_CONFIG(tooltip)
        self.button_compare_new_browse_csv_file_path.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the CSV file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_compare_new_browse_csv_file_path.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
        self.label_compare_key.setText(QCoreApplication.translate("MainWindow", u"Match rows by", None))
        self.label_compare_key.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
#if QT_CONFIG(tooltip)
        self.combobox_compare_key.setToolTip(QCoreApplication.translate("MainWindow", u"A column that identifies a row in both files, e.g. a name or ID.", None))
#endif // QT_CONFIG(tooltip)
        self.combobox_compare_key.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select the old file first", None))
        self.label_compare_options.setText(QCoreApplication.translate("MainWindow", u"Options", None))
        self.label_compare_options.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.checkbox_compare_loose.setText(QCoreApplication.translate("MainWindow", u"Ignore upper/lower case and spaces around values", None))
#if QT_CONFIG(tooltip)
        self.button_compare_cancel.setToolTip(QCoreApplication.translate("MainWindow", u"Stop comparing.", None))
#endif // QT_CONFIG(tooltip)
        self.button_compare_cancel.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
#if QT_CONFIG(tooltip)
        self.button_compare_start.setToolTip(QCoreApplication.translate("MainWindow", u"Compare the files, show them side by side and write a difference report.", None))
#endif // QT_CONFIG(tooltip)
        self.button_compare_start.setText(QCoreApplication.translate("MainWindow", u"Compare", None))
        self.button_compare_start.setProperty(u"role", QCoreApplication.translate("MainWindow", u"primary", None))
        self.frame_compare_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result", None))
        self.label_compare_summary.setText("")
        self.label_compare_result.setText(QCoreApplication.translate("MainWindow", u"Report", None))
        self.label_compare_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result-title", None))
        self.line_edit_compare_result_path.setPlaceholderText("")
#if QT_CONFIG(tooltip)
        self.button_compare_open_report.setToolTip(QCoreApplication.translate("MainWindow", u"Open the report file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_compare_open_report.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.card_compare_diff.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_compare_diff_title.setText(QCoreApplication.translate("MainWindow", u"Side by side", None))
        self.label_card_compare_diff_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_card_compare_diff_hint.setText(QCoreApplication.translate("MainWindow", u"One row per line, header first, numbered as in a spreadsheet: removed and changed rows are red on the left, added and changed rows green on the right, and the changed cells are marked. Rows matched by key at another position are shown where they are in the new file. F7 / Shift+F7 jump to the next / previous change.", None))
        self.label_card_compare_diff_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.tab_widget_csv_tools.setTabText(self.tab_widget_csv_tools.indexOf(self.tab_tool_compare), QCoreApplication.translate("MainWindow", u"Compare", None))
        self.tab_tool_columns.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_columns.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_columns_contents.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.card_columns.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_card_columns_title.setText(QCoreApplication.translate("MainWindow", u"Edit columns", None))
        self.label_card_columns_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_card_columns_hint.setText(QCoreApplication.translate("MainWindow", u"Untick columns to remove them, drag them (or use Move up/down) to reorder, and double-click a name to rename it. Cell values are kept exactly as they are.", None))
        self.label_card_columns_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.label_columns_csv.setText(QCoreApplication.translate("MainWindow", u"CSV file", None))
        self.label_columns_csv.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_columns_csv_file_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"CSV file to edit", None))
#if QT_CONFIG(tooltip)
        self.button_columns_browse_csv_file_path.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the CSV file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_columns_browse_csv_file_path.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
#if QT_CONFIG(tooltip)
        self.button_columns_up.setToolTip(QCoreApplication.translate("MainWindow", u"Move the selected column up (Ctrl+Up).", None))
#endif // QT_CONFIG(tooltip)
        self.button_columns_up.setText(QCoreApplication.translate("MainWindow", u"Move up", None))
#if QT_CONFIG(tooltip)
        self.button_columns_down.setToolTip(QCoreApplication.translate("MainWindow", u"Move the selected column down (Ctrl+Down).", None))
#endif // QT_CONFIG(tooltip)
        self.button_columns_down.setText(QCoreApplication.translate("MainWindow", u"Move down", None))
#if QT_CONFIG(tooltip)
        self.button_columns_all.setToolTip(QCoreApplication.translate("MainWindow", u"Tick every column.", None))
#endif // QT_CONFIG(tooltip)
        self.button_columns_all.setText(QCoreApplication.translate("MainWindow", u"Keep all", None))
#if QT_CONFIG(tooltip)
        self.button_columns_none.setToolTip(QCoreApplication.translate("MainWindow", u"Untick every column.", None))
#endif // QT_CONFIG(tooltip)
        self.button_columns_none.setText(QCoreApplication.translate("MainWindow", u"Keep none", None))
#if QT_CONFIG(tooltip)
        self.button_columns_reset.setToolTip(QCoreApplication.translate("MainWindow", u"Restore the file's original columns, order and names.", None))
#endif // QT_CONFIG(tooltip)
        self.button_columns_reset.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
        self.button_columns_reset.setProperty(u"role", QCoreApplication.translate("MainWindow", u"flat", None))
        self.label_columns_status.setText("")
        self.label_columns_status.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
#if QT_CONFIG(tooltip)
        self.checkbox_columns_overwrite.setToolTip(QCoreApplication.translate("MainWindow", u"When off, the result is saved as <name>_edited.csv next to the original.", None))
#endif // QT_CONFIG(tooltip)
        self.checkbox_columns_overwrite.setText(QCoreApplication.translate("MainWindow", u"Overwrite the original file", None))
#if QT_CONFIG(tooltip)
        self.button_columns_save.setToolTip(QCoreApplication.translate("MainWindow", u"Write the CSV file with the columns above.", None))
#endif // QT_CONFIG(tooltip)
        self.button_columns_save.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.button_columns_save.setProperty(u"role", QCoreApplication.translate("MainWindow", u"primary", None))
        self.frame_columns_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result", None))
        self.label_columns_result.setText(QCoreApplication.translate("MainWindow", u"Saved as", None))
        self.label_columns_result.setProperty(u"role", QCoreApplication.translate("MainWindow", u"result-title", None))
        self.line_edit_columns_result_path.setPlaceholderText("")
#if QT_CONFIG(tooltip)
        self.button_columns_open_result.setToolTip(QCoreApplication.translate("MainWindow", u"Open the saved file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_columns_open_result.setText(QCoreApplication.translate("MainWindow", u"Open", None))
#if QT_CONFIG(tooltip)
        self.button_columns_show_folder.setToolTip(QCoreApplication.translate("MainWindow", u"Open the folder that contains the saved file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_columns_show_folder.setText(QCoreApplication.translate("MainWindow", u"Show in folder", None))
        self.button_columns_show_folder.setProperty(u"role", QCoreApplication.translate("MainWindow", u"flat", None))
        self.tab_widget_csv_tools.setTabText(self.tab_widget_csv_tools.indexOf(self.tab_tool_columns), QCoreApplication.translate("MainWindow", u"Columns", None))
        self.tab_tool_cleanup.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_cleanup.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_cleanup_contents.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.groupbox_lobster_profiles_cleanup.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_groupbox_lobster_profiles_cleanup_title.setText(QCoreApplication.translate("MainWindow", u"Profile export clean-up", None))
        self.label_groupbox_lobster_profiles_cleanup_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Deletes profile XML files that are not listed in the first column of a Lobster profile CSV export. You review and confirm the list before anything is deleted.", None))
        self.label_2.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.label_cleanup_csv.setText(QCoreApplication.translate("MainWindow", u"Profile CSV", None))
        self.label_cleanup_csv.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_profile_cleanup_csv_file_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"CSV export listing the profiles to keep (first column)", None))
#if QT_CONFIG(tooltip)
        self.button_profile_cleanup_browse_csv_file_path.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the exported profile CSV file.", None))
#endif // QT_CONFIG(tooltip)
        self.button_profile_cleanup_browse_csv_file_path.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
        self.label_cleanup_folder.setText(QCoreApplication.translate("MainWindow", u"XML folder", None))
        self.label_cleanup_folder.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_profile_cleanup_folder_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Folder with the exported profile XML files", None))
#if QT_CONFIG(tooltip)
        self.button_profile_cleanup_browse_folder_path.setToolTip(QCoreApplication.translate("MainWindow", u"Choose the folder that contains the XML files.", None))
#endif // QT_CONFIG(tooltip)
        self.button_profile_cleanup_browse_folder_path.setText(QCoreApplication.translate("MainWindow", u"Browse\u2026", None))
#if QT_CONFIG(tooltip)
        self.button_profile_cleanup_cleanup_start.setToolTip(QCoreApplication.translate("MainWindow", u"Show which XML files are not listed in the CSV and delete them after you confirm.", None))
#endif // QT_CONFIG(tooltip)
        self.button_profile_cleanup_cleanup_start.setText(QCoreApplication.translate("MainWindow", u"Delete unlisted XML files\u2026", None))
        self.button_profile_cleanup_cleanup_start.setProperty(u"role", QCoreApplication.translate("MainWindow", u"danger", None))
        self.tab_widget_csv_tools.setTabText(self.tab_widget_csv_tools.indexOf(self.tab_tool_cleanup), QCoreApplication.translate("MainWindow", u"Profile clean-up", None))
        self.tab_tool_hex.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_hex.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.scroll_tab_tool_hex_contents.setProperty(u"role", QCoreApplication.translate("MainWindow", u"transparent", None))
        self.groupbox_hexadecimal_to_decimal.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card", None))
        self.label_groupbox_hexadecimal_to_decimal_title.setText(QCoreApplication.translate("MainWindow", u"Hexadecimal to decimal", None))
        self.label_groupbox_hexadecimal_to_decimal_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"card-title", None))
        self.label_groupbox_hexadecimal_to_decimal_hint.setText(QCoreApplication.translate("MainWindow", u"Converts as you type. A 0x prefix, spaces and underscores are ignored.", None))
        self.label_groupbox_hexadecimal_to_decimal_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.label_from_hexadecimal.setText(QCoreApplication.translate("MainWindow", u"Hexadecimal", None))
        self.label_from_hexadecimal.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_hexadecimal.setPlaceholderText(QCoreApplication.translate("MainWindow", u"e.g. 1F4 or 0x1F4", None))
        self.label_to_decimal.setText(QCoreApplication.translate("MainWindow", u"Decimal", None))
        self.label_to_decimal.setProperty(u"role", QCoreApplication.translate("MainWindow", u"field-label", None))
        self.line_edit_decimal.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Result appears as you type", None))
        self.label_hex_error.setText("")
        self.label_hex_error.setProperty(u"role", QCoreApplication.translate("MainWindow", u"error", None))
        self.tab_widget_csv_tools.setTabText(self.tab_widget_csv_tools.indexOf(self.tab_tool_hex), QCoreApplication.translate("MainWindow", u"Hex \u2192 decimal", None))
        self.page_table.setProperty(u"role", QCoreApplication.translate("MainWindow", u"page", None))
        self.label_page_table_title.setText(QCoreApplication.translate("MainWindow", u"Table viewer", None))
        self.label_page_table_title.setProperty(u"role", QCoreApplication.translate("MainWindow", u"page-title", None))
        self.label_page_table_hint.setText(QCoreApplication.translate("MainWindow", u"Open a CSV, Excel, HTML, JSON or Markdown table, or drop one on the table. Rows load as you scroll. Click a column header to sort, drag it to reorder, right-click it for filters, statistics, duplicates and freezing. Ctrl+C copies the selected cells for Excel.", None))
        self.label_page_table_hint.setProperty(u"role", QCoreApplication.translate("MainWindow", u"hint", None))
        self.line_edit_filter_table.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Quick filter: rows where any column contains this text", None))
        self.label_table_rows.setText("")
        self.label_table_rows.setProperty(u"role", QCoreApplication.translate("MainWindow", u"status", None))
#if QT_CONFIG(tooltip)
        self.button_load_csv.setToolTip(QCoreApplication.translate("MainWindow", u"Open a CSV file in the table viewer.", None))
#endif // QT_CONFIG(tooltip)
        self.button_load_csv.setText(QCoreApplication.translate("MainWindow", u"Open CSV\u2026", None))
        self.button_load_csv.setProperty(u"role", QCoreApplication.translate("MainWindow", u"accent", None))
#if QT_CONFIG(tooltip)
        self.button_clear_table.setToolTip(QCoreApplication.translate("MainWindow", u"Close the table and free its memory.", None))
#endif // QT_CONFIG(tooltip)
        self.button_clear_table.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.file_menu.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.recent_xpath_expressions_menu.setTitle(QCoreApplication.translate("MainWindow", u"Recent expressions", None))
        self.paths_menu.setTitle(QCoreApplication.translate("MainWindow", u"&Paths", None))
        self.menu_autofill.setTitle(QCoreApplication.translate("MainWindow", u"P&resets", None))
        self.view_menu.setTitle(QCoreApplication.translate("MainWindow", u"&View", None))
        self.settings_menu.setTitle(QCoreApplication.translate("MainWindow", u"&Settings", None))
        self.theme_menu.setTitle(QCoreApplication.translate("MainWindow", u"Theme", None))
        self.help_menu.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
        self.dock_output.setWindowTitle(QCoreApplication.translate("MainWindow", u"Output", None))
        self.dock_output_contents.setProperty(u"role", QCoreApplication.translate("MainWindow", u"dock", None))
        self.text_edit_program_output.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Messages from the extract page appear here.", None))
        self.text_edit_program_output.setProperty(u"role", QCoreApplication.translate("MainWindow", u"log", None))
        self.tab_widget_output.setTabText(self.tab_widget_output.indexOf(self.tab_output_extract), QCoreApplication.translate("MainWindow", u"Extract", None))
        self.text_edit_csv_output.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Messages from the CSV tools appear here.", None))
        self.text_edit_csv_output.setProperty(u"role", QCoreApplication.translate("MainWindow", u"log", None))
        self.tab_widget_output.setTabText(self.tab_widget_output.indexOf(self.tab_output_csv), QCoreApplication.translate("MainWindow", u"CSV tools", None))
        self.text_edit_xml_tools_output.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Messages from the XML tools appear here.", None))
        self.text_edit_xml_tools_output.setProperty(u"role", QCoreApplication.translate("MainWindow", u"log", None))
        self.tab_widget_output.setTabText(self.tab_widget_output.indexOf(self.tab_output_xml), QCoreApplication.translate("MainWindow", u"XML tools", None))
    # retranslateUi

