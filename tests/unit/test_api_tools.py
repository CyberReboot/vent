from vent.api.tools import Tools


def test_configure():
    """ Test the configure function """
    tools = Tools()
    tools.configure('foo')


def test_new():
    """ Test the new function """
    tools = Tools()
    tools.new('image', 'redis')
    tools.new('core', '')
    tools.new('repo', 'https://github.com/cyberreboot/poseidon')
