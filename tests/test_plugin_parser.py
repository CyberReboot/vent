import os
import pytest

from vent import plugin_parser
from tests import test_env

def test_pathdirs():
    """ Test path directories """
    path_dirs = plugin_parser.PathDirs()

def test_add_plugins():
    """ Test with valid dirs, invalid dirs, empty dirs, non-extistent plugins, duplicate plugins """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(base_dir="/tmp/")
    invalid2_dirs = test_env.PathDirs(plugin_repos="core/")
    plugin_parser.add_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.add_plugins(invalid_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.add_plugins(path_dirs, "test")
    plugin_parser.add_plugins(path_dirs, "")
    plugin_parser.add_plugins(invalid2_dirs, "https://github.com/template-change")
    plugin_parser.add_plugins(path_dirs, "https://github.com/Joecakes4u/test_template_file_ignore")

def test_remove_plugins():
    """ Remove plugins with valid dirs, invalid dirs """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(base_dir="/tmp/")
    plugin_parser.remove_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.remove_plugins(invalid_dirs, "vent-plugins")
    plugin_parser.remove_plugins(path_dirs, "https://github.com/Joecakes4u/test_template_file_ignore")
    #removing a git repo that isn't installed
    plugin_parser.remove_plugins(path_dirs, "https://github.com/Joecakes4u/test_template_file_ignore")

def test_update_images():
    """ Test update_images function """
    path_dirs = test_env.PathDirs()
    plugin_parser.update_images(path_dirs)

    # Add then Remove plugin & call update_images
    plugin_parser.add_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    plugin_parser.update_images(path_dirs)
    plugin_parser.remove_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")

def test_private_repos():
    """ Tests the entrypoint of plugin_parser with private repo args """
    path_dirs = test_env.PathDirs()
    os.system("python2.7 "+path_dirs.base_dir+"plugin_parser.py add_plugins https://github.com/CyberReboot/vent-plugins.git user pass private "+path_dirs.base_dir+" "+path_dirs.data_dir)
    os.system("python2.7 "+path_dirs.base_dir+"plugin_parser.py update_plugins https://github.com/CyberReboot/vent-plugins.git user pass private "+path_dirs.base_dir+" "+path_dirs.data_dir)

def test_entrypoint():
    """ Tests the entrypoint of plugin_parser """
    path_dirs = test_env.PathDirs()
    plugin_parser.add_plugins(path_dirs, "https://github.com/CyberReboot/vent-plugins.git")
    os.system("python2.7 "+path_dirs.base_dir+"plugin_parser.py update_plugins https://github.com/CyberReboot/vent-plugins.git "+path_dirs.base_dir+" "+path_dirs.data_dir)
    os.system("python2.7 "+path_dirs.base_dir+"plugin_parser.py remove_plugins https://github.com/CyberReboot/vent-plugins.git "+path_dirs.base_dir+" "+path_dirs.data_dir)
    os.system("python2.7 "+path_dirs.base_dir+"plugin_parser.py")
    os.system("python2.7 "+path_dirs.base_dir+"plugin_parser.py invalid_type https://foo.git")
