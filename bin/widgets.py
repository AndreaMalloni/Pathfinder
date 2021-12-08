from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, QRegExp)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QRegExpValidator)
from PySide2.QtWidgets import *
from pyside_dynamic import *

class LayoutWidget(QFrame):
    def __init__(self, UIModel: str) -> None:
        super().__init__()
        loadUi(UIModel, self)
        self.x = 0
        self.y = 0

    def connectButtons(self) -> None:
        pass


class SourceWidget(LayoutWidget):
    def __init__(self, UIModel: str, label: str) -> None:
        super().__init__(UIModel)
        self.textEdit.setText(label)

    def connectButtons(self, editMethod, deleteMethod) -> None:
        self.editButton.clicked.connect(editMethod)
        self.deleteButton.clicked.connect(deleteMethod)


class ExtensionWidget(LayoutWidget):
    def __init__(self, UIModel: str, label: str) -> None:
        super().__init__(UIModel)
        self.textEdit.setText(label)

    def connectButtons(self, deleteMethod) -> None:
        self.deleteButton.clicked.connect(deleteMethod)

    def setEditable(self, editMethod):
        self.textEdit.setReadOnly(False)
        self.textEdit.setFocus()
        self.textEdit.setValidator(QRegExpValidator(QRegExp(r'^\.[a-zA-Z0-9]+$'), self))
        self.textEdit.editingFinished.connect(editMethod)


class DestinationWidget(LayoutWidget):
    def __init__(self, UIModel: str, label: str) -> None:
        super().__init__(UIModel)
        self.textEdit.setText(label)

    def connectButtons(self, linkMethod, editMethod, deleteMethod) -> None:
        self.extButton.clicked.connect(linkMethod)
        self.editButton.clicked.connect(editMethod)
        self.deleteButton.clicked.connect(deleteMethod)

    def connectExtensions(self, tracklist: dict):
        for ext in tracklist[self.textEdit.text()]:
            self.extComboBox.addItem(ext)
            index = self.extComboBox.findText(ext)
            self.extComboBox.model().item(index).setEnabled(False)
