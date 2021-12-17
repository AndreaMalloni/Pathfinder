import sys
import os.path
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileModifiedEvent, FileMovedEvent, FileSystemEventHandler, LoggingEventHandler
from configInterface import ConfigManager

class PathFinder():
    def __init__(self) -> None:
        global configManager
        
        self.event_handler = Handler()
        self.log_handler = LoggingEventHandler()
        self.observer = Observer()
        self.logger = Observer()

    def setupDestinationFolders(self):
        try:
            tracklist = configManager.loadConfig()[3]
            for source in tracklist.keys():
                for file_extension in tracklist[source]:
                    path = source + "\{E}".format(E = file_extension.upper()[1:])
                    if not os.path.exists(path):
                        os.mkdir(path)
            return True
        except:
            return False

    def setupObserversSchedule(self):
        self.observer.unschedule_all()
        self.logger.unschedule_all()
        for path in configManager.loadConfig()[0]:
            self.observer.schedule(self.event_handler, path)
            self.logger.schedule(self.log_handler, path)

    def startTracking(self):
        self.setupDestinationFolders()
        self.setupObserversSchedule()

        self.observer.start()
        self.logger.start()

    def stopTracking(self):
        self.observer.unschedule_all()
        self.logger.unschedule_all()

        self.observer.stop()
        self.logger.stop()

    def run(self):
        try:
            self.startTracking()
            while True:
                if configManager.hasChanged():
                    self.setupDestinationFolders()
                    self.setupObserversSchedule()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stopTracking()
            self.observer.join()
            self.logger.join()
            sys.exit()

class Handler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        global configManager

    def on_created(self, event) -> None:
        if isinstance(event, FileCreatedEvent):
            print("*filtering*\n")
            self.filter(os.path.dirname(event.src_path))

    def on_moved(self, event) -> None:
        if isinstance(event, FileMovedEvent):
            print("*filtering*\n")
            self.filter(os.path.dirname(event.src_path))

    def on_modified(self, event) -> None:
        if isinstance(event, FileModifiedEvent):
            print("*filtering*\n")
            self.filter(os.path.dirname(event.src_path))

    def filter(self, dir_path):
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            file_extension = os.path.splitext(file)[1]
            if os.path.isfile(file_path) and self.isTracked(file_extension):
                self.changeLocation(file_path)

    def isTracked(self, file_extension):
        isTracked = False
        tracklist = configManager.loadConfig()[3]
        for destination in tracklist:
            if file_extension in tracklist[destination]: isTracked = True
        return isTracked

    def changeLocation(self, file):
        file_extension = os.path.splitext(file)[1]
        filename = os.path.split(file)[1]
        tracklist = configManager.loadConfig()[3]
        for destination in tracklist:
            if file_extension in tracklist[destination]:
                new_path = destination + "\{E}".format(E = file_extension.upper()[1:]) + "\{F}".format(F = filename)
                if os.path.exists(new_path):
                    new_path = self.renameDuplicate(new_path)
                os.rename(file, new_path)

    def renameDuplicate(self, file):
        copies = 1
        file_extension = os.path.splitext(file)[1]
        file = file[:-len(file_extension)]
        file = file + " ({C})".format(C = copies) + file_extension
        while(os.path.exists(file)):
            copies += 1
            file = file[:-len(file_extension)]
            file = file[:-4]
            file += " ({C})".format(C = copies)
            file = file + file_extension
        return file

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    configManager = ConfigManager("data.ini")
    pathfinder = PathFinder()
    pathfinder.run()