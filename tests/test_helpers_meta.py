from vent.helpers.meta import Version

def test_version():
    """ Test the version function """
    version = Version()
    assert version != ''
