from vent.api.plugins import Plugin

def test_add():
    """ Test the add function """
    instance = Plugin(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/')
    status = instance.add('https://github.com/cyberreboot/vent', build=False)
    assert status[0] == True
    status = instance.add('https://github.com/cyberreboot/vent.git', build=True)
    assert status[0] == True
    bad_instance = Plugin()
    status = bad_instance.add('https://github.com/cyberreboot/vent', build=False)
    assert status[0] == False
    bad_instance = Plugin(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/')
    status = bad_instance.add('https://github.com/cyberreboot/vent', build=False, user='foo', pw='bar')
    assert status[0] == False

def test_build_tools():
    """ Test the build_tools function """
    instance = Plugin(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/')
    status = instance.build_tools(0)
    assert status[0] == False
    status = instance.build_tools(128)
    assert status[0] == False
    status = instance.build_tools(255)
    assert status[0] == False
    status = instance.build_tools(-1)
    assert status[0] == False

def test_get_tool_matches():
    """ Test the get_tool_matches function """
    instance = Plugin(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/')
    instance.tools = []
    matches = instance.get_tool_matches()
    assert matches == []

def test_add_image():
    """ Test the add_image function """
    Plugin.add_image('foo')

def test_remove():
    """ Test the remove function """
    instance = Plugin(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/')
    status = instance.remove()
    assert status[0] == True

def test_tools():
    """ Test the tools function """
    instance = Plugin(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/')
    tools = instance.tools()
    assert tools == []


