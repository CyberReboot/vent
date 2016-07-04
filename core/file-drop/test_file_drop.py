import pytest

import file_drop

def test_file_drop_GZHandler():
    a = file_drop.GZHandler()

    class Event:
        event_type = None
        src_path = None
        is_directory = None

        def __init__(self, event_type, src_path, is_directory):
            self.event_type = event_type
            self.src_path = src_path
            self.is_directory = is_directory

    b = Event("created", "/dev/null", False)
    a.process(b)
    a.on_created(b)
