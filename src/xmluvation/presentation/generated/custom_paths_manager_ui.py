# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CustomPathsManager.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)
from . import xmluvation_resources_rc

class Ui_CustomPathsManagerWidget(object):
    def setupUi(self, CustomPathsManagerWidget):
        if not CustomPathsManagerWidget.objectName():
            CustomPathsManagerWidget.setObjectName(u"CustomPathsManagerWidget")
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        CustomPathsManagerWidget.setWindowIcon(icon)
        CustomPathsManagerWidget.setMinimumSize(QSize(560, 0))
        self.layout_CustomPathsManagerWidget = QVBoxLayout(CustomPathsManagerWidget)
        self.layout_CustomPathsManagerWidget.setSpacing(14)
        self.layout_CustomPathsManagerWidget.setObjectName(u"layout_CustomPathsManagerWidget")
        self.layout_CustomPathsManagerWidget.setContentsMargins(24, 22, 24, 22)
        self.label_paths_title = QLabel(CustomPathsManagerWidget)
        self.label_paths_title.setObjectName(u"label_paths_title")

        self.layout_CustomPathsManagerWidget.addWidget(self.label_paths_title)

        self.label_paths_hint = QLabel(CustomPathsManagerWidget)
        self.label_paths_hint.setObjectName(u"label_paths_hint")
        self.label_paths_hint.setWordWrap(True)

        self.layout_CustomPathsManagerWidget.addWidget(self.label_paths_hint)

        self.groupBox = QFrame(CustomPathsManagerWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_groupBox = QVBoxLayout(self.groupBox)
        self.layout_groupBox.setSpacing(10)
        self.layout_groupBox.setObjectName(u"layout_groupBox")
        self.layout_groupBox.setContentsMargins(18, 16, 18, 18)
        self.label_groupBox_title = QLabel(self.groupBox)
        self.label_groupBox_title.setObjectName(u"label_groupBox_title")

        self.layout_groupBox.addWidget(self.label_groupBox_title)

        self.label_description_create_custom_path = QLabel(self.groupBox)
        self.label_description_create_custom_path.setObjectName(u"label_description_create_custom_path")
        self.label_description_create_custom_path.setWordWrap(True)

        self.layout_groupBox.addWidget(self.label_description_create_custom_path)

        self.layout_create_form = QFormLayout()
        self.layout_create_form.setObjectName(u"layout_create_form")
        self.layout_create_form.setHorizontalSpacing(10)
        self.layout_create_form.setVerticalSpacing(10)
        self.layout_create_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_create_form.setContentsMargins(0, 4, 0, 4)
        self.label_path_name_2 = QLabel(self.groupBox)
        self.label_path_name_2.setObjectName(u"label_path_name_2")

        self.layout_create_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_path_name_2)

        self.line_edit_custom_path_name = QLineEdit(self.groupBox)
        self.line_edit_custom_path_name.setObjectName(u"line_edit_custom_path_name")
        self.line_edit_custom_path_name.setClearButtonEnabled(True)

        self.layout_create_form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.line_edit_custom_path_name)

        self.label_path_folder = QLabel(self.groupBox)
        self.label_path_folder.setObjectName(u"label_path_folder")

        self.layout_create_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_path_folder)

        self.layout_create_folder = QHBoxLayout()
        self.layout_create_folder.setSpacing(8)
        self.layout_create_folder.setObjectName(u"layout_create_folder")
        self.layout_create_folder.setContentsMargins(0, 0, 0, 0)
        self.line_edit_custom_path_value = QLineEdit(self.groupBox)
        self.line_edit_custom_path_value.setObjectName(u"line_edit_custom_path_value")
        self.line_edit_custom_path_value.setClearButtonEnabled(True)

        self.layout_create_folder.addWidget(self.line_edit_custom_path_value)

        self.button_browse_path_folder = QPushButton(self.groupBox)
        self.button_browse_path_folder.setObjectName(u"button_browse_path_folder")

        self.layout_create_folder.addWidget(self.button_browse_path_folder)


        self.layout_create_form.setLayout(1, QFormLayout.ItemRole.FieldRole, self.layout_create_folder)


        self.layout_groupBox.addLayout(self.layout_create_form)

        self.layout_create_actions = QHBoxLayout()
        self.layout_create_actions.setSpacing(8)
        self.layout_create_actions.setObjectName(u"layout_create_actions")
        self.layout_create_actions.setContentsMargins(0, 0, 0, 0)
        self.spacer_1 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_create_actions.addItem(self.spacer_1)

        self.button_create_custom_path = QPushButton(self.groupBox)
        self.button_create_custom_path.setObjectName(u"button_create_custom_path")

        self.layout_create_actions.addWidget(self.button_create_custom_path)


        self.layout_groupBox.addLayout(self.layout_create_actions)


        self.layout_CustomPathsManagerWidget.addWidget(self.groupBox)

        self.groupBox_2 = QFrame(CustomPathsManagerWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout_groupBox_2 = QVBoxLayout(self.groupBox_2)
        self.layout_groupBox_2.setSpacing(10)
        self.layout_groupBox_2.setObjectName(u"layout_groupBox_2")
        self.layout_groupBox_2.setContentsMargins(18, 16, 18, 18)
        self.label_groupBox_2_title = QLabel(self.groupBox_2)
        self.label_groupBox_2_title.setObjectName(u"label_groupBox_2_title")

        self.layout_groupBox_2.addWidget(self.label_groupBox_2_title)

        self.label_text_desc = QLabel(self.groupBox_2)
        self.label_text_desc.setObjectName(u"label_text_desc")
        self.label_text_desc.setWordWrap(True)

        self.layout_groupBox_2.addWidget(self.label_text_desc)

        self.layout_edit_form = QFormLayout()
        self.layout_edit_form.setObjectName(u"layout_edit_form")
        self.layout_edit_form.setHorizontalSpacing(10)
        self.layout_edit_form.setVerticalSpacing(10)
        self.layout_edit_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout_edit_form.setContentsMargins(0, 4, 0, 4)
        self.label_combobox_desc = QLabel(self.groupBox_2)
        self.label_combobox_desc.setObjectName(u"label_combobox_desc")

        self.layout_edit_form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_combobox_desc)

        self.layout_edit_select = QHBoxLayout()
        self.layout_edit_select.setSpacing(8)
        self.layout_edit_select.setObjectName(u"layout_edit_select")
        self.layout_edit_select.setContentsMargins(0, 0, 0, 0)
        self.combobox_path_names = QComboBox(self.groupBox_2)
        self.combobox_path_names.setObjectName(u"combobox_path_names")

        self.layout_edit_select.addWidget(self.combobox_path_names)

        self.button_load_action = QPushButton(self.groupBox_2)
        self.button_load_action.setObjectName(u"button_load_action")

        self.layout_edit_select.addWidget(self.button_load_action)

        self.button_delete_action = QPushButton(self.groupBox_2)
        self.button_delete_action.setObjectName(u"button_delete_action")

        self.layout_edit_select.addWidget(self.button_delete_action)

        self.layout_edit_select.setStretch(0, 1)

        self.layout_edit_form.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layout_edit_select)

        self.label_path_name = QLabel(self.groupBox_2)
        self.label_path_name.setObjectName(u"label_path_name")

        self.layout_edit_form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_path_name)

        self.line_edit_path_name = QLineEdit(self.groupBox_2)
        self.line_edit_path_name.setObjectName(u"line_edit_path_name")
        self.line_edit_path_name.setClearButtonEnabled(True)

        self.layout_edit_form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.line_edit_path_name)

        self.label_path_value = QLabel(self.groupBox_2)
        self.label_path_value.setObjectName(u"label_path_value")

        self.layout_edit_form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_path_value)

        self.line_edit_path_value = QLineEdit(self.groupBox_2)
        self.line_edit_path_value.setObjectName(u"line_edit_path_value")
        self.line_edit_path_value.setClearButtonEnabled(True)

        self.layout_edit_form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.line_edit_path_value)


        self.layout_groupBox_2.addLayout(self.layout_edit_form)

        self.layout_edit_actions = QHBoxLayout()
        self.layout_edit_actions.setSpacing(8)
        self.layout_edit_actions.setObjectName(u"layout_edit_actions")
        self.layout_edit_actions.setContentsMargins(0, 0, 0, 0)
        self.button_open_config_directory = QPushButton(self.groupBox_2)
        self.button_open_config_directory.setObjectName(u"button_open_config_directory")

        self.layout_edit_actions.addWidget(self.button_open_config_directory)

        self.spacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_edit_actions.addItem(self.spacer_2)

        self.button_save_changes = QPushButton(self.groupBox_2)
        self.button_save_changes.setObjectName(u"button_save_changes")

        self.layout_edit_actions.addWidget(self.button_save_changes)


        self.layout_groupBox_2.addLayout(self.layout_edit_actions)


        self.layout_CustomPathsManagerWidget.addWidget(self.groupBox_2)


        self.retranslateUi(CustomPathsManagerWidget)

        QMetaObject.connectSlotsByName(CustomPathsManagerWidget)
    # setupUi

    def retranslateUi(self, CustomPathsManagerWidget):
        CustomPathsManagerWidget.setWindowTitle(QCoreApplication.translate("CustomPathsManagerWidget", u"Custom paths", None))
        CustomPathsManagerWidget.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"page", None))
        self.label_paths_title.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Custom paths", None))
        self.label_paths_title.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"page-title", None))
        self.label_paths_hint.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Folders you use often, available from the Paths menu.", None))
        self.label_paths_hint.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"hint", None))
        self.groupBox.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"card", None))
        self.label_groupBox_title.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"New path", None))
        self.label_groupBox_title.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"card-title", None))
        self.label_description_create_custom_path.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Save a folder under a name; pick it later from the Paths menu.", None))
        self.label_description_create_custom_path.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"hint", None))
        self.label_path_name_2.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Name", None))
        self.label_path_name_2.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"field-label", None))
        self.line_edit_custom_path_name.setPlaceholderText(QCoreApplication.translate("CustomPathsManagerWidget", u"Shown in the Paths menu", None))
        self.label_path_folder.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Folder", None))
        self.label_path_folder.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"field-label", None))
        self.line_edit_custom_path_value.setPlaceholderText(QCoreApplication.translate("CustomPathsManagerWidget", u"Folder to fill in as the XML source", None))
        self.button_browse_path_folder.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Browse\u2026", None))
        self.button_create_custom_path.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Save path", None))
        self.button_create_custom_path.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"primary", None))
        self.groupBox_2.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"card", None))
        self.label_groupBox_2_title.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Edit saved path", None))
        self.label_groupBox_2_title.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"card-title", None))
        self.label_text_desc.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Load a saved path to rename it, change its folder, or delete it.", None))
        self.label_text_desc.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"hint", None))
        self.label_combobox_desc.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Saved path", None))
        self.label_combobox_desc.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"field-label", None))
        self.combobox_path_names.setPlaceholderText(QCoreApplication.translate("CustomPathsManagerWidget", u"No saved paths", None))
        self.button_load_action.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Load", None))
        self.button_delete_action.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Delete", None))
        self.button_delete_action.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"danger", None))
        self.label_path_name.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Name", None))
        self.label_path_name.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"field-label", None))
        self.line_edit_path_name.setPlaceholderText(QCoreApplication.translate("CustomPathsManagerWidget", u"Name shown in the Paths menu", None))
        self.label_path_value.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Folder", None))
        self.label_path_value.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"field-label", None))
        self.line_edit_path_value.setPlaceholderText(QCoreApplication.translate("CustomPathsManagerWidget", u"Saved folder", None))
        self.button_open_config_directory.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Open config folder", None))
        self.button_open_config_directory.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"flat", None))
        self.button_save_changes.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Save changes", None))
        self.button_save_changes.setProperty(u"role", QCoreApplication.translate("CustomPathsManagerWidget", u"primary", None))
    # retranslateUi

