import sys
import os.path
import time
import logging
import shutil
from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileModifiedEvent, FileMovedEvent, LoggingEventHandler
from data.config import Config
from utils.utility_func import renameAsDuplicate

class PathFinder():
    def __init__(self) -> None:
        global config
        global logger

        self.event_handler = Handler(logger)
        self.observer = Observer()

    def setupDestinationFolders(self):
        tracklist = config.load()[3]
        for source in tracklist.keys():
            for file_extension in tracklist[source]:
                path = source + "\{E}".format(E = file_extension.upper()[1:])
                if not os.path.exists(path):
                    self.event_handler.logger.debug(f'Destination folder for \'{file_extension}\' extension not found, creating it...')
                    os.mkdir(path)
                    self.event_handler.logger.debug(f'Created destination folder: {path}')

    def setupObserversSchedule(self):
        self.observer.unschedule_all()
        for path in config.load()[0]:
            self.observer.schedule(self.event_handler, path)

    def startTracking(self):
        self.setupDestinationFolders()
        self.setupObserversSchedule()

        self.observer.start()

    def stopTracking(self):
        self.observer.unschedule_all()
        self.observer.stop()

    def run(self):
        try:
            self.startTracking()
            while True:
                if config.hasChanged():
                    self.event_handler.logger.debug(f'Configuration file has changed')
                    config.update(includeBackup = True)
                    self.event_handler.logger.debug(f'Configuration file has been updated')
                    self.setupDestinationFolders()
                    self.setupObserversSchedule()
                    self.event_handler.logger.debug(f'Service schedule updated succesfully')
                time.sleep(1)
        except KeyboardInterrupt:
            self.stopTracking()
            self.observer.join()
            self.event_handler.logger.debug(f'Execution stopped succesfully')
            sys.exit()

class Handler(LoggingEventHandler):
    def __init__(self, logger) -> None:
        super().__init__()
        global config
        self.logger = logger

    def on_created(self, event) -> None:
        if isinstance(event, FileCreatedEvent):
            self.filter(os.path.dirname(event.src_path))
            self.logger.debug(f'Created file: {event.src_path}')

    def on_moved(self, event) -> None:
        if isinstance(event, FileMovedEvent):
            self.filter(os.path.dirname(event.src_path))
            self.logger.debug(f'Moved file: {event.src_path}')

    def on_modified(self, event) -> None:
        if isinstance(event, FileModifiedEvent):
            self.filter(os.path.dirname(event.src_path))
            self.logger.debug(f'Modified file: {event.src_path}')

    def filter(self, dir_path) -> None:
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            file_extension = os.path.splitext(file)[1]
            if os.path.isfile(file_path) and self.isTracked(file_extension):
                self.dispatchFile(file_path)

    def isTracked(self, file_extension) -> bool:
        isTracked = False
        tracklist = config.load()[3]
        for destination in tracklist:
            if file_extension in tracklist[destination]: isTracked = True
        return isTracked

    def dispatchFile(self, file) -> None:
        file_extension = os.path.splitext(file)[1]
        filename = os.path.split(file)[1]
        tracklist = config.load()[3]

        for destination in tracklist:
            if file_extension in tracklist[destination]:
                new_path = destination + "\{E}".format(E = file_extension.upper()[1:]) + "\{F}".format(F = filename)
                if os.path.exists(new_path):
                    new_path = renameAsDuplicate(new_path)
                shutil.move(file, new_path)

if __name__ == '__main__': 
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

    log_file_handler = logging.FileHandler('logs\\stdout.log')
    log_file_handler.setLevel(logging.ERROR)
    log_file_handler.setFormatter(log_formatter)

    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(log_formatter)

    logger.addHandler(log_file_handler)
    logger.addHandler(log_stream_handler)

    config = Config("data.ini")
    pathfinder = PathFinder()
    pathfinder.run()