from vent.api.menu_helpers import MenuHelper
from vent.api.plugins import Plugin


def test_cores():
    """ Test the cores function """
    instance = MenuHelper()
    cores = instance.cores('install')
    assert cores[0] == True
    cores = instance.cores('build')
    assert cores[0] == True
    cores = instance.cores('start')
    assert cores[0] == True
    cores = instance.cores('stop')
    assert cores[0] == True
    cores = instance.cores('clean')
    assert cores[0] == True

def test_repo_branches():
    """ Test the repo_branches function """
    instance = MenuHelper()
    status = instance.repo_branches('https://github.com/cyberreboot/vent')
    assert isinstance(status, tuple)
    assert status[0] == True

def test_repo_commits():
    """ Test the repo_commits function """
    instance = Plugin()
    status = instance.add('https://github.com/cyberreboot/vent', build=False)
    assert isinstance(status, tuple)
    assert status[0] == True
    instance = MenuHelper()
    status = instance.repo_commits('https://github.com/cyberreboot/vent')
    assert isinstance(status, tuple)
    assert status[0] == True

def test_repo_tools():
    """ Test the repo_tools function """
    instance = MenuHelper()
    status = instance.repo_tools('https://github.com/cyberreboot/vent',
                                 'master', 'HEAD')
    assert isinstance(status, tuple)
    assert status[0] == True

def test_tools_status():
    """ Test the tools_status function """
    instance = MenuHelper()
    core = instance.tools_status(True)
    assert isinstance(core, tuple)
    plugins = instance.tools_status(False)
    assert isinstance(plugins, tuple)
