# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreBuiltXPathsManager.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
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
import gui.resources.qrc.xmluvation_resources_rc

class Ui_PreBuiltXPathsManagerWidget(object):
    def setupUi(self, PreBuiltXPathsManagerWidget):
        if not PreBuiltXPathsManagerWidget.objectName():
            PreBuiltXPathsManagerWidget.setObjectName(u"PreBuiltXPathsManagerWidget")
        PreBuiltXPathsManagerWidget.setWindowModality(Qt.WindowModality.WindowModal)
        PreBuiltXPathsManagerWidget.resize(1005, 675)
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        PreBuiltXPathsManagerWidget.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(PreBuiltXPathsManagerWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.MainHorLayout = QHBoxLayout()
        self.MainHorLayout.setObjectName(u"MainHorLayout")
        self.LeftSide = QVBoxLayout()
        self.LeftSide.setObjectName(u"LeftSide")
        self.groupBox_pre_built_xpaths_main = QGroupBox(PreBuiltXPathsManagerWidget)
        self.groupBox_pre_built_xpaths_main.setObjectName(u"groupBox_pre_built_xpaths_main")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_pre_built_xpaths_main)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_9 = QLabel(self.groupBox_pre_built_xpaths_main)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_2.addWidget(self.label_9)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lable_pre_built_xpaths = QLabel(self.groupBox_pre_built_xpaths_main)
        self.lable_pre_built_xpaths.setObjectName(u"lable_pre_built_xpaths")

        self.horizontalLayout.addWidget(self.lable_pre_built_xpaths)

        self.combobox_xpath_configs = QComboBox(self.groupBox_pre_built_xpaths_main)
        self.combobox_xpath_configs.setObjectName(u"combobox_xpath_configs")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.combobox_xpath_configs.sizePolicy().hasHeightForWidth())
        self.combobox_xpath_configs.setSizePolicy(sizePolicy)
        self.combobox_xpath_configs.setEditable(True)

        self.horizontalLayout.addWidget(self.combobox_xpath_configs)

        self.button_load_config = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_load_config.setObjectName(u"button_load_config")

        self.horizontalLayout.addWidget(self.button_load_config)

        self.button_delete_config = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_delete_config.setObjectName(u"button_delete_config")

        self.horizontalLayout.addWidget(self.button_delete_config)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.frame_3 = QFrame(self.groupBox_pre_built_xpaths_main)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.frame_3)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_7 = QLabel(self.frame_3)
        self.label_7.setObjectName(u"label_7")
        font = QFont()
        font.setBold(True)
        self.label_7.setFont(font)

        self.verticalLayout_8.addWidget(self.label_7)

        self.list_widget_edit_xpath_expressions = QListWidget(self.frame_3)
        self.list_widget_edit_xpath_expressions.setObjectName(u"list_widget_edit_xpath_expressions")
        self.list_widget_edit_xpath_expressions.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.verticalLayout_8.addWidget(self.list_widget_edit_xpath_expressions)


        self.verticalLayout_2.addWidget(self.frame_3)

        self.line_3 = QFrame(self.groupBox_pre_built_xpaths_main)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_3)

        self.frame_4 = QFrame(self.groupBox_pre_built_xpaths_main)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_8 = QLabel(self.frame_4)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font)

        self.verticalLayout_4.addWidget(self.label_8)

        self.list_widget_edit_csv_headers = QListWidget(self.frame_4)
        self.list_widget_edit_csv_headers.setObjectName(u"list_widget_edit_csv_headers")
        self.list_widget_edit_csv_headers.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.verticalLayout_4.addWidget(self.list_widget_edit_csv_headers)


        self.verticalLayout_2.addWidget(self.frame_4)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_2 = QLabel(self.groupBox_pre_built_xpaths_main)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_6.addWidget(self.label_2)

        self.button_save_changes = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_save_changes.setObjectName(u"button_save_changes")
        sizePolicy.setHeightForWidth(self.button_save_changes.sizePolicy().hasHeightForWidth())
        self.button_save_changes.setSizePolicy(sizePolicy)

        self.horizontalLayout_6.addWidget(self.button_save_changes)

        self.button_open_config_directory = QPushButton(self.groupBox_pre_built_xpaths_main)
        self.button_open_config_directory.setObjectName(u"button_open_config_directory")
        sizePolicy.setHeightForWidth(self.button_open_config_directory.sizePolicy().hasHeightForWidth())
        self.button_open_config_directory.setSizePolicy(sizePolicy)

        self.horizontalLayout_6.addWidget(self.button_open_config_directory)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)


        self.LeftSide.addWidget(self.groupBox_pre_built_xpaths_main)


        self.MainHorLayout.addLayout(self.LeftSide)

        self.RightSide = QVBoxLayout()
        self.RightSide.setObjectName(u"RightSide")
        self.groupBox = QGroupBox(PreBuiltXPathsManagerWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_7.addWidget(self.label)

        self.frame = QFrame(self.groupBox)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.line_edit_xpath_expression = QLineEdit(self.frame)
        self.line_edit_xpath_expression.setObjectName(u"line_edit_xpath_expression")

        self.horizontalLayout_3.addWidget(self.line_edit_xpath_expression)

        self.button_add_xpath_to_list = QPushButton(self.frame)
        self.button_add_xpath_to_list.setObjectName(u"button_add_xpath_to_list")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.button_add_xpath_to_list.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.button_add_xpath_to_list)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.list_widget_xpath_expressions = QListWidget(self.frame)
        self.list_widget_xpath_expressions.setObjectName(u"list_widget_xpath_expressions")
        self.list_widget_xpath_expressions.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.verticalLayout_3.addWidget(self.list_widget_xpath_expressions)


        self.verticalLayout_7.addWidget(self.frame)

        self.line_2 = QFrame(self.groupBox)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_7.addWidget(self.line_2)

        self.frame_2 = QFrame(self.groupBox)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.line_edit_csv_header = QLineEdit(self.frame_2)
        self.line_edit_csv_header.setObjectName(u"line_edit_csv_header")

        self.horizontalLayout_4.addWidget(self.line_edit_csv_header)

        self.button_add_csv_header_to_list = QPushButton(self.frame_2)
        self.button_add_csv_header_to_list.setObjectName(u"button_add_csv_header_to_list")
        self.button_add_csv_header_to_list.setIcon(icon1)

        self.horizontalLayout_4.addWidget(self.button_add_csv_header_to_list)


        self.verticalLayout_6.addLayout(self.horizontalLayout_4)

        self.list_widget_csv_headers = QListWidget(self.frame_2)
        self.list_widget_csv_headers.setObjectName(u"list_widget_csv_headers")
        self.list_widget_csv_headers.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.verticalLayout_6.addWidget(self.list_widget_csv_headers)


        self.verticalLayout_7.addWidget(self.frame_2)

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


        self.RightSide.addWidget(self.groupBox)


        self.MainHorLayout.addLayout(self.RightSide)


        self.verticalLayout.addLayout(self.MainHorLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.button_remove_selected = QPushButton(PreBuiltXPathsManagerWidget)
        self.button_remove_selected.setObjectName(u"button_remove_selected")

        self.horizontalLayout_2.addWidget(self.button_remove_selected)

        self.button_remove_all = QPushButton(PreBuiltXPathsManagerWidget)
        self.button_remove_all.setObjectName(u"button_remove_all")

        self.horizontalLayout_2.addWidget(self.button_remove_all)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.line = QFrame(PreBuiltXPathsManagerWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)


        self.retranslateUi(PreBuiltXPathsManagerWidget)

        QMetaObject.connectSlotsByName(PreBuiltXPathsManagerWidget)
    # setupUi

    def retranslateUi(self, PreBuiltXPathsManagerWidget):
        PreBuiltXPathsManagerWidget.setWindowTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"PreBuilt XPaths Manager Widget", None))
#if QT_CONFIG(tooltip)
        PreBuiltXPathsManagerWidget.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Removes the all items in the focused listbox.", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_pre_built_xpaths_main.setTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Edit Pre-built XPaths", None))
        self.label_9.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Here you can edit the custom pre-built configuration for the autofill:", None))
        self.lable_pre_built_xpaths.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Select Config:", None))
#if QT_CONFIG(tooltip)
        self.button_load_config.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Load the selected configuration and fill the two listboxes.", None))
#endif // QT_CONFIG(tooltip)
        self.button_load_config.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Load", None))
#if QT_CONFIG(tooltip)
        self.button_delete_config.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Deletes the selected configurtion all it's values.", None))
#endif // QT_CONFIG(tooltip)
        self.button_delete_config.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Delete", None))
        self.label_7.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Edit XPath Expressions:", None))
        self.label_8.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Edit CSV Headers:", None))
        self.label_2.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Optons:", None))
#if QT_CONFIG(tooltip)
        self.button_save_changes.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Save changes that you made to the two listboxes.", None))
#endif // QT_CONFIG(tooltip)
        self.button_save_changes.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Save Changes", None))
        self.button_open_config_directory.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Open Config Directory", None))
        self.groupBox.setTitle(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Create pre-built XPaths", None))
        self.label.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Here you can create your own pre-built autofill configuration:", None))
        self.line_edit_xpath_expression.setPlaceholderText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Enter a Xpath Expression here...", None))
#if QT_CONFIG(tooltip)
        self.button_add_xpath_to_list.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Add entered XPath Expression to it's listbox.", None))
#endif // QT_CONFIG(tooltip)
        self.button_add_xpath_to_list.setText("")
        self.line_edit_csv_header.setPlaceholderText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Enter header name here (can be comma-separated)...", None))
#if QT_CONFIG(tooltip)
        self.button_add_csv_header_to_list.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Add entered CSV Header to it's listbox.", None))
#endif // QT_CONFIG(tooltip)
        self.button_add_csv_header_to_list.setText("")
        self.label_4.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Pre-bult name:", None))
        self.line_edit_config_name.setPlaceholderText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Enter a name for the configuration...", None))
#if QT_CONFIG(tooltip)
        self.button_save_config.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Save your configurtion with all items that are in the two listboxes.", None))
#endif // QT_CONFIG(tooltip)
        self.button_save_config.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Save Config", None))
#if QT_CONFIG(tooltip)
        self.button_remove_selected.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Removes the currently selected item in the focused listbox.", None))
#endif // QT_CONFIG(tooltip)
        self.button_remove_selected.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Remove Selected Value", None))
#if QT_CONFIG(tooltip)
        self.button_remove_all.setToolTip(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Removes all items in the focused listbox.", None))
#endif // QT_CONFIG(tooltip)
        self.button_remove_all.setText(QCoreApplication.translate("PreBuiltXPathsManagerWidget", u"Remove All Values", None))
    # retranslateUi

