# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CustomPathsManager.ui'
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
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)
import resources.qrc.xmluvation_resources_rc

class Ui_CustomPathsManagerWidget(object):
    def setupUi(self, CustomPathsManagerWidget):
        if not CustomPathsManagerWidget.objectName():
            CustomPathsManagerWidget.setObjectName(u"CustomPathsManagerWidget")
        CustomPathsManagerWidget.setWindowModality(Qt.WindowModality.WindowModal)
        CustomPathsManagerWidget.resize(586, 410)
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        CustomPathsManagerWidget.setWindowIcon(icon)
        CustomPathsManagerWidget.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(CustomPathsManagerWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox = QGroupBox(CustomPathsManagerWidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)

        self.horizontalLayout_7.addWidget(self.label)

        self.label_description_create_custom_path = QLabel(self.groupBox)
        self.label_description_create_custom_path.setObjectName(u"label_description_create_custom_path")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_description_create_custom_path.sizePolicy().hasHeightForWidth())
        self.label_description_create_custom_path.setSizePolicy(sizePolicy2)
        self.label_description_create_custom_path.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_description_create_custom_path.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_7.addWidget(self.label_description_create_custom_path)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_path_name_2 = QLabel(self.groupBox)
        self.label_path_name_2.setObjectName(u"label_path_name_2")

        self.horizontalLayout.addWidget(self.label_path_name_2)

        self.line_edit_custom_path_name = QLineEdit(self.groupBox)
        self.line_edit_custom_path_name.setObjectName(u"line_edit_custom_path_name")

        self.horizontalLayout.addWidget(self.line_edit_custom_path_name)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_path_folder = QLabel(self.groupBox)
        self.label_path_folder.setObjectName(u"label_path_folder")

        self.horizontalLayout_2.addWidget(self.label_path_folder)

        self.line_edit_custom_path_value = QLineEdit(self.groupBox)
        self.line_edit_custom_path_value.setObjectName(u"line_edit_custom_path_value")

        self.horizontalLayout_2.addWidget(self.line_edit_custom_path_value)

        self.button_browse_path_folder = QPushButton(self.groupBox)
        self.button_browse_path_folder.setObjectName(u"button_browse_path_folder")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.FolderNew))
        self.button_browse_path_folder.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.button_browse_path_folder)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_save_config = QLabel(self.groupBox)
        self.label_save_config.setObjectName(u"label_save_config")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_save_config.sizePolicy().hasHeightForWidth())
        self.label_save_config.setSizePolicy(sizePolicy3)

        self.horizontalLayout_6.addWidget(self.label_save_config)

        self.button_create_custom_path = QPushButton(self.groupBox)
        self.button_create_custom_path.setObjectName(u"button_create_custom_path")

        self.horizontalLayout_6.addWidget(self.button_create_custom_path)


        self.verticalLayout.addLayout(self.horizontalLayout_6)


        self.verticalLayout_4.addWidget(self.groupBox)

        self.line = QFrame(CustomPathsManagerWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_4.addWidget(self.line)

        self.groupBox_2 = QGroupBox(CustomPathsManagerWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_desc = QLabel(self.groupBox_2)
        self.label_desc.setObjectName(u"label_desc")
        sizePolicy1.setHeightForWidth(self.label_desc.sizePolicy().hasHeightForWidth())
        self.label_desc.setSizePolicy(sizePolicy1)
        self.label_desc.setBaseSize(QSize(0, 0))

        self.horizontalLayout_3.addWidget(self.label_desc)

        self.label_text_desc = QLabel(self.groupBox_2)
        self.label_text_desc.setObjectName(u"label_text_desc")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_text_desc.sizePolicy().hasHeightForWidth())
        self.label_text_desc.setSizePolicy(sizePolicy4)
        self.label_text_desc.setWordWrap(True)
        self.label_text_desc.setMargin(0)
        self.label_text_desc.setIndent(-1)

        self.horizontalLayout_3.addWidget(self.label_text_desc)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

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

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_path_name = QLabel(self.groupBox_2)
        self.label_path_name.setObjectName(u"label_path_name")

        self.horizontalLayout_4.addWidget(self.label_path_name)

        self.line_edit_path_name = QLineEdit(self.groupBox_2)
        self.line_edit_path_name.setObjectName(u"line_edit_path_name")

        self.horizontalLayout_4.addWidget(self.line_edit_path_name)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_path_value = QLabel(self.groupBox_2)
        self.label_path_value.setObjectName(u"label_path_value")

        self.horizontalLayout_5.addWidget(self.label_path_value)

        self.line_edit_path_value = QLineEdit(self.groupBox_2)
        self.line_edit_path_value.setObjectName(u"line_edit_path_value")

        self.horizontalLayout_5.addWidget(self.line_edit_path_value)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.button_save_changes = QPushButton(self.groupBox_2)
        self.button_save_changes.setObjectName(u"button_save_changes")

        self.verticalLayout_3.addWidget(self.button_save_changes)

        self.button_open_config_directory = QPushButton(self.groupBox_2)
        self.button_open_config_directory.setObjectName(u"button_open_config_directory")

        self.verticalLayout_3.addWidget(self.button_open_config_directory)


        self.verticalLayout_4.addWidget(self.groupBox_2)


        self.verticalLayout_2.addLayout(self.verticalLayout_4)


        self.retranslateUi(CustomPathsManagerWidget)

        QMetaObject.connectSlotsByName(CustomPathsManagerWidget)
    # setupUi

    def retranslateUi(self, CustomPathsManagerWidget):
        CustomPathsManagerWidget.setWindowTitle(QCoreApplication.translate("CustomPathsManagerWidget", u"Custom Paths Manager", None))
        self.groupBox.setTitle(QCoreApplication.translate("CustomPathsManagerWidget", u"Create custom paths", None))
        self.label.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Description:", None))
        self.label_description_create_custom_path.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Here you can add and create custom path configurations.", None))
        self.label_path_name_2.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path name:", None))
        self.label_path_folder.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path folder:", None))
        self.button_browse_path_folder.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Browse", None))
        self.label_save_config.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Save config:", None))
        self.button_create_custom_path.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Save Configuration", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("CustomPathsManagerWidget", u"Edit custom paths", None))
        self.label_desc.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Description:", None))
        self.label_text_desc.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Here you can load a custom path and change it's values or you can delete it.", None))
        self.label_combobox_desc.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Select a custom path:", None))
        self.button_load_action.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Load Path", None))
        self.button_delete_action.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Delete Path", None))
        self.label_path_name.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path name:", None))
        self.line_edit_path_name.setPlaceholderText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path name as shown in the menubar...", None))
        self.label_path_value.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path folder", None))
        self.line_edit_path_value.setPlaceholderText(QCoreApplication.translate("CustomPathsManagerWidget", u"Path value of the path name...", None))
        self.button_save_changes.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Save Changes", None))
        self.button_open_config_directory.setText(QCoreApplication.translate("CustomPathsManagerWidget", u"Open Config Directory", None))
    # retranslateUi

