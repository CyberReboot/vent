import json
import os

from .watch import file_queue
from .watch import gpu_queue
from vent.api.actions import Action
from vent.helpers.paths import PathDirs


def test_settings():
    """ Tests settings """
    os.environ['REMOTE_REDIS_HOST'] = 'localhost'
    os.environ['REMOTE_REDIS_PORT'] = '6379'
    from . import settings


def test_file_queue():
    """ Tests simulation of new file """
    path_dirs = PathDirs()
    images = file_queue('/tmp/foo')
    assert not images[0]
    images = file_queue('host_/tmp/foo',
                        template_path=path_dirs.base_dir,
                        r_host='localhost')
    assert isinstance(images, tuple)
    assert images[0]
    assert isinstance(images[1], list)
    instance = Action()
    status = instance.add('https://github.com/cyberreboot/vent-plugins',
                          branch='master',
                          tools=[('gpu_example', '')],
                          build=True)
    assert isinstance(status, tuple)
    assert status[0]
    images = file_queue('host_/tmp/foo.matrix',
                        template_path=path_dirs.base_dir,
                        r_host='localhost')
    assert isinstance(images, tuple)
    assert images[0]
    assert isinstance(images[1], list)


def test_gpu_queue():
    """ Tests simulation of gpu job """
    options = json.dumps({'configs': {'devices': ['foo0', 'bar', 'baz3'], 'gpu_options': {
                         'device': '0'}}, 'labels': {}, 'image': 'alpine:latest'})
    status = gpu_queue(options)
    assert isinstance(status, tuple)
