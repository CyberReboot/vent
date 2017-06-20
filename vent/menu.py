#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import npyscreen
import os
import sys

from vent.helpers.meta import Version
from vent.helpers.paths import PathDirs
from vent.menus.core_inventory import CoreInventoryForm
from vent.menus.help import HelpForm
from vent.menus.inventory import InventoryForm
from vent.menus.logs import LogsForm
from vent.menus.main import MainForm
from vent.menus.services import ServicesForm
from vent.menus.start_core_tools import StartCoreToolsForm
from vent.menus.start_tools import StartToolsForm
from vent.menus.tools.tool_forms import BuildCoreToolsForm
from vent.menus.tools.tool_forms import BuildToolsForm
from vent.menus.tools.tool_forms import CleanCoreToolsForm
from vent.menus.tools.tool_forms import CleanToolsForm
from vent.menus.tools.tool_forms import RemoveCoreToolsForm
from vent.menus.tools.tool_forms import RemoveToolsForm
from vent.menus.tools.tool_forms import StopCoreToolsForm
from vent.menus.tools.tool_forms import StopToolsForm
from vent.menus.tools.tool_forms import UpdateCoreToolsForm
from vent.menus.tools.tool_forms import UpdateToolsForm
from vent.menus.tutorials.tutorial_forms import TutorialAddingFilesForm
from vent.menus.tutorials.tutorial_forms import TutorialAddingPluginsForm
from vent.menus.tutorials.tutorial_forms import TutorialBackgroundForm
from vent.menus.tutorials.tutorial_forms import TutorialBuildingCoresForm
from vent.menus.tutorials.tutorial_forms import TutorialGettingSetupForm
from vent.menus.tutorials.tutorial_forms import TutorialIntroForm
from vent.menus.tutorials.tutorial_forms import TutorialSettingUpServicesForm
from vent.menus.tutorials.tutorial_forms import TutorialStartingCoresForm
from vent.menus.tutorials.tutorial_forms import TutorialTerminologyForm


class VentApp(npyscreen.NPSAppManaged):
    """ Main menu app for vent CLI """
    keypress_timeout_default = 10
    repo_value = {}
    paths = PathDirs()
    first_time = paths.ensure_file(paths.init_file)
    if first_time[0] == True and first_time[1] != "exists":
        npyscreen.NPSAppManaged.STARTING_FORM = "TUTORIALINTRO"
    else:
        npyscreen.NPSAppManaged.STARTING_FORM = "MAIN"

    def add_forms(self):
        """ Add in forms that will have dynamic data """
        self.addForm("COREINVENTORY", CoreInventoryForm, name="Inventory of core tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="STANDOUT")
        self.addForm("INVENTORY", InventoryForm, name="Inventory of plugins\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="STANDOUT")
        self.addForm("SERVICES", ServicesForm, name="Services\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="STANDOUT")
        self.addForm("BUILDTOOLS", BuildToolsForm, name="Build tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("STARTTOOLS", StartToolsForm, name="Start tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("STOPTOOLS", StopToolsForm, name="Stop tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("CLEANTOOLS", CleanToolsForm, name="Clean tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("BUILDCORETOOLS", BuildCoreToolsForm, name="Build core tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("STARTCORETOOLS", StartCoreToolsForm, name="Start core tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("STOPCORETOOLS", StopCoreToolsForm, name="Stop core tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("CLEANCORETOOLS", CleanCoreToolsForm, name="Clean core tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("LOGS", LogsForm, name="Logs\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="STANDOUT")
        self.addForm("REMOVETOOLS", RemoveToolsForm, name="Remove tools\t\t\t\t\t\t\t\tPress ^T to toggle help\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("REMOVECORETOOLS", RemoveCoreToolsForm, name="Remove core tools\t\t\t\t\t\t\t\tPress ^T to toggle help\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("UPDATETOOLS", UpdateToolsForm, name="Update tools\t\t\t\t\t\t\t\tPress ^T to toggle help\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("UPDATECORETOOLS", UpdateCoreToolsForm, name="Update core tools\t\t\t\t\t\t\t\tPress ^T to toggle help\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")

    def remove_forms(self):
        """ Remove forms that will have dynamic data """
        self.removeForm("COREINVENTORY")
        self.removeForm("INVENTORY")
        self.removeForm("SERVICES")
        self.removeForm("BUILDTOOLS")
        self.removeForm("STARTTOOLS")
        self.removeForm("STOPTOOLS")
        self.removeForm("CLEANTOOLS")
        self.removeForm("BUILDCORETOOLS")
        self.removeForm("STARTCORETOOLS")
        self.removeForm("STOPCORETOOLS")
        self.removeForm("CLEANCORETOOLS")
        self.removeForm("LOGS")
        self.removeForm("REMOVETOOLS")
        self.removeForm("REMOVECORETOOLS")
        self.removeForm("UPDATETOOLS")
        self.removeForm("UPDATECORETOOLS")

    def onStart(self):
        """ Override onStart method for npyscreen """
        self.paths.host_config()
        version = Version()
        self.addForm("MAIN", MainForm, name="Vent "+version+"\t\t\t\t\tPress ^T to toggle help\t\t\t\t\t\tPress ^Q to quit", color="IMPORTANT")
        self.addForm("HELP", HelpForm, name="Help\t\t\t\t\t\t\t\tPress ^T to toggle previous\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALINTRO", TutorialIntroForm, name="Vent Tutorial"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALBACKGROUND", TutorialBackgroundForm, name="About Vent"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALTERMINOLOGY", TutorialTerminologyForm, name="About Vent"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALGETTINGSETUP", TutorialGettingSetupForm, name="About Vent"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALBUILDINGCORES", TutorialBuildingCoresForm, name="Working with Cores"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALSTARTINGCORES", TutorialStartingCoresForm, name="Working with Cores"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALADDINGPLUGINS", TutorialAddingPluginsForm, name="Working with Plugins"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALADDINGFILES", TutorialAddingFilesForm, name="Files"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALSETTINGUPSERVICES", TutorialSettingUpServicesForm, name="Services"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.add_forms()

    def change_form(self, name):
        """ Changes the form (window) that is displayed """
        self.switchForm(name)
