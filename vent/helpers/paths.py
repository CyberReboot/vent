import errno
import os

class PathDirs:
    """ Global path directories for vent """
    def __init__(self,
                 base_dir=os.path.join(os.path.expanduser("~"), ".vent/"),
                 plugins_dir="plugins/",
                 meta_dir=os.path.join(os.path.expanduser("~"), ".vent")):
        self.base_dir = base_dir
        self.plugins_dir = base_dir + plugins_dir
        self.meta_dir = meta_dir

        # make sure the paths exists, if not create them
        self.ensure_dir(self.base_dir)
        self.ensure_dir(self.plugins_dir)
        self.ensure_dir(self.meta_dir)

    def ensure_dir(self, path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(path):
                return (False, "exists")
            else:
                return (False, e)
        return (True, path)
