# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreBuiltXPathsManager.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)
from . import xmluvation_resources_rc

class Ui_PreBuiltXPathsManagerWidget(object):
    def setupUi(self, PreBuiltXPathsManagerWidget):
        if not PreBuiltXPathsManagerWidget.objectName():
            PreBuiltXPathsManagerWidget.setObjectName(u"PreBuiltXPathsManagerWidget")
        PreBuiltXPathsManagerWidget.resize(1384, 881)
        PreBuiltXPathsManagerWidget.setMinimumSize(QSize(900, 0))
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        PreBuiltXPathsManagerWidget.setWindowIcon(icon)
        self.layout_PreBuiltXPathsManagerWidget = QVBoxLayout(PreBuiltXPathsManagerWidget)
        self.layout_PreBuiltXPathsManagerWidget.setSpacing(14)
        self.layout_PreBuiltXPathsManagerWidget.setObjectName(u"layout_PreBuiltXPathsManagerWidget")
        self.layout_PreBuiltXPathsManagerWidget.setContentsMargins(24, 22, 24, 22)
        self.label_presets_title = QLabel(PreBuiltXPathsManagerWidget)
        self.label_presets_title.setObjectName(u"label_presets_title")

        self.layout_PreBuiltXPathsManagerWidget.addWidget(self.label_presets_title)

        self.label_presets_hint = QLabel(PreBuiltXPathsManagerWidget)
        self.label_presets_hint.setObjectName(u"label_presets_hint")
        self.label_presets_hint.setWordWrap(True)

        self.layout_PreBuiltXPathsManagerWidget.addWidget(self.label_presets_hint)

        self.layout_presets_cards = QHBoxLayout()
        self.layout_presets_cards.setSpacing(14)
        self.layout_presets_cards.setObjectName(u"layout_presets_cards")
        self.layout_presets_cards.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QFrame(PreBuiltXPathsManagerWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_groupBox = QVBoxLayout(self.groupBox)
        self.layout_groupBox.setSpacing(10)
        self.layout_groupBox.setObjectName(u"layout_groupBox")
        self.layout_groupBox.setContentsMargins(18, 16, 18, 18)
        self.label_groupBox_title = QLabel(self.groupBox)
        self.label_groupBox_title.setObjectName(u"label_groupBox_title")

        self.layout_groupBox.addWidget(self.label_groupBox_title)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setWordWrap(True)

        self.layout_groupBox.addWidget(self.label)

        self.label_new_expressions = QLabel(self.groupBox)
        self.label_new_expressions.setObjectName(u"label_new_expressions")

        self.layout_groupBox.addWidget(self.label_new_expressions)

        self.layout_new_expression = QHBoxLayout()
        self.layout_new_expression.setSpacing(8)
        self.layout_new_expression.setObjectName(u"layout_new_expression")
        self.layout_new_expression.setContentsMargins(0, 0, 0, 0)
        self.line_edit_xpath_expression = QLineEdit(self.groupBox)
        self.line_edit_xpath_expression.setObjectName(u"line_edit_xpath_expression")
        self.line_edit_xpath_expression.setClearButtonEnabled(True)

        self.layout_new_expression.addWidget(self.line_edit_xpath_expression)

        self.button_add_xpath_to_list = QPushButton(self.groupBox)
        self.button_add_xpath_to_list.setObjectName(u"button_add_xpath_to_list")

        self.layout_new_expression.addWidget(self.button_add_xpath_to_list)


        self.layout_groupBox.addLayout(self.layout_new_expression)

        self.list_widget_xpath_expressions = QListWidget(self.groupBox)
        self.list_widget_xpath_expressions.setObjectName(u"list_widget_xpath_expressions")
        self.list_widget_xpath_expressions.setMinimumSize(QSize(0, 110))
        self.list_widget_xpath_expressions.setAlternatingRowColors(True)

        self.layout_groupBox.addWidget(self.list_widget_xpath_expressions)

        self.label_new_headers = QLabel(self.groupBox)
        self.label_new_headers.setObjectName(u"label_new_headers")

        self.layout_groupBox.addWidget(self.label_new_headers)

        self.layout_new_header = QHBoxLayout()
        self.layout_new_header.setSpacing(8)
        self.layout_new_header.setObjectName(u"layout_new_header")
        self.layout_new_header.setContentsMargins(0, 0, 0, 0)
        self.line_edit_csv_header = QLineEdit(self.groupBox)
        self.line_edit_csv_header.setObjectName(u"line_edit_csv_header")
        self.line_edit_csv_header.setClearButtonEnabled(True)

        self.layout_new_header.addWidget(self.line_edit_csv_header)

        self.button_add_csv_header_to_list = QPushButton(self.groupBox)
        self.button_add_csv_header_to_list.setObjectName(u"button_add_csv_header_to_list")

        self.layout_new_header.addWidget(self.button_add_csv_header_to_list)


        self.layout_groupBox.addLayout(self.layout_new_header)

        self.list_widget_csv_headers = QListWidget(self.groupBox)
        self.list_widget_csv_headers.setObjectName(u"list_widget_csv_headers")
        self.list_widget_csv_headers.setMinimumSize(QSize(0, 110))
        self.list_widget_csv_headers.setAlternatingRowColors(True)

        self.layout_groupBox.addWidget(self.list_widget_csv_headers)

        self.layout_new_save = QHBoxLayout()
        self.layout_new_save.setSpacing(8)
        self.layout_new_save.setObjectName(u"layout_new_save")
        self.layout_new_save.setContentsMargins(0, 0, 0, 0)
        self.line_edit_config_name = QLineEdit(self.groupBox)
        self.line_edit_config_name.setObjectName(u"line_edit_config_name")
        self.line_edit_config_name.setClearButtonEnabled(True)

        self.layout_new_save.addWidget(self.line_edit_config_name)

        self.button_save_config = QPushButton(self.groupBox)
        self.button_save_config.setObjectName(u"button_save_config")

        self.layout_new_save.addWidget(self.button_save_config)


        self.layout_groupBox.addLayout(self.layout_new_save)


        self.layout_presets_cards.addWidget(self.groupBox)

        self.groupBox_pre_built_xpaths_main = QFrame(PreBuiltXPathsManagerWidget)
        self.groupBox_pre_built_xpaths_main.setObjectName(u"groupBox_pre_built_xpaths_main")
        self.groupBox_pre_built_xpaths_main.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_groupBox_pre_built_xpaths_main = QVBoxLayout(self.groupBox_pre_built_xpaths_main)
        self.layout_groupBox_pre_built_xpaths_main.setSpacing(10)
        self.layout_groupBox_pre_built_xpaths_main.setObjectName(u"layout_groupBox_pre_built_xpaths_main")
        self.layout_groupBox_pre_built_xpaths_main.setContentsMargins(18, 16, 18, 18)
        self.label_groupBox_pre_built_xpaths_main_title = QLabel(self.groupBox_pre_built_xpaths_main)
        self.label_groupBox_pre_built_xpaths_main_title.setObjectName(u"label_groupBox_pre_built_xpaths_main_title")

        self.layout_groupBox_pre_built_xpaths_main.addWidget(self.label_groupBox_pre_built_xpaths_main_title)

        self.label_9 = QLabel(self.groupBox_pre_built_xpaths_main)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setWordWrap(True)

        self.layout_groupBox_pre_built_xpaths_main.addWidget(self.label_9)

        self.layout_edit_select = QHBoxLayout()
        self.layout_edit_select.setSpacing(8)
        self.layout_edit_select.setObjectName(u"layout_edit_select")
        self.layout_edit_select.setContentsMargins(0, 0, 0, 0)
        self.combobox_xpath_configs = QComboBox(self.groupBox_pre_built_xpaths_main)
        self.combobox_xpath_configs.setObjectName(u"combobox_xpath_configs")

        self.layout_edit_select.addWidget(self.combobox_xpath_configs)

        self.button_load_config = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_load_config.setObjectName(u"button_load_config")

        self.layout_edit_select.addWidget(self.button_load_config)

        self.button_delete_config = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_delete_config.setObjectName(u"button_delete_config")

        self.layout_edit_select.addWidget(self.button_delete_config)

        self.layout_edit_select.setStretch(0, 1)

        self.layout_groupBox_pre_built_xpaths_main.addLayout(self.layout_edit_select)

        self.label_7 = QLabel(self.groupBox_pre_built_xpaths_main)
        self.label_7.setObjectName(u"label_7")

        self.layout_groupBox_pre_built_xpaths_main.addWidget(self.label_7)

        self.list_widget_edit_xpath_expressions = QListWidget(self.groupBox_pre_built_xpaths_main)
        self.list_widget_edit_xpath_expressions.setObjectName(u"list_widget_edit_xpath_expressions")
        self.list_widget_edit_xpath_expressions.setMinimumSize(QSize(0, 110))
        self.list_widget_edit_xpath_expressions.setAlternatingRowColors(True)

        self.layout_groupBox_pre_built_xpaths_main.addWidget(self.list_widget_edit_xpath_expressions)

        self.label_8 = QLabel(self.groupBox_pre_built_xpaths_main)
        self.label_8.setObjectName(u"label_8")

        self.layout_groupBox_pre_built_xpaths_main.addWidget(self.label_8)

        self.list_widget_edit_csv_headers = QListWidget(self.groupBox_pre_built_xpaths_main)
        self.list_widget_edit_csv_headers.setObjectName(u"list_widget_edit_csv_headers")
        self.list_widget_edit_csv_headers.setMinimumSize(QSize(0, 110))
        self.list_widget_edit_csv_headers.setAlternatingRowColors(True)

        self.layout_groupBox_pre_built_xpaths_main.addWidget(self.list_widget_edit_csv_headers)

        self.layout_edit_actions = QHBoxLayout()
        self.layout_edit_actions.setSpacing(8)
        self.layout_edit_actions.setObjectName(u"layout_edit_actions")
        self.layout_edit_actions.setContentsMargins(0, 0, 0, 0)
        self.button_open_config_directory = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_open_config_directory.setObjectName(u"button_open_config_directory")

        self.layout_edit_actions.addWidget(self.button_open_config_directory)

        self.spacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_edit_actions.addItem(self.spacer_3)

        self.button_save_changes = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_save_changes.setObjectName(u"button_save_changes")

        self.layout_edit_actions.addWidget(self.button_save_changes)


        self.layout_groupBox_pre_built_xpaths_main.addLayout(self.layout_edit_actions)


        self.layout_presets_cards.addWidget(self.groupBox_pre_built_xpaths_main)


        self.layout_PreBuiltXPathsManagerWidget.addLayout(self.layout_presets_cards)

        self.layout_presets_footer = QHBoxLayout()
        self.layout_presets_footer.setSpacing(8)
        self.layout_presets_footer.setObjectName(u"layout_presets_footer")
        self.layout_presets_footer.setContentsMargins(0, 0, 0, 0)
        self.label_remove_hint = QLabel(PreBuiltXPathsManagerWidget)
        self.label_remove_hint.setObjectName(u"label_remove_hint")
        self.label_remove_hint.setWordWrap(True)

        self.layout_presets_footer.addWidget(self.label_remove_hint)

        self.spacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_presets_footer.addItem(self.spacer_4)

        self.button_remove_selected = QPushButton(PreBuiltXPathsManagerWidget)
        self.button_remove_selected.setObjectName(u"button_remove_selected")

        self.layout_presets_footer.addWidget(self.button_remove_selected)

        self.button_remove_all = QPushButton(PreBuiltXPathsManagerWidget)
        self.button_remove_all.setObjectName(u"button_remove_all")

        self.layout_presets_footer.addWidget(self.button_remove_all)


        self.layout_PreBuiltXPathsManagerWidget.addLayout(self.layout_presets_footer)


        self.retranslateUi(PreBuiltXPathsManagerWidget)

        QMetaObject.connectSlotsByName(PreBuiltXPathsManagerWidget)
    # setupUi

    def retranslateUi(self, PreBuiltXPathsManagerWidget):
        PreBuiltXPathsManagerWidget.setWindowTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"XPath presets", None))
        PreBuiltXPathsManagerWidget.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"page", None))
        self.label_presets_title.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"XPath presets", None))
        self.label_presets_title.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"page-title", None))
        self.label_presets_hint.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Reusable sets of expressions and headers, available from the Presets menu.", None))
        self.label_presets_hint.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"hint", None))
        self.groupBox.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"card", None))
        self.label_groupBox_title.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"New preset", None))
        self.label_groupBox_title.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"card-title", None))
        self.label.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Expressions and headers are paired in order: the first header names the first expression's column.", None))
        self.label.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"hint", None))
        self.label_new_expressions.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"XPath expressions", None))
        self.label_new_expressions.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"field-label", None))
        self.line_edit_xpath_expression.setPlaceholderText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"XPath expression", None))
#if QT_CONFIG(tooltip)
        self.button_add_xpath_to_list.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Add the expression to the list below.", None))
#endif // QT_CONFIG(tooltip)
        self.button_add_xpath_to_list.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Add", None))
        self.label_new_headers.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"CSV headers", None))
        self.label_new_headers.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"field-label", None))
        self.line_edit_csv_header.setPlaceholderText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Header (comma-separated for several)", None))
#if QT_CONFIG(tooltip)
        self.button_add_csv_header_to_list.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Add the header(s) to the list below.", None))
#endif // QT_CONFIG(tooltip)
        self.button_add_csv_header_to_list.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Add", None))
        self.line_edit_config_name.setPlaceholderText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Preset name", None))
#if QT_CONFIG(tooltip)
        self.button_save_config.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Save the expressions and headers above as a new preset.", None))
#endif // QT_CONFIG(tooltip)
        self.button_save_config.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Save preset", None))
        self.button_save_config.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"primary", None))
        self.groupBox_pre_built_xpaths_main.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"card", None))
        self.label_groupBox_pre_built_xpaths_main_title.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Edit preset", None))
        self.label_groupBox_pre_built_xpaths_main_title.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"card-title", None))
        self.label_9.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Load a preset to change or reorder its expressions and headers.", None))
        self.label_9.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"hint", None))
        self.combobox_xpath_configs.setPlaceholderText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"No presets", None))
#if QT_CONFIG(tooltip)
        self.button_load_config.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Load the selected preset into the lists below.", None))
#endif // QT_CONFIG(tooltip)
        self.button_load_config.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Load", None))
#if QT_CONFIG(tooltip)
        self.button_delete_config.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Delete the selected preset.", None))
#endif // QT_CONFIG(tooltip)
        self.button_delete_config.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Delete", None))
        self.button_delete_config.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"danger", None))
        self.label_7.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"XPath expressions", None))
        self.label_7.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"field-label", None))
        self.label_8.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"CSV headers", None))
        self.label_8.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"field-label", None))
        self.button_open_config_directory.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Open config folder", None))
        self.button_open_config_directory.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"flat", None))
#if QT_CONFIG(tooltip)
        self.button_save_changes.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Save the edited lists to the loaded preset.", None))
#endif // QT_CONFIG(tooltip)
        self.button_save_changes.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Save changes", None))
        self.button_save_changes.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"primary", None))
        self.label_remove_hint.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Remove actions apply to the list you clicked last.", None))
        self.label_remove_hint.setProperty(u"role", QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"hint", None))
#if QT_CONFIG(tooltip)
        self.button_remove_selected.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Remove the selected entry from the list you clicked last.", None))
#endif // QT_CONFIG(tooltip)
        self.button_remove_selected.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Remove selected", None))
#if QT_CONFIG(tooltip)
        self.button_remove_all.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Remove every entry from the list you clicked last.", None))
#endif // QT_CONFIG(tooltip)
        self.button_remove_all.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Remove all", None))
    # retranslateUi

