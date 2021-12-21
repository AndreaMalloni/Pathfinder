from PySide2.QtCore import QRegExp
from PySide2.QtGui import QRegExpValidator
from PySide2.QtWidgets import *
from pyside_dynamic import *

class LayoutWidget(QFrame):
    def __init__(self, UIModel: str, label: str) -> None:
        super().__init__()
        loadUi(UIModel, self)
        self.textEdit.setText(label)
        self.x = 0
        self.y = 0

    def connectButtons(self) -> None:
        pass


class SourceWidget(LayoutWidget):
    def __init__(self, UIModel: str, label: str) -> None:
        super().__init__(UIModel, label)

    def connectButtons(self, editMethod, deleteMethod) -> None:
        self.editButton.clicked.connect(editMethod)
        self.deleteButton.clicked.connect(deleteMethod)


class ExtensionWidget(LayoutWidget):
    def __init__(self, UIModel: str, label: str) -> None:
        super().__init__(UIModel, label)

    def connectButtons(self, deleteMethod) -> None:
        self.deleteButton.clicked.connect(deleteMethod)

    def setEditable(self, editMethod):
        self.textEdit.setReadOnly(False)
        self.textEdit.setFocus()
        self.textEdit.setValidator(QRegExpValidator(QRegExp(r'^\.[a-zA-Z0-9]+$'), self))
        self.textEdit.editingFinished.connect(editMethod)


class DestinationWidget(LayoutWidget):
    def __init__(self, UIModel: str, label: str) -> None:
        super().__init__(UIModel, label)

    def connectButtons(self, linkMethod, editMethod, deleteMethod) -> None:
        self.extButton.clicked.connect(linkMethod)
        self.editButton.clicked.connect(editMethod)
        self.deleteButton.clicked.connect(deleteMethod)

    def connectExtensions(self, tracklist: dict):
        for ext in tracklist[self.textEdit.text()]:
            self.extComboBox.addItem(ext)
            index = self.extComboBox.findText(ext)
            self.extComboBox.model().item(index).setEnabled(False)
