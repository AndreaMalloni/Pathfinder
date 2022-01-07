import sys
from PySide2 import QtCore
from PySide2.QtWidgets import *
from pyside_dynamic import *
from resources import *

from config import Config
from service import Service
from widgets import *
from dialog import Dialog
from utility_func import toFormat, askdirectory


class MainWindow(QMainWindow):
    def __init__(self, UIModel):
        QMainWindow.__init__(self)
        global config
        global service

        loadUi(UIModel, self)

        self.scrollLayout = GridLayout() 
        self.scrollAreaContent.setLayout(self.scrollLayout)

        self.setFixedSize(800, 500) 
        self.setSidebarButtonsClick()
        self.setToolbarButtonsClick()

        self.startStopSwitch(service.status())

        self.focus = 0
        self.drawSourceWidgets()
        self.show()

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

    def setSidebarButtonsClick(self):
        self.sourceButton.clicked.connect(self.drawSourceWidgets)
        self.extButton.clicked.connect(self.drawExtensionWidgets)
        self.destButton.clicked.connect(self.drawDestinationWidgets)
        self.infoButton.clicked.connect(self.drawInfoWidgets)

    def setToolbarButtonsClick(self):
        self.startButton.clicked.connect(service.start)
        self.startButton.clicked.connect(lambda: self.startStopSwitch(service.status()))
        self.stopButton.clicked.connect(service.stop)
        self.stopButton.clicked.connect(lambda: self.startStopSwitch(service.status()))
        self.addButton.clicked.connect(self.newLayoutWidget)

    def initLayout(self, focus = 0, labelText="") -> None:
        if (self.focus == 3 and focus < 3) or (self.focus < 3 and focus == 3):
            self.toggleToolbar()
        self.focus = focus
        self.toggleSidebarButton(self.sender())
        self.scrollLayout.clear()
        self.addButton.setDisabled(False)
        self.descriptionLabel.setText(labelText)

    def toggleSidebarButton(self, button: QPushButton) -> None:
        for widget in self.sidebarFrame.children():
            if isinstance(widget, QPushButton) and widget != button and widget.isChecked():
                widget.setChecked(False)

    def toggleToolbar(self):
        for widget in self.buttonFrame.children():
            if isinstance(widget, QPushButton):
                widget.setDisabled(not widget.isEnabled())
                widget.setVisible(not widget.isVisible())

    def startStopSwitch(self, status: str):
        if status == "SERVICE_RUNNING":
            self.startButton.setDisabled(True)
            self.stopButton.setDisabled(False)
        elif status == "SERVICE_STOPPED" or status == "SERVICE_PAUSED":
            self.stopButton.setDisabled(True)
            self.startButton.setDisabled(False)
        else:
            self.startButton.setDisabled(True)
            self.stopButton.setDisabled(True)

    @QtCore.Slot()
    def drawSourceWidgets(self) -> None:
        text = "Manage here the folders you want Pathfinder to extract your files from"
        self.initLayout(labelText=text)
        self.scrollLayout.fill(self.buildSourceWidgets(config.data[0]), verticalStyle = True)
        self.sourceButton.setChecked(True)

    @QtCore.Slot()
    def drawExtensionWidgets(self) -> None:
        text = "Add here the extensions of the files you want Pathfinder to move"
        self.initLayout(focus = 1, labelText = text)

        self.extButton.setChecked(True)
        self.scrollLayout.fill(self.buildExtensionWidgets(config.data[1]), verticalStyle = False)
        for widget in self.scrollLayout:
            if widget.textEdit.text() == ".":
                widget.setEditable(self.editLayoutWidget)
                self.addButton.setDisabled(True)

    @QtCore.Slot()
    def drawDestinationWidgets(self) -> None:
        text = "Manage here the folders where you want Pathfinder to place your files"
        self.initLayout(focus = 2, labelText = text)
        
        self.destButton.setChecked(True)

        self.scrollLayout.fill(self.buildDestinationWidgets(config.data[2]), verticalStyle = True)
        for widget in self.scrollLayout:
            widget.connectExtensions(config.data[3])

    @QtCore.Slot()
    def drawInfoWidgets(self) -> None:
        text = "About this software"
        self.initLayout(focus = 3, labelText = text)

        self.infoButton.setChecked(True)
        widget = loadUi('UI\\info.ui')
        self.scrollLayout.addWidget(widget)
        
    @QtCore.Slot()
    def newLayoutWidget(self) -> None:
        if self.focus == 0:
            dir = askdirectory()
            config.add("TRACKED", "sources", dir)
            self.drawSourceWidgets()
        elif self.focus == 1:
            config.add("TRACKED", "extensions", ".")
            self.drawExtensionWidgets()
        elif self.focus == 2:
            dir = askdirectory()
            config.add("TRACKED", "destinations", dir)
            self.drawDestinationWidgets()

    @QtCore.Slot()
    def editLayoutWidget(self) -> None:
        widgetLabel = self.sender().parent().parent().textEdit.text()
        if self.focus == 0:
            dir = askdirectory()
            config.edit("TRACKED", "sources", widgetLabel, dir)
            self.drawSourceWidgets()
        elif self.focus == 1:
            config.edit("TRACKED", "extensions", ".", widgetLabel)
            self.drawExtensionWidgets()
        elif self.focus == 2:
            dir = askdirectory()
            config.edit("TRACKED", "destinations", widgetLabel, dir)
            self.drawDestinationWidgets()

    @QtCore.Slot()
    def removeLayoutWidget(self) -> None:
        widgetLabel = self.sender().parent().parent().textEdit.text()
        if self.focus == 0:
            config.delete("TRACKED", "sources", widgetLabel)
            self.drawSourceWidgets()
        elif self.focus == 1:
            config.delete("TRACKED", "extensions", widgetLabel)
            self.drawExtensionWidgets()
        elif self.focus == 2:
            config.delete("TRACKED", "destinations", widgetLabel)
            self.drawDestinationWidgets()

    @QtCore.Slot()
    def linkExtension(self) -> None:
        destination = self.sender().parent().parent().textEdit.text()
        dialog = Dialog(UIModel = 'UI\\dialog.ui', destination = destination, userConfig = config)
        dialog.exec()

        oldSelections = config.parser.get("TRACKLIST", destination)
        newSelections = toFormat(dialog.selections)
        config.edit("TRACKLIST", destination, oldSelections, newSelections)
        self.drawDestinationWidgets()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    config = Config("data.ini")
    service = Service("PathFinder")
    window = MainWindow(UIModel = 'UI\\pathfinder-main.ui')
    sys.exit(app.exec_())