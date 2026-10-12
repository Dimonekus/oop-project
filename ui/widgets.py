from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QTableWidget, QListWidget,
    QComboBox, QCheckBox, QTextEdit, QStatusBar, QWidget,
)

class MyLabel(QLabel):
    def mousePressEvent(self, event):
        self.setStyleSheet("color: #2a6df4;")
        super().mousePressEvent(event)

class MyLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        super().keyPressEvent(event)

class MyPushButton(QPushButton):
    def mousePressEvent(self, event):
        self.setStyleSheet("background-color: #d0e0ff;")
        super().mousePressEvent(event)

class MyTableWidget(QTableWidget):
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

class MyListWidget(QListWidget):
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

class MyComboBox(QComboBox):
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

class MyCheckBox(QCheckBox):
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

class MyTextEdit(QTextEdit):
    def keyPressEvent(self, event):
        super().keyPressEvent(event)

class MyStatusBar(QStatusBar):
    def showMessage(self, message, timeout=0):
        super().showMessage(message, timeout)

class MyWidget(QWidget):
    def mousePressEvent(self, event):
        super().mousePressEvent(event)