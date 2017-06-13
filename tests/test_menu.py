# -*- coding: utf-8 -*-

import curses
import npyscreen

from vent.helpers.paths import PathDirs
from vent.menu import VentApp

npyscreen.TEST_SETTINGS['CONTINUE_AFTER_TEST_INPUT'] = False

def run_menu(test_input):
    """ Actually run the menu and process any input """
    # initialize tutorial
    paths = PathDirs()
    first_time = paths.ensure_file(paths.init_file)
    assert first_time[0] == True

    npyscreen.TEST_SETTINGS['TEST_INPUT'] = test_input

    A = VentApp()
    try:
        A.run(fork=False)
    except npyscreen.ExhaustedTestInput as e:
        pass

def test_menu():
    """ Run menu tests """
    CTRL_T = '^T'
    CTRL_X = '^X'
    ENTER = curses.ascii.CR
    TAB = curses.ascii.TAB
    RIGHT = curses.KEY_RIGHT
    DOWN = curses.KEY_DOWN

    # go through help menus
    run_menu([ENTER, CTRL_T, CTRL_X, 'b', 'm', ENTER, ENTER, CTRL_X, 'b', 'p',
              ENTER, ENTER, CTRL_X, 'b', 't', ENTER, ENTER, CTRL_X, 'b', 'f',
              ENTER, ENTER, CTRL_X, 'b', 'c', ENTER, ENTER, CTRL_X, 'b', 's',
              ENTER, ENTER, CTRL_X, 'p', 'a', ENTER, ENTER, CTRL_X, 'p', 'b',
              ENTER, ENTER, ENTER])

    # go to help menu and leave again
    run_menu([ENTER, CTRL_T, RIGHT, ENTER])

    # go through the core tools menus
    run_menu([ENTER, CTRL_X, 'c', 'i', ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'b', RIGHT, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'c', RIGHT, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'v', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 'r', RIGHT, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 's', RIGHT, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'p', RIGHT, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'u', RIGHT, ENTER, ENTER])

    # go through the plugins menus
    # TODO

    # go through the logs menus
    run_menu([ENTER, CTRL_X, 'l', DOWN, CTRL_T])

    # go through the services running menus
    run_menu([ENTER, CTRL_X, 's', 'c', CTRL_T])
    run_menu([ENTER, CTRL_X, 's', 'p', CTRL_T])

    # go through the system commands menus
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 'r', TAB, RIGHT,
              ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 'u'])

    # go through the tutorials menus
    run_menu([ENTER, CTRL_X, 't', 'v', 'b', RIGHT, ENTER, CTRL_X, 't', 'v',
              't', RIGHT, ENTER, CTRL_X, 't', 'v', 's', RIGHT, ENTER, CTRL_X,
              't', 'c', 'b', RIGHT, ENTER, CTRL_X, 't', 'c', 'c', RIGHT, ENTER,
              CTRL_X, 't', 'p', 'a', RIGHT, ENTER, CTRL_X, 't', 'f', 'a',
              RIGHT, ENTER, CTRL_X, 't', 's', 's', RIGHT, ENTER])
