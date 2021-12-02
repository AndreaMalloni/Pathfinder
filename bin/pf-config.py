import sys
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, QRegExp)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QRegExpValidator)
from PySide2.QtWidgets import *
from pyside_dynamic import *
from resources import *
from configInterface import ConfigManager

class Window():
    def __init__(self, UIModel: str) -> None:
        self.configManager = ConfigManager("data.ini")
        self.scrollLayout =  QGridLayout(Alignment = QtCore.Qt.AlignTop)
        self.itemsX = 0
        self.itemsY = 0

        loadUi(UIModel, self)
        self.scrollAreaContent.setLayout(self.scrollLayout)
        self.scrollLayout.setHorizontalSpacing(12)

    def setStructs(self):
        self.sources, self.extensions, self.destinations, self.tracklist = self.configManager.loadConfig()

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
                self.updateItemsXY(1, 1, maxColumn = 4, gridAlignment = True)
            else:
                self.updateItemsXY(0, 1)
            widgets.append(widget)
        return widgets

    def updateItemsXY(self, dx = 0, dy = 0, maxColumn = 99999, gridAlignment = False):
        if gridAlignment:
            if self.itemsX < maxColumn - 1:
                self.itemsX += dx
            else:
                self.itemsX = 0
                self.itemsY += dy
        else:
            self.itemsX += dx
            self.itemsY += dy

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
        self.addButton.clicked.connect(self.newLayoutItem)

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

    def makeExtEditable(self, widget):
        widget.textEdit.setReadOnly(False)
        widget.textEdit.setFocus()
        widget.textEdit.setValidator(QRegExpValidator(QRegExp(r'^\.[a-zA-Z0-9]+$'), self))
        widget.textEdit.editingFinished.connect(self.editLayoutItem)

    @QtCore.Slot()
    def sourceUI(self) -> None:
        text = "Manage here the folders you want Pathfinder to extract your files from"
        self.initSectionUI(labelText=text)

        self.sourceButton.setChecked(True)
        layoutContent = self.fillLayout(self.scrollLayout, self.sources, 'D:\\Projects\\pathfinder\\gui\\source.ui')
        for widget in layoutContent:
            widget.editButton.clicked.connect(self.editLayoutItem)
            widget.deleteButton.clicked.connect(self.removeLayoutItem)
                    
    @QtCore.Slot()
    def extUI(self) -> None:
        text = "Add here the extensions of the files you want Pathfinder to move"
        self.initSectionUI(focus = 1, labelText = text)

        self.extButton.setChecked(True)
        layoutContent = self.fillLayout(self.scrollLayout, self.extensions, 'D:\\Projects\\pathfinder\\gui\\extension.ui', gridAlignment = True)
        for widget in layoutContent:
            widget.deleteButton.clicked.connect(self.removeLayoutItem)

            if widget.textEdit.text() == ".":
                self.makeExtEditable(widget)
                self.addButton.setDisabled(True)

    @QtCore.Slot()
    def destUI(self) -> None:
        text = "Manage here the folders where you want Pathfinder to place your files"
        self.initSectionUI(focus = 2, labelText = text)
        
        self.destButton.setChecked(True)

        layoutContent = self.fillLayout(self.scrollLayout, self.destinations, 'D:\\Projects\\pathfinder\\gui\\destination.ui')
        for widget in layoutContent:
            widget.extButton.clicked.connect(self.connectExtension)
            widget.editButton.clicked.connect(self.editLayoutItem)
            widget.deleteButton.clicked.connect(self.removeLayoutItem)

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
    def newLayoutItem(self) -> None:
        if self.focus == 0:
            self.configManager.addToConfig(self.focus, "TRACKED", "sources")
            self.sourceUI()
        elif self.focus == 1:
            self.configManager.addToConfig(self.focus, "TRACKED", "extensions")
            self.extUI()
        elif self.focus == 2:
            self.configManager.addToConfig(self.focus, "TRACKED", "destinations")
            self.destUI()

    @QtCore.Slot()
    def editLayoutItem(self) -> None:
        item = self.sender().parent().parent().textEdit.text()
        if self.focus == 0:
            self.configManager.editConfig(self.focus, "TRACKED", "sources", item)
            self.sourceUI()
        elif self.focus == 1:
            self.configManager.editConfig(self.focus, "TRACKED", "extensions", item)
            self.extUI()
        elif self.focus == 2:
            self.configManager.editConfig(self.focus, "TRACKED", "destinations", item)
            self.destUI()

    @QtCore.Slot()
    def removeLayoutItem(self) -> None:
        item = self.sender().parent().parent().textEdit.text()
        if self.focus == 0:
            self.configManager.removeFromConfig(self.focus, "TRACKED", "sources", item)
            self.sourceUI()
        elif self.focus == 1:
            self.configManager.removeFromConfig(self.focus, "TRACKED", "extensions", item)
            self.extUI()
        elif self.focus == 2:
            self.configManager.removeFromConfig(self.focus, "TRACKED", "destinations", item)
            self.destUI()

    @QtCore.Slot()
    def connectExtension(self):
        dialog = Dialog(UIModel = 'D:\\Projects\\pathfinder\\gui\\dialog.ui')
        dialog.exec()
        destination = self.sender().parent().parent().textEdit.text()
        selections = dialog.checkedExt
        associations = self.configManager.readRawOption("TRACKLIST", destination)

        for ext in selections:
            associations = associations + "|" + ext

        self.configManager.writeRawOption("TRACKLIST", destination, associations)
        self.destUI()

class Dialog(Window, QDialog):
    def __init__(self, UIModel, parent=None):
        QDialog.__init__(self, parent)
        Window.__init__(self, UIModel)

        self.setFixedSize(500, 300)
        self.setStructs()
        self.availableExt = []
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
            if not self.existIn(ext, self.tracklist):
                self.availableExt.append(ext)
                
        self.fillLayout(self.scrollLayout, self.availableExt, 'D:\\Projects\\pathfinder\\gui\\ext-choice.ui', gridAlignment = True)

    def accept(self) -> None:
        for i in reversed(range(self.scrollLayout.count())):
            widget = self.scrollLayout.itemAt(i).widget()
            if widget.textEdit.isChecked():
                self.checkedExt.append(widget.textEdit.text())
                
        return super().accept()
    
    def reject(self) -> None:
        self.checkedExt = []
        return super().reject()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(UIModel = 'D:\\Projects\\pathfinder\\gui\\pathfinder-main.ui')
    sys.exit(app.exec_())