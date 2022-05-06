from PySide2.QtCore import QRegExp
from PySide2 import QtCore
from PySide2.QtGui import QRegExpValidator, QValidator
from PySide2.QtWidgets import *
from utils.pyside_dynamic import *
from typing import Callable

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

    def connectButtons(self, editMethod: Callable, deleteMethod: Callable) -> None:
        self.editButton.clicked.connect(editMethod)
        self.deleteButton.clicked.connect(deleteMethod)


class ExtensionWidget(LayoutWidget):
    def __init__(self, UIModel: str, label: str) -> None:
        super().__init__(UIModel, label)
        self.validator = None

    def connectButtons(self, deleteMethod: Callable) -> None:
        self.deleteButton.clicked.connect(deleteMethod)

    def setEditable(self, editMethod: Callable):
        self.validator = QRegExpValidator(QRegExp(r'^\.[a-zA-Z0-9]+$'), self)
        self.textEdit.setReadOnly(False)
        self.textEdit.setFocus()
        self.textEdit.setValidator(self.validator)
        self.textEdit.textChanged.connect(self.changeBorder)
        self.textEdit.editingFinished.connect(editMethod)
        self.textEdit.editingFinished.connect(lambda: self.textEdit.setReadOnly(True))
        self.textEdit.editingFinished.connect(lambda: self.lineFrame.setStyleSheet("QFrame {background-color: rgb(26, 32, 50);border-radius: 10px;}"))
        self.changeBorder()

    def changeBorder(self):
        state, string, pos = self.validator.validate(self.textEdit.text(), 0)
        if state == QValidator.Acceptable:
            self.lineFrame.setStyleSheet("QFrame {border: 2px solid green;background-color: rgb(26, 32, 50);border-radius: 10px;}")
        else:
            self.lineFrame.setStyleSheet("QFrame {border: 2px solid red;background-color: rgb(26, 32, 50);border-radius: 10px;}")

class DestinationWidget(LayoutWidget):
    def __init__(self, UIModel: str, label: str) -> None:
        super().__init__(UIModel, label)

    def connectButtons(self, linkMethod: Callable, editMethod: Callable, deleteMethod: Callable) -> None:
        self.extButton.clicked.connect(linkMethod)
        self.editButton.clicked.connect(editMethod)
        self.deleteButton.clicked.connect(deleteMethod)

    def connectExtensions(self, tracklist: dict):
        for ext in tracklist[self.textEdit.text()]:
            self.extComboBox.addItem(ext)
            index = self.extComboBox.findText(ext)
            self.extComboBox.model().item(index).setEnabled(False)


class GridLayout(QGridLayout):
    def __init__(self) -> None:
        super().__init__()
        self.setHorizontalSpacing(10)
        self.rowWidgets = 0
        self.widgets = []

    def isEmpty(self) -> bool:
        return (False if self.count() != 0 else True)

    def clear(self) -> None:  
        for index in reversed(range(self.count())):
            self.itemAt(index).widget().setParent(None)

    def fill(self, widgets: list[QWidget]) -> None:
        if widgets != []:
            currentX, currentY = 0, 0
            self.setAlignment(QtCore.Qt.AlignTop)
            for widget in widgets:
                widget.x, widget.y = currentX, currentY
                self.addWidget(widget, widget.y, widget.x)
                
                currentX, currentY = self.__nextPosition(currentX, currentY)
        else:
            widget = loadUi('UI\\default.ui')
            self.setAlignment(QtCore.Qt.AlignVCenter)
            self.addWidget(widget)
        self.widgets = widgets

    def __nextPosition(self, x: int, y: int) -> tuple[int, int]:
        if x < self.rowWidgets - 1:
            x += 1
        else:
            x = 0
            y += 1
        return (x, y)

    def __iter__(self):
        return LayoutIterator(self)

class LayoutIterator:
    def __init__(self, layout) -> None:
        self._layout = layout
        self._index = 0

    def __next__(self):
        if self._index < len(self._layout.widgets):
            result = self._layout.widgets[self._index]
            self._index += 1
            return result
        raise StopIteration

if __name__ == '__main__':
    widget = SourceWidget('UI\\sourceWidget.ui', 'test')