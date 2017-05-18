import os

from vent.api.actions import Action

def test_add():
    """ Test the add function """
    instance = Action()
    status = instance.add('bad')
    assert status[0] == False
    status = instance.add('https://github.com/cyberreboot/vent', build=False)
    assert status[0] == True

def test_remove():
    """ Test the remove function """
    instance = Action()
    status = instance.remove()
    assert status[0] == False
    status = instance.remove(repo='https://github.com/cyberreboot/vent')
    assert status[0] == True

def test_build():
    """ Test the build function """
    instance = Action()
    status = instance.add('https://github.com/cyberreboot/vent-plugins',
                          branch='experimental',
                          tools=[('kibana','')],
                          build=False)
    status = instance.build(branch='experimental')
    assert status[0] == True

def test_start():
    """ Test the start function """
    instance = Action()
    status = instance.add('https://github.com/cyberreboot/vent-plugins',
                          branch='experimental',
                          tools=[('kibana','')],
                          groups='foo')
    assert status[0] == True
    status = instance.start(name='kibana', branch='experimental')
    assert status[0] == True
    status = instance.add('https://github.com/cyberreboot/vent',
                          branch='experimental',
                          tools=[('vent/core/file-drop',''),
                                 ('vent/core/redis', ''),
                                 ('vent/core/syslog', '')])
    assert status[0] == True
    status = instance.start(groups='core', branch='experimental')
    assert status[0] == True

def test_stop():
    """ Test the stop function """
    instance = Action()
    status = instance.stop()

def test_clean():
    """ Test the clean function """
    instance = Action()
    status = instance.clean()

def test_update():
    """ Test the update function """
    Action.update()

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

def test_configure():
    """ Test the configure function """
    Action.configure()

def test_system_commands():
    """ Test the system_commands function """
    Action.system_commands()

def test_logs():
    """ Test the logs function """
    Action.logs()

def test_help():
    """ Test the help function """
    Action.help()
