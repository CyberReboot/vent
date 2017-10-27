import docker
import os
import requests
import shutil

from vent.api.menu_helpers import MenuHelper
from vent.helpers.meta import Containers
from vent.helpers.meta import Cpu
from vent.helpers.meta import Docker
from vent.helpers.meta import Gpu
from vent.helpers.meta import Images
from vent.helpers.meta import Jobs
from vent.helpers.meta import ParsedSections
from vent.helpers.meta import Services
from vent.helpers.meta import System
from vent.helpers.meta import Timestamp
from vent.helpers.meta import Tools
from vent.helpers.meta import Uptime
from vent.helpers.meta import Version
from vent.helpers.paths import PathDirs

def test_run_containers():
    """ Run some containers for testing purposes """
    d_client = docker.from_env()
    d_client.containers.run("alpine:latest", "tail -f /etc/passwd", detach=True, labels=["vent", "vent-plugins"])

def test_version():
    """ Test the version function """
    version = Version()
    assert version.startswith('v')

def test_system():
    """ Test the system function """
    system = System()
    assert system != ''

def test_docker():
    """ Test the docker function """
    docker = Docker()
    assert isinstance(docker, dict)
    assert isinstance(docker['server'], dict)
    os.environ['DOCKER_MACHINE_NAME'] = 'foo'
    docker = Docker()
    assert isinstance(docker, dict)
    assert docker['type'] == 'docker-machine'
    del os.environ['DOCKER_MACHINE_NAME']
    os.environ['DOCKER_HOST'] = 'foo'
    docker = Docker()
    assert isinstance(docker, dict)
    assert docker['type'] == 'remote'
    del os.environ['DOCKER_HOST']

def test_containers():
    """ Test the containers function """
    containers = Containers()
    containers = Containers(vent=False)
    assert isinstance(containers, list)

def test_images():
    """ Test the images function """
    images = Images()
    images = Images(vent=False)
    assert isinstance(images, list)

def test_tools():
    """ Test the tools function """
    tools = Tools()
    assert isinstance(tools, list)

def test_services():
    """ Test the services function """
    services = Services(True)
    assert isinstance(services, list)
    services = Services(False)
    assert isinstance(services, list)
    services = Services(True, vent=False)
    assert isinstance(services, list)

def test_timestamp():
    """ Test the timestamp function """
    timestamp = Timestamp()
    assert isinstance(timestamp, str)

def test_uptime():
    """ Test the uptime function """
    uptime = Uptime()
    assert isinstance(uptime, str)

def test_cpu():
    """ Test the cpu function """
    cpu = Cpu()
    assert isinstance(cpu, str)

def test_gpu():
    """ Test the gpu function """
    gpu = Gpu()
    assert isinstance(gpu, tuple)
    gpu = Gpu(pull=True)
    assert isinstance(gpu, tuple)

def test_jobs():
    """ Test the jobs function """
    jobs = Jobs()
    assert isinstance(jobs, tuple)
    path = PathDirs()
    status = path.host_config()
    assert isinstance(status, tuple)
    assert status[0]
    m_helper = MenuHelper()
    status = m_helper.cores('install')
    assert isinstance(status, tuple)
    assert status[0]
    status = m_helper.cores('build')
    assert isinstance(status, tuple)
    assert status[0]
    status = m_helper.cores('start')
    assert isinstance(status, tuple)
    assert status[0]
    status = m_helper.api_action.add('https://github.com/cyberreboot/vent-plugins')
    assert isinstance(status, tuple)
    assert status[0]
    # run test job
    with open('/opt/vent_files/foo.matrix', 'w') as f:
        f.write('24,23\n10,22')
    pcap = 'https://s3.amazonaws.com/tcpreplay-pcap-files/test.pcap'
    r = requests.get(pcap, stream=True)

    if r.status_code == 200:
        with open('/opt/vent_files/foo.pcap', 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    services = Services(True)
    assert isinstance(services, list)
    jobs = Jobs()
    assert isinstance(jobs, tuple)

def test_parsed_sections():
    """ Test the ParsedSections function """
    test_val = '[docker]\nenvironment = ["TEST_VAR=5", "RANDOM_VAR=10"]\ntest = yes'
    template_dict = ParsedSections(test_val)
    assert isinstance(template_dict, dict)
    assert len(template_dict) == 1
    assert 'docker' in template_dict
    assert len(template_dict['docker']) == 2
    assert 'environment' in template_dict['docker']
    assert template_dict['docker']['environment'] == '["TEST_VAR=5", "RANDOM_VAR=10"]'
    assert 'test' in template_dict['docker']
    assert template_dict['docker']['test'] == 'yes'
