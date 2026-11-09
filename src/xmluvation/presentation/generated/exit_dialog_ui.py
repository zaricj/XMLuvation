# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ExitDialogBox.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)
from . import xmluvation_resources_rc

class Ui_ExitAppDialog(object):
    def setupUi(self, ExitAppDialog):
        if not ExitAppDialog.objectName():
            ExitAppDialog.setObjectName(u"ExitAppDialog")
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ExitAppDialog.setWindowIcon(icon)
        ExitAppDialog.setMinimumSize(QSize(380, 0))
        ExitAppDialog.setModal(True)
        self.layout_ExitAppDialog = QVBoxLayout(ExitAppDialog)
        self.layout_ExitAppDialog.setSpacing(14)
        self.layout_ExitAppDialog.setObjectName(u"layout_ExitAppDialog")
        self.layout_ExitAppDialog.setContentsMargins(24, 22, 24, 22)
        self.layout_exit_message = QHBoxLayout()
        self.layout_exit_message.setSpacing(14)
        self.layout_exit_message.setObjectName(u"layout_exit_message")
        self.layout_exit_message.setContentsMargins(0, 0, 0, 0)
        self.image = QLabel(ExitAppDialog)
        self.image.setObjectName(u"image")
        self.image.setPixmap(QPixmap(u":/images/question-circle_48x48.png"))
        self.image.setMaximumSize(QSize(40, 40))
        self.image.setScaledContents(True)

        self.layout_exit_message.addWidget(self.image)

        self.label = QLabel(ExitAppDialog)
        self.label.setObjectName(u"label")
        self.label.setWordWrap(True)

        self.layout_exit_message.addWidget(self.label)


        self.layout_ExitAppDialog.addLayout(self.layout_exit_message)

        self.layout_exit_buttons = QHBoxLayout()
        self.layout_exit_buttons.setSpacing(8)
        self.layout_exit_buttons.setObjectName(u"layout_exit_buttons")
        self.layout_exit_buttons.setContentsMargins(0, 0, 0, 0)
        self.check_box_dont_ask_again = QCheckBox(ExitAppDialog)
        self.check_box_dont_ask_again.setObjectName(u"check_box_dont_ask_again")

        self.layout_exit_buttons.addWidget(self.check_box_dont_ask_again)

        self.spacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_exit_buttons.addItem(self.spacer_5)

        self.button_box = QDialogButtonBox(ExitAppDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.No|QDialogButtonBox.StandardButton.Yes)

        self.layout_exit_buttons.addWidget(self.button_box)


        self.layout_ExitAppDialog.addLayout(self.layout_exit_buttons)


        self.retranslateUi(ExitAppDialog)
        self.button_box.accepted.connect(ExitAppDialog.accept)
        self.button_box.rejected.connect(ExitAppDialog.reject)

        QMetaObject.connectSlotsByName(ExitAppDialog)
    # setupUi

    def retranslateUi(self, ExitAppDialog):
        ExitAppDialog.setWindowTitle(QCoreApplication.translate("ExitAppDialog", u"Exit XMLuvation", None))
        ExitAppDialog.setProperty(u"role", QCoreApplication.translate("ExitAppDialog", u"page", None))
        self.image.setText("")
        self.label.setText(QCoreApplication.translate("ExitAppDialog", u"Exit XMLuvation? Running tasks will be cancelled.", None))
        self.check_box_dont_ask_again.setText(QCoreApplication.translate("ExitAppDialog", u"Don't ask again", None))
    # retranslateUi

