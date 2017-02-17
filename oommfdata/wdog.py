import sys
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class MyEventHandler(FileSystemEventHandler):
    def __init__(self, observer):
        self.observer = observer

    def on_created(self, event):
        if not event.is_directory:
            if event.src_path.endswith(".txt"):
                print("file created")
            if event.src_path.endswith("stop.txt"):
                self.observer.stop()

observer = Observer()
event_handler = MyEventHandler(observer)

observer.schedule(event_handler, ".", recursive=False)
observer.start()
observer.join()

print("Done")
