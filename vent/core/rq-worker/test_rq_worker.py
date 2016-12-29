import os
import pytest
import subprocess
import time

from tests import test_env
import file_watch

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

    # Test with installed plugins
    url = "https://github.com/CyberReboot/vent-plugins.git"
    env = test_env.TestEnv()
    path_dirs = test_env.PathDirs()
    env.add_plugin(path_dirs, url)
    file_watch.file_queue("vent_/dev/null", base_dir=os.getcwd()+"/")
    env.remove_plugin(path_dirs, url)

def test_template_queue():
    """ Tests simulation of new/modified template """
    path_dirs = test_env.PathDirs()
    os.environ['HOSTNAME'] = "test"
    os.system('docker run -d alpine:3.5 /bin/sh -c "echo core hello world;"')
    os.system('docker run --name core-template-queue1 -d alpine:3.5 /bin/sh -c "while true; do echo core hello world; sleep 1; done"')
    os.system('docker run --name active-template-queue1 -d alpine:3.5 /bin/sh -c "while true; do echo core hello world; sleep 1; done"')
    os.system('docker run --name passive-template-queue1 -d alpine:3.5 /bin/sh -c "while true; do echo core hello world; sleep 1; done"')
    os.system('docker run --name visualization-template-queue1 -d alpine:3.5 /bin/sh -c "while true; do echo core hello world; sleep 1; done"')
    file_watch.template_queue("/dev/null")
    file_watch.template_queue("/modes.template")
    file_watch.template_queue("/core.template")
    file_watch.template_queue("/collectors.template")
    file_watch.template_queue("/visualization.template")

    os.environ['HOSTNAME'] = subprocess.check_output('docker run --name core-template-queue2 -d alpine:3.5 /bin/sh -c "while true; do echo core hello world; sleep 1; done"', shell=True)[:4]
    file_watch.template_queue("/core.template")
    os.environ['HOSTNAME'] = subprocess.check_output('docker run --name active-template-queue2 -d alpine:3.5 /bin/sh -c "while true; do echo core hello world; sleep 1; done"', shell=True)[:4]
    file_watch.template_queue("/collectors.template")
    os.environ['HOSTNAME'] = subprocess.check_output('docker run --name passive-template-queue2 -d alpine:3.5 /bin/sh -c "while true; do echo core hello world; sleep 1; done"', shell=True)[:4]
    file_watch.template_queue("/collectors.template")
    os.environ['HOSTNAME'] = subprocess.check_output('docker run --name visualization-template-queue2 -d alpine:3.5 /bin/sh -c "while true; do echo core hello world; sleep 1; done"', shell=True)[:4]
    file_watch.template_queue("/visualization.template")

    file_watch.template_queue("/modes.template", base_dir=path_dirs.base_dir+"/")
    file_watch.template_queue("/core.template", base_dir=path_dirs.base_dir+"/")
    file_watch.template_queue("/collectors.template", base_dir=path_dirs.base_dir+"/")
    file_watch.template_queue("/visualization.template", base_dir=path_dirs.base_dir+"/")
