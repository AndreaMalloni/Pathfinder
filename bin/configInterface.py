import configparser
from tkinter import filedialog, Tk
from tkinter.constants import N

class DataParser():
    def __init__(self, file) -> None:
        self.configFile = file
        self.parser = configparser.ConfigParser(delimiters=('='), allow_no_value=True)

        self.parser.optionxform = str
        self.parser.read(file)

    def loadConfig(self):
        self.parser.read(self.configFile)
        tracklist = {}

        sources = list(self.parser.get("TRACKED", "sources").split("|"))
        extensions = list(self.parser.get("TRACKED", "extensions").split("|"))
        destinations = list(self.parser.get("TRACKED", "destinations").split("|"))

        for key in self.parser["TRACKLIST"]:
            tracklist[key] = list(self.parser["TRACKLIST"][key].split("|"))

        return (sources if '' not in sources else [], 
                extensions if '' not in extensions else [], 
                destinations if '' not in destinations else [],
                tracklist)

    def readRawOption(self, section, key):
        return self.parser.get(section, key)

    def writeRawOption(self, section, key, value = ""):
        self.parser.set(section, key, value)
        self.saveConfig()

    def getOptionItemIndex(self, focus, option, item):
        parsedOption = self.loadConfig()[focus]
        parsedIndex = parsedOption.index(item)
        return self.findOccurrence(option, "|", parsedIndex)

    def addKey(self, section, newKey):
        self.parser[section][newKey] = ""
        self.saveConfig()

    def removeKey(self, section, oldKey):
        for key in self.parser[section]:
            if key == oldKey:
                self.parser.remove_option(section, key)
        self.saveConfig()

    def editKey(self, section, oldKey, newKey):
        for key in self.parser[section]:
            if key == oldKey:
                value = self.readRawOption(section, key)
                self.parser.remove_option(section, key)
                self.parser[section][newKey] = value

        self.saveConfig()

    def saveConfig(self):
        with open(self.configFile, 'w') as configfile:
            self.parser.write(configfile)

class ConfigManager(DataParser):
    def __init__(self, file) -> None:
        DataParser.__init__(self, file)
        
    def addToConfig(self, focus: int, section, key) -> None:
        rawOption = self.readRawOption(section, key)
        newOption = rawOption

        if focus == 0 or focus == 2: 
            dir = self.getPath()
            if dir != "":
                newOption = rawOption + "|" + dir if len(rawOption) > 0 else rawOption + dir  
        elif focus == 1:
            newOption = rawOption + "|" + "." if len(rawOption) > 0 else rawOption + "."
        if focus == 2:
            self.addKey("TRACKLIST", dir)

        self.writeRawOption(section, key, newOption)

    def editConfig(self, focus: int, section, key, value) -> None:
        rawOption = self.readRawOption(section, key)

        if focus == 0 or focus == 2:
            rawIndex = self.getOptionItemIndex(focus, rawOption, value)
            parsedOption = self.loadConfig()[focus]
            dir = self.getPath()

            if dir != "":
                newItem = "|" + dir if rawIndex > 0 else dir + "|"
                if len(parsedOption) == 1: newItem = dir 
                newOption = rawOption[:rawIndex] + newItem + rawOption[rawIndex + len(value) + 1:]
                self.writeRawOption(section, key, newOption)

                if focus == 2:
                    self.editKey("TRACKLIST", value, dir)

        elif focus == 1:
            self.writeRawOption(section, key, rawOption.rsplit(".", 1)[0] + value)

    def removeFromConfig(self, focus: int, section, key, value) -> None:
        rawOption = self.readRawOption(section, key)
        rawIndex = self.getOptionItemIndex(focus, rawOption, value)

        newOption = rawOption[:rawIndex] + rawOption[rawIndex + len(value) + 1:]

        self.writeRawOption(section, key, newOption)

        if focus == 2:
            self.removeKey("TRACKLIST", value)

    def getPath(self):
        root = Tk()
        root.withdraw()

        dir = filedialog.askdirectory()
        return dir.replace("/", "\\")

    def findOccurrence(self, string, substring, n):
        if n == 0: return 0
        start = string.find(substring)
        while start >= 0 and n > 1:
            start = string.find(substring, start+len(substring))
            n -= 1
        return start