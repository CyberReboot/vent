import os
import sys
import time
import uuid

from redis import Redis
from redis import StrictRedis
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
        uid = str(uuid.uuid4())
        hostname = os.environ.get("VENT_HOST")
        if not hostname:
            hostname = ""
        # let jobs run for up to one day
        try:
            q = Queue(connection=Redis(host=r_host), default_timeout=86400)
            # TODO should directories be treated as bulk paths to send to a plugin?
            if event.event_type == "created" and event.is_directory == False:
                # check if the file was already queued and ignore
                time.sleep(15)
                exists = False
                print(uid+" started " + event.src_path)
                r = StrictRedis(host=r_host, port=6379, db=0)
                jobs = r.keys(pattern="rq:job*")
                for job in jobs:
                    print(uid+" ***")
                    description = r.hget(job, 'description')
                    print(uid+" "+description)
                    print(uid+" "+description.split("file_watch.file_queue('"+hostname+"_")[1][:-2])
                    print(uid+" "+event.src_path)
                    if description.split("file_watch.file_queue('"+hostname+"_")[1][:-2] == event.src_path:
                        print(uid+" true")
                        exists = True
                    print(uid+" ***")
                if not exists:
                    # !! TODO this should be a configuration option in the vent.template
                    print(uid+" let's queue it "+event.src_path)
                    # let jobs be queued for up to 30 days
                    result = q.enqueue('file_watch.file_queue', hostname+"_"+event.src_path, ttl=2592000)
                print(uid+" end "+event.src_path)
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
