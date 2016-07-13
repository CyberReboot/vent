import ConfigParser
import os
import pexpect
import pytest
import time

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
                 vis_dir="visualization",
                 info_dir="info_tools/"):
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
        self.info_dir=info_dir

def test_pathdirs():
    """ Gets path directory class from menu_launcher """
    path_dirs = menu_launcher.PathDirs()

def test_update_images():
    """ Test update_images function """
    path_dirs = PathDirs()
    menu_launcher.update_images(path_dirs)

    # Add then Remove plugin & call update_images
    url = "https://github.com/CyberReboot/vent-plugins.git"
    env = test_env.TestEnv()
    env.add_plugin(path_dirs, url)
    env.remove_plugin(path_dirs, url)
    menu_launcher.update_images(path_dirs)


def test_get_mode_config():
    """ Test get_mode_config function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(template_dir="/tmp/foo")
    menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_config(invalid_dirs)

    # Mode_Config after init
    env = test_env.TestEnv()
    env.initconfigs(path_dirs, False)
    menu_launcher.get_mode_config(path_dirs)

def test_get_core_config():
    """ Test get_core_config function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(template_dir="/tmp/foo")
    menu_launcher.get_core_config(path_dirs)
    menu_launcher.get_core_config(invalid_dirs)

    # Mode_Config after init
    env = test_env.TestEnv()
    env.initconfigs(path_dirs, False)
    menu_launcher.get_core_config(path_dirs)

def test_get_installed_cores():
    """ Test get_installed_cores function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(core_dir="/tmp/foo")
    menu_launcher.get_installed_cores(path_dirs)
    menu_launcher.get_installed_cores(invalid_dirs)

def test_get_installed_collectors():
    """ Test get_installed_collectors function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(collectors_dir="/tmp/foo")
    menu_launcher.get_installed_collectors(path_dirs, "all")
    menu_launcher.get_installed_collectors(path_dirs, "passive")
    menu_launcher.get_installed_collectors(path_dirs, "active")
    menu_launcher.get_installed_collectors(invalid_dirs, "all")
    menu_launcher.get_installed_collectors(invalid_dirs, "passive")
    menu_launcher.get_installed_collectors(invalid_dirs, "active")
    menu_launcher.get_installed_collectors(path_dirs, "foobar")

def test_get_installed_vis():
    """ Test get_installed_vis function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(vis_dir="/tmp/foo")
    menu_launcher.get_installed_vis(path_dirs)
    menu_launcher.get_installed_vis(invalid_dirs)

def test_get_installed_plugins():
    """ Test get_installed_plugins function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(plugins_dir="/tmp/foo")
    menu_launcher.get_installed_plugins(path_dirs)
    menu_launcher.get_installed_plugins(invalid_dirs)

    # Test with installed plugins
    url = "https://github.com/CyberReboot/vent-plugins.git"
    env = test_env.TestEnv()
    env.add_plugin(path_dirs, url)

def test_get_all_installed():
    """ Test get_all_installed function with valid and invalid directories """
    path_dirs = PathDirs()
    invalid_dirs = PathDirs(vis_dir="/tmp/doesntexist")
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

    os.system("cp core.backup templates/core.template")

    filedata = None
    with open(path_dirs.template_dir + 'core.template', 'r') as f:
        filedata = f.read()
    filedata = filedata.replace('#passive', 'passive')
    filedata = filedata.replace('#active', 'active')
    with open(path_dirs.template_dir + 'core.template', 'w') as f:
        f.write(filedata)

    core_config = menu_launcher.get_core_config(path_dirs)
    menu_launcher.get_core_enabled(path_dirs, core_config)
    empty_config = menu_launcher.get_core_config(invalid_dirs)
    menu_launcher.get_core_enabled(invalid_dirs, empty_config)
    os.system("cp core.backup templates/core.template")

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

    ### Visualization Test ###
    # Find modes.template
    os.system("touch "+path_dirs.template_dir+'modes.template')
    config = ConfigParser.RawConfigParser()
    config.read(path_dirs.template_dir+'modes.template')

    # Check for valid sections/options
    if not config.has_section("plugins"):
        config.add_section("plugins")
    config.set("plugins", "vis_test", "all")

    with open(path_dirs.template_dir+'modes.template', 'w') as f:
        config.write(f)

    # Test with one visualization plugin (filewalk)
    vis_test = "/vis_test"
    if not os.path.exists(path_dirs.vis_dir):
        os.system("mkdir "+path_dirs.vis_dir)
    if not os.path.exists(path_dirs.vis_dir+vis_test):
        os.system("mkdir "+path_dirs.vis_dir+vis_test)

    menu_launcher.run_plugins(path_dirs, "start")

    ### Collectors: Passive/Active Test ###
    # Find core.template
    os.system("touch "+path_dirs.template_dir+'core.template')
    config = ConfigParser.RawConfigParser()
    config.read(path_dirs.template_dir+'core.template')

    # Check for valid sections/options
    if not config.has_section("local-collection"):
        config.add_section("local-collection")
    config.set("local-collection", "passive", "on")
    config.set("local-collection", "active", "on")

    with open(path_dirs.template_dir+'core.template', 'w') as f:
        config.write(f)

    # Test with one passive/active collector.
    active = "/active-test-collector"
    passive = "/passive-test-collector"
    if not os.path.exists(path_dirs.collectors_dir):
        os.system("mkdir "+path_dirs.collectors_dir)
    if not os.path.exists(path_dirs.collectors_dir+active):
        os.system("mkdir "+path_dirs.collectors_dir+active)
    if not os.path.exists(path_dirs.collectors_dir+passive):
        os.system("mkdir "+path_dirs.collectors_dir+passive)

    menu_launcher.run_plugins(path_dirs, "start")

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

def test_get_container_menu():
    """test get_container_menu"""
    path_dirs = PathDirs()
    menu_launcher.get_container_menu(path_dirs)

def test_get_namespace_menu():
    """test get_namespace_menu"""
    path_dirs = PathDirs()
    menu_launcher.get_namespace_menu(path_dirs)

def test_running_menu():
    """ test running the actual menu """
    cmd = "python2.7 menu_launcher.py"
    child = pexpect.spawn(cmd)
    # expect main menu
    child.expect('Exit')
    # go to mode
    time.sleep(1)
    child.sendline('1')
    child.expect('Return to Vent menu')
    # go to start
    time.sleep(1)
    child.sendline('1')
    child.expect('Return to Mode menu')
    # return to mode
    time.sleep(1)
    child.sendline('2')
    child.expect('Return to Vent menu')
    # go to stop
    time.sleep(1)
    child.sendline('2')
    child.expect('Return to Mode menu')
    # return to mode
    time.sleep(1)
    child.sendline('2')
    child.expect('Return to Vent menu')
    # go to clean
    time.sleep(1)
    child.sendline('3')
    child.expect('Return to Mode menu')
    # return to mode
    time.sleep(1)
    child.sendline('2')
    child.expect('Return to Vent menu')
    # go to status
    time.sleep(1)
    child.sendline('4')
    child.expect('Return to Mode menu')
    # return to mode
    time.sleep(1)
    child.sendline('8')
    child.expect('Return to Vent menu')
    # go to configure
    time.sleep(1)
    child.sendline('5')
    child.expect('Return to Mode menu')
    # return to mode
    time.sleep(1)
    child.sendline('3')
    child.expect('Return to Vent menu')
    # return to main menu
    time.sleep(1)
    child.sendline('6')
    child.expect('Exit')
    # go to plugins menu
    time.sleep(1)
    child.sendline('2')
    child.expect('Return to Vent menu')
    # go to remove plugin
    time.sleep(1)
    child.sendline('2')
    child.expect('Return to Plugins menu')
    # go to plugins menu
    time.sleep(1)
    child.sendline('1')
    child.expect('Return to Vent menu')
    # go to install plugins
    time.sleep(1)
    child.sendline('3')
    child.expect('Return to Plugins menu')
    # go to plugins menu
    time.sleep(1)
    child.sendline('1')
    child.expect('Return to Vent menu')
    # go to update plugins
    time.sleep(1)
    child.sendline('4')
    child.expect('Return to Plugins menu')
    # go to plugins menu
    time.sleep(1)
    child.sendline('1')
    child.expect('Return to Vent menu')
    # go to main menu
    time.sleep(1)
    child.sendline('5')
    child.expect('Exit')
    # go to system commands
    time.sleep(1)
    child.sendline('5')
    child.expect('Return to Vent menu')
    # go to logs menu
    time.sleep(1)
    child.sendline('1')
    child.expect('Return to System Commands menu')
    # go to containers menu
    time.sleep(1)
    child.sendline('1')
    child.expect('Return to Logs menu')
    # return to logs menu
    time.sleep(1)
    child.sendline('2')
    child.expect('Return to System Commands menu')
    # go to namespaces menu
    time.sleep(1)
    child.sendline('2')
    child.expect('Return to Logs menu')
    # return to logs menu
    time.sleep(1)
    child.sendline('2')
    child.expect('Return to System Commands menu')
    # return to system commands menu
    time.sleep(1)
    child.sendline('5')
    child.expect('Return to Vent menu')
    # go to main menu
    time.sleep(1)
    child.sendline('5')
    child.expect('Exit')

    # !! TODO need to pull out hardcoded paths for this to work
    # go to system info
    #child.sendline('3')
    #child.expect('Return to Vent menu')
    # return to main menu
    #child.sendline('9')
    #child.expect('Exit')
    # exit
    time.sleep(1)
    child.sendline('7')
    time.sleep(1)
    child.read()
    # TODO finish going through menu actions
