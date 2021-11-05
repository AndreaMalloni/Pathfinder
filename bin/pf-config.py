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

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        
        loadUi('D:\\Projects\\pathfinder\\gui\\pathfinder-main.ui', self)
        self.setFixedSize(800, 500)

        self.updateStructs()
        self.focus = 0

        self.scrollLayout =  QGridLayout()
        self.scrollAreaContent.setLayout(self.scrollLayout)
        self.spacer = QSpacerItem(40, 20,  QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        self.sourceUI()
        
        self.sourceButton.clicked.connect(self.sourceUI)
        self.extButton.clicked.connect(self.extUI)
        self.destButton.clicked.connect(self.destUI)
        self.infoButton.clicked.connect(self.infoUI)
        self.addButton.clicked.connect(self.addItem)

        self.show()

    def updateStructs(self):
        self.tracklist, self.sources, self.extensions, self.destinations = readINI("data.ini")

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

        self.updateStructs()

    def readRawOption(self, section, key):
        parser = configparser.ConfigParser(delimiters=('='), allow_no_value=True)
        parser.optionxform = str
        parser.read("data.ini")
        return parser.get(section, key)

    def clearContent(self, layout):
        layout.removeItem(self.spacer)

        #for i in range(layout.count()):
            #layout.itemAt(i).widget().deleteLater()

        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    def toggleSidebarItem(self, button):
        for widget in self.sidebarFrame.children():
            if isinstance(widget, QPushButton) and widget != button and widget.isChecked():
                widget.setChecked(False)

    @QtCore.Slot()
    def sourceUI(self):
        self.updateStructs()
        self.toggleSidebarItem(self.sender())
        self.clearContent(self.scrollLayout)

        self.sourceButton.setChecked(True)
        self.addButton.setDisabled(False)
        self.focus = 0

        self.descriptionLabel.setText("Manage here the folders you want Pathfinder to extract your files from")
        y, x = 0, 0
        
        for source in self.sources:
            widget = loadUi('D:\\Projects\\pathfinder\\gui\\source.ui')
            widget.textEdit.setText(source)
            widget.editButton.clicked.connect(self.editItem)
            widget.deleteButton.clicked.connect(lambda: self.deleteItem("TRACKED", "sources", widget.textEdit.text()))
            self.scrollLayout.addWidget(widget, y, x)
            y += 1
        
        self.scrollLayout.addItem(self.spacer, Alignment = QtCore.Qt.AlignTop)
            
    @QtCore.Slot()
    def extUI(self):
        self.updateStructs()
        self.toggleSidebarItem(self.sender())
        self.clearContent(self.scrollLayout)

        self.extButton.setChecked(True)
        self.addButton.setDisabled(False)
        self.focus = 1

        self.descriptionLabel.setText("Add here the extensions of the files you want Pathfinder to move")
        y, x = 0, 0

        for ext in self.extensions:
            widget = loadUi('D:\\Projects\\pathfinder\\gui\\extension.ui')
            widget.textEdit.setText(ext)
            widget.deleteButton.clicked.connect(lambda: self.deleteItem("TRACKED", "extensions", widget.textEdit.text()))
            self.scrollLayout.addWidget(widget, y, x)

            if x < 3:
                x += 1
            else:
                x = 0
                y += 1

            if ext == "." or " " in ext:
                widget.textEdit.setReadOnly(False)
                widget.textEdit.setFocus()
                self.addButton.setDisabled(True)
                widget.textEdit.returnPressed.connect(lambda: self.extConfirmed(widget.textEdit.text()))

        self.scrollLayout.addItem(self.spacer, Alignment = QtCore.Qt.AlignTop)

    @QtCore.Slot()
    def destUI(self):
        self.updateStructs()
        self.toggleSidebarItem(self.sender())
        self.clearContent(self.scrollLayout)

        self.destButton.setChecked(True)
        self.addButton.setDisabled(False)
        self.focus = 2

        self.descriptionLabel.setText("Manage here the folders where you want Pathfinder to place your files")
        y, x = 0, 0

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
            self.scrollLayout.addWidget(widget, y, x)
            y += 1
  
        self.scrollLayout.addItem(self.spacer, Alignment = QtCore.Qt.AlignTop)

    @QtCore.Slot()
    def infoUI(self):
        self.toggleSidebarItem(self.sender())
        self.clearContent(self.scrollLayout)

        self.infoButton.setChecked(True)
        self.focus = 3
        self.addButton.setDisabled(True)

        self.descriptionLabel.setText("About this software")

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

            self.updateStructs()
            
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
        dialog = loadUi('D:\\Projects\\pathfinder\\gui\\dialog.ui')
        grid = QGridLayout()
        
        for ext in self.extensions:
            if ext not in self.tracklist.values():
                widget = loadUi('D:\\Projects\\pathfinder\\gui\\ext-choice.ui')
                widget.setText(ext)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())