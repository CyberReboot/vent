import npyscreen
import os
import sys
import threading
import time

from docker.errors import DockerException
from vent.api.actions import Action
from vent.helpers.meta import Containers
from vent.helpers.meta import Core
from vent.helpers.meta import Images
from vent.helpers.meta import Timestamp
from vent.helpers.meta import Uptime

class MainForm(npyscreen.FormBaseNewWithMenus):
    """ Main information landing form for the Vent CLI """
    triggered = False

    def exit(self, *args, **keywords):
        os.system('reset')
        os.system('stty sane')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    def while_waiting(self):
        """ Update fields periodically if nothing is happening """
        def popup(message):
            npyscreen.notify_confirm(str(message), title="Docker Error", form_color='DANGER', wrap=True)
            self.exit()

        if not self.triggered:
            self.triggered = True
            try:
                self.api_action = Action()
            except DockerException as de:
                popup(de)

        # give a little extra time for file descriptors to close
        time.sleep(0.01)

        self.addfield.value = Timestamp()
        self.addfield.display()
        self.addfield2.value = Uptime()
        self.addfield2.display()
        self.addfield3.value = str(len(Containers()))+" running"
        self.addfield3.display()

        # set core value string
        # !! TODO remove hardcoded experimental
        core = Core(branch='experimental')
        installed = 0
        custom_installed = 0
        built = 0
        custom_built = 0
        running = 0
        custom_running = 0
        normal = str(len(core['normal']))
        for tool in core['running']:
            if tool in core['normal']:
                running += 1
            else:
                custom_running += 1
        for tool in core['built']:
            if tool in core['normal']:
                built += 1
            else:
                custom_built += 1
        for tool in core['installed']:
            if tool in core['normal']:
                installed += 1
            else:
                custom_installed += 1
        core_str = str(running+custom_running)+"/"+normal+" running"
        if custom_running > 0:
            core_str += " ("+str(custom_running)+" custom)"
        core_str += ", "+str(built+custom_built)+"/"+normal+" built"
        if custom_built > 0:
            core_str += " ("+str(custom_built)+" custom)"
        core_str += ", "+str(installed+custom_installed)+"/"+normal+" installed"
        if custom_built > 0:
            core_str += " ("+str(custom_installed)+" custom)"
        self.addfield5.value = core_str
        if running+custom_running == 0:
            color = "DANGER"
        elif running >= int(normal):
            color = "GOOD"
        else:
            color = "CAUTION"
        self.addfield5.labelColor = color
        self.addfield5.display()
        # !! TODO update fields such as health status, jobs, etc.
        return

    def core_tools(self, action):
        """ Perform actions for core tools """
        def diff(first, second):
            """
            Get the elements that exist in the first list and not in the second
            """
            second = set(second)
            return [item for item in first if item not in second]

        def popup(original, orig_type, thr, title):
            """
            Start the thread and display a popup of info
            until the thread is finished
            """
            thr.start()
            info_str = ""
            while thr.is_alive():
                if orig_type == 'containers':
                    info = diff(Containers(), original)
                elif orig_type == 'images':
                    info = diff(Images(), original)
                if info:
                    info_str = ""
                for entry in info:
                    # TODO limit length of info_str to fit box
                    info_str += entry[0]+": "+entry[1]+"\n"
                npyscreen.notify_wait(info_str, title=title)
                time.sleep(1)
            return

        # !! TODO remove hardcoded experimental branch
        if action == 'install':
            original_images = Images()
            thr = threading.Thread(target=self.api_action.cores, args=(),
                                   kwargs={"action":"install",
                                           "branch":"experimental"})
            popup(original_images, "images", thr,
                  'Please wait, installing core containers...')
            npyscreen.notify_confirm("Done installing core containers.",
                                     title='Installed core containers')
        elif action == 'build':
            # !! TODO select which tools to build
            original_images = Images()
            thr = threading.Thread(target=self.api_action.cores, args=(),
                                   kwargs={"action":"build",
                                           "branch":"experimental"})
            popup(original_images, "images", thr,
                  'Please wait, building core containers...')
            npyscreen.notify_confirm("Done building core containers.",
                                     title='Built core containers')
        elif action == 'start':
            self.parentApp.change_form('STARTCORETOOLS')
        elif action == 'stop':
            self.parentApp.change_form('STOPCORETOOLS')
        elif action == 'clean':
            self.parentApp.change_form('CLEANCORETOOLS')
        elif action == "inventory":
            self.parentApp.change_form('COREINVENTORY')
        elif action == 'update':
            # !! TODO
            pass
        elif action == 'remove':
            # !! TODO
            pass
        return

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
            self.parentApp.change_form('STARTTOOLS')
        elif action == 'stop':
            self.parentApp.change_form('STOPTOOLS')
        elif action == 'clean':
            self.parentApp.change_form('CLEANTOOLS')
        elif action == "inventory":
            self.parentApp.change_form('INVENTORY')
        elif action == "update":
            # !! TODO
            pass
        elif action == "remove":
            # !! TODO
            pass
        elif action == "build":
            # !! TODO
            pass
        elif action == "background":
            self.parentApp.change_form('TUTORIALBACKGROUND')
        return

    def system_commands(self, action):
        """ Perform system commands """
        if action == "reset":
            # !! TODO
            pass
        elif action == "upgrade":
            # !! TODO
            pass
        return

    def create(self):
        """ Override method for creating FormBaseNewWithMenu form """
        self.add_handlers({"^T": self.change_forms, "^Q": self.exit})
        self.addfield = self.add(npyscreen.TitleFixedText, name='Date:',
                                 labelColor='DEFAULT', value=Timestamp())
        self.addfield2 = self.add(npyscreen.TitleFixedText, name='Uptime:',
                                  labelColor='DEFAULT', value=Uptime())
        self.addfield3 = self.add(npyscreen.TitleFixedText, name='Containers:',
                                  labelColor='DEFAULT',
                                  value="0 "+" running")
        self.addfield4 = self.add(npyscreen.TitleFixedText, name='Status:',
                                  value="To Be Implemented...")
        self.addfield5 = self.add(npyscreen.TitleFixedText,
                                  name='Core Tools:', labelColor='DANGER',
                                  value="Not built")
        #self.addfield6 = self.add(npyscreen.TitleFixedText, name='Clustered:',
        #                          value="No", labelColor='DEFAULT')
        self.addfield7 = self.add(npyscreen.TitleFixedText, name='Jobs:',
                                  value="To Be Implemented...", labelColor='DEFAULT')
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
        self.m2 = self.add_menu(name="Core Tools", shortcut="c")
        self.m2.addItem(text='Install all latest core tools',
                        onSelect=self.core_tools,
                        arguments=['install'], shortcut='i')
        self.m2.addItem(text='Inventory of core tools',
                        onSelect=self.core_tools,
                        arguments=['inventory'], shortcut='v')
        self.m2.addItem(text='Build all core tools',
                        onSelect=self.core_tools,
                        arguments=['build'], shortcut='b')
        self.m2.addItem(text='Update all core tools (To Be Implemented...)',
                        onSelect=self.core_tools,
                        arguments=['update'], shortcut='u')
        self.m2.addItem(text='Start core tools',
                        onSelect=self.core_tools,
                        arguments=['start'], shortcut='s')
        self.m2.addItem(text='Stop core tools',
                        onSelect=self.core_tools,
                        arguments=['stop'], shortcut='p')
        self.m2.addItem(text='Clean core tools',
                        onSelect=self.core_tools,
                        arguments=['clean'], shortcut='c')
        self.m2.addItem(text='Remove all core tools (To Be Implemented...)',
                        onSelect=self.core_tools,
                        arguments=['remove'], shortcut='r')
        self.m3 = self.add_menu(name="Plugins", shortcut="p")
        self.m3.addItem(text='Add new plugin',
                        onSelect=self.perform_action,
                        arguments=['add'], shortcut='a')
        self.m3.addItem(text='Inventory of installed plugins',
                        onSelect=self.perform_action,
                        arguments=['inventory'], shortcut='i')
        self.m3.addItem(text='Update plugins (To Be Implemented...)',
                        onSelect=self.perform_action,
                        arguments=['update'], shortcut='u')
        self.m3.addItem(text='Remove plugins (To Be Implemented...)',
                        onSelect=self.perform_action,
                        arguments=['remove'], shortcut='r')
        self.m3.addItem(text='Build plugins (To Be Implemented...)',
                        onSelect=self.perform_action,
                        arguments=['build'], shortcut='b')
        self.m3.addItem(text='Start plugin tools',
                        onSelect=self.perform_action,
                        arguments=['start'], shortcut='s')
        self.m3.addItem(text='Stop plugin tools',
                        onSelect=self.perform_action,
                        arguments=['stop'], shortcut='p')
        self.m3.addItem(text='Clean plugin tools',
                        onSelect=self.perform_action,
                        arguments=['clean'], shortcut='c')
        self.m3.addItem(text='Services Running', onSelect=self.services_form,
                        arguments=[])
        self.m4 = self.add_menu(name="Logs (To Be Implemented...)", shortcut="l")
        self.m5 = self.add_menu(name="System Commands (To Be Implemented...)", shortcut="s")
        self.m5.addItem(text='Reset (To Be Implemented...)',
                        onSelect=self.system_commands,
                        arguments=['reset'], shortcut='r')
        self.m5.addItem(text='Upgrade (To Be Implemented...)',
                        onSelect=self.system_commands,
                        arguments=['upgrade'], shortcut='u')
        self.m6 = self.add_menu(name="Tutorials", shortcut="t")
        self.s1 = self.m6.addNewSubmenu(name="About Vent", shortcut='v')
        self.s1.addItem(text="Background", onSelect=self.perform_action,
                        arguments=['background'], shortcut='b')
        self.s1.addItem(text="Terminology", shortcut='t')
        self.s1.addItem(text="Getting Setup", shortcut='s')
        self.s2 = self.m6.addNewSubmenu(name="Working with Cores", shortcut='c')
        self.s2.addItem(text="Building Cores", shortcut='b')
        self.s2.addItem(text="Starting Cores", shortcut='c')
        self.s3 = self.m6.addNewSubmenu(name="Working with Plugins", shortcut='p')
        self.s3.addItem(text="Adding Plugins", shortcut='a')
        self.s4 = self.m6.addNewSubmenu(name="Files", shortcut='f')
        self.s4.addItem(text="Adding Files", shortcut='a')
        self.s5 = self.m6.addNewSubmenu(name="Services", shortcut='s')
        self.s5.addItem(text="Setting up Services", shortcut='s')

    def services_form(self, *args, **keywords):
        self.parentApp.change_form("SERVICES")

    def change_forms(self, *args, **keywords):
        """
        Checks which form is currently displayed and toggles it to the other
        one
        """
        if self.name == "Help\t\t\t\t\t\t\t\tPress ^T to toggle main\t\t\t\t\t\tPress ^Q to quit":
            change_to = "MAIN"
        else:
            change_to = "HELP"

        # Tell the VentApp object to change forms.
        self.parentApp.change_form(change_to)
