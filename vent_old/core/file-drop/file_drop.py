import os
import sys
import time

from redis import Redis
from rq import Queue
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class GZHandler(PatternMatchingEventHandler):
    """
    Handles when an event on the directory being watched happens that matches
    the values in patterns
    """

    patterns = ["*"]

    @staticmethod
    def process(event, r_host):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        hostname = os.environ.get("VENT_HOST")
        if not hostname:
            hostname = ""
        # let jobs run for up to one day
        try:
            q = Queue(connection=Redis(host=r_host), default_timeout=86400)
            if event.event_type == "created" and event.is_directory == False:
                print(event.src_path)
                # let jobs be queued for up to 30 days
                result = q.enqueue('file_watch.file_queue', hostname+"_"+event.src_path, ttl=2592000)
        except Exception as e:
            print(str(e))

    def on_created(self, event):
        self.process(event, 'redis')

if __name__ == '__main__': # pragma: no cover
    args = None
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    observer = Observer()
    observer.schedule(GZHandler(), path=args[0] if args else '/files')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
