import subprocess

from helpers.paths import PathDirs

class Plugin:
    """ Handle Plugins """
    def __init__(self, **kargs):
        self.path_dirs = PathDirs(**kargs)

    def add(self, repo, tools=[], overrides=[], version=None):
        """ Adds a plugin of tool(s) """
        status = subprocess.call("cd "+self.path_dirs.plugins_dir+" && git clone "+repo, shell=True)
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
