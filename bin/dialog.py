from PySide2 import QtCore
from PySide2.QtWidgets import *
from pyside_dynamic import *
from resources import *
from utility_func import existInDict
from widgets import LayoutWidget, GridLayout

class Dialog(QDialog):
    def __init__(self, UIModel, destination, userConfig, parent=None):
        QDialog.__init__(self, parent)

        self.destination = destination
        self.config = userConfig
        self.selections = []
        loadUi(UIModel, self)

        self.scrollLayout = GridLayout() 
        self.scrollAreaContent.setLayout(self.scrollLayout)

        self.setFixedSize(500, 300)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.drawDialogWidgets()
        self.show()

    def buildDialogWidgets(self, labels: list[str]) -> list[object]:
        widgets = []
        for label in labels:
            if existInDict(label, self.config.data[3]):
                for possibleDestination in self.config.data[3]:
                    if label in self.config.data[3][possibleDestination] and possibleDestination == self.destination: 
                        widget = LayoutWidget('UI\\ext-choice.ui', label)
                        widget.textEdit.setChecked(True)
                        widgets.append(widget)
            else:
                widget = LayoutWidget('UI\\ext-choice.ui', label)
                widgets.append(widget)
        return widgets

    def drawDialogWidgets(self):
        widgets = self.buildDialogWidgets(self.config.data[1])
        self.scrollLayout.fill(widgets, verticalStyle = False)

    def accept(self) -> None:
        for i in reversed(range(self.scrollLayout.count())):
            widget = self.scrollLayout.itemAt(i).widget()
            if widget.textEdit.isChecked():
                self.selections.append(widget.textEdit.text())
                
        return super().accept()
    
    def reject(self) -> None:
        self.selections = []
        return super().reject()