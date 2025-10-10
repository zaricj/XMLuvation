from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QCheckBox, QStyle, QApplication
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal


class CustomQuestionDialog(QDialog):
    accepted_with_option = Signal(bool)

    def __init__(self, question: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Action")
        self.setModal(True)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.setFixedSize(360, 180)

        # Layouts
        layout = QVBoxLayout(self)
        text_layout = QHBoxLayout()

        # Icon
        icon_label = QLabel()
        icon = self.style().standardIcon(QStyle.SP_MessageBoxQuestion)
        icon_label.setPixmap(icon.pixmap(48, 48))
        text_layout.addWidget(icon_label, alignment=Qt.AlignTop)

        # Message
        msg_label = QLabel(question)
        msg_label.setWordWrap(True)
        text_layout.addWidget(msg_label)

        layout.addLayout(text_layout)

        # Extra widget (optional)
        self.remember_checkbox = QCheckBox("Don't ask me again")
        layout.addWidget(self.remember_checkbox)

        # Buttons
        btn_layout = QHBoxLayout()
        yes_btn = QPushButton("Yes")
        no_btn = QPushButton("No")
        btn_layout.addStretch()
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)
        layout.addLayout(btn_layout)

        # Connections
        yes_btn.clicked.connect(self.accept)
        no_btn.clicked.connect(self.reject)

    def exec_with_result(self):
        """Return tuple (accepted: bool, remember: bool)"""
        result = self.exec()
        return result == QDialog.Accepted, self.remember_checkbox.isChecked()


# Example usage:
if __name__ == "__main__":
    app = QApplication([])

    dlg = CustomQuestionDialog("Are you sure you want to delete this item?")
    accepted, remember = dlg.exec_with_result()
    print(f"Accepted: {accepted}, Remember: {remember}")
