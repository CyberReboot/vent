from vent.api.system import System


def test_configure():
    """ Test the configure function """
    system = System()
    system.configure()


def test_gpu():
    """ Test the gpu function """
    system = System()
    system.gpu()


def test_history():
    """ Test the history function """
    system = System()
    system.history()


def test_restore():
    """ Test the restore function """
    system = System()
    system.restore('foo')


def test_rollback():
    """ Test the rollback function """
    system = System()
    system.rollback()


def test_upgrade():
    """ Test the upgrade function """
    system = System()
    system.upgrade()
