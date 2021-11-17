import sys
import os.path
import time
from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent, FileSystemEventHandler
from dataParser import CustomParser

'''
Function that iterates over the directories contained in "sources" global list,
matching every file extension with those contained in "tracklist" global dict.
Those file whose extension matches the ones contained in "tracklist" are moved
to a new path.
'''
def filter(source_path):
    for file in os.listdir(source_path):
        file_path = os.path.join(source_path, file)
        if os.path.isfile(file_path):
            filename, file_extension = os.path.splitext(file_path)
            for destination in tracklist:
                if file_extension in tracklist[destination]:
                    new_path = destination + "\{E}".format(E = file_extension.upper()[1:]) + "\{F}".format(F = file)
                    if os.path.exists(new_path):
                        copies = 1
                        filename, file_extension = os.path.splitext(new_path)
                        new_path = new_path[:-len(file_extension)]
                        new_path = new_path + " ({C})".format(C = copies) + file_extension
                        while(os.path.exists(new_path)):
                            copies += 1
                            new_path = new_path[:-len(file_extension)]
                            new_path = new_path[:-4]
                            new_path += " ({C})".format(C = copies)
                            new_path = new_path + file_extension
                    os.rename(file_path, new_path)
                        

'''
Function executed on startup that searches for destination sources
in every tracked directory. In case they do not exists, it creates them.
'''
def startup():
    try:
        for source in tracklist.keys():
            for file_extension in tracklist[source]:
                path = source + "\{E}".format(E = file_extension.upper()[1:])
                if not os.path.exists(path):
                    os.mkdir(path)
        for source_path in sources:
            filter(source_path)
        return True
    except:
        return False

'''
Subclass of FileSystemEventHadler class. On_any_event method is overridden
and calls "filter" function whenever a new file system event occurs inside
the sources specified in "sources" global list.
'''
class Handler(FileSystemEventHandler):

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
            filter(os.path.dirname(event.src_path))

    def on_moved(self, event) -> None:
        if isinstance(event, FileMovedEvent):
            print("*filtering*\n")
            filter(os.path.dirname(event.src_path))

    def on_modified(self, event) -> None:
        if isinstance(event, FileModifiedEvent):
            print("*filtering*\n")
            filter(os.path.dirname(event.src_path))

if __name__ == '__main__':
    parser = CustomParser("data.ini")
    tracklist, sources, extensions, destinations = parser.loadConfig("data.ini")
    
    if not startup():
        sys.exit()

    event_handler = Handler()
    observer = Observer()

    for source_path in sources:
        observer.schedule(event_handler, source_path)

    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.unschedule_all()
        observer.stop()

    observer.join()