import os
import pytest

import file_drop

def test_first_setup():
    os.system("cp templates/core.template core.backup")
    os.system("cp templates/modes.template modes.backup")

def test_file_drop_GZHandler():
    """ Tests the GZZHandler for file drop """
    a = file_drop.GZHandler()

    class Event:
        """ Creates a mock event object for tests """
        event_type = None
        src_path = None
        is_directory = None

        def __init__(self, event_type, src_path, is_directory):
            """ initializes necessary variables for the object """
            self.event_type = event_type
            self.src_path = src_path
            self.is_directory = is_directory

    b = Event("created", "/dev/null", False)
    a.process(b, "localhost")
    a.on_created(b)
