import sys
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, QRegExp)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QRegExpValidator)
from PySide2.QtWidgets import *
from pyside_dynamic import *
from resources import *
from configInterface import ConfigManager
from widgets import SourceWidget, ExtensionWidget, DestinationWidget

class Window(QMainWindow):
    def __init__(self, UIModel: str) -> None:
        super().__init__()
        self.configManager = ConfigManager("data.ini")
        self.scrollLayout =  QGridLayout(Alignment = QtCore.Qt.AlignTop)

        loadUi(UIModel, self)
        self.scrollAreaContent.setLayout(self.scrollLayout)
        self.scrollLayout.setHorizontalSpacing(12)

    def setStructs(self):
        self.sources, self.extensions, self.destinations, self.tracklist = self.configManager.loadConfig()


class MainWindow(Window, QMainWindow):
    def __init__(self, UIModel, parent=None):
        super().__init__(UIModel)

        self.setFixedSize(800, 500)
        
        self.sourceButton.clicked.connect(self.generateSourceUI)
        self.extButton.clicked.connect(self.generateExtUI)
        self.destButton.clicked.connect(self.generateDestUI)
        self.infoButton.clicked.connect(self.generateInfoUI)
        self.addButton.clicked.connect(self.newLayoutWidget)

        self.generateSourceUI()
        self.show()

    def clearLayout(self, layout: QLayout) -> None:
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    def fillLayout(self, layout: QGridLayout, widgets: list[object], gridAlignment: bool) -> None:
        currentX, currentY = 0, 0
        for widget in widgets:
            widget.x, widget.y = currentX, currentY
            layout.addWidget(widget, widget.y, widget.x)
            
            if gridAlignment:
                currentX, currentY = self.updateWidgetXY(currentX, currentY, 1, 1, maxColumn = 4, gridAlignment = True)
            else:
                currentX, currentY = self.updateWidgetXY(currentX, currentY, 0, 1)

    def updateWidgetXY(self, x, y, dx = 0, dy = 0, maxColumn = 99999, gridAlignment = False):
        if gridAlignment:
            if x < maxColumn - 1:
                x += dx
            else:
                x = 0
                y += dy
        else:
            y += dy
        return x, y

    def buildSourceWidgets(self, labels: list[str]) -> list[object]:
        widgets = []
        for label in labels:
            widget = SourceWidget('UI\\sourceWidget.ui', label)
            widget.connectButtons(self.editLayoutWidget, self.removeLayoutWidget)
            widgets.append(widget)
        return widgets

    def buildExtensionWidgets(self, labels: list[str]) -> list[object]:
        widgets = []
        for label in labels:
            widget = ExtensionWidget('UI\\extensionWidget.ui', label)
            widget.connectButtons(self.removeLayoutWidget)
            widgets.append(widget)
        return widgets

    def buildDestinationWidgets(self, labels: list[str]) -> list[object]:
        widgets = []
        for label in labels:
            widget = DestinationWidget('UI\\destinationWidget.ui', label)
            widget.connectButtons(self.linkExtension, self.editLayoutWidget, self.removeLayoutWidget)
            widgets.append(widget)
        return widgets

    def buildGridWidgets(self) -> None:
        self.sourceWidgets = self.buildSourceWidgets(self.sources)
        self.extensionWidgets = self.buildExtensionWidgets(self.extensions)
        self.destinationWidgets = self.buildDestinationWidgets(self.destinations)

    def initTabUI(self, focus=0, labelText="") -> None:
        self.setStructs()
        self.buildGridWidgets()
        self.toggleSidebarButton(self.sender())
        self.clearLayout(self.scrollLayout)

        self.addButton.setDisabled(False)
        self.focus = focus

        self.descriptionLabel.setText(labelText)

    def toggleSidebarButton(self, button: QPushButton) -> None:
        for widget in self.sidebarFrame.children():
            if isinstance(widget, QPushButton) and widget != button and widget.isChecked():
                widget.setChecked(False)

    @QtCore.Slot()
    def generateSourceUI(self) -> None:
        text = "Manage here the folders you want Pathfinder to extract your files from"
        self.initTabUI(labelText=text)

        self.sourceButton.setChecked(True)

        self.fillLayout(self.scrollLayout, self.sourceWidgets, gridAlignment = False)
                    
    @QtCore.Slot()
    def generateExtUI(self) -> None:
        text = "Add here the extensions of the files you want Pathfinder to move"
        self.initTabUI(focus = 1, labelText = text)

        self.extButton.setChecked(True)
        self.fillLayout(self.scrollLayout, self.extensionWidgets, gridAlignment = True)
        for widget in self.extensionWidgets:
            if widget.textEdit.text() == ".":
                widget.setEditable(self.editLayoutWidget)
                self.addButton.setDisabled(True)

    @QtCore.Slot()
    def generateDestUI(self) -> None:
        text = "Manage here the folders where you want Pathfinder to place your files"
        self.initTabUI(focus = 2, labelText = text)
        
        self.destButton.setChecked(True)

        self.fillLayout(self.scrollLayout, self.destinationWidgets, gridAlignment = False)
        for widget in self.destinationWidgets:
            widget.connectExtensions(self.tracklist)

    @QtCore.Slot()
    def generateInfoUI(self) -> None:
        text = "About this software"
        self.initTabUI(focus = 3, labelText = text)

        self.infoButton.setChecked(True)
        widget = loadUi('UI\\info.ui')
        self.scrollLayout.addWidget(widget)
        self.addButton.setDisabled(True)
        
    @QtCore.Slot()
    def newLayoutWidget(self) -> None:
        if self.focus == 0:
            self.configManager.addToConfig(self.focus, "TRACKED", "sources")
            self.generateSourceUI()
        elif self.focus == 1:
            self.configManager.addToConfig(self.focus, "TRACKED", "extensions")
            self.generateExtUI()
        elif self.focus == 2:
            self.configManager.addToConfig(self.focus, "TRACKED", "destinations")
            self.generateDestUI()

    @QtCore.Slot()
    def editLayoutWidget(self) -> None:
        widgetLabel = self.sender().parent().parent().textEdit.text()
        if self.focus == 0:
            self.configManager.editConfig(self.focus, "TRACKED", "sources", widgetLabel)
            self.generateSourceUI()
        elif self.focus == 1:
            self.configManager.editConfig(self.focus, "TRACKED", "extensions", widgetLabel)
            self.generateExtUI()
        elif self.focus == 2:
            self.configManager.editConfig(self.focus, "TRACKED", "destinations", widgetLabel)
            self.generateDestUI()

    @QtCore.Slot()
    def removeLayoutWidget(self) -> None:
        widgetLabel = self.sender().parent().parent().textEdit.text()
        if self.focus == 0:
            self.configManager.removeFromConfig(self.focus, "TRACKED", "sources", widgetLabel)
            self.generateSourceUI()
        elif self.focus == 1:
            self.configManager.removeFromConfig(self.focus, "TRACKED", "extensions", widgetLabel)
            self.generateExtUI()
        elif self.focus == 2:
            self.configManager.removeFromConfig(self.focus, "TRACKED", "destinations", widgetLabel)
            self.generateDestUI()

    @QtCore.Slot()
    def linkExtension(self) -> None:
        dialog = Dialog(UIModel = 'UI\\dialog.ui')
        dialog.exec()
        destination = self.sender().parent().parent().textEdit.text()
        selections = dialog.checkedExt
        associations = self.configManager.readRawOption("TRACKLIST", destination)

        for ext in selections:
            associations = associations + "|" + ext

        self.configManager.writeRawOption("TRACKLIST", destination, associations)
        self.generateDestUI()


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
                
        self.fillLayout(self.scrollLayout, self.availableExt, 'UI\\ext-choice.ui', gridAlignment = True)

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
    window = MainWindow(UIModel = 'UI\\pathfinder-main.ui')
    sys.exit(app.exec_())