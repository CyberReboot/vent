import errno
import os
import shlex
import subprocess

from helpers.paths import PathDirs

class Plugin:
    """ Handle Plugins """
    def __init__(self, **kargs):
        self.path_dirs = PathDirs(**kargs)

    def add(self, repo, tools=[], overrides=[], version=None, branch="master"):
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
    def add_image(image, tag="latest"):
        """
        Add an image from a registry/hub rather than building from a
        repository
        """
        return

    @staticmethod
    def remove(tool=None, repo=None, branch="master"):
        """ Remove tool or repository """
        return

    @staticmethod
    def versions(tool, branch="master"):
        """ Get available versions (built) of a tool """
        return

    @staticmethod
    def version(tool, branch="master"):
        """ Return active version for a given tool """
        return

    @staticmethod
    def state(tool, branch="master"):
        """ Return state of a tool, disabled/enabled """
        return

    @staticmethod
    def checkout(tool, version, branch="master"):
        """ Checkout and build a specific version of a tool """
        return

    @staticmethod
    def enable(tool, version="head", branch="master"):
        """ Enable tool at a specific version, default to head """
        return

    @staticmethod
    def disable(tool, version="head", branch="master"):
        """ Disable tool at a specific version, default to head """
        return
