import errno
import os

class PathDirs:
    """ Global path directories for vent """
    def __init__(self,
                 base_dir="/var/lib/docker/data/",
                 collectors_dir="collectors",
                 core_dir="core",
                 plugins_dir="plugins/",
                 plugin_repos="plugin_repos",
                 template_dir="templates/",
                 vis_dir="visualization",
                 info_dir="info_tools/",
                 vent_dir="/vent/",
                 data_dir="/vent/",
                 vendor_dir="/vendor/",
                 meta_dir=os.path.join(os.path.expanduser("~"), ".vent"),
                 scripts_dir="/scripts/"):
        self.base_dir = base_dir
        self.collectors_dir = base_dir + collectors_dir
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        self.template_dir = base_dir + template_dir
        self.vis_dir = base_dir + vis_dir
        self.scripts_dir = scripts_dir
        self.info_dir = scripts_dir + info_dir
        self.vent_dir = vent_dir
        self.data_dir = data_dir
        self.meta_dir = meta_dir
        self.vendor_dir = vendor_dir

        # make sure the paths exists, if not create them
        self.ensure_dir(self.base_dir)
        self.ensure_dir(self.collectors_dir)
        self.ensure_dir(self.core_dir)
        self.ensure_dir(self.plugins_dir)
        self.ensure_dir(self.plugin_repos)
        self.ensure_dir(self.template_dir)
        self.ensure_dir(self.vis_dir)
        self.ensure_dir(self.scripts_dir)
        self.ensure_dir(self.info_dir)
        self.ensure_dir(self.vent_dir)
        self.ensure_dir(self.data_dir)
        self.ensure_dir(self.meta_dir)
        self.ensure_dir(self.vendor_dir)

    def ensure_dir(self, path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                return (False, e)
        return (True, path)
