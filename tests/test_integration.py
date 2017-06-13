import npyscreen

from vent.menu import VentApp

npyscreen.TEST_SETTINGS['CONTINUE_AFTER_TEST_INPUT'] = False

def test_integration():
    """ Run integration tests """
    # close tutorial
    npyscreen.TEST_SETTINGS['TEST_INPUT'] = ['\n']

    # go to help
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += ["^T"]

    # go through help menus
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += ["^X", 'b', 'm', '\n', '\n']
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += ["^X", 'b', 'p', '\n', '\n']
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += ["^X", 'b', 't', '\n', '\n']
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += ["^X", 'b', 'f', '\n', '\n']
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += ["^X", 'b', 'c', '\n', '\n']
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += ["^X", 'b', 's', '\n', '\n']
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += ["^X", 'p', 'a', '\n', '\n']
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += ["^X", 'p', 'b', '\n', '\n']

    # leave help menu
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += ['\n']

    # run twice, once with tutorial, once without
    for x in xrange(2):
        A = VentApp()
        try:
            A.run(fork=False)
        except npyscreen.ExhaustedTestInput as e:
            pass
        else:
            raise npyscreen.ExhaustedTestInput

    # add a repo, build it, remove it
    # add a tool in a repo, build it, remove it
    # add a set of tools at a specific version in a repo, build them, and remove them
