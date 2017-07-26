import os
import watch

from vent.helpers.paths import PathDirs


def test_settings():
    """ Tests settings """
    os.environ['REMOTE_REDIS_HOST'] = "localhost"
    os.environ['REMOTE_REDIS_PORT'] = "6379"
    import settings


def test_file_queue():
    """ Tests simulation of new file """
    path_dirs = PathDirs()
    images = watch.file_queue('/tmp/foo')
    assert not images[0]
    images = watch.file_queue('host_/tmp/foo',
                              template_path=path_dirs.base_dir)
    assert isinstance(images, tuple)
    assert images[0]
    assert isinstance(images[1], list)
