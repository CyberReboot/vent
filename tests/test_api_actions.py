import os

from vent.api.actions import Action

def test_add():
    """ Test the add function """
    instance = Action()
    status = instance.add('bad')
    assert type(status) == tuple
    assert status[0] == False
    status = instance.add('https://github.com/cyberreboot/vent', build=False)
    assert type(status) == tuple
    assert status[0] == True

def test_remove():
    """ Test the remove function """
    instance = Action()
    status = instance.remove()
    assert type(status) == tuple
    assert status[0] == True
    status = instance.remove(repo='https://github.com/cyberreboot/vent')
    assert type(status) == tuple
    assert status[0] == True

def test_build():
    """ Test the build function """
    instance = Action()
    status = instance.add('https://github.com/cyberreboot/vent-plugins',
                          branch='master',
                          tools=[('kibana','')],
                          build=False)
    assert type(status) == tuple
    assert status[0] ==  True
    status = instance.build(branch='master', name='kibana')
    assert type(status) == tuple
    assert status[0] == True

def test_prep_start():
    """ Test the prep_start function """
    instance = Action()
    status = instance.add('https://github.com/cyberreboot/vent-plugins',
                          branch='master',
                          tools=[('kibana','')],
                          groups='foo')
    assert type(status) == tuple
    assert status[0] == True
    status = instance.prep_start(name='kibana', branch='master')
    assert type(status) == tuple
    assert status[0] == True
    status = instance.add('https://github.com/cyberreboot/vent',
                          branch='master',
                          tools=[('vent/core/file-drop',''),
                                 ('vent/core/redis', ''),
                                 ('vent/core/syslog', '')])
    assert type(status) == tuple
    assert status[0] == True
    status = instance.prep_start(groups='core', branch='master')
    assert type(status) == tuple
    assert status[0] == True

def test_start():
    """ Test the start function """
    instance = Action()
    status = instance.start({})
    assert type(status) == tuple
    assert status[0] == True

def test_stop():
    """ Test the stop function """
    instance = Action()
    status = instance.stop()
    assert type(status) == tuple

def test_clean():
    """ Test the clean function """
    instance = Action()
    status = instance.clean()
    assert type(status) == tuple

def test_update():
    """ Test the update function """
    instance = Action()
    status = instance.update(name='elasticsearch', branch='master')
    assert type(status) == tuple

def test_backup():
    """ Test the backup function """
    Action.backup()

def test_restore():
    """ Test the restore function """
    Action.restore()

def test_inventory():
    """ Test the inventory function """
    instance = Action()
    status = instance.inventory(choices=[])
    assert type(status) == tuple
    assert status[0] == False
    status = instance.inventory(choices=['repos', 'core', 'tools', 'images', 'built', 'running', 'enabled', 'foo'])
    assert type(status) == tuple
    assert status[0] == True
    assert type(status[1]) == dict

def test_configure():
    """ Test the configure function """
    Action.configure()

def test_upgrade():
    """ Test the upgrade function """
    Action.upgrade()

def test_reset():
    """ Test the reset function """
    instance = Action()
    status = instance.reset()
    assert type(status) == tuple
    assert status[0] == False

def test_logs():
    """ Test the logs function """
    instance = Action()
    status = instance.logs()
    assert type(status) == tuple
    assert status[0] == True
    status = instance.logs(grep_list=['foo'])
    assert type(status) == tuple
    assert status[0] == True
    status = instance.logs(c_type="core")
    assert type(status) == tuple
    assert status[0] == True

def test_help():
    """ Test the help function """
    Action.help()

def test_cores():
    """ Test the cores function """
    instance = Action()
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
