import configparser
from tkinter import filedialog, Tk

class DataParser():
    def __init__(self, file) -> None:
        self.configFile = file
        self.parser = configparser.ConfigParser(delimiters=('='), allow_no_value=True)

        self.parser.optionxform = str
        self.parser.read(file)

    def loadConfig(self):
        tracklist = {}

        sources = list(self.parser.get("TRACKED", "sources").split(" "))
        extensions = list(self.parser.get("TRACKED", "extensions").split(" "))
        destinations = list(self.parser.get("TRACKED", "destinations").split(" "))

        for key in self.parser["TRACKLIST"]:
            tracklist[key] = list(self.parser["TRACKLIST"][key].split(" "))

        return (tracklist, 
                sources if '' not in sources else [], 
                extensions if '' not in extensions else [], 
                destinations if '' not in destinations else [])

    def readRawOption(self, section, key):
        return self.parser.get(section, key)

    def writeRawOption(self, section, key, value = ""):
        self.parser.set(section, key, value)
        self.saveConfig()

    def writeRawKey(self, section, key, newKey = ""):
        for oldKey in self.parser[section]:
            if oldKey == key:
                self.parser.remove_option(section, key)
                break
        self.saveConfig()

    def saveConfig(self):
        with open(self.configFile, 'w') as configfile:
            self.parser.write(configfile)

class ConfigManager(DataParser):
    def __init__(self, file) -> None:
        DataParser.__init__(self, file)
        
    def addToConfig(self, focus: int, section, key) -> None:
        option = self.readRawOption(section, key)
        newOption = option

        if focus == 0 or focus == 2: 
            dir = self.getPath()
            newOption = option + " " + dir if len(option) > 0 else option + dir  
        elif focus == 1:
            newOption = option + " " + "." if len(option) > 0 else option + "."
        if focus == 2:
            self.writeRawOption(section, dir)

        self.writeRawOption(section, key, newOption)

    def editConfig(self, focus: int, section, key, value) -> None:
        option = self.readRawOption(section, key)

        if focus == 0 or focus == 2:
            dir = self.getPath()

            if dir != "":
                self.writeRawOption(section, key, option.replace(value, dir))
        elif focus == 1:
            self.writeRawOption(section, key, value.join(option.rsplit(".", 1)))
        if focus == 2:
            pass
        '''replace old key in tracklist'''

    def removeFromConfig(self, focus: int, section, key, value) -> None:
        option = self.readRawOption(section, key)
        itemToRemove = " " + value if len(option) > 0 else value
        self.writeRawOption(section, key, option.replace(itemToRemove, ""))
        #self.writeRawOption(section, key, self.readRawOption(section, key)[:-(len(value) + 1)])

        if focus == 2:
            self.parser.writeRawKey(section, value)

    def getPath(self):
        root = Tk()
        root.withdraw()

        dir = filedialog.askdirectory()
        return dir.replace("/", "\\")