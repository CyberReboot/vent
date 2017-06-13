import pexpect

def test_integration():
    """ Run integration tests """
    CTRL_C = '\003'
    CTRL_Q = '\011'
    CTRL_T = '\014'
    CTRL_X = '\018'
    ESC = '\033'
    vent = 'python2.7 vent/menu.py'
    child = pexpect.spawn(vent, dimensions=(25,80))
    child.expect('Menu')
    child.sendline()
    child.expect('Menu')
    child.send(CTRL_T)
    child.expect('Menu')
    child.send(CTRL_T)
    child.expect('Menu')
    child.send(CTRL_X)
    child.expect('Menu')
    child.send(ESC)
    child.expect('Menu')
    child.send(CTRL_C)
    child.read()
    child.close()
    # add a repo, build it, remove it
    # add a tool in a repo, build it, remove it
    # add a set of tools at a specific version in a repo, build them, and remove them
