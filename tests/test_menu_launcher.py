import os
import pytest

from .. import menu_launcher
import test_env

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
        if not os.path.exists(self.collectors_dir):
            os.makedirs(self.collectors_dir)
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        if not os.path.exists(self.plugin_repos):
            os.makedirs(self.plugin_repos)
        self.template_dir = base_dir + template_dir
        self.vis_dir = base_dir + vis_dir
        if not os.path.exists(self.vis_dir):
            os.makedirs(self.vis_dir)

def test_pathdirs():
    """ Gets path directory class from menu_launcher """
    path_dirs = menu_launcher.PathDirs()

def test_update_images():
    """ Test update_images function """
    path_dirs = PathDirs()
    menu_launcher.update_images(path_dirs)

    # Add then Remove plugin & call update_images
    url = "https://github.com/CyberReboot/vent-plugins.git"
    Env = test_env.TestEnv()
    Env.add_plugin(path_dirs, url)
    Env.remove_plugin(path_dirs, url)
    menu_launcher.update_images(path_dirs)


def test_get_mode_config():
    """ Test get_mode_config function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_config(invalid_dirs)

def test_get_core_config():
    """ Test get_core_config function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/", template_dir="foo")
    menu_launcher.get_core_config(path_dirs)
    menu_launcher.get_core_config(invalid_dirs)

def test_get_installed_cores():
    """ Test get_installed_cores function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.get_installed_cores(path_dirs)
    menu_launcher.get_installed_cores(invalid_dirs)

def test_get_installed_collectors():
    """ Test get_installed_collectors function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.get_installed_collectors(path_dirs, "all")
    menu_launcher.get_installed_collectors(path_dirs, "passive")
    menu_launcher.get_installed_collectors(path_dirs, "active")
    menu_launcher.get_installed_collectors(invalid_dirs, "all")
    menu_launcher.get_installed_collectors(invalid_dirs, "passive")
    menu_launcher.get_installed_collectors(invalid_dirs, "active")
    menu_launcher.get_installed_collectors(path_dirs, "invalidtype")

def test_get_installed_vis():
    """ Test get_installed_vis function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.get_installed_vis(path_dirs)
    menu_launcher.get_installed_vis(invalid_dirs)

def test_get_installed_plugins():
    """ Test get_installed_plugins function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.get_installed_plugins(path_dirs)
    menu_launcher.get_installed_plugins(invalid_dirs)

def test_get_all_installed():
    """ Test get_all_installed function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.get_all_installed(path_dirs)
    menu_launcher.get_all_installed(invalid_dirs)

def test_get_mode_enabled():
    """ Test get_mode_enabled function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)
    empty_config = menu_launcher.get_mode_config(invalid_dirs)
    menu_launcher.get_mode_enabled(invalid_dirs, empty_config)

def test_get_core_enabled():
    """ Test get_core_enabled function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    core_config = menu_launcher.get_core_config(path_dirs)
    menu_launcher.get_core_enabled(path_dirs, core_config)
    empty_config = menu_launcher.get_core_config(invalid_dirs)
    menu_launcher.get_core_enabled(invalid_dirs, empty_config)

def test_get_enabled():
    """ Test get_enabled function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.get_enabled(path_dirs)
    menu_launcher.get_enabled(invalid_dirs)

def test_get_plugin_status():
    """ Test get_plugin_status function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.get_plugin_status(path_dirs)
    menu_launcher.get_plugin_status(invalid_dirs)

def test_run_plugins():
    """ Test get_run_plugins function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.run_plugins(path_dirs, "start")
    menu_launcher.run_plugins(invalid_dirs, "start")

def test_get_installed_plugin_repos():
    """ Test get_installed_plugin_repos function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.get_installed_plugin_repos(path_dirs, "INFO", "remove")
    menu_launcher.get_installed_plugin_repos(path_dirs, "INFO", "update")
    menu_launcher.get_installed_plugin_repos(path_dirs, "INFO", "")
    menu_launcher.get_installed_plugin_repos(invalid_dirs, "INFO", "remove")
    menu_launcher.get_installed_plugin_repos(invalid_dirs, "INFO", "update")
    menu_launcher.get_installed_plugin_repos(invalid_dirs, "INFO", "")

def test_update_plugins():
    """ Test update_plugins function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    menu_launcher.update_plugins(path_dirs)
    menu_launcher.update_plugins(invalid_dirs)

def test_build_menu_dict():
    """ Test build_menu_dict """
    path_dirs = PathDirs()
    menu_launcher.build_menu_dict(path_dirs)
