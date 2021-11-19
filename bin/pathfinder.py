import sys
import os.path
import time
from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent, FileSystemEventHandler
from configInterface import ConfigManager

class PathFinder():
    def __init__(self, file) -> None:
        self.tracklist, self.sources, self.extensions, self.destinations = self.configManager.loadConfig()
        self.configManager = ConfigManager(file)
        self.event_handler = Handler(self.tracklist)
        self.observer = Observer()

    def startupFiltering(self):
        try:
            for source in self.tracklist.keys():
                for file_extension in self.tracklist[source]:
                    path = source + "\{E}".format(E = file_extension.upper()[1:])
                    if not os.path.exists(path):
                        os.mkdir(path)
            for source_path in self.sources:
                filter(source_path)
            return True
        except:
            return False

    def setupSchedule(self):
        for path in self.sources:
            self.observer.schedule(self.event_handler, path)

    def run(self):
        if self.startupFiltering():
            self.setupSchedule()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
        else:
            sys.exit()

    def stop(self):
        self.observer.unschedule_all()
        self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    def __init__(self, tracklist) -> None:
        super().__init__()
        self.tracklist = tracklist

    def on_any_event(self, event) -> None:
        print("----------- New Event ------------")
        print("Type: " + event.event_type)
        print("File: " + event.src_path)
        print("Created event:" + str(isinstance(event, FileCreatedEvent)))
        print("Moved event:" + str(isinstance(event, FileMovedEvent)))
        print("Modified event:" + str(isinstance(event, FileModifiedEvent)))
        print("Deleted event:" + str(isinstance(event, FileDeletedEvent)))
        print("----------------------------------\n")

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
            if os.path.isfile(file_path):
                self.dispatch(file_path)

    def dispatch(self, file):
        filename, file_extension = os.path.splitext(file)
        for destination in self.tracklist:
            if file_extension in self.tracklist[destination]:
                new_path = destination + "\{E}".format(E = file_extension.upper()[1:]) + "\{F}".format(F = file)
                if os.path.exists(new_path):
                    new_path = self.renameDuplicates(new_path)
                os.rename(file, new_path)

    def renameDuplicates(self, file):
        copies = 1
        filename, file_extension = os.path.splitext(file)
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
    pathfinder = PathFinder("data.ini")
    pathfinder.run()
    sys.exit()