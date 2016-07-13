import ConfigParser
import os
import pexpect
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
    os.system("cp modes.backup templates/modes.template")

    path_dirs = PathDirs()
    invalid_dirs = PathDirs(base_dir="/tmp/")
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)
    empty_config = menu_launcher.get_mode_config(invalid_dirs)
    menu_launcher.get_mode_enabled(invalid_dirs, empty_config)

    # Set modes.template to have an option = "none"
    env = test_env.TestEnv()
    new_conf = {'modes.template': [('plugins', 'core', 'none')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have an option with a value not "all"/"none"
    new_conf = {'modes.template': [('plugins', 'core', 'rmq-es-connector')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have collectors = "all"
    new_conf = {'modes.template': [('plugins', 'collectors', 'all')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have collectors = "none"
    new_conf = {'modes.template': [('plugins', 'collectors', 'none')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have collectors = not "all"/"none"
    new_conf = {'modes.template': [('plugins', 'collectors', 'active-dns')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have visualization = "none"
    new_conf = {'modes.template': [('plugins', 'visualization', 'none')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have visualization = not "all"/"none"
    new_conf = {'modes.template': [('plugins', 'visualization', 'test')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have zzz = "none"
    new_conf = {'modes.template': [('plugins', 'zzz', 'none')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have zzz = not "all"/none"
    new_conf = {'modes.template': [('plugins', 'zzz', 'test')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have a section it didn't have
    new_conf = {'modes.template': [('foo', 'zzz', 'test')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Delete template and call get_mode_config
    os.system("rm "+path_dirs.template_dir+'modes.template')
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Create template without 'core' section
    os.system("touch "+path_dirs.template_dir+'modes.template')
    new_conf = {'modes.template': [('foo', 'zzz', 'test')]}
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

    # Cleanup
    os.system("cp modes.backup templates/modes.template")



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

    env = test_env.TestEnv()
    # Set core.template to have passive = on
    new_conf = {'core.template': [('local-collection', 'passive', 'on')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)
    # Set core.template to have active = on
    new_conf = {'core.template': [('local-collection', 'active', 'on')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = menu_launcher.get_mode_config(path_dirs)
    menu_launcher.get_mode_enabled(path_dirs, mode_config)

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
    # Prep
    os.system("cp modes.backup templates/modes.template")
    os.system("cp core.backup templates/core.template")

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
    if not os.path.exists(path_dirs.vis_dir+vis_test):
        os.system("mkdir "+path_dirs.vis_dir+vis_test)

    menu_launcher.run_plugins(path_dirs, "start")

    # Cleanup
    os.system("rm -rf "+path_dirs.vis_dir+vis_test)
    os.system("cp modes.backup templates/modes.template")

    ### Collectors: Passive/Active Test ###
    # Find core.template
    os.system("touch "+path_dirs.template_dir+'core.template')
    config = ConfigParser.RawConfigParser()
    config.read(path_dirs.template_dir+'core.template')

    # Check for valid sections/options
    config.set("local-collection", "passive", "on")
    config.set("local-collection", "active", "on")

    with open(path_dirs.template_dir+'core.template', 'w') as f:
        config.write(f)

    # Test with one passive/active collector.
    active = "/active-test-collector"
    passive = "/passive-test-collector"

    if not os.path.exists(path_dirs.collectors_dir+active):
        os.system("mkdir "+path_dirs.collectors_dir+active)
    if not os.path.exists(path_dirs.collectors_dir+passive):
        os.system("mkdir "+path_dirs.collectors_dir+passive)

    # Cleanup
    os.system("rm -rf "+path_dirs.collectors_dir+active)
    os.system("rm -rf "+path_dirs.collectors_dir+active)
    os.system("cp core.backup templates/core.template")

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
    child.sendline('1')
    child.expect('Return to Vent menu')
    # go to start
    child.sendline('1')
    child.expect('Return to Mode menu')
    # return to mode
    child.sendline('2')
    child.expect('Return to Vent menu')
    # go to stop
    child.sendline('2')
    child.expect('Return to Mode menu')
    # return to mode
    child.sendline('2')
    child.expect('Return to Vent menu')
    # go to clean
    child.sendline('3')
    child.expect('Return to Mode menu')
    # return to mode
    child.sendline('2')
    child.expect('Return to Vent menu')
    # go to status
    child.sendline('4')
    child.expect('Return to Mode menu')
    # return to mode
    child.sendline('8')
    child.expect('Return to Vent menu')
    # go to configure
    child.sendline('5')
    child.expect('Return to Mode menu')
    # return to mode
    child.sendline('3')
    child.expect('Return to Vent menu')
    # return to main menu
    child.sendline('6')
    child.expect('Exit')
    # !! TODO need to pull out hardcoded paths for this to work
    # go to system info
    #child.sendline('3')
    #child.expect('Return to Vent menu')
    # return to main menu
    #child.sendline('9')
    #child.expect('Exit')
    # exit
    child.sendline('7')
    child.read()
    # TODO finish going through menu actions
