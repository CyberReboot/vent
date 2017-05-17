#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import npyscreen

from vent.helpers.meta import Version
from vent.helpers.paths import PathDirs
from vent.menus.add import AddForm
from vent.menus.add_options import AddOptionsForm
from vent.menus.choose_tools import ChooseToolsForm
from vent.menus.help import HelpForm
from vent.menus.main import MainForm
from vent.menus.services import ServicesForm

class VentApp(npyscreen.NPSAppManaged):
    """ Main menu app for vent CLI """
    keypress_timeout_default = 10
    repo_value = {}

    def onStart(self):
        """ Override onStart method for npyscreen """
        paths = PathDirs()
        paths.host_config()
        version = Version()
        self.addForm("MAIN", MainForm, name="Vent "+version+"\t\t\t\t\tPress ^T to toggle help\t\t\t\t\t\tPress ^Q to quit", color="IMPORTANT")
        self.addForm("HELP", HelpForm, name="Help\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("ADD", AddForm, name="Add\t\t\t\t\t\t\t\tPress ^T to toggle help (To Be Implemented...)\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("ADDOPTIONS", AddOptionsForm, name="Set options for new plugin\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("CHOOSETOOLS", ChooseToolsForm, name="Choose tools to add for new plugin\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("SERVICES", ServicesForm, name="Services\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="STANDOUT")

    def change_form(self, name):
        """ Changes the form (window) that is displayed """
        self.switchForm(name)
        self.resetHistory()
