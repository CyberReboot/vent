#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import ast
import npyscreen
import threading
import time

from vent.api.actions import Action
from vent.api.plugins import Plugin
from vent.helpers.meta import Containers
from vent.helpers.meta import Services
from vent.helpers.meta import Timestamp
from vent.helpers.meta import Tools
from vent.helpers.meta import Uptime
from vent.helpers.meta import Version

repo_value = {}

class ServicesForm(npyscreen.FormBaseNew):
    """ Services form for the Vent CLI """
    # !! TODO need to navigate key handlers
    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.change_forms,'^Q': self.quit})
        self.addfield = self.add(npyscreen.TitleFixedText, name='Services:', value="")
        services = Services()
        for service in services:
            value = ""
            for val in service[1]:
                value += val+", "
            self.add(npyscreen.TitleFixedText, name=service[0], value=value[:-2])

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)

    def change_forms(self, *args, **keywords):
        """ Checks which form is currently displayed and toggles it to the other one """
        if self.name == "Help\t\t\t\t\t\t\t\tPress ^T to toggle help":
            change_to = "MAIN"
        else:
            change_to = "SERVICES"

        # Tell the VentApp object to change forms.
        self.parentApp.change_form(change_to)

class ChooseToolsForm(npyscreen.ActionForm):
    """ For picking which tools to add """
    tools_tc = {}
    triggered = 0
    def repo_tools(self, branch):
        """ Set the appropriate repo dir and get the tools available of it """
        tools = []
        plugin = Plugin()
        t = plugin.repo_tools(repo_value['repo'], branch, repo_value['versions'][branch])
        for tool in t:
            tools.append(tool[0])
        return tools

    def create(self):
        self.add(npyscreen.TitleText, name='Select which tools to add from each branch selected:', editable=False)

    def while_waiting(self):
        """ Update with current tools for each branch at the version chosen """
        global repo_value

        if not self.triggered:
            i = 4
            for branch in repo_value['versions']:
                self.tools_tc[branch] = {}
                self.add(npyscreen.TitleText, name='Branch: '+branch, editable=False, rely=i, relx=5, max_width=25)
                tools = self.repo_tools(branch)
                i += 1
                for tool in tools:
                    value = True
                    if tool.startswith("/dev"):
                        value = False
                    if tool == "":
                        tool = "/"
                    self.tools_tc[branch][tool] = self.add(npyscreen.CheckBox, name=tool, value=value, relx=10)
                    i += 1
                i += 2
            self.triggered = 1

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)

    def on_ok(self):
        """
        Take the tool selections and add them as plugins
        """
        global repo_value

        def diff(first, second):
            """
            Get the elements that exist in the first list and not in the second
            """
            second = set(second)
            return [item for item in first if item not in second]

        def popup(original_tools, branch, thr, title):
            """
            Start the thread and display a popup of the tools being added until
            the thread is finished
            """
            thr.start()
            tool_str = "Adding tools..."
            npyscreen.notify_wait(tool_str, title=title)
            while thr.is_alive():
                tools = diff(Tools(), original_tools)
                if tools:
                    tool_str = ""
                for tool in tools:
                    # TODO limit length of tool_str to fit box
                    tool_str = "Added: "+branch+"/"+tool+"\n"+tool_str
                npyscreen.notify_wait(tool_str, title=title)
                time.sleep(1)
            return

        original_tools = Tools()
        for branch in self.tools_tc:
            api_action = Action()
            tools = []
            for tool in self.tools_tc[branch]:
                if self.tools_tc[branch][tool].value:
                    if tool == '/':
                        tools.append(('.',''))
                    else:
                        tools.append((tool,''))
            thr = threading.Thread(target=api_action.add, args=(),
                                   kwargs={'repo':repo_value['repo'],
                                           'branch':branch,
                                           'tools':tools,
                                           'version':repo_value['versions'][branch],
                                           'build':repo_value['build'][branch]})
            popup(original_tools, branch, thr,
                  'Please wait, adding tools for the '+branch+' branch...')
        npyscreen.notify_confirm("Done adding repository: "+repo_value['repo'],
                                 title='Added Repository')
        self.quit()

    def on_cancel(self):
        self.quit()

class AddOptionsForm(npyscreen.ActionForm):
    """ For specifying options when adding a repo """
    branch_cb = {}
    commit_tc = {}
    build_tc = {}
    branches = []
    commits = {}
    def repo_values(self):
        """ Set the appropriate repo dir and get the branches and commits of it """
        global repo_value
        branches = []
        commits = {}
        plugin = Plugin()
        branches = plugin.repo_branches(repo_value['repo'])[1]
        c = plugin.repo_commits(repo_value['repo'])
        for commit in c:
            commits[commit[0]] = commit[1]
        return branches, commits

    def create(self):
        self.add(npyscreen.TitleText, name='Branches:', editable=False)

    def while_waiting(self):
        """ Update with current branches and commits """
        if not self.branches or not self.commits:
            self.branches, self.commits = self.repo_values()
            i = 3
            for branch in self.branches:
                self.branch_cb[branch] = self.add(npyscreen.CheckBox,
                                                    name=branch, rely=i,
                                                    relx=5, max_width=25)
                self.commit_tc[branch] = self.add(npyscreen.TitleCombo, value=0, rely=i+1,
                                                  relx=10, max_width=30, name='Commit:',
                                                  values=self.commits[branch])
                self.build_tc[branch] = self.add(npyscreen.TitleCombo, value=0, rely=i+1,
                                                 relx=45, max_width=25, name='Build:',
                                                 values=[True, False])
                i += 3

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)

    def on_ok(self):
        """
        Take the branch, commit, and build selection and add them as plugins
        """
        global repo_value

        repo_value['versions'] = {}
        repo_value['build'] = {}
        for branch in self.branch_cb:
            if self.branch_cb[branch].value:
                # process checkboxes
                repo_value['versions'][branch] = self.commit_tc[branch].values[self.commit_tc[branch].value]
                repo_value['build'][branch] = self.build_tc[branch].values[self.build_tc[branch].value]
        self.parentApp.change_form("CHOOSETOOLS")

    def on_cancel(self):
        self.quit()

class AddForm(npyscreen.ActionForm):
    """ For for adding a new repo """
    def create(self):
        """ Create widgets for AddForm """
        self.repo = self.add(npyscreen.TitleText, name='Repository',
                             value='https://github.com/cyberreboot/vent-plugins')
        self.user = self.add(npyscreen.TitleText, name='Username')
        self.pw = self.add(npyscreen.TitlePassword, name='Password')
        self.repo.when_value_edited()

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)

    def on_ok(self):
        """ Add the repository """
        global repo_value
        repo_value['repo'] = self.repo.value
        def popup(thr, title):
            """
            Start the thread and display a popup of the plugin being cloned
            until the thread is finished
            """
            thr.start()
            tool_str = "Cloning repository..."
            npyscreen.notify_wait(tool_str, title=title)
            while thr.is_alive():
                time.sleep(1)
            return

        api_plugin = Plugin()
        thr = threading.Thread(target=api_plugin.clone, args=(),
                               kwargs={'repo':self.repo.value,
                                       'user':self.user.value,
                                       'pw':self.pw.value})
        popup(thr, 'Please wait, adding repository...')
        self.parentApp.change_form('ADDOPTIONS')

    def on_cancel(self):
        self.quit()

class VentForm(npyscreen.FormBaseNewWithMenus):
    """ Main information landing form for the Vent CLI """
    api_action = Action()

    def while_waiting(self):
        """ Update fields periodically if nothing is happening """
        self.addfield.value = Timestamp()
        self.addfield.display()
        self.addfield2.value = Uptime()
        self.addfield2.display()
        self.addfield3.value = str(len(Containers()))+" running"
        self.addfield3.display()

    def perform_action(self, action):
        """ Perform actions in the api from the CLI """
        def diff(first, second):
            """
            Get the elements that exist in the first list and not in the second
            """
            second = set(second)
            return [item for item in first if item not in second]

        def popup(original_containers, thr, title):
            """
            Start the thread and display a popup of the running containers
            until the thread is finished
            """
            thr.start()
            container_str = ""
            while thr.is_alive():
                containers = diff(Containers(), original_containers)
                if containers:
                    container_str = ""
                for container in containers:
                    # TODO limit length of container_str to fit box
                    container_str += container[0]+": "+container[1]+"\n"
                npyscreen.notify_wait(container_str, title=title)
                time.sleep(1)
            return

        original_containers = Containers()
        if action == 'add':
            self.parentApp.change_form('ADD')
        elif action == 'start':
            # TODO pass in actual args and kwargs
            # TODO show a build popup first to improve UX
            thr = threading.Thread(target=self.api_action.start, args=(),
                                   kwargs={'branch':'experimental'})
            popup(original_containers, thr,
                  'Please wait, starting containers...')
            npyscreen.notify_confirm("Done starting containers.",
                                     title='Started Containers')
        elif action == 'stop':
            # TODO pass in actual args and kwargs
            thr = threading.Thread(target=self.api_action.stop, args=(),
                                   kwargs={'branch':'experimental'})
            popup(original_containers, thr,
                  'Please wait, stopping containers...')
            npyscreen.notify_confirm("Done stopping containers.",
                                     title='Stopped Containers')
        elif action == 'clean':
            # TODO pass in actual args and kwargs
            thr = threading.Thread(target=self.api_action.clean, args=(),
                                   kwargs={'branch':'experimental'})
            popup(original_containers, thr,
                  'Please wait, cleaning containers...')
            npyscreen.notify_confirm("Done cleaning containers.",
                                     title='Cleaned Containers')
        return

    def create(self):
        """ Override method for creating FormBaseNewWithMenu form """
        self.add_handlers({"^T": self.change_forms, "^S": self.services_form})
        self.addfield = self.add(npyscreen.TitleFixedText, name='Date:',
                                 labelColor='DEFAULT', value=Timestamp())
        self.addfield2 = self.add(npyscreen.TitleFixedText, name='Uptime:',
                                  labelColor='DEFAULT', value=Uptime())
        self.addfield3 = self.add(npyscreen.TitleFixedText, name='Containers:',
                                  labelColor='DEFAULT',
                                  value=str(len(Containers()))+" running")
        self.addfield4 = self.add(npyscreen.TitleFixedText, name='Status:',
                                  value="Healthy")
        self.addfield5 = self.add(npyscreen.TitleFixedText,
                                  name='Core Tools:', labelColor='DANGER',
                                  value="Not built")
        self.addfield6 = self.add(npyscreen.TitleFixedText, name='Clustered:',
                                  value="No", labelColor='DEFAULT')
        self.addfield7 = self.add(npyscreen.TitleFixedText, name='Jobs:',
                                  value="None", labelColor='DEFAULT')
        self.multifield1 =  self.add(npyscreen.MultiLineEdit, max_height=22,
                                     editable=False, value = """

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
                           """)
        self.m1 = self.add_menu(name="Tools", shortcut="t")
        self.m1.addItemsFromList([
            ("Just Beep", None, "e"),
        ])
        self.m2 = self.add_menu(name="Plugins", shortcut="p",)
        self.m2.addItem(text='Add', onSelect=self.perform_action,
                        arguments=['add'], shortcut='a')
        self.m2.addItem(text='List', onSelect=self.perform_action,
                        arguments=['list'], shortcut='l')
        self.m2.addItem(text='Update', onSelect=self.perform_action,
                        arguments=['update'], shortcut='u')
        self.m2.addItem(text='Remove', onSelect=self.perform_action,
                        arguments=['Remove'], shortcut='r')
        self.m2.addItem(text='Build', onSelect=self.perform_action,
                        arguments=['build'], shortcut='b')
        self.m2.addItem(text='Start', onSelect=self.perform_action,
                        arguments=['start'], shortcut='s')
        self.m2.addItem(text='Stop', onSelect=self.perform_action,
                        arguments=['stop'], shortcut='p')
        self.m2.addItem(text='Clean', onSelect=self.perform_action,
                        arguments=['clean'], shortcut='c')
        self.m3 = self.add_menu(name="Logs", shortcut="l",)
        self.m3.addItemsFromList([
            ("Just Beep", None),
        ])
        self.m4 = self.add_menu(name="Core Tools", shortcut="c",)
        self.m4.addItemsFromList([
            ("Just Beep", None),
        ])
        self.m5 = self.add_menu(name="System Commands", shortcut="s",)
        self.m5.addItemsFromList([
            ("Just Beep", None),
        ])
        self.m6 = self.add_menu(name="System Configuration", shortcut="g",)
        self.m6.addItemsFromList([
            ("Just Beep", None),
        ])
        self.m7 = self.add_menu(name="Cluster Management", shortcut="m",)
        self.m7.addItemsFromList([
            ("Just Beep", None),
        ])

    def services_form(self, *args, **keywords):
        self.parentApp.change_form("SERVICES")

    def change_forms(self, *args, **keywords):
        """
        Checks which form is currently displayed and toggles it to the other
        one
        """
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
        self.add_handlers({"^T": self.change_forms,'^Q': self.quit})
        self.addfield = self.add(npyscreen.TitlePager, name="Vent", values="""Help\nmore\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more""".split("\n"))

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)

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
        version = Version()
        self.addForm("MAIN", VentForm, name="Vent "+version+"\t\t\t\t\tPress ^T to toggle help", color="IMPORTANT")
        self.addForm("HELP", HelpForm, name="Help\t\t\t\t\t\t\t\tPress ^T to toggle help", color="DANGER")
        self.addForm("ADD", AddForm, name="Add\t\t\t\t\t\t\t\tPress ^T to toggle help", color="CONTROL")
        self.addForm("ADDOPTIONS", AddOptionsForm, name="Set options for new plugin", color="CONTROL")
        self.addForm("CHOOSETOOLS", ChooseToolsForm, name="Choose tools to add for new plugin", color="CONTROL")
        self.addForm("SERVICES", ServicesForm, name="", color="STANDOUT")

    def change_form(self, name):
        """ Changes the form (window) that is displayed """
        self.switchForm(name)
        self.resetHistory()

if __name__ == '__main__':
    # !! TODO should actually have a way to quit
    while True:
        app = VentApp()
        app.run()
