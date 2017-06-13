# -*- coding: utf-8 -*-

import npyscreen

from vent.helpers.paths import PathDirs
from vent.menu import VentApp

npyscreen.TEST_SETTINGS['CONTINUE_AFTER_TEST_INPUT'] = False

def test_integration():
    """ Run integration tests """
    CTRL_T = '^T'
    CTRL_X = '^X'
    ENTER = '\n'

    # run twice, once with tutorial, once without
    for x in xrange(2):
        if x == 0:
            # close tutorial
            npyscreen.TEST_SETTINGS['TEST_INPUT'] = [ENTER]

        A = VentApp()
        try:
            A.run(fork=True)
        except npyscreen.ExhaustedTestInput as e:
            pass

        if x == 0:
            # initialize tutorial
            paths = PathDirs()
            first_time = paths.ensure_file(paths.init_file)

            # go to help
            npyscreen.TEST_SETTINGS['TEST_INPUT'] = [CTRL_T]

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
