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
    """ Test path directories """
    path_dirs = plugin_parser.PathDirs()

def test_add_plugins():
    """ Test with valid dirs, invalid dirs, emtpy dirs, non-extistent plugins, duplicate plugins """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    invalid2_dirs = PathDirs(plugin_repos="core/")
    plugin_parser.add_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.add_plugins(invalid_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.add_plugins(path_dirs, "test")
    plugin_parser.add_plugins(path_dirs, "")
    plugin_parser.add_plugins(invalid2_dirs, "https://github.com/template-change")

def test_remove_plugins():
    """ Remove with valid dirs, invalid dirs """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    plugin_parser.remove_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.remove_plugins(invalid_dirs, "vent-plugins")
