import pytest

import template_change

def test_template_change_GZHandler():
    a = template_change.GZHandler()

    class Event:
        event_type = None
        src_path = None
        is_directory = None

        def __init__(self, event_type, src_path, is_directory):
            self.event_type = event_type
            self.src_path = src_path
            self.is_directory = is_directory

    b = Event("created", "/dev/null", False)
    c = Event("deleted", "/dev/null", False)
    d = Event("modified", "/dev/null", False)
    a.process(b)
    a.on_created(b)
    a.on_deleted(c)
    a.on_modified(d)
