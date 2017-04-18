#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import datetime
import docker
import npyscreen
import subprocess

class VentForm(npyscreen.FormBaseNewWithMenus):
    """ Main information landing form for the Vent CLI """
    d_client = docker.from_env()

    def while_waiting(self):
        """ Update fields periodically if nothing is happening """
        self.addfield.value = str(datetime.datetime.now())+" UTC"
        self.addfield.display()
        self.addfield2.value = str(subprocess.check_output(["uptime"]))[1:]
        self.addfield2.display()
        self.addfield3.value = str(len(self.d_client.containers.list()))+" running"
        self.addfield3.display()

    def create(self):
        """ Override method for creating FormBaseNewWithMenu form """
        self.add_handlers({"^T": self.change_forms})
        self.addfield = self.add(npyscreen.TitleFixedText, name='Date:', value=str(datetime.datetime.now())+" UTC")
        self.addfield2 = self.add(npyscreen.TitleFixedText, name='Uptime:', value=str(subprocess.check_output(["uptime"]))[1:])
        self.addfield3 = self.add(npyscreen.TitleFixedText, name='Containers:', value=str(len(self.d_client.containers.list()))+" running")
        self.addfield4 = self.add(npyscreen.TitleFixedText, name='Version:', value="")
        self.addfield5 = self.add(npyscreen.TitleFixedText, name='Jobs:', value="")
        self.addfield6 = self.add(npyscreen.TitleFixedText, name='Status:', value="Healthy")
        self.addfield7 = self.add(npyscreen.TitleFixedText, name='Management:', value="Running")
        self.addfield8 = self.add(npyscreen.TitleFixedText, name='Clustered:', value="No")
        self.multifield1 =  self.add(npyscreen.MultiLineEdit,
               value = """

            '.,
              'b      *
               '$    #.
                $:   #:
                *#  @):
                :@,@):   ,.**:'
      ,         :@@*: ..**'
       '#o.    .:(@'.@*"'
          'bq,..:,@@*'   ,*
          ,p$q8,:@)'  .p*'
         '    '@@Pp@@*'
               Y7'.'
              :@):.
             .:@:'.
           .::(@:.
                       _
      __   _____ _ __ | |_
      \ \ / / _ \ '_ \| __|
       \ V /  __/ | | | |_
        \_/ \___|_| |_|\__|
                           """,
               max_height=22, editable=False)

        self.m1 = self.add_menu(name="Tools", shortcut="t")
        self.m1.addItemsFromList([
            ("Just Beep", None, "e"),
        ])
        self.m2 = self.add_menu(name="Plugins", shortcut="p",)
        self.m2.addItemsFromList([
            ("Just Beep", None),
        ])
        self.m3 = self.add_menu(name="Logs", shortcut="l",)
        self.m3.addItemsFromList([
            ("Just Beep", None),
        ])
        self.m3 = self.add_menu(name="System Commands", shortcut="s",)
        self.m3.addItemsFromList([
            ("Just Beep", None),
        ])
        self.m4 = self.add_menu(name="System Configuration", shortcut="c",)
        self.m4.addItemsFromList([
            ("Just Beep", None),
        ])
        self.m5 = self.add_menu(name="Cluster Management", shortcut="m",)
        self.m5.addItemsFromList([
            ("Just Beep", None),
        ])

    def change_forms(self, *args, **keywords):
        """ Checks which form is currently displayed and toggles it to the other one """
        if self.name == "Help\t\t\t\t\t\t\t\tPress ^T to toggle help":
            change_to = "MAIN"
        else:
            change_to = "HELP"

        # Tell the VentApp object to change forms.
        self.parentApp.change_form(change_to)

class HelpForm(npyscreen.FormBaseNew):
    """ Help form for the Vent CLI """
    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.change_forms})
        self.addfield = self.add(npyscreen.TitlePager, name="Vent", values="""Help\nmore\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more""".split("\n"))

    def change_forms(self, *args, **keywords):
        """ Checks which form is currently displayed and toggles it to the other one """
        if self.name == "Help\t\t\t\t\t\t\t\tPress ^T to toggle help":
            change_to = "MAIN"
        else:
            change_to = "HELP"

        # Tell the VentApp object to change forms.
        self.parentApp.change_form(change_to)

class VentApp(npyscreen.NPSAppManaged):
    """ Main menu app for vent CLI """
    keypress_timeout_default = 10

    def onStart(self):
        """ Override onStart method for npyscreen """
        self.addForm("MAIN", VentForm, name="Vent\t\t\t\t\t\t\t\tPress ^T to toggle help", color="IMPORTANT")
        self.addForm("HELP", HelpForm, name="Help\t\t\t\t\t\t\t\tPress ^T to toggle help", color="DANGER")

    def change_form(self, name):
        """ Changes the form (window) that is displayed """
        self.switchForm(name)
        self.resetHistory()

if __name__ == '__main__':
    app = VentApp()
    app.run()
