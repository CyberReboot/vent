import os
import pytest

from vent import plugin_parser

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
    """ Test with valid dirs, invalid dirs, empty dirs, non-extistent plugins, duplicate plugins """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    invalid2_dirs = PathDirs(plugin_repos="core/")
    plugin_parser.add_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.add_plugins(invalid_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.add_plugins(path_dirs, "test")
    plugin_parser.add_plugins(path_dirs, "")
    plugin_parser.add_plugins(invalid2_dirs, "https://github.com/template-change")
    plugin_parser.add_plugins(path_dirs, "https://github.com/Joecakes4u/test_template_file_ignore")

def test_remove_plugins():
    """ Remove plugins with valid dirs, invalid dirs """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    plugin_parser.remove_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.remove_plugins(invalid_dirs, "vent-plugins")
    plugin_parser.remove_plugins(path_dirs, "https://github.com/Joecakes4u/test_template_file_ignore")
    #removing a git repo that isn't installed
    plugin_parser.remove_plugins(path_dirs, "https://github.com/Joecakes4u/test_template_file_ignore")

def test_update_images():
    """ Test update_images function """
    path_dirs = PathDirs()
    plugin_parser.update_images(path_dirs)

    # Add then Remove plugin & call update_images
    plugin_parser.add_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.remove_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.update_images(path_dirs)

def test_entrypoint():
    """ Tests the entrypoint of plugin_parser """
    path_dirs = PathDirs()
    plugin_parser.add_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    os.system("python2.7 "+path_dirs.base_dir+"plugin_parser.py update_plugins https://github.com/CyberReboot/vent-plugins.git "+path_dirs.base_dir)
    os.system("python2.7 "+path_dirs.base_dir+"plugin_parser.py")
    os.system("python2.7 "+path_dirs.base_dir+"plugin_parser.py invalid_type https://github.com/CyberReboot/vent-plugins.git")
