import os

from vent.api.plugins import Plugin
from vent.api.templates import Template

def test_add():
    """ Test the add function """
    instance = Plugin()
    status = instance.add('https://github.com/cyberreboot/vent', build=False)
    assert type(status) == tuple
    assert status[0] == True
    status = instance.add('https://github.com/cyberreboot/vent.git', build=False)
    assert type(status) == tuple
    assert status[0] == True
    bad_instance = Plugin()
    status = bad_instance.add('https://github.com/cyberreboot/vent', build=False)
    assert type(status) == tuple
    assert status[0] == True
    instance = Plugin()
    status = instance.add('https://github.com/cyberreboot/vent', build=False, user='foo', pw='bar')
    assert type(status) == tuple
    assert status[0] == True
    instance = Plugin()
    status = instance.add('https://github.com/cyberreboot/vent', build=False, overrides=[('.', 'HEAD')])
    assert type(status) == tuple
    assert status[0] == True
    instance = Plugin()
    status = instance.add('https://github.com/cyberreboot/vent', build=False, tools=[('vent/', 'HEAD')], overrides=[('vent', 'HEAD')])
    assert type(status) == tuple
    assert status[0] == True

def test_get_tool_matches():
    """ Test the get_tool_matches function """
    instance = Plugin()
    instance.tools = []
    matches = instance.get_tool_matches()
    assert matches == []

def test_add_image():
    """ Test the add_image function """
    Plugin.add_image('foo')

def test_builder():
    """ Test the builder function """
    instance = Plugin()
    template = Template(instance.manifest)
    template = instance.builder(template, os.getcwd()+'/plugins/cyberreboot/vent', 'image_name', 'section')
    template = instance.builder(template, 'bad_path', 'image_name', 'section', build=True, branch='master', version='HEAD')

def test_build_tools():
    """ Test the _build_tools function """
    instance = Plugin()
    status = instance._build_tools(256)
    assert status[0] == False

def test_tools():
    """ Test the tools function """
    instance = Plugin()
    tools = instance.tools()

def test_remove():
    """ Test the remove function """
    instance = Plugin()
    status = instance.remove()
    assert status[0] == True

def test_versions():
    """ Test the versions function """
    instance = Plugin()
    status = instance.add('https://github.com/cyberreboot/vent', build=False, branch='master')
    assert status[0] == True
    versions = instance.versions('elasticsearch', branch='master')
    assert versions == [('cyberreboot:vent:/vent/core/elasticsearch:master:HEAD', ['HEAD'])]

def test_current_version():
    """ Test the current_version function """
    instance = Plugin()
    versions = instance.current_version('elasticsearch', branch='master')
    assert versions == [('cyberreboot:vent:/vent/core/elasticsearch:master:HEAD', 'HEAD')]

def test_state():
    """ Test the state function """
    instance = Plugin()
    states = instance.state('elasticsearch', branch='master')
    assert states == [('cyberreboot:vent:/vent/core/elasticsearch:master:HEAD', 'enabled')]

def test_enable():
    """ Test the enable function """
    instance = Plugin()
    status = instance.enable('elasticsearch', branch='master')
    assert status[0] == True

def test_disable():
    """ Test the disable function """
    instance = Plugin()
    status = instance.disable('elasticsearch', branch='master')
    assert status[0] == True

def test_apply_path():
    """ Test the apply_path function """
    instance = Plugin()
    status = instance.apply_path('https://github.com/cyberreboot/vent')
    assert type(status) == tuple
    assert status[0] == True
    status = instance.apply_path('https://github.com/cyberreboot/vent.git')
    assert type(status) == tuple
    assert status[0] == True

def test_repo_branches():
    """ Test the repo_branches function """
    instance = Plugin()
    status = instance.repo_branches('https://github.com/cyberreboot/vent')
    assert status[0] == True
    assert type(status[1]) == list

def test_repo_commits():
    """ Test the repo_commits function """
    instance = Plugin()
    commits = instance.repo_commits('https://github.com/cyberreboot/vent')
    assert commits[0] == True
    assert type(commits[1]) == list

def test_repo_tools():
    """ Test the repo_tools function """
    instance = Plugin()
    tools = instance.repo_tools('https://github.com/cyberreboot/vent', 'master', 'HEAD')
    assert tools[0] == True
    assert type(tools[1]) == list
