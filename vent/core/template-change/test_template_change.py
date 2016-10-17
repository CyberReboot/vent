import pytest

import template_change

def test_template_change_GZHandler():
    """ Simulates a template change """
    handler = template_change.GZHandler()

    class Event:
        """ Simple event class """
        event_type = None
        src_path = None
        is_directory = None

        def __init__(self, event_type, src_path, is_directory):
            self.event_type = event_type
            self.src_path = src_path
            self.is_directory = is_directory

    created = Event("created", "/dev/null", False)
    deleted = Event("deleted", "/dev/null", False)
    modified = Event("modified", "/dev/null", False)

    # Testing for paths ending with .template
    created_template = Event("created", "/tmp/file.template", False)
    deleted_template = Event("deleted", "/tmp/file.template", False)
    modified_template = Event("modified", "/tmp/file.template", False)

    handler.process(created)
    handler.on_created(created)
    handler.on_deleted(deleted)
    handler.on_modified(modified)
    handler.on_created(created_template)
    handler.on_deleted(deleted_template)
    handler.on_modified(modified_template)
