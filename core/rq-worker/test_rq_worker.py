import os
import pytest

import pcap_drop
import template_change

def test_settings():
    os.environ['REMOTE_REDIS_HOST'] = "test"
    os.environ['REMOTE_REDIS_PORT'] = "test"
    import settings

def test_pcap_queue():
    pcap_drop.pcap_queue("/dev/null")

def test_template_queue():
    template_change.template_queue("/dev/null")
