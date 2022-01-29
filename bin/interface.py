from configparser import NoOptionError, NoSectionError, ParsingError
import sys
import logging
from PySide2 import QtCore
from PySide2.QtWidgets import *
from utils.pyside_dynamic import *
from graphics.resources import *

from data.config import Config
from utils.service import Service
from graphics.widgets import *
from graphics.dialog import Dialog
from utils.utility_func import toFormat, askdirectory


class MainWindow(QMainWindow):
    def __init__(self, UIModel):
        QMainWindow.__init__(self)
        global config
        global service
        global logger

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
        logger.debug("Main window succesfully initialized")

    def buildSourceWidgets(self, labels: list[str]) -> list[object]:
        widgets = []
        for label in labels:
            widget = SourceWidget('UI\\sourceWidget.ui', label)
            widget.connectButtons(self.editLayoutWidget, self.removeLayoutWidget)
            widgets.append(widget)
        logger.debug("Generated source widgets")
        return widgets

    def buildExtensionWidgets(self, labels: list[str]) -> list[object]:
        widgets = []
        for label in labels:
            widget = ExtensionWidget('UI\\extensionWidget.ui', label)
            widget.connectButtons(self.removeLayoutWidget)
            widgets.append(widget)
        logger.debug("Generated extension widgets")
        return widgets

    def buildDestinationWidgets(self, labels: list[str]) -> list[object]:
        widgets = []
        for label in labels:
            widget = DestinationWidget('UI\\destinationWidget.ui', label)
            widget.connectButtons(self.linkExtension, self.editLayoutWidget, self.removeLayoutWidget)
            widgets.append(widget)
        logger.debug("Generated destination widgets")
        return widgets

    def setSidebarButtonsClick(self):
        self.sourceButton.clicked.connect(self.drawSourceWidgets)
        self.extButton.clicked.connect(self.drawExtensionWidgets)
        self.destButton.clicked.connect(self.drawDestinationWidgets)
        self.infoButton.clicked.connect(self.drawInfoWidgets)
        logger.debug("Sidebar buttons activated")

    def setToolbarButtonsClick(self):
        self.startButton.clicked.connect(service.start)
        self.startButton.clicked.connect(lambda: self.startStopSwitch(service.status()))
        self.stopButton.clicked.connect(service.stop)
        self.stopButton.clicked.connect(lambda: self.startStopSwitch(service.status()))
        self.addButton.clicked.connect(self.newLayoutWidget)
        logger.debug("Toolbar buttons activated")

    def initLayout(self, focus = 0, labelText="") -> None:
        if (self.focus == 3 and focus < 3) or (self.focus < 3 and focus == 3):
            self.toggleToolbar()
        self.focus = focus
        self.scrollLayout.clear()
        logger.debug("Layout cleared succesfully")
        self.toggleSidebarButton(self.sender())
        self.addButton.setDisabled(False)
        self.descriptionLabel.setText(labelText)
        logger.debug("Section label changed succesfully")
        logger.debug("Ready to switch section")

    def toggleSidebarButton(self, button: QPushButton) -> None:
        for widget in self.sidebarFrame.children():
            if isinstance(widget, QPushButton) and widget != button and widget.isChecked():
                widget.setChecked(False)
                logger.debug(f"'{widget.text()}' button unchecked, switching to '{button.text()}'")

    def toggleToolbar(self):
        for widget in self.buttonFrame.children():
            if isinstance(widget, QPushButton):
                widget.setDisabled(not widget.isEnabled())
                widget.setVisible(not widget.isVisible())
        logger.debug("Toolbar visibility updated")

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
        logger.debug("Layout succesfully filled with source widgets")
        self.sourceButton.setChecked(True)

    @QtCore.Slot()
    def drawExtensionWidgets(self) -> None:
        text = "Add here the extensions of the files you want Pathfinder to move"
        self.initLayout(focus = 1, labelText = text)

        self.extButton.setChecked(True)
        self.scrollLayout.fill(self.buildExtensionWidgets(config.data[1]), verticalStyle = False)
        logger.debug("Layout succesfully filled with extension widgets")
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
        logger.debug("Layout succesfully filled with destination widgets")
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
            self.addButton.setDisabled(False)
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

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

    log_file_handler = logging.FileHandler('logs\\interface.log')
    log_file_handler.setLevel(logging.ERROR)
    log_file_handler.setFormatter(log_formatter)

    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(log_formatter)

    logger.addHandler(log_file_handler)
    logger.addHandler(log_stream_handler)
    
    try:
        app = QApplication(sys.argv)
        config = Config("data.ini")
        service = Service("PathFinder")
        window = MainWindow(UIModel = 'UI\\pathfinder-main.ui')
    except ParsingError:
        logger.error("A parsing error occured. Configuration file might be corrupted")
    except Exception as e:
        logger.error(str(e))
    else:
        sys.exit(app.exec_())