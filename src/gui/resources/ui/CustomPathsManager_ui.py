# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CustomPathsManager.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QFrame,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)
from gui.resources.qrc import xmluvation_resources_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(689, 195)
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Form.setWindowIcon(icon)
        Form.setStyleSheet(u"    QWidget {\n"
"        background-color: #232428;\n"
"        color: #ffffff;\n"
"        font-family: Arial, sans-serif;\n"
"        border-radius: 6px;\n"
"    }\n"
"	\n"
"	QPushButton#button_delete_action {\n"
"	     background-color: #ff5757;\n"
"        color: #000000;\n"
"        border: none;\n"
"        padding: 8px 14px;\n"
"        border-radius: 6px;\n"
"        font: bold;\n"
"	}\n"
"	\n"
"    QPushButton#button_delete_action:hover {\n"
"        background-color: #a33c3c;\n"
"    }\n"
"\n"
"    QPushButton#button_delete_action:pressed {\n"
"        background-color: #313338;\n"
"        color: #ffffff;\n"
"        padding-left: 9px; /* Creates a \"pressed\" effect */\n"
"        padding-top: 8px;\n"
"    }\n"
"	\n"
"    QPushButton {\n"
"        background-color: #ffc857;\n"
"        color: #000000;\n"
"        border: none;\n"
"        padding: 8px 14px;\n"
"        border-radius: 6px;\n"
"        font: bold;\n"
"    }\n"
"\n"
"    QPushButton:hover {\n"
"        background-color: #a3803c;\n"
""
                        "    }\n"
"\n"
"    QPushButton:pressed {\n"
"        background-color: #313338;\n"
"        color: #ffffff;\n"
"        padding-left: 9px; /* Creates a \"pressed\" effect */\n"
"        padding-top: 8px;\n"
"    }\n"
"	\n"
"    QLineEdit, QComboBox {\n"
"        background-color: #313338;\n"
"        border: 1px solid #4a4a4a;\n"
"        padding: 6px;\n"
"        border-radius: 6px;\n"
"    }\n"
"	\n"
"    QPushButton:disabled {\n"
"        background-color: #808080;\n"
"    }\n"
"\n"
"    QComboBox:disabled {\n"
"        background-color: #808080;    \n"
"    }\n"
"	\n"
"   QComboBox::drop-down {\n"
"      border: none;\n"
"      background-color: #ffc857;\n"
"      width: 20px;\n"
"      border-top-right-radius: 6px;\n"
"      border-bottom-right-radius: 6px;\n"
"  	  image: url(:/images/drpdwn_arrow.png)\n"
"    }")
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.hor_layout_main = QHBoxLayout()
        self.hor_layout_main.setObjectName(u"hor_layout_main")
        self.label_combobox_desc = QLabel(Form)
        self.label_combobox_desc.setObjectName(u"label_combobox_desc")
        self.label_combobox_desc.setMaximumSize(QSize(145, 16777215))

        self.hor_layout_main.addWidget(self.label_combobox_desc)

        self.combobox_path_names = QComboBox(Form)
        self.combobox_path_names.setObjectName(u"combobox_path_names")

        self.hor_layout_main.addWidget(self.combobox_path_names)

        self.button_load_action = QPushButton(Form)
        self.button_load_action.setObjectName(u"button_load_action")
        self.button_load_action.setMaximumSize(QSize(100, 16777215))

        self.hor_layout_main.addWidget(self.button_load_action)

        self.button_delete_action = QPushButton(Form)
        self.button_delete_action.setObjectName(u"button_delete_action")
        self.button_delete_action.setMaximumSize(QSize(100, 16777215))
        self.button_delete_action.setStyleSheet(u"")

        self.hor_layout_main.addWidget(self.button_delete_action)


        self.verticalLayout_2.addLayout(self.hor_layout_main)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        self.form_layout_main = QFormLayout()
        self.form_layout_main.setObjectName(u"form_layout_main")
        self.form_layout_main.setHorizontalSpacing(6)
        self.form_layout_main.setContentsMargins(-1, 0, -1, -1)
        self.label_path_name = QLabel(Form)
        self.label_path_name.setObjectName(u"label_path_name")

        self.form_layout_main.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_path_name)

        self.line_edit_path_name = QLineEdit(Form)
        self.line_edit_path_name.setObjectName(u"line_edit_path_name")

        self.form_layout_main.setWidget(2, QFormLayout.ItemRole.FieldRole, self.line_edit_path_name)

        self.label_path_value = QLabel(Form)
        self.label_path_value.setObjectName(u"label_path_value")

        self.form_layout_main.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_path_value)

        self.line_edit_path_value = QLineEdit(Form)
        self.line_edit_path_value.setObjectName(u"line_edit_path_value")

        self.form_layout_main.setWidget(3, QFormLayout.ItemRole.FieldRole, self.line_edit_path_value)

        self.label_desc = QLabel(Form)
        self.label_desc.setObjectName(u"label_desc")
        self.label_desc.setBaseSize(QSize(0, 0))

        self.form_layout_main.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_desc)

        self.label_text_desc = QLabel(Form)
        self.label_text_desc.setObjectName(u"label_text_desc")
        self.label_text_desc.setMargin(0)
        self.label_text_desc.setIndent(-1)

        self.form_layout_main.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label_text_desc)


        self.verticalLayout_2.addLayout(self.form_layout_main)

        self.button_save_changes = QPushButton(Form)
        self.button_save_changes.setObjectName(u"button_save_changes")

        self.verticalLayout_2.addWidget(self.button_save_changes)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Custom Paths Manager", None))
        self.label_combobox_desc.setText(QCoreApplication.translate("Form", u"Select a custom path here:", None))
        self.combobox_path_names.setPlaceholderText(QCoreApplication.translate("Form", u"Custom path names...", None))
        self.button_load_action.setText(QCoreApplication.translate("Form", u"Load Path", None))
        self.button_delete_action.setText(QCoreApplication.translate("Form", u"Delete Path", None))
        self.label_path_name.setText(QCoreApplication.translate("Form", u"Path Name:", None))
        self.line_edit_path_name.setPlaceholderText(QCoreApplication.translate("Form", u"Path name as shown in the menubar...", None))
        self.label_path_value.setText(QCoreApplication.translate("Form", u"Path Value:", None))
        self.line_edit_path_value.setPlaceholderText(QCoreApplication.translate("Form", u"Path value of the path name...", None))
        self.label_desc.setText(QCoreApplication.translate("Form", u"Description:", None))
        self.label_text_desc.setText(QCoreApplication.translate("Form", u"User created paths manager, you can load a custom path any change it's values here or you can delete the path.", None))
        self.button_save_changes.setText(QCoreApplication.translate("Form", u"Save Changes", None))
    # retranslateUi

