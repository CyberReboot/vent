import os
import pytest

from .. import plugin_parser

class PathDirs:
    """ Global path directories for parsing templates """
    def __init__(self,
                 base_dir=os.getcwd()+"/",
                 collectors_dir="collectors",
                 core_dir="core",
                 plugins_dir="plugins/",
                 plugin_repos="plugin_repos",
                 template_dir="templates/",
                 vis_dir="visualization"):
        self.base_dir = base_dir
        self.collectors_dir = base_dir + collectors_dir
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        self.template_dir = base_dir + template_dir
        self.vis_dir = base_dir + vis_dir

def test_pathdirs():
    path_dirs = plugin_parser.PathDirs()

def test_add_plugins():
    path_dirs = PathDirs()
    plugin_parser.add_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")

def test_remove_plugins():
    path_dirs = PathDirs()
    plugin_parser.remove_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
