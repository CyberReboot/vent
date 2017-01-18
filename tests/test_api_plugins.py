from vent.api.plugins import Plugin

def test_add():
    """ Test the add function """
    instance = Plugin()
    status = instance.add('https://github.com/cyberreboot/vent')
    assert status[0] == True

def test_build_tools():
    """ Test the build_tools function """
    instance = Plugin()
    status = instance.build_tools(0)
    assert status[0] == True
    status = instance.build_tools(128)
    assert status[0] == True
    status = instance.build_tools(255)
    assert status[0] == False
    status = instance.build_tools(-1)
    assert status[0] == False
