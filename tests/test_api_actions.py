from vent.api.actions import Action

def test_add():
    """ Test the add function """
    instance = Action(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/', meta_dir='/tmp/.vent')
    status = instance.add('bad')
    assert status[0] == False
    status = instance.add('https://github.com/cyberreboot/vent', branch='experimental', build=False)
    assert status[0] == True

def test_remove():
    """ Test the remove function """
    Action.remove()

def test_build():
    """ Test the build function """
    instance = Action(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/', meta_dir='/tmp/.vent')
    instance.add('https://github.com/cyberreboot/vent-plugins', branch='experimental', tools=[('kibana','')], build=False)
    status = instance.build()
    assert status[0] == True

def test_start():
    """ Test the start function """
    instance = Action(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/', meta_dir='/tmp/.vent')
    status = instance.add('https://github.com/cyberreboot/vent-plugins', branch='experimental', tools=[('kibana','')])
    assert status[0] == True
    status = instance.start('kibana')
    assert status[0] == True

def test_stop():
    """ Test the stop function """
    Action.stop()

def test_clean():
    """ Test the clean function """
    Action.clean()

def test_backup():
    """ Test the backup function """
    Action.backup()

def test_restore():
    """ Test the restore function """
    Action.restore()

def test_show():
    """ Test the show function """
    Action.show()

def test_configure():
    """ Test the configure function """
    Action.configure()

def test_system_info():
    """ Test the system_info function """
    Action.system_info()

def test_system_conf():
    """ Test the system_conf function """
    Action.system_conf()

def test_system_commands():
    """ Test the system_commands function """
    Action.system_commands()

def test_logs():
    """ Test the logs function """
    Action.logs()

def test_help():
    """ Test the help function """
    Action.help()
