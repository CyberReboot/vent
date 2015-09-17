import sys
import time

from redis import Redis
from rq import Queue
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class GZHandler(PatternMatchingEventHandler):

    patterns = ["*.pcap"]

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        if event.event_type == "created":
            print event.src_path
            q = Queue(connection=Redis(host="redis"))
            result = q.enqueue('pcap_drop.pcap_queue', event.src_path)

    def on_created(self, event):
        self.process(event)

if __name__ == '__main__':
    args = None
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    observer = Observer()
    observer.schedule(GZHandler(), path=args[0] if args else '/data')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
