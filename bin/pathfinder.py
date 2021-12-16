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
        self.sources, self.extensions, self.destinations, self.tracklist = configManager.loadConfig()
        self.event_handler = Handler(self.tracklist)
        self.log_handler = LoggingEventHandler()
        self.observer = Observer()
        self.logger = Observer()

    def setupDestinationFolders(self):
        try:
            for source in self.tracklist.keys():
                for file_extension in self.tracklist[source]:
                    path = source + "\{E}".format(E = file_extension.upper()[1:])
                    if not os.path.exists(path):
                        os.mkdir(path)
            return True
        except:
            return False

    def setupObserversSchedule(self):
        for path in self.sources:
            self.observer.schedule(self.event_handler, path)
            self.logger.schedule(self.log_handler, path)

    def run(self):
        if self.setupDestinationFolders():
            self.setupObserversSchedule()
            
            self.observer.start()
            self.logger.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
        else:
            print("failed")
            sys.exit()

    def stop(self):
        self.observer.unschedule_all()
        self.logger.unschedule_all()

        self.observer.stop()
        self.logger.stop()

        self.observer.join()
        self.logger.join()

class Handler(FileSystemEventHandler):
    def __init__(self, tracklist) -> None:
        super().__init__()
        self.tracklist = tracklist

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
        for destination in self.tracklist:
            if file_extension in self.tracklist[destination]: isTracked = True
        return isTracked

    def changeLocation(self, file):
        file_extension = os.path.splitext(file)[1]
        filename = os.path.split(file)[1]
        for destination in self.tracklist:
            if file_extension in self.tracklist[destination]:
                new_path = destination + "\{E}".format(E = file_extension.upper()[1:]) + "\{F}".format(F = filename)
                if os.path.exists(new_path):
                    new_path = self.renameDuplicates(new_path)
                os.rename(file, new_path)

    def renameDuplicates(self, file):
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
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    configManager = ConfigManager("data.ini")
    pathfinder = PathFinder()
    pathfinder.run()