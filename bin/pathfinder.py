from configparser import ParsingError
import sys
import os.path
import time
import logging
import shutil
from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileModifiedEvent, FileMovedEvent, LoggingEventHandler
from config.config import Config
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
                path = source + f"\{file_extension.upper()[1:]}"
                try:
                    os.mkdir(path)
                    self.event_handler.logger.debug(f'Created destination folder: {path}')
                except FileExistsError:
                    self.event_handler.logger.debug(f'Destination folder for \'{file_extension}\' extension already exists')

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
        self.startTracking()
        while True:
            try:
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
            except FileNotFoundError:
                self.setupDestinationFolders()

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
                new_path = destination + f"\{file_extension.upper()[1:]}\{filename}"
                if os.path.exists(new_path):
                    self.logger.debug(f'The file {new_path} already exists')
                    new_path = renameAsDuplicate(new_path)
                    self.logger.debug(f'The file {new_path} has been succesfully renamed')
                try:
                    shutil.move(file, new_path)
                    self.logger.debug(f'File succesfully moved to: {new_path}')
                except PermissionError as e:
                    self.logger.error(str(e))
                except FileNotFoundError as e:
                    os.mkdir(destination + f"\{file_extension.upper()[1:]}")
                    shutil.move(file, new_path)

if __name__ == '__main__': 
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

    log_file_handler = logging.FileHandler('logs\\pathfinder.log')
    log_file_handler.setLevel(logging.ERROR)
    log_file_handler.setFormatter(log_formatter)

    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(log_formatter)

    logger.addHandler(log_file_handler)
    logger.addHandler(log_stream_handler)

    try:
        config = Config("data.ini")
        pathfinder = PathFinder()
        pathfinder.run()
    except ParsingError:
        logger.error("A parsing error occured. Configuration file might be corrupted")
    except Exception as e:
        logger.error(str(e))