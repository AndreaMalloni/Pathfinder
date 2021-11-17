import sys
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, QRegExp)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QRegExpValidator)
from PySide2.QtWidgets import *
from pyside_dynamic import *
from resources import *
from tkinter import filedialog, Tk
from dataParser import CustomParser

def askDir():
    root = Tk()
    root.withdraw()

    dir = filedialog.askdirectory()
    return dir

class Window():
    def __init__(self, UIModel: str) -> None:
        self.parser = CustomParser("data.ini")
        self.scrollLayout =  QGridLayout(Alignment = QtCore.Qt.AlignTop)
        self.itemsX = 0
        self.itemsY = 0

        loadUi(UIModel, self)
        self.scrollAreaContent.setLayout(self.scrollLayout)
        self.scrollLayout.setHorizontalSpacing(12)

    def setStructs(self):
        self.tracklist, self.sources, self.extensions, self.destinations = self.parser.loadConfig()

    def clearLayout(self, layout) -> None:
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    def fillLayout(self, layout, items: list[str], UIModel: str, gridAlignment = False) -> list:
        widgets = []
        for item in items:
            widget = loadUi(UIModel)
            widget.textEdit.setText(item)
            layout.addWidget(widget, self.itemsY, self.itemsX)
            if gridAlignment:
                self.itemsX, self.itemsY = self.updateXY(self.itemsX, self.itemsY, 1, 1, maxColumn = 4, gridAlignment = True)
            else:
                self.itemsX, self.itemsY = self.updateXY(self.itemsX, self.itemsY, 0, 1)
            widgets.append(widget)
        return widgets

    def updateXY(self, x: int, y: int, dx = 0, dy = 0, maxColumn = 99999, gridAlignment = False):
        if gridAlignment:
            if x < maxColumn - 1:
                x += dx
            else:
                x = 0
                y += dy
        else:
            x += dx
            y += dy
        return (x, y)

class MainWindow(Window, QMainWindow):
    def __init__(self, UIModel, parent=None):
        QMainWindow.__init__(self, parent)
        Window.__init__(self, UIModel)

        self.setFixedSize(800, 500)

        self.sourceUI()
        
        self.sourceButton.clicked.connect(self.sourceUI)
        self.extButton.clicked.connect(self.extUI)
        self.destButton.clicked.connect(self.destUI)
        self.infoButton.clicked.connect(self.infoUI)
        self.addButton.clicked.connect(self.addItem)

        self.show()

    def initSectionUI(self, focus=0, labelText="") -> None:
        self.setStructs()
        self.toggleSidebarItem(self.sender())
        self.clearLayout(self.scrollLayout)

        self.addButton.setDisabled(False)
        self.focus = focus

        self.descriptionLabel.setText(labelText)
        self.itemsX, self.itemsY = 0, 0

    def toggleSidebarItem(self, button: QPushButton) -> None:
        for widget in self.sidebarFrame.children():
            if isinstance(widget, QPushButton) and widget != button and widget.isChecked():
                widget.setChecked(False)
                
    @QtCore.Slot()
    def sourceUI(self) -> None:
        text = "Manage here the folders you want Pathfinder to extract your files from"
        self.initSectionUI(labelText=text)

        self.sourceButton.setChecked(True)
        layoutContent = self.fillLayout(self.scrollLayout, self.sources, 'D:\\Projects\\pathfinder\\gui\\source.ui')
        for widget in layoutContent:
            widget.editButton.clicked.connect(self.editItem)
            widget.deleteButton.clicked.connect(lambda: self.deleteItem("TRACKED", "sources", widget.textEdit.text()))
                    
    @QtCore.Slot()
    def extUI(self) -> None:
        text = "Add here the extensions of the files you want Pathfinder to move"
        self.initSectionUI(focus = 1, labelText = text)

        self.extButton.setChecked(True)
        layoutContent = self.fillLayout(self.scrollLayout, self.extensions, 'D:\\Projects\\pathfinder\\gui\\extension.ui', gridAlignment = True)
        for widget in layoutContent:
            widget.deleteButton.clicked.connect(lambda: self.deleteItem("TRACKED", "extensions", widget.textEdit.text()))

            if widget.textEdit.text() == ".":
                widget.textEdit.setReadOnly(False)
                widget.textEdit.setFocus()
                self.addButton.setDisabled(True)
                widget.textEdit.setValidator(QRegExpValidator(QRegExp(r'^\.[a-zA-Z0-9]+$'), self))
                widget.textEdit.editingFinished.connect(lambda: self.extConfirmed(widget.textEdit.text()))

    @QtCore.Slot()
    def destUI(self) -> None:
        text = "Manage here the folders where you want Pathfinder to place your files"
        self.initSectionUI(focus = 2, labelText = text)
        
        self.destButton.setChecked(True)

        layoutContent = self.fillLayout(self.scrollLayout, self.destinations, 'D:\\Projects\\pathfinder\\gui\\destination.ui')
        for widget in layoutContent:
            widget.extButton.clicked.connect(lambda: self.associate(widget.textEdit.text()))
            widget.editButton.clicked.connect(self.editItem)
            widget.deleteButton.clicked.connect(lambda: self.deleteItem("TRACKED", "destinations", widget.textEdit.text()))

            for ext in self.tracklist[widget.textEdit.text()]:
                widget.extComboBox.addItem(ext)
                index = widget.extComboBox.findText(ext)
                widget.extComboBox.model().item(index).setEnabled(False)

    @QtCore.Slot()
    def infoUI(self) -> None:
        text = "About this software"
        self.initSectionUI(focus = 3, labelText = text)

        self.infoButton.setChecked(True)
        widget = loadUi('D:\\Projects\\pathfinder\\gui\\info.ui')
        self.scrollLayout.addWidget(widget)
        
    @QtCore.Slot()
    def addItem(self) -> None:
        if self.focus == 0:
            sources = self.parser.readRawOption(self.configFile, "TRACKED", "sources") 
            dir = askDir()
            self.parser.writeRawOption(self.configFile, "TRACKED", "sources", sources + " " + dir)  
            self.sourceUI()
        if self.focus == 1:
            extensions = self.parser.readRawOption(self.configFile, "TRACKED", "extensions")
            self.parser.writeRawOption(self.configFile, "TRACKED", "extensions", extensions + " " + ".")
            self.extUI()
        if self.focus == 2:
            destinations = self.parser.readRawOption(self.configFile, "TRACKED", "destinations") 
            dir = askDir()
            self.parser.writeRawOption(self.configFile, "TRACKED", "destinations", destinations + " " + dir)
            self.parser.writeRawOption(self.configFile, "TRACKLIST", dir)
            self.destUI()

    @QtCore.Slot()
    def editItem(self) -> None:
        if self.focus == 0:
            sources = self.parser.readRawOption(self.configFile, "TRACKED", "sources") 
            dir = askDir()
            if dir != "":
                self.parser.writeRawOption(self.configFile, "TRACKED", "sources", sources.replace(self.sender().parent().parent().textEdit.text(), dir))
                self.sourceUI()
        if self.focus == 2:
            destinations = self.parser.readRawOption(self.configFile, "TRACKED", "destinations") 
            dir = askDir()
            if dir != "":
                path = self.sender().parent().parent().textEdit.text()
                self.parser.writeRawOption(self.configFile, "TRACKED", "destinations", destinations.replace(path, dir))
                self.destUI()

    @QtCore.Slot()
    def deleteItem(self, section, key, value) -> None:
        self.parser.writeRawOption(section, key, self.parser.readRawOption(self.configFile, section, key)[:-(len(value) + 1)])

        if self.focus == 0:
            self.sourceUI()
        if self.focus == 1:
            self.extUI()
        if self.focus == 2:
            self.parser.writeRawKey("TRACKLIST", value)
            self.destUI()

    @QtCore.Slot()
    def extConfirmed(self, ext: str):
        if (ext != ".") and (ext != "") and (" " not in ext) and (ext not in self.extensions):
            extensions = self.parser.readRawOption(self.configFile, "TRACKED", "extensions")
            self.parser.writeRawOption(self.configFile, "TRACKED", "extensions", ext.join(extensions.rsplit(".", 1)))
            self.extUI()

    @QtCore.Slot()
    def associate(self, destination: str):
        dialog = Dialog(UIModel = 'D:\\Projects\\pathfinder\\gui\\dialog.ui')
        dialog.exec()
        selections = dialog.checkedExt
        associations = self.parser.readRawOption(self.configFile, "TRACKLIST", destination)

        for ext in selections:
            associations = associations + " " + ext

        self.parser.writeRawOption(self.configFile, "TRACKLIST", destination, associations)
        self.destUI()

class Dialog(Window, QDialog):
    def __init__(self, UIModel, parent=None):
        QDialog.__init__(self, parent)
        Window.__init__(self, UIModel)

        self.setFixedSize(500, 300)
        self.setStructs()
        self.dialogUI()

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.checkedExt = []
        self.show()
    
    def existIn(self, value, dict: dict):
        for pool in dict.values():
            if value in pool:
                return True
        
        return False

    def dialogUI(self):
        for ext in self.extensions:
            if self.existIn(ext, self.tracklist) == True:
                self.extensions.remove(ext)
                
        self.fillLayout(self.scrollLayout, self.extensions, 'D:\\Projects\\pathfinder\\gui\\ext-choice.ui', gridAlignment = True)

    def accept(self) -> None:
        for i in reversed(range(self.scrollLayout.count())):
            widget = self.scrollLayout.itemAt(i).widget()
            if widget.extButton.isChecked():
                self.checkedExt.append(widget.extButton.text())
                
        return super().accept()
    
    def reject(self) -> None:
        self.checkedExt = []
        return super().reject()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(UIModel = 'D:\\Projects\\pathfinder\\gui\\pathfinder-main.ui')
    sys.exit(app.exec_())