from .file_drop import GZHandler
from redis import Redis
from redis import StrictRedis
from rq import Queue


def test_file_drop_GZHandler():
    """ Tests the GZZHandler for file drop """
    a = GZHandler()

    class Event:
        """ Creates a mock event object for tests """
        event_type = None
        src_path = None
        is_directory = None
        q = None
        r = None

        def __init__(self, event_type, src_path, is_directory):
            """ initializes necessary variables for the object """
            self.event_type = event_type
            self.src_path = src_path
            self.is_directory = is_directory
            self.q = Queue(connection=Redis(host='localhost'),
                           default_timeout=86400)
            self.r = StrictRedis(host='localhost', port=6379, db=0)

    b = Event("created", "/dev/null", False)
    c = Event("modified", "/etc/hosts", False)
    a.process(b)
    a.process(b)
    a.process(b)
    a.on_created(b)
    a.on_modified(c)
