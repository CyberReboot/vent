import file_watch
import os
import pytest
import time

def test_settings():
    """ Tests settings """
    os.environ['REMOTE_REDIS_HOST'] = "localhost"
    os.environ['REMOTE_REDIS_PORT'] = "6379"
    import settings

def test_file_queue():
    """ Tests simulation of new file """
    pass
