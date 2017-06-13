# -*- coding: utf-8 -*-

import curses
import npyscreen

from vent.helpers.paths import PathDirs
from vent.menu import VentApp

npyscreen.TEST_SETTINGS['CONTINUE_AFTER_TEST_INPUT'] = False

def test_integration():
    """ Run integration tests """
    CTRL_T = '^T'
    CTRL_X = '^X'
    ENTER = curses.ascii.CR

    # initialize tutorial
    paths = PathDirs()
    first_time = paths.ensure_file(paths.init_file)
    assert first_time[0] == True

    # leave the tutorial menu
    npyscreen.TEST_SETTINGS['TEST_INPUT'] = [ENTER]

    # go to help
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_T]

    # go through help menus
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'b', 'm', ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'b', 'p', ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'b', 't', ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'b', 'f', ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'b', 'c', ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'b', 's', ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'p', 'a', ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'p', 'b', ENTER,
                                              ENTER]

    # leave help menu
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [ENTER]

    A = VentApp()
    try:
        A.run(fork=False)
    except npyscreen.ExhaustedTestInput as e:
        pass
