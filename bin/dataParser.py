import configparser

class CustomParser():
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

        with open(self.configFile, 'w') as configfile:
            self.parser.write(configfile)

    def writeRawKey(self, section, key, newKey = ""):
        for oldKey in self.parser[section]:
            if oldKey == key:
                self.parser.remove_option(section, key)
                break

        with open('data.ini', 'w') as configfile:
            self.parser.write(configfile)