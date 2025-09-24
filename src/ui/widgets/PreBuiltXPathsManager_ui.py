# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreBuiltXPathsManagerVXMRRa.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(737, 730)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_7.addWidget(self.label)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBox_2 = QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.line_edit_create_xpath_expression = QLineEdit(self.groupBox_2)
        self.line_edit_create_xpath_expression.setObjectName(u"line_edit_create_xpath_expression")

        self.horizontalLayout_3.addWidget(self.line_edit_create_xpath_expression)

        self.button_edit_add_xpath_to_list = QPushButton(self.groupBox_2)
        self.button_edit_add_xpath_to_list.setObjectName(u"button_edit_add_xpath_to_list")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.button_edit_add_xpath_to_list.setIcon(icon)

        self.horizontalLayout_3.addWidget(self.button_edit_add_xpath_to_list)


        self.verticalLayout_8.addLayout(self.horizontalLayout_3)

        self.list_widget_create_xpath_expressions = QListWidget(self.groupBox_2)
        self.list_widget_create_xpath_expressions.setObjectName(u"list_widget_create_xpath_expressions")

        self.verticalLayout_8.addWidget(self.list_widget_create_xpath_expressions)


        self.verticalLayout_6.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(self.groupBox)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_3 = QLabel(self.groupBox_3)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.line_edit_create_csv_header = QLineEdit(self.groupBox_3)
        self.line_edit_create_csv_header.setObjectName(u"line_edit_create_csv_header")

        self.horizontalLayout_4.addWidget(self.line_edit_create_csv_header)

        self.button_edit_add_csv_header_to_list = QPushButton(self.groupBox_3)
        self.button_edit_add_csv_header_to_list.setObjectName(u"button_edit_add_csv_header_to_list")
        self.button_edit_add_csv_header_to_list.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.button_edit_add_csv_header_to_list)


        self.verticalLayout_9.addLayout(self.horizontalLayout_4)

        self.list_widget_create_csv_headers = QListWidget(self.groupBox_3)
        self.list_widget_create_csv_headers.setObjectName(u"list_widget_create_csv_headers")

        self.verticalLayout_9.addWidget(self.list_widget_create_csv_headers)


        self.verticalLayout_6.addWidget(self.groupBox_3)


        self.verticalLayout_7.addLayout(self.verticalLayout_6)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_5.addWidget(self.label_4)

        self.line_edit_create_config_name = QLineEdit(self.groupBox)
        self.line_edit_create_config_name.setObjectName(u"line_edit_create_config_name")

        self.horizontalLayout_5.addWidget(self.line_edit_create_config_name)

        self.button_create_save_config = QPushButton(self.groupBox)
        self.button_create_save_config.setObjectName(u"button_create_save_config")

        self.horizontalLayout_5.addWidget(self.button_create_save_config)


        self.verticalLayout_7.addLayout(self.horizontalLayout_5)


        self.verticalLayout.addWidget(self.groupBox)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.groupBox_pre_built_xpaths_main = QGroupBox(Form)
        self.groupBox_pre_built_xpaths_main.setObjectName(u"groupBox_pre_built_xpaths_main")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_pre_built_xpaths_main)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lable_pre_built_xpaths = QLabel(self.groupBox_pre_built_xpaths_main)
        self.lable_pre_built_xpaths.setObjectName(u"lable_pre_built_xpaths")

        self.horizontalLayout.addWidget(self.lable_pre_built_xpaths)

        self.combobox_pre_built_xpaths_configs = QComboBox(self.groupBox_pre_built_xpaths_main)
        self.combobox_pre_built_xpaths_configs.setObjectName(u"combobox_pre_built_xpaths_configs")
        self.combobox_pre_built_xpaths_configs.setEditable(True)

        self.horizontalLayout.addWidget(self.combobox_pre_built_xpaths_configs)

        self.button_pre_built_xpaths_load_config = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_pre_built_xpaths_load_config.setObjectName(u"button_pre_built_xpaths_load_config")

        self.horizontalLayout.addWidget(self.button_pre_built_xpaths_load_config)

        self.button_pre_built_xpaths_delete_config = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_pre_built_xpaths_delete_config.setObjectName(u"button_pre_built_xpaths_delete_config")

        self.horizontalLayout.addWidget(self.button_pre_built_xpaths_delete_config)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_xpath_expressions = QGroupBox(self.groupBox_pre_built_xpaths_main)
        self.groupBox_xpath_expressions.setObjectName(u"groupBox_xpath_expressions")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_xpath_expressions)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.list_widget_pre_built_xpath_expressions = QListWidget(self.groupBox_xpath_expressions)
        self.list_widget_pre_built_xpath_expressions.setObjectName(u"list_widget_pre_built_xpath_expressions")

        self.verticalLayout_4.addWidget(self.list_widget_pre_built_xpath_expressions)


        self.verticalLayout_3.addWidget(self.groupBox_xpath_expressions)

        self.groupBox_csv_headers = QGroupBox(self.groupBox_pre_built_xpaths_main)
        self.groupBox_csv_headers.setObjectName(u"groupBox_csv_headers")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_csv_headers)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.list_widget_pre_built_csv_headers = QListWidget(self.groupBox_csv_headers)
        self.list_widget_pre_built_csv_headers.setObjectName(u"list_widget_pre_built_csv_headers")

        self.verticalLayout_5.addWidget(self.list_widget_pre_built_csv_headers)


        self.verticalLayout_3.addWidget(self.groupBox_csv_headers)


        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.button_pre_built_remove_selected = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_pre_built_remove_selected.setObjectName(u"button_pre_built_remove_selected")

        self.horizontalLayout_2.addWidget(self.button_pre_built_remove_selected)

        self.button_pre_built_remove_all = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_pre_built_remove_all.setObjectName(u"button_pre_built_remove_all")

        self.horizontalLayout_2.addWidget(self.button_pre_built_remove_all)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addWidget(self.groupBox_pre_built_xpaths_main)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"Create pre-built XPaths", None))
        self.label.setText(QCoreApplication.translate("Form", u"Here you can create your own pre-built XPath Expression and CSV Headers autofill configuration:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"XPath Expressions", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Enter a XPath Expression:", None))
        self.button_edit_add_xpath_to_list.setText("")
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", u"CSV Headers", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Enter a CSV Header:", None))
        self.button_edit_add_csv_header_to_list.setText("")
        self.label_4.setText(QCoreApplication.translate("Form", u"Enter a name for the pre-built autofill:", None))
        self.button_create_save_config.setText(QCoreApplication.translate("Form", u"Save Autofill", None))
        self.groupBox_pre_built_xpaths_main.setTitle(QCoreApplication.translate("Form", u"Edit Pre-built XPaths", None))
        self.lable_pre_built_xpaths.setText(QCoreApplication.translate("Form", u"Select pre-built XPath autofill:", None))
        self.button_pre_built_xpaths_load_config.setText(QCoreApplication.translate("Form", u"Load", None))
        self.button_pre_built_xpaths_delete_config.setText(QCoreApplication.translate("Form", u"Delete", None))
        self.groupBox_xpath_expressions.setTitle(QCoreApplication.translate("Form", u"XPath Expresions", None))
        self.groupBox_csv_headers.setTitle(QCoreApplication.translate("Form", u"CSV Headers", None))
        self.button_pre_built_remove_selected.setText(QCoreApplication.translate("Form", u"Remove Selected", None))
        self.button_pre_built_remove_all.setText(QCoreApplication.translate("Form", u"Remove All", None))
    # retranslateUi

