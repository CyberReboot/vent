from vent.api.repository import Repository
from vent.api.system import System


def test_update():
    """ Test the update class """
    repo = Repository(System().manifest)
    repo.update('foo')
