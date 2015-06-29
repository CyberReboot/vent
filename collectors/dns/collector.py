import os
import sys
import time
import uuid
import zipfile

from os import walk
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class GZHandler(PatternMatchingEventHandler):

    patterns = ["*.zip"]

    def unzip(self, source_filename, dest_dir):
        with zipfile.ZipFile(source_filename) as zf:
            zf.extractall(dest_dir)

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
            if event.src_path.endswith(".zip"):
                tmp_dir = str(uuid.uuid4())
                self.unzip(event.src_path, tmp_dir)
                p = []
                f = []
                for (dirpath, dirnames, filenames) in walk(tmp_dir):
                    for fi in filenames:
                        if fi.endswith(".csv"):
                            p.append(dirpath)
                            f.append(fi)
                print p, f

    def on_created(self, event):
        self.process(event)

if __name__ == '__main__':
    args = None
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    # !! TODO think through using relative path...
    if not os.path.exists('processed_zips'):
        os.makedirs('processed_zips')
    if not os.path.exists('tmp_zips'):
        os.makedirs('tmp_zips')

    observer = Observer()
    observer.schedule(GZHandler(), path=args[0] if args else '/data')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
