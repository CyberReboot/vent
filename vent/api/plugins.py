import errno
import os
import shlex
import subprocess

from helpers.paths import PathDirs

class Plugin:
    """ Handle Plugins """
    def __init__(self, **kargs):
        self.path_dirs = PathDirs(**kargs)

    def add(self, repo, tools=[], overrides=[], version=None):
        """ Adds a plugin of tool(s) """
        org = None
        name = None
        if repo.endswith(".git"):
            repo = repo.split(".git")[0]
        org, name = repo.split("/")[-2:]
        path = self.path_dirs.plugins_dir + '/' + org + '/' + name
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                return ('failed', e)

        os.chdir(path)
        status = subprocess.call(shlex.split("git clone " + repo + " ."))
        if status == 0:
            # TODO check tools, overrides, and version
            # TODO create a manifest file of which tools are enabled/disabled at which versions, and are built or not.
            pass
        else:
            return ('failed', status)

    @staticmethod
    def add_image(image):
        return

    @ staticmethod
    def remove():
        return
