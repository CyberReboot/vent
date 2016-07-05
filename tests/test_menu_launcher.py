import os
import pytest

from .. import menu_launcher

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

class InvalidDirs:
    """ Testing class for invalid directories """
    def __init__(self,
                 base_dir=os.getcwd()+"/",
                 collectors_dir="collectorsinvalid",
                 core_dir="coreinvalid",
                 plugins_dir="pluginsinvalid/",
                 plugin_repos="plugin_reposinvalid",
                 template_dir="templatesinvalid/",
                 vis_dir="visualizationinvalid"):
        self.base_dir = base_dir
        self.collectors_dir = base_dir + collectors_dir
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        self.template_dir = base_dir + template_dir
        self.vis_dir = base_dir + vis_dir

def test_pathdirs():
    path_dirs = menu_launcher.PathDirs()

def test_update_images():
    path_dirs = PathDirs()
    menu_launcher.update_images(path_dirs)

def test_get_mode_config():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_config(invalid_dirs)

def test_get_core_config():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.get_core_config(path_dirs)
    menu_launcher.get_core_config(invalid_dirs)

def test_get_installed_cores():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.get_installed_cores(path_dirs)
    menu_launcher.get_installed_cores(invalid_dirs)

def test_get_installed_collectors():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.get_installed_collectors(path_dirs, "all")
    menu_launcher.get_installed_collectors(path_dirs, "passive")
    menu_launcher.get_installed_collectors(path_dirs, "active")
    menu_launcher.get_installed_collectors(invalid_dirs, "all")
    menu_launcher.get_installed_collectors(invalid_dirs, "passive")
    menu_launcher.get_installed_collectors(invalid_dirs, "active")

def test_get_installed_vis():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.get_installed_vis(path_dirs)
    menu_launcher.get_installed_vis(invalid_dirs)

def test_get_installed_plugins():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.get_installed_plugins(path_dirs)
    menu_launcher.get_installed_plugins(invalid_dirs)

def test_get_all_installed():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.get_all_installed(path_dirs)
    menu_launcher.get_all_installed(invalid_dirs)

def test_get_mode_enabled():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)
    empty_config = menu_launcher.get_mode_config(invalid_dirs)
    menu_launcher.get_mode_enabled(invalid_dirs, empty_config)

def test_get_core_enabled():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    core_config = menu_launcher.get_core_config(path_dirs)
    menu_launcher.get_core_enabled(path_dirs, core_config)
    empty_config = menu_launcher.get_core_config(invalid_dirs)
    menu_launcher.get_core_enabled(invalid_dirs, empty_config)

def test_get_enabled():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.get_enabled(path_dirs)
    menu_launcher.get_enabled(invalid_dirs)

def test_get_plugin_status():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.get_plugin_status(path_dirs)
    menu_launcher.get_plugin_status(invalid_dirs)

def test_run_plugins():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.run_plugins(path_dirs, "start")
    menu_launcher.run_plugins(invalid_dirs, "start")

def test_get_installed_plugin_repos():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.get_installed_plugin_repos(path_dirs, "INFO", "remove")
    menu_launcher.get_installed_plugin_repos(path_dirs, "INFO", "update")
    menu_launcher.get_installed_plugin_repos(path_dirs, "INFO", "")
    menu_launcher.get_installed_plugin_repos(invalid_dirs, "INFO", "remove")
    menu_launcher.get_installed_plugin_repos(invalid_dirs, "INFO", "update")
    menu_launcher.get_installed_plugin_repos(invalid_dirs, "INFO", "")

def test_update_plugins():
    path_dirs = PathDirs()
    invalid_dirs = InvalidDirs()
    menu_launcher.update_plugins(path_dirs)
    menu_launcher.update_plugins(invalid_dirs)

def test_build_menu_dict():
    path_dirs = PathDirs()
    menu_launcher.build_menu_dict(path_dirs)
