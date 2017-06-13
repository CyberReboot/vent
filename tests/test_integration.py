import pexpect

def test_integration():
    """ Run integration tests """
    CTRL_C = '\003'
    vent = 'vent'
    child = pexpect.spawn(vent, dimensions=(25,80))
    child.expect('Menu')
    child.send(CTRL_C)
    child.read()
    child.close()
    # add a repo, build it, remove it
    # add a tool in a repo, build it, remove it
    # add a set of tools at a specific version in a repo, build them, and remove them
