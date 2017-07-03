from vent.api.menu_helpers import MenuHelper


def test_repo_tools():
    """ Test the repo_tools function """
    instance = MenuHelper()
    status = instance.repo_tools('https://github.com/cyberreboot/vent', 'master', 'HEAD')
    assert isinstance(status, tuple)
    assert status[0] == False
