import configparser

class Config():
    def __init__(self, file) -> None:
        self.configFile = file
        self.parser = configparser.ConfigParser(delimiters=('='), allow_no_value=True)

        self.parser.optionxform = str
        self.parser.read(self.configFile)
        self.data = list(self.load())
        self.backup = list(self.load())

    def load(self) -> tuple[list, list, list, dict]:
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
                tracklist if '' not in tracklist else [])

    def update(self, includeBackup = False) -> None:
        self.data = list(self.load())
        if includeBackup: self.backup = list(self.load())

    def hasChanged(self) -> bool:
        return False if self.data == self.backup else True

    def addKey(self, section, newKey) -> None:
        self.parser[section][newKey] = ""
        self.saveChanges()

    def deleteKey(self, section, oldKey) -> None:
        for key in self.parser[section]:
            if key == oldKey:
                self.parser.remove_option(section, key)
        self.saveChanges()

    def editKey(self, section, oldKey, newKey) -> None:
        for key in self.parser[section]:
            if key == oldKey:
                value = self.parser.get(section, key)
                self.parser.remove_option(section, key)
                self.parser[section][newKey] = value
        self.saveChanges()

    def saveChanges(self) -> None:
        with open(self.configFile, 'w') as configfile:
            self.parser.write(configfile)
        self.update()

    def add(self, section, key, value) -> None:
        option = self.parser.get(section, key)
        newOption = f"{option}|{value}" if len(option) > 0 else f"{value}"

        if key == "destinations":
            self.addKey("TRACKLIST", value)

        self.parser.set(section, key, newOption)
        self.saveChanges()

    def edit(self, section, key, oldValue, newValue) -> None:
        option = self.parser.get(section, key)
        newOption = option.replace(oldValue, newValue)
            
        if key == "destinations":
            self.editKey("TRACKLIST", oldValue, newValue)
        elif key == "extensions":
            newOption = option.rsplit(".", 1)[0] + newValue

        self.parser.set(section, key, newOption)
        self.saveChanges()

    def delete(self, section, key, value) -> None:
        option = self.parser.get(section, key)
        if option.find(f"|{value}") != -1: valueToDelete = f"|{value}"
        elif option.find(f"{value}|") != -1: valueToDelete = f"{value}|"
        else: valueToDelete = f"{value}"
        newOption = option.replace(valueToDelete, "")

        if key == "destinations": self.deleteKey("TRACKLIST", value)      
        if value == ".": newOption = option.rsplit("|.", 1)[0]

        self.parser.set(section, key, newOption)
        self.saveChanges()