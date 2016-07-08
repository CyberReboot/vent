import os
import pytest

import file_watch

def test_settings():
    """ Tests settings """
    os.environ['REMOTE_REDIS_HOST'] = "test"
    os.environ['REMOTE_REDIS_PORT'] = "test"
    import settings

def test_pcap_queue():
    """ Tests simulation of new pcap """
    file_watch.pcap_queue("/tmp")
    file_watch.pcap_queue("/dev/null")


def test_template_queue():
    """ Tests simulation of new/modified template """
    os.system('docker run -d alpine:latest /bin/sh -c "echo hello world;"')
    os.system('docker run --name core -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"')
    os.system('docker run --name active -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"')
    os.system('docker run --name passive -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"')
    os.system('docker run --name visualization -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"')
    file_watch.template_queue("/dev/null")
    file_watch.template_queue("/modes.template")
    file_watch.template_queue("/core.template")
    file_watch.template_queue("/collectors.template")
    file_watch.template_queue("/visualization.template")
