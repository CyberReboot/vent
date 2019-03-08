from vent.api.image import Image
from vent.api.system import System


def test_update():
    """ Test the update class """
    image = Image(System().manifest)
    image.update('foo')
