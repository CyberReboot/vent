import file_watch
import os
import pytest
import subprocess
import time

def test_settings():
    """ Tests settings """
    os.environ['REMOTE_REDIS_HOST'] = "localhost"
    os.environ['REMOTE_REDIS_PORT'] = "6379"
    import settings

def test_file_queue():
    """ Tests simulation of new file """
    os.system('docker run -d alpine:3.5 /bin/sh -c "echo core hello world;"')
    os.system('docker run -d alpine:3.5 /bin/sh -c "echo core hello world;"')
    os.system('docker run -d alpine:3.5 /bin/sh -c "echo core hello world;"')
    time.sleep(5)
    file_watch.file_queue("/tmp")
    file_watch.file_queue("/dev/null")
    file_watch.file_queue("/dev/null", base_dir=os.getcwd()+"/")
