import file_watch
import os
import pytest
import time

from vent.helpers.paths import PathDirs

def test_settings():
    """ Tests settings """
    os.environ['REMOTE_REDIS_HOST'] = "localhost"
    os.environ['REMOTE_REDIS_PORT'] = "6379"
    import settings

def test_file_queue():
    """ Tests simulation of new file """
    path_dirs = PathDirs()
    images = file_watch.file_queue('/tmp/foo')
    assert images[0] == False
    images = file_watch.file_queue('host_/tmp/foo', template_path=path_dirs.base_dir)
    assert images[0] == True
    assert type(images[1]) == list
