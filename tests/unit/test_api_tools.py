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
    tools.new('repo', 'https://github.com/cyberreboot/vent')


def test_inventory():
    """ Test the inventory function """
    tools = Tools()
    tools.inventory()


def test_stop():
    """ Test the stop function """
    tools = Tools()
    tools.stop('https://github.com/cyberreboot/vent', 'rabbitmq')


def test_remove():
    """ Test the remove function """
    tools = Tools()
    tools.remove('https://github.com/cyberreboot/vent', 'rabbitmq')
