#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import curses
import time
from threading import Thread

import npyscreen

from vent.api.system import System
from vent.helpers.meta import Version
from vent.helpers.paths import PathDirs
from vent.menus.help import HelpForm
from vent.menus.main import MainForm
from vent.menus.tutorial_forms import TutorialAddingFilesForm
from vent.menus.tutorial_forms import TutorialAddingPluginsForm
from vent.menus.tutorial_forms import TutorialBackgroundForm
from vent.menus.tutorial_forms import TutorialGettingSetupForm
from vent.menus.tutorial_forms import TutorialIntroForm
from vent.menus.tutorial_forms import TutorialStartingCoresForm
from vent.menus.tutorial_forms import TutorialTerminologyForm
from vent.menus.tutorial_forms import TutorialTroubleshootingForm


class VentApp(npyscreen.NPSAppManaged):
    """ Main menu app for vent CLI """
    keypress_timeout_default = 10
    repo_value = {}
    paths = PathDirs()
    first_time = paths.ensure_file(paths.init_file)
    if first_time[0] and first_time[1] != 'exists':
        npyscreen.NPSAppManaged.STARTING_FORM = 'TUTORIALINTRO'
    else:
        npyscreen.NPSAppManaged.STARTING_FORM = 'MAIN'

    def onStart(self):
        """ Override onStart method for npyscreen """
        curses.mousemask(0)
        self.paths.host_config()
        version = Version()

        # setup initial runtime stuff
        if self.first_time[0] and self.first_time[1] != 'exists':
            system = System()
            thr = Thread(target=system.start, args=(), kwargs={})
            thr.start()
            countdown = 60
            while thr.is_alive():
                npyscreen.notify_wait('Completing initialization:...' + str(countdown),
                                      title='Setting up things...')
                time.sleep(1)
                countdown -= 1
            thr.join()

        quit_s = '\t'*4 + '^Q to quit'
        tab_esc = '\t'*4 + 'ESC to close menu popup'
        self.addForm('MAIN',
                     MainForm,
                     name='Vent ' + version +
                     '\t\t\t\t\t^T for help' + quit_s + tab_esc,
                     color='IMPORTANT')
        self.addForm('HELP',
                     HelpForm,
                     name='Help\t\t\t\t\t\t\t\t^T to toggle previous' +
                     quit_s,
                     color='DANGER')
        self.addForm('TUTORIALINTRO',
                     TutorialIntroForm,
                     name='Vent Tutorial' + quit_s,
                     color='DANGER')
        self.addForm('TUTORIALBACKGROUND',
                     TutorialBackgroundForm,
                     name='About Vent' + quit_s,
                     color='DANGER')
        self.addForm('TUTORIALTERMINOLOGY',
                     TutorialTerminologyForm,
                     name='About Vent' + quit_s,
                     color='DANGER')
        self.addForm('TUTORIALGETTINGSETUP',
                     TutorialGettingSetupForm,
                     name='About Vent' + quit_s,
                     color='DANGER')
        self.addForm('TUTORIALSTARTINGCORES',
                     TutorialStartingCoresForm,
                     name='Working with Cores' + quit_s,
                     color='DANGER')
        self.addForm('TUTORIALADDINGPLUGINS',
                     TutorialAddingPluginsForm,
                     name='Working with Plugins' + quit_s,
                     color='DANGER')
        self.addForm('TUTORIALADDINGFILES',
                     TutorialAddingFilesForm,
                     name='Files' + quit_s,
                     color='DANGER')
        self.addForm('TUTORIALTROUBLESHOOTING',
                     TutorialTroubleshootingForm,
                     name='Troubleshooting' + quit_s,
                     color='DANGER')

    def change_form(self, name):
        """ Changes the form (window) that is displayed """
        self.switchForm(name)
