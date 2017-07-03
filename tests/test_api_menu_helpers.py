from vent.api.menu_helpers import MenuHelper


def test_repo_branches():
    """ Test the repo_branches function """
    instance = MenuHelper()
    status = instance.repo_branches('https://github.com/cyberreboot/vent')
    assert isinstance(status, tuple)
    assert status[0] == False

def test_repo_commits():
    """ Test the repo_commits function """
    instance = MenuHelper()
    status = instance.repo_commits('https://github.com/cyberreboot/vent')
    assert isinstance(status, tuple)
    assert status[0] == False

def test_repo_tools():
    """ Test the repo_tools function """
    instance = MenuHelper()
    status = instance.repo_tools('https://github.com/cyberreboot/vent',
                                 'master', 'HEAD')
    assert isinstance(status, tuple)
    assert status[0] == False
