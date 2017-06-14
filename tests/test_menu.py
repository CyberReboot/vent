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
    CTRL_Q = '^Q'
    CTRL_T = '^T'
    CTRL_X = '^X'
    ENTER = curses.ascii.CR
    TAB = curses.ascii.TAB
    LEFT = curses.KEY_LEFT
    RIGHT = curses.KEY_RIGHT
    DOWN = curses.KEY_DOWN
    SPACE = curses.ascii.SP

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
    run_menu([ENTER, CTRL_X, 'c', 'b', ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'b', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 'c', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'c', ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'c', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'c', 'c', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 'v', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 'r', RIGHT, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'r', ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'r', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 's', RIGHT, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 's', ENTER])
    run_menu([ENTER, CTRL_X, 'c', 's', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 'p', RIGHT, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'p', ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'p', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 'u', RIGHT, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'u', ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'u', CTRL_T])

    # go through the plugins menus
    run_menu([ENTER, CTRL_X, 'p', 'a', CTRL_T, CTRL_T, TAB, TAB, TAB, RIGHT,
              ENTER, RIGHT, ENTER, RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'a', CTRL_T, CTRL_T, TAB, TAB, TAB, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'b', RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'b', ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'b', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'c', RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'c', ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'c', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'i', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 's', RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 's', ENTER])
    run_menu([ENTER, CTRL_X, 'p', 's', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'p', RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'p', ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'p', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'u', RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'u', ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'u', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'r', RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'r', ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'r', CTRL_T])

    # go through the logs menus
    run_menu([ENTER, CTRL_X, 'l', DOWN, ENTER, CTRL_T])
    run_menu([ENTER, CTRL_X, 'l', DOWN, ENTER, CTRL_Q])

    # go through the services running menus
    run_menu([ENTER, CTRL_X, 's', 'c', CTRL_T])
    run_menu([ENTER, CTRL_X, 's', 'p', CTRL_T])

    # go through the system commands menus
    # commenting out for now as this removes the coverage report, it seems
    #run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 'r', TAB, RIGHT,
    #          ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 'u'])

    # go through the tutorials menus
    run_menu([ENTER, CTRL_X, 't', 'v', 'b', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'v', 't', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'v', 's', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'c', 'b', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'c', 'c', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'p', 'a', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'f', 'a', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 's', 's', RIGHT, ENTER])
