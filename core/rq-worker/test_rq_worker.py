import os
import pytest

import pcap_drop

def test_settings():
    os.environ['REMOTE_REDIS_HOST'] = "test"
    os.environ['REMOTE_REDIS_PORT'] = "test"
    import settings

def test_pcap_queue():
    pcap_drop.pcap_queue("/dev/null")
