import os
import pytest

from .. import plugin_parser

class PathDirs:
    def __init__(self,
                 base_dir="../",
                 collectors_dir="collectors",
                 core_dir="core",
                 plugins_dir="plugins/",
                 plugin_repos="plugin_repos",
                 template_dir="templates/",
                 vis_dir="visualization"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.collectors_dir = base_dir + collectors_dir
        if not os.path.exists(self.collectors_dir):
            os.makedirs(self.collectors_dir)
        self.core_dir = base_dir + core_dir
        if not os.path.exists(self.core_dir):
            os.makedirs(self.core_dir)
        self.plugins_dir = base_dir + plugins_dir
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
        self.plugin_repos = base_dir + plugin_repos
        if not os.path.exists(self.plugin_repos):
            os.makedirs(self.plugin_repos)
        self.template_dir = base_dir + template_dir
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        self.vis_dir = base_dir + vis_dir
        if not os.path.exists(self.vis_dir):
            os.makedirs(self.vis_dir)

def test_add_plugins():
    path_dirs = PathDirs()
    plugin_parser.add_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")

def test_remove_plugins():
    path_dirs = PathDirs()
    plugin_parser.remove_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
