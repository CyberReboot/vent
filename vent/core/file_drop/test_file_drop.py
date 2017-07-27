import file_drop

from redis import Redis
from redis import StrictRedis
from rq import Queue


def test_file_drop_GZHandler():
    """ Tests the GZZHandler for file drop """
    a = file_drop.GZHandler()

    class Event:
        """ Creates a mock event object for tests """
        event_type = None
        src_path = None
        is_directory = None
        q = Queue(connection=Redis(host='localhost'), default_timeout=86400)
        r = StrictRedis(host='localhsot', port=6379, db=0)

        def __init__(self, event_type, src_path, is_directory, q, r):
            """ initializes necessary variables for the object """
            self.event_type = event_type
            self.src_path = src_path
            self.is_directory = is_directory
            self.q = q
            self.r = r

    b = Event("created", "/dev/null", False)
    a.process(b)
    a.process(b)
    a.process(b)
    a.on_created(b)
    a.on_modified(b)
