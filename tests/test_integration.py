import curses
import npyscreen

from vent.menu import VentApp

npyscreen.TEST_SETTINGS['TEST_INPUT'] = ['\n', '^T', '^T', '^X', '\033']
npyscreen.TEST_SETTINGS['CONTINUE_AFTER_TEST_INPUT'] = False

def test_integration():
    """ Run integration tests """
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
