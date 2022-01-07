from tkinter import filedialog, Tk
import platform
import os

def existInDict(value, dict: dict):
    for pool in dict.values():
        if value in pool:
            return True
    return False

def askdirectory():
    root = Tk()
    root.withdraw()

    dir = filedialog.askdirectory()
    return dir.replace("/", "\\") if platform.system() == "Windows" else dir

def renameAsDuplicate(file):
    copies = 1
    file_extension = os.path.splitext(file)[1]
    file = file[:-len(file_extension)]
    file = file + " ({C})".format(C = copies) + file_extension
    while(os.path.exists(file)):
        copies += 1
        file = file[:-len(file_extension)]
        file = file[:-(len(str(copies)) + 3)]
        file += " ({C})".format(C = copies)
        file = file + file_extension
    return file

def toFormat(values: list[str]):
    formattedString = ""
    for index, string in enumerate(values):
        formattedString += string
        if index != len(values): formattedString += "|"
    return formattedString

if __name__ == "__main__":
    print(askdirectory())