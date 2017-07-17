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

def test_tools_status():
    """ Test the staticmethod tools_status """
    a, b = MainForm.t_status(True)
    assert isinstance(a, str)
    assert isinstance(b, tuple)

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
    BACKSPACE = curses.ascii.BS

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
    run_menu([ENTER, CTRL_X, 'c', 'b', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'b', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'b', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'c', 'b', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 't', TAB, SPACE, TAB, SPACE, TAB, SPACE, TAB,
              SPACE, TAB, SPACE, TAB, SPACE, TAB, SPACE, TAB, SPACE, TAB, TAB,
              TAB, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 't', TAB, SPACE, TAB, SPACE, TAB, SPACE, TAB,
              SPACE, TAB, SPACE, TAB, SPACE, TAB, SPACE, TAB, SPACE, TAB, TAB,
              TAB, TAB, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'c', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'c', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'c', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'c', 'c', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 'v', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'c', 'v', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 's', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 's', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              ENTER])
    run_menu([ENTER, CTRL_X, 'c', 's', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'c', 's', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 'p', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'p', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'p', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'c', 'p', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 'u', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'u', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'u', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'c', 'u', CTRL_T])
    run_menu([ENTER, CTRL_X, 's', 'c', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 'r', TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB,
              RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'r', ENTER])
    run_menu([ENTER, CTRL_X, 'c', 'r', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'c', 'r', CTRL_T])
    run_menu([ENTER, CTRL_X, 'c', 't', TAB, ENTER, ENTER, ENTER])

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
    run_menu(cmd)
    run_menu([ENTER, CTRL_X, 'p', 'a', TAB, TAB, TAB, 'alpine', TAB, 'alpine',
              TAB, TAB, TAB, TAB, TAB, ENTER, ENTER, ENTER, TAB, TAB, ENTER,
              ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'a', CTRL_T, CTRL_T, TAB, TAB, TAB, TAB, TAB,
              TAB, TAB, TAB, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'b', TAB, TAB, RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'b', TAB, TAB, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'b', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'p', 'b', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'c', TAB, TAB, RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'c', TAB, TAB, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'c', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'p', 'c', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'i', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 's', TAB, TAB, RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 's', TAB, TAB, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 's', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'p', 's', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'p', RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'p', ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'p', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'p', 'p', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'u', TAB, TAB, RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'u', TAB, TAB, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'u', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'p', 'u', CTRL_T])
    run_menu([ENTER, CTRL_X, 's', 'p', CTRL_T])
    run_menu([ENTER, CTRL_X, 'p', 'r', TAB, TAB, RIGHT, ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'r', ENTER])
    run_menu([ENTER, CTRL_X, 'p', 'r', CTRL_Q])
    run_menu([ENTER, CTRL_X, 'p', 'r', CTRL_T])

    # go through the logs menus
    run_menu([ENTER, CTRL_X, 'l', DOWN, ENTER, CTRL_T])
    run_menu([ENTER, CTRL_X, 'l', DOWN, ENTER, CTRL_Q])

    # go through the services running menus
    run_menu([ENTER, CTRL_X, 's', 'c', CTRL_T])
    run_menu([ENTER, CTRL_X, 's', 'p', CTRL_T])

    # go through the system commands menus
    # causes .coverage file to not exist
    # run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 'r', TAB, RIGHT,
    #           ENTER, ENTER, ENTER])
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 'g', ENTER, ENTER])
    run_menu([ENTER, CTRL_X, DOWN, DOWN, DOWN, DOWN, ENTER, 's'])
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

    # exit
    # causes .coverage file to not exist
    # run_menu([ENTER, CTRL_Q])
