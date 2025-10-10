# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'exit_dialog_box.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QHBoxLayout, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)
import resources.qrc.xmluvation_resources_rc

class Ui_ExitAppDialog(object):
    def setupUi(self, ExitAppDialog):
        if not ExitAppDialog.objectName():
            ExitAppDialog.setObjectName(u"ExitAppDialog")
        ExitAppDialog.setWindowModality(Qt.WindowModality.NonModal)
        ExitAppDialog.setEnabled(True)
        ExitAppDialog.resize(330, 120)
        ExitAppDialog.setMinimumSize(QSize(330, 120))
        ExitAppDialog.setMaximumSize(QSize(330, 120))
        icon = QIcon()
        icon.addFile(u":/icons/xml_256px.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ExitAppDialog.setWindowIcon(icon)
        ExitAppDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(ExitAppDialog)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, -1, -1, 6)
        self.image = QLabel(ExitAppDialog)
        self.image.setObjectName(u"image")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
        self.image.setSizePolicy(sizePolicy)
        self.image.setMinimumSize(QSize(32, 32))
        self.image.setPixmap(QPixmap(u":/images/question-circle_48x48.png"))

        self.horizontalLayout_2.addWidget(self.image)

        self.label = QLabel(ExitAppDialog)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(9, -1, -1, 6)
        self.check_box_dont_ask_again = QCheckBox(ExitAppDialog)
        self.check_box_dont_ask_again.setObjectName(u"check_box_dont_ask_again")
        self.check_box_dont_ask_again.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.horizontalLayout.addWidget(self.check_box_dont_ask_again)

        self.button_box = QDialogButtonBox(ExitAppDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.No|QDialogButtonBox.StandardButton.Yes)
        self.button_box.setCenterButtons(False)

        self.horizontalLayout.addWidget(self.button_box)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(ExitAppDialog)
        self.button_box.accepted.connect(ExitAppDialog.accept)
        self.button_box.rejected.connect(ExitAppDialog.reject)

        QMetaObject.connectSlotsByName(ExitAppDialog)
    # setupUi

    def retranslateUi(self, ExitAppDialog):
        ExitAppDialog.setWindowTitle(QCoreApplication.translate("ExitAppDialog", u"Exit Application", None))
        self.image.setText("")
        self.label.setText(QCoreApplication.translate("ExitAppDialog", u"Are you sure you want to exit the application?", None))
        self.check_box_dont_ask_again.setText(QCoreApplication.translate("ExitAppDialog", u"Don't ask me again", None))
    # retranslateUi

