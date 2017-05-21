#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import npyscreen

from vent.helpers.meta import Version
from vent.helpers.paths import PathDirs
from vent.menus.add import AddForm
from vent.menus.add_options import AddOptionsForm
from vent.menus.core_inventory import CoreInventoryForm
from vent.menus.choose_tools import ChooseToolsForm
from vent.menus.clean_core_tools import CleanCoreToolsForm
from vent.menus.clean_tools import CleanToolsForm
from vent.menus.help import HelpForm
from vent.menus.inventory import InventoryForm
from vent.menus.main import MainForm
from vent.menus.services import ServicesForm
from vent.menus.start_core_tools import StartCoreToolsForm
from vent.menus.start_tools import StartToolsForm
from vent.menus.stop_core_tools import StopCoreToolsForm
from vent.menus.stop_tools import StopToolsForm
from vent.menus.tutorials.intro import TutorialIntroForm
from vent.menus.tutorials.background import TutorialBackgroundForm
from vent.menus.tutorials.terminology import TutorialTerminologyForm
from vent.menus.tutorials.getting_setup import TutorialGettingSetupForm
from vent.menus.tutorials.building_cores import TutorialBuildingCoresForm
from vent.menus.tutorials.starting_cores import TutorialStartingCoresForm
from vent.menus.tutorials.adding_plugins import TutorialAddingPluginsForm
from vent.menus.tutorials.adding_files import TutorialAddingFilesForm
from vent.menus.tutorials.setting_up_services import TutorialSettingUpServicesForm

class VentApp(npyscreen.NPSAppManaged):
    """ Main menu app for vent CLI """
    keypress_timeout_default = 10
    repo_value = {}
    paths = PathDirs()
    first_time = paths.ensure_file(paths.init_file)
    if first_time[0] == True and first_time[1] != "exists":
        npyscreen.NPSAppManaged.STARTING_FORM = "TUTORIALINTRO"

    def onStart(self):
        """ Override onStart method for npyscreen """
        self.paths.host_config()
        version = Version()
        self.addForm("MAIN", MainForm, name="Vent "+version+"\t\t\t\t\tPress ^T to toggle help\t\t\t\t\t\tPress ^Q to quit", color="IMPORTANT")
        self.addForm("HELP", HelpForm, name="Help\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("COREINVENTORY", CoreInventoryForm, name="Inventory of core tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="STANDOUT")
        self.addForm("INVENTORY", InventoryForm, name="Inventory of plugins\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="STANDOUT")
        self.addForm("ADD", AddForm, name="Add\t\t\t\t\t\t\t\tPress ^T to toggle help (To Be Implemented...)\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("ADDOPTIONS", AddOptionsForm, name="Set options for new plugin\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("CHOOSETOOLS", ChooseToolsForm, name="Choose tools to add for new plugin\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("SERVICES", ServicesForm, name="Services\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="STANDOUT")
        self.addForm("STARTTOOLS", StartToolsForm, name="Start tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("STOPTOOLS", StopToolsForm, name="Stop tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("CLEANTOOLS", CleanToolsForm, name="Clean tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("STARTCORETOOLS", StartCoreToolsForm, name="Start core tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("STOPCORETOOLS", StopCoreToolsForm, name="Stop core tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("CLEANCORETOOLS", CleanCoreToolsForm, name="Clean core tools\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.addForm("TUTORIALINTRO", TutorialIntroForm, name="Vent Tutorial"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALBACKGROUND", TutorialBackgroundForm, name="About Vent"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALTERMINOLOGY", TutorialTerminologyForm, name="About Vent"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALGETTINGSETUP", TutorialGettingSetupForm, name="About Vent"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALBUILDINGCORES", TutorialBuildingCoresForm, name="Working with Cores"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALSTARTINGCORES", TutorialStartingCoresForm, name="Working with Cores"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALADDINGPLUGINS", TutorialAddingPluginsForm, name="Working with Plugins"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALADDINGFILES", TutorialAddingFilesForm, name="Files"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")
        self.addForm("TUTORIALSETTINGUPSERVICES", TutorialSettingUpServicesForm, name="Services"+"\t\t\t\t\t\tPress ^Q to quit", color="DANGER")

    def change_form(self, name):
        """ Changes the form (window) that is displayed """
        self.switchForm(name)
        self.resetHistory()
