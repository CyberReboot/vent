# -*- coding: utf-8 -*-
import curses

import npyscreen

from vent.helpers.paths import PathDirs
from vent.menu import VentApp
from vent.menus.main import MainForm

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
    CTRL_V = '^V'
    ENTER = curses.ascii.CR
    TAB = curses.ascii.TAB
    LEFT = curses.KEY_LEFT
    RIGHT = curses.KEY_RIGHT
    DOWN = curses.KEY_DOWN
    SPACE = curses.ascii.SP
    BACKSPACE = curses.ascii.BS

    # go through help menus
    run_menu([ENTER, CTRL_T, CTRL_X, 'p', 'a',
              ENTER, ENTER, ENTER, ENTER, ENTER, ENTER, ENTER, ENTER, ENTER])

    # go to help menu and leave again
    run_menu([ENTER, CTRL_T, RIGHT, ENTER])

    # configure - quit in the middle of add
    # run_menu([ENTER, CTRL_X, 'c', 't', SPACE, TAB, SPACE, TAB, SPACE, TAB,
    #          SPACE, TAB, SPACE, TAB, SPACE, TAB, SPACE, TAB, TAB, SPACE, TAB,
    #          SPACE, TAB, TAB, ENTER, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN,
    #          DOWN, DOWN, DOWN, DOWN, DOWN, LEFT, BACKSPACE, '3', TAB, TAB,
    #          ENTER, ENTER, TAB, ENTER, ENTER, TAB, ENTER, CTRL_Q])
    # configure - instances add (add an instance of rq_worker)
    # run_menu([ENTER, CTRL_X, 'c', 't', SPACE, TAB, SPACE, TAB, SPACE, TAB,
    #          SPACE, TAB, SPACE, TAB, SPACE, TAB, SPACE, TAB, TAB, SPACE, TAB,
    #          SPACE, TAB, TAB, ENTER, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN,
    #          DOWN, DOWN, DOWN, DOWN, DOWN, LEFT, BACKSPACE, '3', TAB, TAB,
    #          ENTER, ENTER, TAB, ENTER, ENTER, TAB, ENTER, TAB, TAB, ENTER])
    # configure - quit in the middle of delete
    # run_menu([ENTER, CTRL_X, 'c', 't', SPACE, TAB, SPACE, TAB, SPACE, TAB,
    #          SPACE, TAB, SPACE, TAB, SPACE, TAB, SPACE, TAB, TAB, SPACE, TAB,
    #          SPACE, TAB, SPACE, TAB, TAB, ENTER, DOWN, DOWN, DOWN, DOWN, DOWN,
    #          DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, LEFT, BACKSPACE, '2',
    #          TAB, TAB, ENTER, ENTER, TAB, ENTER, CTRL_Q])
    # configure - instances delete (delete an instance of file_drop)
    # run_menu([ENTER, CTRL_X, 'c', 't', SPACE, TAB, SPACE, TAB, SPACE, TAB,
    #          SPACE, TAB, SPACE, TAB, SPACE, TAB, SPACE, TAB, TAB, SPACE, TAB,
    #          SPACE, TAB, SPACE, TAB, TAB, ENTER, DOWN, DOWN, DOWN, DOWN, DOWN,
    #          DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, LEFT, BACKSPACE, '2',
    #          TAB, TAB, ENTER, ENTER, TAB, ENTER, SPACE, TAB, TAB, ENTER])

    # go through the plugins menus
    run_menu([ENTER, CTRL_X, 'p', 'a', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              RIGHT, ENTER, SPACE, TAB, TAB, TAB, TAB, TAB, TAB, TAB, ENTER,
              SPACE, TAB, SPACE, TAB, SPACE, TAB, TAB, SPACE, TAB, SPACE, TAB,
              TAB, ENTER, ENTER, ENTER])
    cmds = [ENTER, CTRL_X, 'p', 'a', TAB, TAB, TAB, 'alpine', TAB, TAB, TAB,
            TAB, TAB, TAB, ENTER, ENTER, ENTER]
    cmds += (43 * [BACKSPACE])
    cmds += [TAB, TAB, TAB, BACKSPACE, BACKSPACE, BACKSPACE, BACKSPACE,
             BACKSPACE, BACKSPACE, TAB, TAB, TAB, TAB, TAB, TAB, ENTER, ENTER,
             ENTER, CTRL_Q]
    run_menu(cmds)
    run_menu([ENTER, CTRL_X, 'p', 'a', TAB, TAB, TAB, 'alpine', TAB, 'alpine',
              TAB, TAB, TAB, TAB, TAB, ENTER, ENTER, ENTER, TAB, TAB, ENTER,
              ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'a', CTRL_T, CTRL_T, TAB, TAB, TAB, TAB, TAB,
              TAB, TAB, TAB, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'i', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 's', TAB, TAB, RIGHT, ENTER, ENTER, ENTER,
              ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 's', TAB, TAB, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 's', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'p', 's', CTRL_T])
    # services running - plugin services
    run_menu([ENTER, CTRL_X, 'p', 'p', RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'p', ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'p', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'p', 'p', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'r', TAB, TAB, RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'r', ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'r', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'p', 'r', CTRL_T])

    # go through the services running menus
    run_menu([ENTER, CTRL_X, 's', 'e', CTRL_T])

    # go through the system commands menus
    # causes .coverage file to not exist
    # run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 'r', TAB, RIGHT,
    #           ENTER, ENTER, ENTER])
    # system commands - backup
    run_menu([ENTER, CTRL_X, 'y', 'b', ENTER, ENTER])
    # system commands - configure - cancel
    run_menu([ENTER, CTRL_X, 'y', 'c', TAB, ENTER, ENTER, ENTER])
    # system commands - configure - ok
    run_menu([ENTER, CTRL_X, 'y', 'c', TAB, TAB, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 'g', ENTER, ENTER])
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 's'])
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 'u'])
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 'b', ENTER, ENTER])
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 't', SPACE, TAB,
              ENTER])
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 't', SPACE, TAB,
              TAB, ENTER, ENTER, ENTER])

    # go through the tutorials menus
    run_menu([ENTER, CTRL_X, 't', 'v', 'b', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'v', 't', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'v', 's', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'c', 'c', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'p', 'a', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 'f', 'a', RIGHT, ENTER])
    run_menu([ENTER, CTRL_X, 't', 's', 't', RIGHT, ENTER])

    # exit
    # causes .coverage file to not exist
    # run_menu([ENTER, CTRL_Q])
