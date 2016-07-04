import pytest

from .. import menu_launcher

def test_update_images():
    menu_launcher.update_images()

def test_get_mode_config():
    menu_launcher.get_mode_config()

def test_get_core_config():
    menu_launcher.get_core_config()

def test_get_installed_cores():
    menu_launcher.get_installed_cores()

def test_get_installed_collectors():
    menu_launcher.get_installed_collectors("all")
    menu_launcher.get_installed_collectors("passive")
    menu_launcher.get_installed_collectors("active")

def test_get_installed_vis():
    menu_launcher.get_installed_vis()

def test_get_installed_plugins():
    menu_launcher.get_installed_plugins()

def test_get_all_installed():
    menu_launcher.get_all_installed()

def test_get_mode_enabled():
    mode_config = menu_launcher.get_mode_config()
    menu_launcher.get_mode_enabled(mode_config)

def test_get_core_enabled():
    core_config = menu_launcher.get_core_config()
    menu_launcher.get_core_enabled(core_config)

def test_get_enabled():
    menu_launcher.get_enabled()

def test_get_plugin_status():
    menu_launcher.get_plugin_status()
