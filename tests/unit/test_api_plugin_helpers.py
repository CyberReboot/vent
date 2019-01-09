from vent.api.plugin_helpers import PluginHelper


def test_get_path():
    """ Test the get_path function """
    instance = PluginHelper()
    path, _, _ = instance.get_path(
        'https://github.com/cyberreboot/vent', core=True)
    assert '.internals' not in path
    path, _, _ = instance.get_path(
        'https://github.com/cyberreboot/vent-plugins')
    assert '.internals' not in path


def test_apply_path():
    """ Test the apply_path function """
    instance = PluginHelper()
    status = instance.apply_path('https://github.com/cyberreboot/vent')
    assert isinstance(status, tuple)
    assert status[0] == True
    status = instance.apply_path('https://github.com/cyberreboot/vent.git')
    assert isinstance(status, tuple)
    assert status[0] == True


def test_checkout():
    """ Test the checkout function """
    instance = PluginHelper()
    status = instance.checkout()
    assert isinstance(status, tuple)
    assert status[0] == True
