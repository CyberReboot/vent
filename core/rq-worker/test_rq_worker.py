import os
import pytest

import file_watch

def test_settings():
    os.environ['REMOTE_REDIS_HOST'] = "test"
    os.environ['REMOTE_REDIS_PORT'] = "test"
    import settings

def test_pcap_queue():
    file_watch.pcap_queue("/dev/null")

def test_template_queue():
    file_watch.template_queue("/dev/null")
