from vent.helpers.meta import Containers
from vent.helpers.meta import Docker
from vent.helpers.meta import Images
from vent.helpers.meta import System
from vent.helpers.meta import Tools
from vent.helpers.meta import Version

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
    assert type(docker) == dict
    assert type(docker['server']) == dict

def test_containers():
    """ Test the containers function """
    containers = Containers()
    assert type(containers) == list

def test_images():
    """ Test the images function """
    images = Images()
    assert type(images) == list

def test_tools():
    """ Test the tools function """
    tools = Tools()
    assert type(tools) == list
