# -*- coding: utf-8 -*-

import curses
import npyscreen

from vent.helpers.paths import PathDirs
from vent.menu import VentApp

npyscreen.TEST_SETTINGS['CONTINUE_AFTER_TEST_INPUT'] = False

def test_menu():
    """ Run integration tests """
    CTRL_T = '^T'
    CTRL_X = '^X'
    ENTER = curses.ascii.CR
    TAB = curses.ascii.TAB
    RIGHT = curses.KEY_RIGHT
    DOWN = curses.KEY_DOWN

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

    # leave help menu, come back and leave again
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [ENTER, CTRL_T, RIGHT, ENTER]

    # go through the core tools menus
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'c', 'i', ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'c', 'b', RIGHT, ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'c', 'c', RIGHT, ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'c', 'v', CTRL_T]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'c', 'r', RIGHT, ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'c', 's', RIGHT, ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'c', 'p', RIGHT, ENTER,
                                              ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'c', 'u', RIGHT, ENTER,
                                              ENTER]

    # go through the plugins menus
    # TODO

    # go through the logs menus
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 'l', DOWN, CTRL_T]

    # go through the services running menus
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 's', 'c', CTRL_T]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 's', 'p', CTRL_T]

    # go through the system commands menus
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, DOWN, DOWN, DOWN, DOWN,
                                              ENTER, 'r', TAB, RIGHT, ENTER,
                                              ENTER, ENTER]
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, DOWN, DOWN, DOWN, DOWN,
                                              ENTER, 'u']

    # go through the tutorials menus
    npyscreen.TEST_SETTINGS['TEST_INPUT'] += [CTRL_X, 't', 's', 's', RIGHT,
                                              ENTER]

    A = VentApp()
    try:
        A.run(fork=False)
    except npyscreen.ExhaustedTestInput as e:
        pass
