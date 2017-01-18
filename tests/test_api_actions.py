from vent.api.actions import Action

def test_add():
    """ Test the add function """
    Action.add()

def test_remove():
    """ Test the remove function """
    Action.remove()

def test_start():
    """ Test the start function """
    Action.start()

def test_stop():
    """ Test the stop function """
    Action.stop()

def test_clean():
    """ Test the clean function """
    Action.clean()

def test_build():
    """ Test the build function """
    instance = Action()
    status = instance.build()
    assert status[0] == True

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
