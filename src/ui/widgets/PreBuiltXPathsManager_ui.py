# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreBuiltXPathsManagerjPpWdA.ui'
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
import resources.qrc.xmluvation_resources_rc

class Ui_PreBuiltXPathsManagerWidget(object):
    def setupUi(self, PreBuiltXPathsManagerWidget):
        if not PreBuiltXPathsManagerWidget.objectName():
            PreBuiltXPathsManagerWidget.setObjectName(u"PreBuiltXPathsManagerWidget")
        PreBuiltXPathsManagerWidget.resize(550, 675)
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        PreBuiltXPathsManagerWidget.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(PreBuiltXPathsManagerWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(PreBuiltXPathsManagerWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_7.addWidget(self.label)

        self.groupBox_2 = QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.line_edit_xpath_expression = QLineEdit(self.groupBox_2)
        self.line_edit_xpath_expression.setObjectName(u"line_edit_xpath_expression")

        self.horizontalLayout_3.addWidget(self.line_edit_xpath_expression)

        self.button_add_xpath_to_list = QPushButton(self.groupBox_2)
        self.button_add_xpath_to_list.setObjectName(u"button_add_xpath_to_list")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.button_add_xpath_to_list.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.button_add_xpath_to_list)


        self.verticalLayout_8.addLayout(self.horizontalLayout_3)

        self.list_widget_xpath_expressions = QListWidget(self.groupBox_2)
        self.list_widget_xpath_expressions.setObjectName(u"list_widget_xpath_expressions")

        self.verticalLayout_8.addWidget(self.list_widget_xpath_expressions)


        self.verticalLayout_7.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(self.groupBox)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_3 = QLabel(self.groupBox_3)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.line_edit_csv_header = QLineEdit(self.groupBox_3)
        self.line_edit_csv_header.setObjectName(u"line_edit_csv_header")

        self.horizontalLayout_4.addWidget(self.line_edit_csv_header)

        self.button_add_csv_header_to_list = QPushButton(self.groupBox_3)
        self.button_add_csv_header_to_list.setObjectName(u"button_add_csv_header_to_list")
        self.button_add_csv_header_to_list.setIcon(icon1)

        self.horizontalLayout_4.addWidget(self.button_add_csv_header_to_list)


        self.verticalLayout_9.addLayout(self.horizontalLayout_4)

        self.list_widget_csv_headers = QListWidget(self.groupBox_3)
        self.list_widget_csv_headers.setObjectName(u"list_widget_csv_headers")

        self.verticalLayout_9.addWidget(self.list_widget_csv_headers)


        self.verticalLayout_7.addWidget(self.groupBox_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_5.addWidget(self.label_4)

        self.line_edit_config_name = QLineEdit(self.groupBox)
        self.line_edit_config_name.setObjectName(u"line_edit_config_name")

        self.horizontalLayout_5.addWidget(self.line_edit_config_name)

        self.button_save_config = QPushButton(self.groupBox)
        self.button_save_config.setObjectName(u"button_save_config")

        self.horizontalLayout_5.addWidget(self.button_save_config)


        self.verticalLayout_7.addLayout(self.horizontalLayout_5)


        self.verticalLayout.addWidget(self.groupBox)

        self.line = QFrame(PreBuiltXPathsManagerWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.groupBox_pre_built_xpaths_main = QGroupBox(PreBuiltXPathsManagerWidget)
        self.groupBox_pre_built_xpaths_main.setObjectName(u"groupBox_pre_built_xpaths_main")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_pre_built_xpaths_main)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lable_pre_built_xpaths = QLabel(self.groupBox_pre_built_xpaths_main)
        self.lable_pre_built_xpaths.setObjectName(u"lable_pre_built_xpaths")

        self.horizontalLayout.addWidget(self.lable_pre_built_xpaths)

        self.combobox_xpath_configs = QComboBox(self.groupBox_pre_built_xpaths_main)
        self.combobox_xpath_configs.setObjectName(u"combobox_xpath_configs")
        self.combobox_xpath_configs.setEditable(True)

        self.horizontalLayout.addWidget(self.combobox_xpath_configs)

        self.button_load_config = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_load_config.setObjectName(u"button_load_config")

        self.horizontalLayout.addWidget(self.button_load_config)

        self.button_delete_config = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_delete_config.setObjectName(u"button_delete_config")

        self.horizontalLayout.addWidget(self.button_delete_config)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.groupBox_xpath_expressions = QGroupBox(self.groupBox_pre_built_xpaths_main)
        self.groupBox_xpath_expressions.setObjectName(u"groupBox_xpath_expressions")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_xpath_expressions)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.list_widget_edit_xpath_expressions = QListWidget(self.groupBox_xpath_expressions)
        self.list_widget_edit_xpath_expressions.setObjectName(u"list_widget_edit_xpath_expressions")

        self.verticalLayout_4.addWidget(self.list_widget_edit_xpath_expressions)


        self.verticalLayout_2.addWidget(self.groupBox_xpath_expressions)

        self.groupBox_csv_headers = QGroupBox(self.groupBox_pre_built_xpaths_main)
        self.groupBox_csv_headers.setObjectName(u"groupBox_csv_headers")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_csv_headers)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.list_widget_edit_csv_headers = QListWidget(self.groupBox_csv_headers)
        self.list_widget_edit_csv_headers.setObjectName(u"list_widget_edit_csv_headers")

        self.verticalLayout_5.addWidget(self.list_widget_edit_csv_headers)


        self.verticalLayout_2.addWidget(self.groupBox_csv_headers)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.button_remove_selected = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_remove_selected.setObjectName(u"button_remove_selected")

        self.horizontalLayout_2.addWidget(self.button_remove_selected)

        self.button_remove_all = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_remove_all.setObjectName(u"button_remove_all")

        self.horizontalLayout_2.addWidget(self.button_remove_all)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addWidget(self.groupBox_pre_built_xpaths_main)


        self.retranslateUi(PreBuiltXPathsManagerWidget)

        QMetaObject.connectSlotsByName(PreBuiltXPathsManagerWidget)
    # setupUi

    def retranslateUi(self, PreBuiltXPathsManagerWidget):
        PreBuiltXPathsManagerWidget.setWindowTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Create pre-built XPaths", None))
        self.label.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Here you can create your own pre-built XPath Expression and CSV Headers autofill configuration:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"XPath Expressions", None))
        self.label_2.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Enter a XPath Expression:", None))
        self.button_add_xpath_to_list.setText("")
        self.groupBox_3.setTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"CSV Headers", None))
        self.label_3.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Enter a CSV Header:", None))
        self.button_add_csv_header_to_list.setText("")
        self.label_4.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Enter a name for the pre-built autofill:", None))
        self.button_save_config.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Save Autofill", None))
        self.groupBox_pre_built_xpaths_main.setTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Edit Pre-built XPaths", None))
        self.lable_pre_built_xpaths.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Select pre-built XPath autofill:", None))
        self.button_load_config.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Load", None))
        self.button_delete_config.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Delete", None))
        self.groupBox_xpath_expressions.setTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"XPath Expresions", None))
        self.groupBox_csv_headers.setTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"CSV Headers", None))
        self.button_remove_selected.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Remove Selected", None))
        self.button_remove_all.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Remove All", None))
    # retranslateUi

