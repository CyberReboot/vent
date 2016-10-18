import os
import pytest

from scripts.info_tools import get_status
import test_env

def test_get_mode_config():
    """ Test get_mode_config function with valid and invalid directories """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(template_dir="/tmp/foo")
    get_status.get_mode_config(path_dirs)
    get_status.get_mode_config(invalid_dirs)

    # Mode_Config after init
    env = test_env.TestEnv()
    env.initconfigs(path_dirs, False)
    get_status.get_mode_config(path_dirs)

def test_get_core_config():
    """ Test get_core_config function with valid and invalid directories """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(template_dir="/tmp/foo")
    get_status.get_core_config(path_dirs)
    get_status.get_core_config(invalid_dirs)

    # Mode_Config after init
    env = test_env.TestEnv()
    env.initconfigs(path_dirs, False)
    get_status.get_core_config(path_dirs)

def test_get_installed_cores():
    """ Test get_installed_cores function with valid and invalid directories """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(core_dir="/tmp/foo")
    get_status.get_installed_cores(path_dirs)
    get_status.get_installed_cores(invalid_dirs)

def test_get_installed_collectors():
    """ Test get_installed_collectors function with valid and invalid directories """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(collectors_dir="/tmp/foo")
    get_status.get_installed_collectors(path_dirs, "all")
    get_status.get_installed_collectors(path_dirs, "passive")
    get_status.get_installed_collectors(path_dirs, "active")
    get_status.get_installed_collectors(invalid_dirs, "all")
    get_status.get_installed_collectors(invalid_dirs, "passive")
    get_status.get_installed_collectors(invalid_dirs, "active")
    get_status.get_installed_collectors(path_dirs, "foobar")

def test_get_installed_vis():
    """ Test get_installed_vis function with valid and invalid directories """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(vis_dir="/tmp/foo")
    get_status.get_installed_vis(path_dirs)
    get_status.get_installed_vis(invalid_dirs)


def test_get_installed_repos():
    """Test get_installed_repos function with valid and invalid directories"""
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(vis_dir="/tmp/foo")
    get_status.get_installed_repos(path_dirs)
    get_status.get_installed_repos(invalid_dirs)

def test_get_installed_plugins():
    """ Test get_installed_plugins function with valid and invalid directories """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(plugins_dir="/tmp/foo")
    get_status.get_installed_plugins(path_dirs)
    get_status.get_installed_plugins(invalid_dirs)

    # Test with installed plugins
    url = "https://github.com/CyberReboot/vent-plugins.git"
    env = test_env.TestEnv()
    env.add_plugin(path_dirs, url)
    env.remove_plugin(path_dirs, url)

def test_get_all_installed():
    """ Test get_all_installed function with valid and invalid directories """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(vis_dir="/tmp/doesntexist")
    get_status.get_all_installed(path_dirs)
    get_status.get_all_installed(invalid_dirs)

def test_get_mode_enabled():
    """ Test get_mode_enabled function with valid and invalid directories """
    os.system("cp modes.backup templates/modes.template")

    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(base_dir="/tmp/")
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)
    empty_config = get_status.get_mode_config(invalid_dirs)
    get_status.get_mode_enabled(invalid_dirs, empty_config)

    # Set modes.template to have an option = "none"
    env = test_env.TestEnv()
    new_conf = {'modes.template': [('plugins', 'core', 'none')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have an option with a value not "all"/"none"
    new_conf = {'modes.template': [('plugins', 'core', 'rmq-es-connector')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have collectors = "all"
    new_conf = {'modes.template': [('plugins', 'collectors', 'all')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have collectors = "none"
    new_conf = {'modes.template': [('plugins', 'collectors', 'none')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have collectors = not "all"/"none"
    new_conf = {'modes.template': [('plugins', 'collectors', 'active-dns')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have visualization = "none"
    new_conf = {'modes.template': [('plugins', 'visualization', 'none')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have visualization = not "all"/"none"
    new_conf = {'modes.template': [('plugins', 'visualization', 'test')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have zzz = "none"
    new_conf = {'modes.template': [('plugins', 'zzz', 'none')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have zzz = not "all"/none"
    new_conf = {'modes.template': [('plugins', 'zzz', 'test')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    # modes.template doesn't have the namespace for an installed plugin
    os.system("mkdir "+path_dirs.plugins_dir+"namespacetest")
    os.system("mkdir "+path_dirs.plugins_dir+"namespacetest/plugintest")
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Set modes.template to have a section it didn't have
    new_conf = {'modes.template': [('foo', 'zzz', 'test')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Delete template and call get_mode_config
    os.system("rm "+path_dirs.template_dir+'modes.template')
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)
    os.system("cp modes.backup templates/modes.template")

    # Test with config with only one defined namespace
    get_status.get_mode_enabled(path_dirs, {'core': 'all'})
    get_status.get_mode_enabled(path_dirs, {'collectors': 'all'})
    get_status.get_mode_enabled(path_dirs, {'visualization': 'all'})
    get_status.get_mode_enabled(path_dirs, mode_config)

    # Cleanup
    os.system("cp modes.backup templates/modes.template")

def test_get_core_enabled():
    """ Test get_core_enabled function with valid and invalid directories """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(base_dir="/tmp/")

    os.system("cp core.backup templates/core.template")

    filedata = None
    with open(path_dirs.template_dir + 'core.template', 'r') as f:
        filedata = f.read()
    filedata = filedata.replace('#passive', 'passive')
    filedata = filedata.replace('#active', 'active')
    with open(path_dirs.template_dir + 'core.template', 'w') as f:
        f.write(filedata)

    core_config = get_status.get_core_config(path_dirs)
    get_status.get_core_enabled(path_dirs, core_config)
    empty_config = get_status.get_core_config(invalid_dirs)
    get_status.get_core_enabled(invalid_dirs, empty_config)

    env = test_env.TestEnv()
    # Set core.template to have passive = on
    new_conf = {'core.template': [('local-collection', 'passive', 'on')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)
    # Set core.template to have active = on
    new_conf = {'core.template': [('local-collection', 'active', 'on')]}
    env.modifyconfigs(path_dirs, new_conf)
    mode_config = get_status.get_mode_config(path_dirs)
    get_status.get_mode_enabled(path_dirs, mode_config)

    os.system("cp core.backup templates/core.template")

def test_get_external():
    """ Test get_external function with valid and invalid directories """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(base_dir="/tmp/")
    get_status.get_external(path_dirs)
    get_status.get_external(invalid_dirs)

def test_get_enabled():
    """ Test get_enabled function with valid and invalid directories """
    path_dirs = test_env.PathDirs()
    invalid_dirs = test_env.PathDirs(base_dir="/tmp/")
    get_status.get_enabled(path_dirs)
    get_status.get_enabled(invalid_dirs)

    # Modify modes.template to create some disabled images
    url = "https://github.com/CyberReboot/vent-plugins.git"
    url2 = "https://github.com/Joecakes4u/test_template_file_ignore.git"
    env = test_env.TestEnv()
    env.add_plugin(path_dirs, url)
    env.add_plugin(path_dirs, url2)
    get_status.get_enabled(path_dirs)
    env.remove_plugin(path_dirs, url)
    env.remove_plugin(path_dirs, url2)

def test_arg_parse():
    """ Tests arg parse parsing of arguments """
    path_dirs = test_env.PathDirs()
    # All is a reserved python keyword
    # Setting up cmds to call get_status with
    cmds = [
        "all",
        "cconfig",
        "cenabled",
        "collectors",
        "cores",
        "enabled",
        "installed",
        "mconfig",
        "menabled",
        "plugins",
        "vis",
        "repos"
    ]

    # Test with no commands
    os.system('python2.7 '+path_dirs.info_dir+'get_status.py')

    # Test with all commands
    for cmd in cmds:
        os.system('python2.7 '+path_dirs.info_dir+'get_status.py '+cmd)
