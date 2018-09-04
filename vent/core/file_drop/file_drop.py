import json
import os
import sys
import time
import uuid

import pika
from redis import Redis
from redis import StrictRedis
from rq import Queue
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class GZHandler(PatternMatchingEventHandler):
    """
    Handles when an event on the directory being watched happens that matches
    the values in patterns
    """

    patterns = ['*']
    # want to ignore certain pcap files from splitter as they contain junk
    ignore_patterns = ['*-miscellaneous*']

    # don't want to process files in on_modified for files that have already
    # been created and processed
    created_files = set()
    try:
        # let jobs run for up to one day
        q = Queue(connection=Redis(host='redis'), default_timeout=86400)
        r = StrictRedis(host='redis', port=6379, db=0)
    except Exception as e:  # pragma: no cover
        print('Unable to connect to redis:', str(e))

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        uid = str(uuid.uuid4())
        hostname = os.environ.get('VENT_HOST')
        if not hostname:
            hostname = ''

        try:
            # TODO should directories be treated as bulk paths to send to a
            #      plugin?
            if not event.is_directory:
                spath = event.src_path
                # wait for long copies to finish
                historicalSize = -1
                while (historicalSize != os.path.getsize(spath)):
                    historicalSize = os.path.getsize(spath)
                    time.sleep(0.1)

                if os.path.getsize(spath) == 0:
                    print('file drop ignoring empty file: ' + str(spath))
                    if spath.startswith('trace_'):
                        key = spath.split('_')[1]
                        # Rabbit settings
                        exchange = 'topic-poseidon-internal'
                        exchange_type = 'topic'
                        routing_key = 'poseidon.algos.decider'

                        message = {}
                        message[key] = {'valid': False}
                        message = json.dumps(message)

                        # Send Rabbit message
                        try:
                            connection = pika.BlockingConnection(
                                pika.ConnectionParameters(host='rabbit')
                            )

                            channel = connection.channel()
                            channel.exchange_declare(
                                exchange=exchange, exchange_type=exchange_type
                            )
                            channel.basic_publish(exchange=exchange,
                                                  routing_key=routing_key,
                                                  body=message)
                            connection.close()
                        except Exception as e:
                            print('failed to send rabbit message because: ' +
                                  str(e))

                    return

                # check if the file was already queued and ignore
                exists = False
                print(uid + ' started ' + spath)
                jobs = self.r.keys(pattern='rq:job*')
                for job in jobs:
                    print(uid + ' ***')
                    description = self.r.hget(
                        job, 'description').decode('utf-8')
                    print(uid + ' ' + description)
                    if description.startswith("watch.file_queue('"):
                        print(uid + ' ' +
                              description.split("watch.file_queue('" +
                                                hostname + '_')[1][:-2])
                        print(uid + ' ' + spath)
                        if description.split("watch.file_queue('" +
                                             hostname +
                                             '_')[1][:-2] == spath:
                            print(uid + ' true')
                            exists = True
                    elif description.startswith("watch.gpu_queue('"):
                        print(uid + ' ' +
                              description.split('"file": "')[1].split('"')[0])
                        print(uid + ' ' + spath)
                        if description.split('"file": "')[1].split('"')[0] == spath:
                            print(uid + ' true')
                            exists = True
                    print(uid + ' ***')

                if not exists:
                    # !! TODO this should be a configuration option in the
                    #         vent.template
                    print(uid + " let's queue it " + spath)
                    # let jobs be queued for up to 30 days
                    self.q.enqueue('watch.file_queue',
                                   hostname + '_' + spath,
                                   ttl=2592000)
                print(uid + ' end ' + spath)
        except Exception as e:  # pragma: no cover
            print('file drop error: ' + str(e))

    def on_created(self, event):
        self.created_files.add(event.src_path)
        self.process(event)

    def on_modified(self, event):
        # don't perform any action if file was already created or file is
        # deleted
        if (event.src_path not in self.created_files and
                os.path.exists(event.src_path)):
            # add to created files because the file was moved into directory,
            # which is what should be creating it, but some OS's treat it as a
            # modification with docker mounts
            self.created_files.add(event.src_path)
            self.process(event)


if __name__ == '__main__':  # pragma: no cover
    args = None
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    observer = Observer()
    observer.schedule(GZHandler(), path=args[0] if args else '/files',
                      recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:  # pragma: no cover
        observer.stop()

    observer.join()
