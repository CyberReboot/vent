from vent.helpers.paths import PathDirs

def test_pathdirs():
    """ Test the pathdirs class """
    path = PathDirs()
    path.host_config()

def test_ensure_file():
    """ Test the ensure_file function """
    paths = PathDirs()
    status = paths.ensure_file(paths.init_file)
    assert type(status) == tuple
    assert status[0] == True
