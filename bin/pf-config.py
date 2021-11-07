import sys
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *
from pyside_dynamic import *
from resources import *
from pathfinder import readINI
from tkinter import filedialog, Tk
import configparser

class Window():
    def __init__(self, UIModel="") -> None:
        self.scrollLayout =  QGridLayout(Alignment = QtCore.Qt.AlignTop)
        self.itemsX = 0
        self.itemsY = 0

        loadUi(UIModel, self)
        self.scrollAreaContent.setLayout(self.scrollLayout)
        self.scrollLayout.setHorizontalSpacing(12)

    def resetStructs(self):
        self.tracklist, self.sources, self.extensions, self.destinations = readINI("data.ini")

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

    def askDir(self):
        root = Tk()
        root.withdraw()

        dir = filedialog.askdirectory()
        return dir

    def writeRawOption(self, section, key, value = ""):
        parser = configparser.ConfigParser(delimiters=('='), allow_no_value=True)
        parser.optionxform = str
        parser.read("data.ini")
    
        parser.set(section, key, value)

        with open('data.ini', 'w') as configfile:
            parser.write(configfile)

        self.resetStructs()

    def readRawOption(self, section, key):
        parser = configparser.ConfigParser(delimiters=('='), allow_no_value=True)
        parser.optionxform = str
        parser.read("data.ini")
        return parser.get(section, key)

    def clearLayoutContent(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    def toggleSidebarItem(self, button):
        for widget in self.sidebarFrame.children():
            if isinstance(widget, QPushButton) and widget != button and widget.isChecked():
                widget.setChecked(False)

    def initUI(self, focus=0, labelText=""):
        self.resetStructs()
        self.toggleSidebarItem(self.sender())
        self.clearLayoutContent(self.scrollLayout)

        self.addButton.setDisabled(False)
        self.focus = focus

        self.descriptionLabel.setText(labelText)
        self.itemsX, self.itemsY = 0, 0

    @QtCore.Slot()
    def sourceUI(self):
        text = "Manage here the folders you want Pathfinder to extract your files from"
        self.initUI(labelText=text)
        
        self.sourceButton.setChecked(True)

        for source in self.sources:
            widget = loadUi('D:\\Projects\\pathfinder\\gui\\source.ui')
            widget.textEdit.setText(source)
            widget.editButton.clicked.connect(self.editItem)
            widget.deleteButton.clicked.connect(lambda: self.deleteItem("TRACKED", "sources", widget.textEdit.text()))
            self.scrollLayout.addWidget(widget, self.itemsY, self.itemsX)
            self.itemsY += 1
                    
    @QtCore.Slot()
    def extUI(self):
        text = "Add here the extensions of the files you want Pathfinder to move"
        self.initUI(focus = 1, labelText = text)

        self.extButton.setChecked(True)

        for ext in self.extensions:
            widget = loadUi('D:\\Projects\\pathfinder\\gui\\extension.ui')
            widget.textEdit.setText(ext)
            widget.deleteButton.clicked.connect(lambda: self.deleteItem("TRACKED", "extensions", widget.textEdit.text()))
            self.scrollLayout.addWidget(widget, self.itemsY, self.itemsX)

            if self.itemsX < 3:
                self.itemsX += 1
            else:
                self.itemsX = 0
                self.itemsY += 1

            if ext == "." or " " in ext:
                widget.textEdit.setReadOnly(False)
                widget.textEdit.setFocus()
                self.addButton.setDisabled(True)
                widget.textEdit.returnPressed.connect(lambda: self.extConfirmed(widget.textEdit.text()))
                #swidget.textEdit.focusOutEvent.connect(lambda: self.deleteItem("TRACKED", "extensions", "."))

    @QtCore.Slot()
    def destUI(self):
        text = "Manage here the folders where you want Pathfinder to place your files"
        self.initUI(focus = 2, labelText = text)
        
        self.destButton.setChecked(True)

        for destination in self.destinations:
            widget = loadUi('D:\\Projects\\pathfinder\\gui\\destination.ui')
            widget.textEdit.setText(destination)

            for ext in self.tracklist[destination]:
                widget.extComboBox.addItem(ext)
                index = widget.extComboBox.findText(ext)
                widget.extComboBox.model().item(index).setEnabled(False)

            widget.extButton.clicked.connect(self.associate)
            widget.editButton.clicked.connect(self.editItem)
            widget.deleteButton.clicked.connect(lambda: self.deleteItem("TRACKED", "destinations", widget.textEdit.text()))
            self.scrollLayout.addWidget(widget, self.itemsY, self.itemsX)
            self.itemsY += 1

    @QtCore.Slot()
    def infoUI(self):
        text = "About this software"
        self.initUI(focus = 3, labelText = text)

        self.infoButton.setChecked(True)

    @QtCore.Slot()
    def deleteItem(self, section, key, value):
        self.writeRawOption(section, key, self.readRawOption(section, key)[:-(len(value) + 1)])

        if self.focus == 0:
            self.sourceUI()
        if self.focus == 1:
            self.extUI()
        if self.focus == 2:
            parser = configparser.ConfigParser(delimiters=('='), allow_no_value=True)
            parser.optionxform = str
            parser.read("data.ini")
        
            for key in parser["TRACKLIST"]:
                if key == value:
                    parser.remove_option("TRACKLIST", value)

            with open('data.ini', 'w') as configfile:
                parser.write(configfile)

            self.resetStructs()
            
            self.destUI()

    @QtCore.Slot()
    def addItem(self):
        if self.focus == 0:
            sources = self.readRawOption("TRACKED", "sources") 
            dir = self.askDir()
            self.writeRawOption("TRACKED", "sources", sources + " " + dir)  
            self.sourceUI()
        if self.focus == 1:
            extensions = self.readRawOption("TRACKED", "extensions")
            self.writeRawOption("TRACKED", "extensions", extensions + " " + ".")
            self.extUI()
        if self.focus == 2:
            destinations = self.readRawOption("TRACKED", "destinations") 
            dir = self.askDir()
            self.writeRawOption("TRACKED", "destinations", destinations + " " + dir)
            self.writeRawOption("TRACKLIST", dir)
            self.destUI()

    @QtCore.Slot()
    def extConfirmed(self, ext):
        if (ext != ".") and (ext != "") and (" " not in ext) and (ext not in self.extensions):
            extensions = self.readRawOption("TRACKED", "extensions")
            self.writeRawOption("TRACKED", "extensions", ext.join(extensions.rsplit(".", 1)))
            self.extUI()

    @QtCore.Slot()
    def editItem(self):
        if self.focus == 0:
            sources = self.readRawOption("TRACKED", "sources") 
            dir = self.askDir()
            if dir != "":
                self.writeRawOption("TRACKED", "sources", sources.replace(self.sender().parent().parent().textEdit.text(), dir))
                self.sourceUI()
        if self.focus == 2:
            destinations = self.readRawOption("TRACKED", "destinations") 
            dir = self.askDir()
            if dir != "":
                self.writeRawOption("TRACKED", "destinations", destinations.replace(self.sender().parent().parent().textEdit.text(), dir))
                self.destUI()

    @QtCore.Slot()
    def associate(self):
        dialog = Dialog(UIModel = 'D:\\Projects\\pathfinder\\gui\\dialog.ui')
        dialog.show()

class Dialog(Window, QDialog):
    def __init__(self, UIModel, parent=None):
        QDialog.__init__(self, parent)
        Window.__init__(self, UIModel)

        self.setFixedSize(510, 360)
        self.resetStructs()
        self.fillScrollArea()
        self.show()
    
    def fillScrollArea(self):
        for ext in self.extensions:
            if ext not in self.tracklist.values() and ext != ("." or " "):
                widget = loadUi('D:\\Projects\\pathfinder\\gui\\ext-choice.ui')
                widget.extButton.setText(ext)

                self.scrollLayout.addWidget(widget, self.itemsY, self.itemsX)

                if self.itemsX < 3:
                    self.itemsX += 1
                else:
                    self.itemsX = 0
                    self.itemsY += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(UIModel = 'D:\\Projects\\pathfinder\\gui\\pathfinder-main.ui')
    sys.exit(app.exec_())