import sys
from PySide2 import QtCore
from PySide2.QtWidgets import *
from pyside_dynamic import *
from resources import *
from configInterface import ConfigManager
from serviceinterface import ServiceManager
from widgets import SourceWidget, ExtensionWidget, DestinationWidget, LayoutWidget

class DefaultLayoutWindow():
    def __init__(self, UIModel: str) -> None:
        loadUi(UIModel, self)

        self.scrollLayout =  QGridLayout() 
        self.scrollAreaContent.setLayout(self.scrollLayout)
        self.scrollLayout.setHorizontalSpacing(12)

    def clearLayout(self, layout: QLayout) -> None:
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    def isLayoutEmpty(self, layout: QLayout):
        return (False if layout.count() != 0 else True)

    def fillLayout(self, layout: QGridLayout, widgets: list[QWidget], gridAlignment: bool) -> None:
        if widgets != []:
            currentX, currentY = 0, 0
            self.scrollLayout.setAlignment(QtCore.Qt.AlignTop)
            for widget in widgets:
                widget.x, widget.y = currentX, currentY
                layout.addWidget(widget, widget.y, widget.x)
                
                if gridAlignment:
                    currentX, currentY = self.updateWidgetXY(currentX, currentY, 1, 1, maxColumn = 4, gridAlignment = True)
                else:
                    currentX, currentY = self.updateWidgetXY(currentX, currentY, 0, 1)
        else:
            widget = loadUi('UI\\default.ui')
            self.scrollLayout.setAlignment(QtCore.Qt.AlignVCenter)
            self.scrollLayout.addWidget(widget)

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

class MainWindow(DefaultLayoutWindow, QMainWindow):
    def __init__(self, UIModel, parent=None):
        QMainWindow.__init__(self)
        DefaultLayoutWindow.__init__(self, UIModel)
        global configManager
        global serviceManager

        self.setFixedSize(800, 500) 
        self.setSidebarButtonsClick()
        self.setToolbarButtonsClick()

        self.startStopSwitch(serviceManager.checkServiceStatus())

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
        self.startButton.clicked.connect(serviceManager.startService)
        self.startButton.clicked.connect(lambda: self.startStopSwitch(serviceManager.checkServiceStatus()))
        self.stopButton.clicked.connect(serviceManager.stopService)
        self.stopButton.clicked.connect(lambda: self.startStopSwitch(serviceManager.checkServiceStatus()))
        self.addButton.clicked.connect(self.newLayoutWidget)

    def initLayout(self, focus = 0, labelText="") -> None:
        if (self.focus == 3 and focus < 3) or (self.focus < 3 and focus == 3):
            self.toggleToolbar()
        self.focus = focus
        self.toggleSidebarButton(self.sender())
        self.clearLayout(self.scrollLayout)
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
        self.fillLayout(self.scrollLayout, self.buildSourceWidgets(configManager.loadConfig()[0]), gridAlignment = False)
        self.sourceButton.setChecked(True)

    @QtCore.Slot()
    def drawExtensionWidgets(self) -> None:
        text = "Add here the extensions of the files you want Pathfinder to move"
        self.initLayout(focus = 1, labelText = text)

        self.extButton.setChecked(True)
        extensionWidgets = self.buildExtensionWidgets(configManager.loadConfig()[1])
        self.fillLayout(self.scrollLayout, extensionWidgets, gridAlignment = True)
        for widget in extensionWidgets:
            if widget.textEdit.text() == ".":
                widget.setEditable(self.editLayoutWidget)
                self.addButton.setDisabled(True)

    @QtCore.Slot()
    def drawDestinationWidgets(self) -> None:
        text = "Manage here the folders where you want Pathfinder to place your files"
        self.initLayout(focus = 2, labelText = text)
        
        self.destButton.setChecked(True)

        destinationWidgets = self.buildDestinationWidgets(configManager.loadConfig()[2])
        self.fillLayout(self.scrollLayout, destinationWidgets, gridAlignment = False)
        for widget in destinationWidgets:
            widget.connectExtensions(configManager.loadConfig()[3])

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
            configManager.addToConfig(self.focus, "TRACKED", "sources")
            self.drawSourceWidgets()
        elif self.focus == 1:
            configManager.addToConfig(self.focus, "TRACKED", "extensions")
            self.drawExtensionWidgets()
        elif self.focus == 2:
            configManager.addToConfig(self.focus, "TRACKED", "destinations")
            self.drawDestinationWidgets()

    @QtCore.Slot()
    def editLayoutWidget(self) -> None:
        widgetLabel = self.sender().parent().parent().textEdit.text()
        if self.focus == 0:
            configManager.editConfig(self.focus, "TRACKED", "sources", widgetLabel)
            self.drawSourceWidgets()
        elif self.focus == 1:
            configManager.editConfig(self.focus, "TRACKED", "extensions", widgetLabel)
            self.drawExtensionWidgets()
        elif self.focus == 2:
            configManager.editConfig(self.focus, "TRACKED", "destinations", widgetLabel)
            self.drawDestinationWidgets()

    @QtCore.Slot()
    def removeLayoutWidget(self) -> None:
        widgetLabel = self.sender().parent().parent().textEdit.text()
        if self.focus == 0:
            configManager.removeFromConfig(self.focus, "TRACKED", "sources", widgetLabel)
            self.drawSourceWidgets()
        elif self.focus == 1:
            configManager.removeFromConfig(self.focus, "TRACKED", "extensions", widgetLabel)
            self.drawExtensionWidgets()
        elif self.focus == 2:
            configManager.removeFromConfig(self.focus, "TRACKED", "destinations", widgetLabel)
            self.drawDestinationWidgets()

    @QtCore.Slot()
    def linkExtension(self) -> None:
        dialog = Dialog(UIModel = 'UI\\dialog.ui')
        dialog.exec()
        destination = self.sender().parent().parent().textEdit.text()
        selections = dialog.checkedExt
        associations = configManager.readRawOption("TRACKLIST", destination)

        for ext in selections:
            associations = associations + "|" + ext

        configManager.writeRawOption("TRACKLIST", destination, associations)
        self.drawDestinationWidgets()

class Dialog(DefaultLayoutWindow, QDialog):
    def __init__(self, UIModel, parent=None):
        QDialog.__init__(self, parent)
        DefaultLayoutWindow.__init__(self, UIModel)
        global configManager

        self.setFixedSize(500, 300)
        self.availableExt = []
        self.drawDialogWidgets()

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.checkedExt = []
        self.show()
    
    def existIn(self, value, dict: dict):
        for pool in dict.values():
            if value in pool:
                return True
        return False

    def buildDialogWidgets(self, labels: list[str]) -> list[object]:
        widgets = []
        for label in labels:
            widget = LayoutWidget('UI\\ext-choice.ui', label)
            widgets.append(widget)
        return widgets

    def drawDialogWidgets(self):
        for ext in configManager.loadConfig()[1]:
            if not self.existIn(ext, configManager.loadConfig()[3]):
                self.availableExt.append(ext)
                
        widgets = self.buildDialogWidgets(self.availableExt)
        self.fillLayout(self.scrollLayout, widgets, gridAlignment = True)

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
    configManager = ConfigManager("data.ini")
    serviceManager = ServiceManager("PathFinder")
    window = MainWindow(UIModel = 'UI\\pathfinder-main.ui')
    sys.exit(app.exec_())