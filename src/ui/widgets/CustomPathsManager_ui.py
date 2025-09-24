# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CustomPathsManager.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)
import resources.qrc.xmluvation_resources_rc

class Ui_CustomPathsManagerWidget(object):
    def setupUi(self, CustomPathsManagerWidget):
        if not CustomPathsManagerWidget.objectName():
            CustomPathsManagerWidget.setObjectName(u"CustomPathsManagerWidget")
        CustomPathsManagerWidget.resize(515, 518)
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        CustomPathsManagerWidget.setWindowIcon(icon)
        CustomPathsManagerWidget.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(CustomPathsManagerWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(CustomPathsManagerWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_description_create_custom_path = QLabel(self.groupBox)
        self.label_description_create_custom_path.setObjectName(u"label_description_create_custom_path")

        self.verticalLayout.addWidget(self.label_description_create_custom_path)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_path_name_2 = QLabel(self.groupBox)
        self.label_path_name_2.setObjectName(u"label_path_name_2")

        self.horizontalLayout.addWidget(self.label_path_name_2)

        self.line_edit_path_name_2 = QLineEdit(self.groupBox)
        self.line_edit_path_name_2.setObjectName(u"line_edit_path_name_2")

        self.horizontalLayout.addWidget(self.line_edit_path_name_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_path_folder = QLabel(self.groupBox)
        self.label_path_folder.setObjectName(u"label_path_folder")

        self.horizontalLayout_2.addWidget(self.label_path_folder)

        self.line_edit_path_folder = QLineEdit(self.groupBox)
        self.line_edit_path_folder.setObjectName(u"line_edit_path_folder")

        self.horizontalLayout_2.addWidget(self.line_edit_path_folder)

        self.button_borwse_path_folder = QPushButton(self.groupBox)
        self.button_borwse_path_folder.setObjectName(u"button_borwse_path_folder")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.FolderNew))
        self.button_borwse_path_folder.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.button_borwse_path_folder)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.button_create_custom_path = QPushButton(self.groupBox)
        self.button_create_custom_path.setObjectName(u"button_create_custom_path")

        self.verticalLayout.addWidget(self.button_create_custom_path)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.line = QFrame(CustomPathsManagerWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        self.groupBox_2 = QGroupBox(CustomPathsManagerWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_Buttons = QHBoxLayout()
        self.horizontalLayout_Buttons.setObjectName(u"horizontalLayout_Buttons")
        self.label_combobox_desc = QLabel(self.groupBox_2)
        self.label_combobox_desc.setObjectName(u"label_combobox_desc")
        self.label_combobox_desc.setMaximumSize(QSize(145, 16777215))

        self.horizontalLayout_Buttons.addWidget(self.label_combobox_desc)

        self.combobox_path_names = QComboBox(self.groupBox_2)
        self.combobox_path_names.setObjectName(u"combobox_path_names")
        self.combobox_path_names.setPlaceholderText(u"Custom paths...")

        self.horizontalLayout_Buttons.addWidget(self.combobox_path_names)

        self.button_load_action = QPushButton(self.groupBox_2)
        self.button_load_action.setObjectName(u"button_load_action")
        self.button_load_action.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_Buttons.addWidget(self.button_load_action)

        self.button_delete_action = QPushButton(self.groupBox_2)
        self.button_delete_action.setObjectName(u"button_delete_action")
        self.button_delete_action.setMaximumSize(QSize(100, 16777215))
        self.button_delete_action.setStyleSheet(u"")

        self.horizontalLayout_Buttons.addWidget(self.button_delete_action)


        self.verticalLayout_3.addLayout(self.horizontalLayout_Buttons)

        self.form_layout_main = QFormLayout()
        self.form_layout_main.setObjectName(u"form_layout_main")
        self.form_layout_main.setHorizontalSpacing(6)
        self.form_layout_main.setContentsMargins(-1, 0, -1, -1)
        self.label_path_name = QLabel(self.groupBox_2)
        self.label_path_name.setObjectName(u"label_path_name")

        self.form_layout_main.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_path_name)

        self.line_edit_path_name = QLineEdit(self.groupBox_2)
        self.line_edit_path_name.setObjectName(u"line_edit_path_name")

        self.form_layout_main.setWidget(2, QFormLayout.ItemRole.FieldRole, self.line_edit_path_name)

        self.label_path_value = QLabel(self.groupBox_2)
        self.label_path_value.setObjectName(u"label_path_value")

        self.form_layout_main.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_path_value)

        self.line_edit_path_value = QLineEdit(self.groupBox_2)
        self.line_edit_path_value.setObjectName(u"line_edit_path_value")

        self.form_layout_main.setWidget(3, QFormLayout.ItemRole.FieldRole, self.line_edit_path_value)

        self.label_desc = QLabel(self.groupBox_2)
        self.label_desc.setObjectName(u"label_desc")
        self.label_desc.setBaseSize(QSize(0, 0))

        self.form_layout_main.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_desc)

        self.label_text_desc = QLabel(self.groupBox_2)
        self.label_text_desc.setObjectName(u"label_text_desc")
        self.label_text_desc.setWordWrap(True)
        self.label_text_desc.setMargin(0)
        self.label_text_desc.setIndent(-1)

        self.form_layout_main.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label_text_desc)


        self.verticalLayout_3.addLayout(self.form_layout_main)


        self.verticalLayout_2.addWidget(self.groupBox_2)

        self.button_save_changes = QPushButton(CustomPathsManagerWidget)
        self.button_save_changes.setObjectName(u"button_save_changes")

        self.verticalLayout_2.addWidget(self.button_save_changes)


        self.retranslateUi(CustomPathsManagerWidget)

        QMetaObject.connectSlotsByName(CustomPathsManagerWidget)
    # setupUi

    def retranslateUi(self, CustomPathsManagerWidget):
        CustomPathsManagerWidget.setWindowTitle(QCoreApplication.translate("CustomPathsManagerWidget", u"Custom Paths Manager", None))
        self.groupBox.setTitle(QCoreApplication.translate("CustomPathsManagerWidget", u"Create custom paths", None))
        self.label_description_create_custom_path.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Here you can add and create custom path configurations.\n"
"Enter a path name which will be added to the menubar.\n"
"Enter a folder path which is associated with the give path name.", None))
        self.label_path_name_2.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path name:", None))
        self.label_path_folder.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path folder:", None))
        self.button_borwse_path_folder.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Browse", None))
        self.button_create_custom_path.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Create custom path", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("CustomPathsManagerWidget", u"Edit custom paths", None))
        self.label_combobox_desc.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Select a custom path here:", None))
        self.button_load_action.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Load Path", None))
        self.button_delete_action.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Delete Path", None))
        self.label_path_name.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path name:", None))
        self.line_edit_path_name.setPlaceholderText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path name as shown in the menubar...", None))
        self.label_path_value.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path folder", None))
        self.line_edit_path_value.setPlaceholderText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path value of the path name...", None))
        self.label_desc.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Description:", None))
        self.label_text_desc.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"User created paths manager, you can load a custom path and change it's values here or you can delete the path.", None))
        self.button_save_changes.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Save Changes", None))
    # retranslateUi

