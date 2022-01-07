from PySide2.QtCore import QRegExp
from PySide2 import QtCore
from PySide2.QtGui import QRegExpValidator
from PySide2.QtWidgets import *
from pyside_dynamic import *
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

    def connectButtons(self, deleteMethod: Callable) -> None:
        self.deleteButton.clicked.connect(deleteMethod)

    def setEditable(self, editMethod: Callable):
        self.textEdit.setReadOnly(False)
        self.textEdit.setFocus()
        self.textEdit.setValidator(QRegExpValidator(QRegExp(r'^\.[a-zA-Z0-9]+$'), self))
        self.textEdit.editingFinished.connect(editMethod)


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
        self.setHorizontalSpacing(12)
        self.widgets = []

    def isEmpty(self) -> bool:
        return (False if self.count() != 0 else True)

    def clear(self) -> None:  
        for i in reversed(range(self.count())):
            self.itemAt(i).widget().setParent(None)

    def fill(self, widgets: list[QWidget], verticalStyle: bool) -> None:
        if widgets != []:
            currentX, currentY = 0, 0
            self.setAlignment(QtCore.Qt.AlignTop)
            for widget in widgets:
                widget.x, widget.y = currentX, currentY
                self.addWidget(widget, widget.y, widget.x)
                
                currentX, currentY = self.__nextPosition(currentX, currentY, verticalStyle)
        else:
            widget = loadUi('UI\\default.ui')
            self.setAlignment(QtCore.Qt.AlignVCenter)
            self.addWidget(widget)
        self.widgets = widgets

    def __nextPosition(self, x: int, y: int, verticalStyle: bool) -> tuple[int, int]:
        if not verticalStyle:
            if x < 3:
                x += 1
            else:
                x = 0
                y += 1
        else:
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