from configparser import ParsingError
import sys
import logging
from PySide2 import QtCore
from PySide2.QtWidgets import *
from utils.pyside_dynamic import *
from graphics.resources import *
from win10toast import ToastNotifier

from config.config import Config
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

        self.sourceLayout = GridLayout() 
        self.extensionLayout = GridLayout() 
        self.destinationLayout = GridLayout()
        self.aboutLayout = QVBoxLayout()

        widget = loadUi('UI\\info.ui')
        self.aboutLayout.addWidget(widget)

        self.sourceLayout.fill(self.buildSourceWidgets(config.data[0]), verticalStyle = True)
        self.extensionLayout.fill(self.buildExtensionWidgets(config.data[1]), verticalStyle = False)
        self.destinationLayout.fill(self.buildDestinationWidgets(config.data[2]), verticalStyle = True)

        self.sourceAreaContent.setLayout(self.sourceLayout)
        self.extensionAreaContent.setLayout(self.extensionLayout)
        self.destinationAreaContent.setLayout(self.destinationLayout)
        self.about.setLayout(self.aboutLayout)

        self.setFixedSize(800, 500) 
        self.setSidebarButtonsClick()
        self.setToolbarButtonsClick()

        self.startStopSwitch(service.status())

        self.switchToSources()
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
        self.logoButton.clicked.connect(self.switchToHome)
        self.sourceButton.clicked.connect(self.switchToSources)
        self.extButton.clicked.connect(self.switchToExtensions)
        self.destButton.clicked.connect(self.switchToDestinations)
        self.infoButton.clicked.connect(self.switchToInfo)
        logger.debug("Sidebar buttons activated")

    def setToolbarButtonsClick(self):
        self.startButton.clicked.connect(service.start)
        self.startButton.clicked.connect(lambda: self.startStopSwitch(service.status()))
        self.stopButton.clicked.connect(service.stop)
        self.stopButton.clicked.connect(lambda: self.startStopSwitch(service.status()))
        self.checkButton.clicked.connect(self.checkService)
        logger.debug("Toolbar buttons activated")

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
            self.checkButton.setDisabled(False)
            self.stopButton.setDisabled(False)
        elif status == "SERVICE_STOPPED" or status == "SERVICE_PAUSED":
            self.stopButton.setDisabled(True)
            self.checkButton.setDisabled(False)
            self.startButton.setDisabled(False)
        else:
            self.startButton.setDisabled(True)
            self.stopButton.setDisabled(True)
            self.checkButton.setDisabled(False)

    def checkService(self):
        toast = ToastNotifier()

        if service.status() == "":
            toast.show_toast("PathFinder", "No service found, we recommend you to install it using the script provided in the app folder.", 
            duration = 10,
            icon_path ="assets\\logo.ico",
            threaded = True)
        else:
            toast.show_toast("PathFinder", "Service found! The program is correctly running in background.", 
            duration = 10,
            icon_path ="assets\\logo.ico",
            threaded = True)

    @QtCore.Slot()
    def switchToSources(self) -> None:
        self.stackedWidget.setCurrentWidget(self.sources)
        self.toggleSidebarButton(self.sourceButton)
        self.sourceButton.setChecked(True)
        text = "Manage here the folders you want Pathfinder to extract your files from"
        self.sourceLabel.setText(text)
        logger.debug("Layout succesfully filled with source widgets")

    @QtCore.Slot()
    def switchToExtensions(self) -> None:
        self.stackedWidget.setCurrentWidget(self.extensions)
        self.toggleSidebarButton(self.extButton)
        self.extButton.setChecked(True)
        text = "Add here the extensions of the files you want Pathfinder to move"
        self.extensionLabel.setText(text)
        
        logger.debug("Layout succesfully filled with extension widgets")
        for widget in self.extensionLayout:
            if widget.textEdit.text() == ".":
                widget.setEditable(self.editLayoutWidget)
                self.addButton.setDisabled(True)

    @QtCore.Slot()
    def switchToDestinations(self) -> None:
        self.stackedWidget.setCurrentWidget(self.destinations)
        self.toggleSidebarButton(self.destButton)
        self.destButton.setChecked(True)
        text = "Manage here the folders where you want Pathfinder to place your files"
        self.destinationLabel.setText(text)
        
        logger.debug("Layout succesfully filled with destination widgets")
        for widget in self.destinationLayout:
            widget.connectExtensions(config.data[3])

    @QtCore.Slot()
    def switchToInfo(self) -> None:
        self.stackedWidget.setCurrentWidget(self.about)
        self.toggleSidebarButton(self.infoButton)
        self.infoButton.setChecked(True)
    
    @QtCore.Slot()
    def switchToHome(self) -> None:
        self.stackedWidget.setCurrentWidget(self.home)
        self.toggleSidebarButton(self.logoButton)
        self.logoButton.setChecked(True)
        
    @QtCore.Slot()
    def newLayoutWidget(self) -> None:
        if self.focus == 0:
            dir = askdirectory()
            config.add("TRACKED", "sources", dir)
            self.switchToSources()
        elif self.focus == 1:
            config.add("TRACKED", "extensions", ".")
            self.switchToExtensions()
        elif self.focus == 2:
            dir = askdirectory()
            config.add("TRACKED", "destinations", dir)
            self.switchToDestinations()

    def editLayoutWidget(self) -> None:
        widgetLabel = self.sender().parent().parent().textEdit.text()
        if self.focus == 0:
            dir = askdirectory()
            config.edit("TRACKED", "sources", widgetLabel, dir)
            self.switchToSources()
        elif self.focus == 1:
            config.edit("TRACKED", "extensions", ".", widgetLabel)
            self.addButton.setDisabled(False)
        elif self.focus == 2:
            dir = askdirectory()
            config.edit("TRACKED", "destinations", widgetLabel, dir)
            self.switchToDestinations()

    def removeLayoutWidget(self) -> None:
        widgetLabel = self.sender().parent().parent().textEdit.text()
        if self.focus == 0:
            config.delete("TRACKED", "sources", widgetLabel)
            self.switchToSources()
        elif self.focus == 1:
            config.delete("TRACKED", "extensions", widgetLabel)
            self.switchToExtensions()
        elif self.focus == 2:
            config.delete("TRACKED", "destinations", widgetLabel)
            self.switchToDestinations()

    def linkExtension(self) -> None:
        destination = self.sender().parent().parent().textEdit.text()
        dialog = Dialog(UIModel = 'UI\\dialog.ui', destination = destination, userConfig = config)
        dialog.exec()

        oldSelections = config.parser.get("TRACKLIST", destination)
        newSelections = toFormat(dialog.selections)
        config.edit("TRACKLIST", destination, oldSelections, newSelections)
        self.switchToDestinations()

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