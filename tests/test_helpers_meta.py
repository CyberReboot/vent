import docker
import os

from vent.helpers.meta import Containers
from vent.helpers.meta import Cpu
from vent.helpers.meta import Docker
from vent.helpers.meta import Gpu
from vent.helpers.meta import Images
from vent.helpers.meta import Jobs
from vent.helpers.meta import Services
from vent.helpers.meta import System
from vent.helpers.meta import Timestamp
from vent.helpers.meta import Tools
from vent.helpers.meta import Uptime
from vent.helpers.meta import Version

def test_run_containers():
    """ Run some containers for testing purposes """
    d_client = docker.from_env()
    d_client.containers.run("alpine:latest", "tail -f /etc/passwd", detach=True, labels=["vent", "vent-plugins"])

def test_version():
    """ Test the version function """
    version = Version()
    assert version != ''

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
    assert isinstance(gpu, str)
    gpu = Gpu(pull=True)

def test_jobs():
    """ Test the jobs function """
    jobs = Jobs()
    assert isinstance(jobs, tuple)
