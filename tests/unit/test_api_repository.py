from vent.api.repository import Repository
from vent.api.system import System


def test_add():
    """ Test the add function """
    repo = Repository(System().manifest)
    repo.add('https://github.com/cyberreboot/poseidon')


def test_update():
    """ Test the update function """
    repo = Repository(System().manifest)
    repo.update('foo')
