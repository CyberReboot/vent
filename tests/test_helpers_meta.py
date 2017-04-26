from vent.helpers.meta import Docker
from vent.helpers.meta import System
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
