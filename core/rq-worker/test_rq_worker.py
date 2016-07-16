import os
import pytest
import subprocess
import time

import file_watch

def test_settings():
    """ Tests settings """
    os.environ['REMOTE_REDIS_HOST'] = "test"
    os.environ['REMOTE_REDIS_PORT'] = "test"
    import settings

def test_pcap_queue():
    """ Tests simulation of new pcap """
    os.system('docker run -d alpine:latest /bin/sh -c "echo hello world;"')
    os.system('docker run -d alpine:latest /bin/sh -c "echo hello world;"')
    os.system('docker run -d alpine:latest /bin/sh -c "echo hello world;"')
    time.sleep(5)
    file_watch.pcap_queue("/tmp")
    file_watch.pcap_queue("/dev/null")
    file_watch.pcap_queue("/dev/null", base_dir=os.cwd()+"/")


def test_template_queue():
    """ Tests simulation of new/modified template """
    os.environ['HOSTNAME'] = "test"
    os.system('docker run -d alpine:latest /bin/sh -c "echo hello world;"')
    os.system('docker run --name core-template-queue1 -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"')
    os.system('docker run --name active-template-queue1 -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"')
    os.system('docker run --name passive-template-queue1 -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"')
    os.system('docker run --name visualization-template-queue1 -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"')
    file_watch.template_queue("/dev/null")
    file_watch.template_queue("/modes.template")
    file_watch.template_queue("/core.template")
    file_watch.template_queue("/collectors.template")
    file_watch.template_queue("/visualization.template")

    os.environ['HOSTNAME'] = subprocess.check_output('docker run --name core-template-queue2 -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"', shell=True)[:4]
    file_watch.template_queue("/core.template")
    os.environ['HOSTNAME'] = subprocess.check_output('docker run --name active-template-queue2 -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"', shell=True)[:4]
    file_watch.template_queue("/collectors.template")
    os.environ['HOSTNAME'] = subprocess.check_output('docker run --name passive-template-queue2 -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"', shell=True)[:4]
    file_watch.template_queue("/collectors.template")
    os.environ['HOSTNAME'] = subprocess.check_output('docker run --name visualization-template-queue2 -d alpine:latest /bin/sh -c "while true; do echo hello world; sleep 1; done"', shell=True)[:4]
    file_watch.template_queue("/visualization.template")

    file_watch.template_queue("/modes.template", base_dir=os.getcwd()+"/")
    file_watch.template_queue("/core.template", base_dir=os.getcwd()+"/")
    file_watch.template_queue("/collectors.template", base_dir=os.getcwd()+"/")
    file_watch.template_queue("/visualization.template", base_dir=os.getcwd()+"/")
