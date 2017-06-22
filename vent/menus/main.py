import docker
import npyscreen
import os
import shutil
import sys
import threading
import time

from docker.errors import DockerException
from npyscreen import notify_confirm

from vent.api.actions import Action
from vent.helpers.meta import Containers
from vent.helpers.meta import Core
from vent.helpers.meta import Cpu
from vent.helpers.meta import Gpu
from vent.helpers.meta import Images
from vent.helpers.meta import Jobs
from vent.helpers.meta import Timestamp
from vent.helpers.meta import Uptime
from vent.menus.add import AddForm
from vent.menus.inventory_forms import InventoryCoreToolsForm
from vent.menus.inventory_forms import InventoryToolsForm
from vent.menus.tool_forms import BuildCoreToolsForm
from vent.menus.tool_forms import BuildToolsForm
from vent.menus.tool_forms import CleanCoreToolsForm
from vent.menus.tool_forms import CleanToolsForm
from vent.menus.tool_forms import RemoveCoreToolsForm
from vent.menus.tool_forms import RemoveToolsForm
from vent.menus.tool_forms import StartCoreToolsForm
from vent.menus.tool_forms import StartToolsForm
from vent.menus.tool_forms import StopCoreToolsForm
from vent.menus.tool_forms import StopToolsForm
from vent.menus.tool_forms import UpdateCoreToolsForm
from vent.menus.tool_forms import UpdateToolsForm


class MainForm(npyscreen.FormBaseNewWithMenus):
    """ Main information landing form for the Vent CLI """
    def exit(self, *args, **keywords):
        os.system('reset')
        os.system('stty sane')
        try:
            sys.exit(0)
        except SystemExit:  # pragma: no cover
            os._exit(0)

    def while_waiting(self):
        """ Update fields periodically if nothing is happening """
        # clean up forms with dynamic data
        self.parentApp.remove_forms()
        self.parentApp.add_forms()

        # give a little extra time for file descriptors to close
        time.sleep(0.1)

        try:
            current_path = os.getcwd()
        except Exception as e:  # pragma: no cover
            self.exit()
        self.addfield.value = Timestamp()
        self.addfield.display()
        self.addfield2.value = Uptime()
        self.addfield2.display()
        self.addfield3.value = str(len(Containers()))+" running"
        if len(Containers()) > 0:
            self.addfield3.labelColor = "GOOD"
        else:
            self.addfield3.labelColor = "DEFAULT"
        self.addfield3.display()

        # set core value string
        core = Core()
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
            self.addfield4.labelColor = "CAUTION"
            self.addfield4.value = "Idle"
        elif running >= int(normal):
            color = "GOOD"
            self.addfield4.labelColor = color
            self.addfield4.value = "Ready to start jobs"
        else:
            color = "CAUTION"
            self.addfield4.labelColor = color
            self.addfield4.value = "Ready to start jobs"
        self.addfield5.labelColor = color

        # get jobs
        jobs = Jobs()
        # number of jobs, number of tool containers
        self.addfield6.value = str(jobs[0])+" jobs running ("+str(jobs[1])+" tool containers), "+str(jobs[2])+" completed jobs"

        # TODO check if there are jobs running and update addfield4
        if jobs[0] > 0:
            self.addfield4.labelColor = "GOOD"
            self.addfield4.value = "Processing jobs"
            self.addfield6.labelColor = "GOOD"
        else:
            self.addfield6.labelColor = "DEFAULT"
        self.addfield4.display()
        self.addfield5.display()
        self.addfield6.display()

        os.chdir(current_path)
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

        if action == 'install':
            original_images = Images()
            thr = threading.Thread(target=self.api_action.cores, args=(),
                                   kwargs={"action":"install"})
            popup(original_images, "images", thr,
                  'Please wait, installing core containers...')
            notify_confirm("Done installing core containers.",
                           title='Installed core containers')
        return

    def add_form(self, form, form_name, form_args):
        """ Add new form and switch to it """
        self.parentApp.addForm(form_name,
                               form,
                               **form_args)
        self.parentApp.change_form(form_name)
        return

    def remove_forms(self, form_names):
        """ Remove all forms supplied """
        for form in form_names:
            try:
                self.parentApp.removeForm(form)
            except Exception as e:  # pragma: no cover
                pass
        return

    def perform_action(self, action):
        """ Perform actions in the api from the CLI """
        forms = []
        form_args = {'color': 'CONTROL'}
        if action == 'add':
            form = AddForm
            forms = ['ADD', 'ADDOPTIONS', 'CHOOSETOOLS']
            form_args['name'] = "Add plugins\t\t\t\t\t\t\t\tPress ^T to toggle help\t\t\t\t\t\tPress ^Q to quit"
        elif action == "build":
            form = BuildToolsForm
            forms = ['BUILDTOOLS']
            form_args['name'] = "Build tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == 'start':
            form = StartToolsForm
            forms = ['STARTTOOLS']
            form_args['name'] = "Start tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == 'stop':
            form = StopToolsForm
            forms = ['STOPTOOLS']
            form_args['name'] = "Stop tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == 'clean':
            form = CleanToolsForm
            forms = ['CLEANTOOLS']
            form_args['name'] = "Clean tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == "inventory":
            form = InventoryToolsForm
            forms = ['INVENTORY']
            form_args = {'color': "STANDOUT",
                         'name': "Inventory of tools\t\t\t\t\t\t\t\tPress ^T"
                                 " to toggle main"
                        }
        elif action == "update":
            form = UpdateToolsForm
            forms = ['UPDATETOOLS']
            form_args['name'] = "Update tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == "remove":
            form = RemoveToolsForm
            forms = ['REMOVETOOLS']
            form_args['name'] = "Remove tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == 'build_core':
            form = BuildCoreToolsForm
            forms = ['BUILDCORETOOLS']
            form_args['name'] = "Build core tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == 'start_core':
            form = StartCoreToolsForm
            forms = ['STARTCORETOOLS']
            form_args['name'] = "Start core tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == 'stop_core':
            form = StopCoreToolsForm
            forms = ['STOPCORETOOLS']
            form_args['name'] = "Stop core tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == 'clean_core':
            form = CleanCoreToolsForm
            forms = ['CLEANCORETOOLS']
            form_args['name'] = "Clean core tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == "inventory_core":
            form = InventoryCoreToolsForm
            forms = ['COREINVENTORY']
            form_args = {'color': "STANDOUT",
                         'name': "Inventory of core tools\t\t\t\t\t\t\t\tPress"
                                 " ^T to toggle main"
                        }
        elif action == 'update_core':
            form = UpdateCoreToolsForm
            forms = ['UPDATECORETOOLS']
            form_args['name'] = "Update core tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        elif action == 'remove_core':
            form = RemoveCoreToolsForm
            forms = ['REMOVECORETOOLS']
            form_args['name'] = "Remove core tools\t\t\t\t\t\t\t\tPress ^T to toggle main"
        try:
            self.remove_forms(forms)
            self.add_form(form, forms[0], form_args)
        except Exception as e:  # pragma: no cover
            pass
        return

    def switch_tutorial(self, action):
        """ Tutorial forms """
        if action == "background":
            self.parentApp.change_form('TUTORIALBACKGROUND')
        elif action == "terminology":
            self.parentApp.change_form('TUTORIALTERMINOLOGY')
        elif action == "setup":
            self.parentApp.change_form('TUTORIALGETTINGSETUP')
        elif action == "building_cores":
            self.parentApp.change_form('TUTORIALBUILDINGCORES')
        elif action == "starting_cores":
            self.parentApp.change_form('TUTORIALSTARTINGCORES')
        elif action == "adding_plugins":
            self.parentApp.change_form('TUTORIALADDINGPLUGINS')
        elif action == "adding_files":
            self.parentApp.change_form('TUTORIALADDINGFILES')
        elif action == "setting_up_services":
            self.parentApp.change_form('TUTORIALSETTINGUPSERVICES')
        return

    def system_commands(self, action):
        """ Perform system commands """
        if action == "reset":
            okay = npyscreen.notify_ok_cancel(
                    "This factory reset will remove ALL of Vent's user data, "
                    "containers, and images. Are you sure?",
                    title="Confirm system command")
            if okay:
                failed = False
                try:
                    d_cli = docker.from_env()
                except Exception as e:  # pragma: no cover
                    notify_confirm("Error connecting to Docker: " + repr(e))
                    self.exit()

                # remove containers
                try:
                    list = d_cli.containers.list(filters={'label':'vent'},
                                                 all=True)
                    for c in list:
                        c.remove(force=True)
                except Exception as e:  # pragma: no cover
                    notify_confirm("Error deleting Vent containers: " +
                                   repr(e))
                    failed = True

                # remove images
                try:
                    list = d_cli.images.list(filters={'label':'vent'},
                                             all=True)
                    for i in list:
                        d_cli.images.remove(image=i.id, force=True)
                except Exception as e:  # pragma: no cover
                    notify_confirm("Error deleting Vent images: " + repr(e))
                    failed = True

                # remove .vent folder
                try:
                    shutil.rmtree(os.path.join(os.path.expanduser('~'),
                                               '.vent'))
                except Exception as e:  # pragma: no cover
                    notify_confirm("Error deleting Vent data: " + repr(e))
                    failed = True

                if not failed:
                    notify_confirm("Vent reset complete. "
                                   "Press OK to exit Vent Manager console.")
                self.exit()
        elif action == "upgrade":
            # !! TODO
            pass
        return

    def create(self):
        """ Override method for creating FormBaseNewWithMenu form """
        try:
            self.api_action = Action()
        except DockerException as de:  # pragma: no cover
            notify_confirm(str(de),
                           title="Docker Error",
                           form_color='DANGER',
                           wrap=True)
            self.exit()

        self.add_handlers({"^T": self.help_form, "^Q": self.exit})

        #######################
        # MAIN SCREEN WIDGETS #
        #######################

        self.addfield = self.add(npyscreen.TitleFixedText, name='Date:',
                                 labelColor='DEFAULT', value=Timestamp())
        self.addfield2 = self.add(npyscreen.TitleFixedText, name='Uptime:',
                                  labelColor='DEFAULT', value=Uptime())
        self.cpufield = self.add(npyscreen.TitleFixedText, name='Logical CPUs:',
                                 labelColor='DEFAULT', value=Cpu())
        self.gpufield = self.add(npyscreen.TitleFixedText, name='GPUs:',
                                 labelColor='DEFAULT', value=Gpu())
        self.addfield3 = self.add(npyscreen.TitleFixedText, name='Containers:',
                                  labelColor='DEFAULT',
                                  value="0 "+" running")
        self.addfield4 = self.add(npyscreen.TitleFixedText, name='Status:',
                                  labelColor='CAUTION',
                                  value="Idle")
        self.addfield5 = self.add(npyscreen.TitleFixedText,
                                  name='Core Tools:', labelColor='DANGER',
                                  value="Not built")
        self.addfield6 = self.add(npyscreen.TitleFixedText, name='Jobs:',
                                  value="0 jobs running (0 tool containers), 0 completed jobs", labelColor='DEFAULT')
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

        ################
        # MENU OPTIONS #
        ################

        # Core Tools Menu Items
        self.m2 = self.add_menu(name="Core Tools", shortcut="c")
        self.m2.addItem(text='Add all latest core tools',
                        onSelect=self.core_tools,
                        arguments=['install'], shortcut='i')
        self.m2.addItem(text='Build core tools',
                        onSelect=self.perform_action,
                        arguments=['build_core'], shortcut='b')
        self.m2.addItem(text='Clean core tools',
                        onSelect=self.perform_action,
                        arguments=['clean_core'], shortcut='c')
        self.m2.addItem(text='Inventory of core tools',
                        onSelect=self.perform_action,
                        arguments=['inventory_core'], shortcut='v')
        self.m2.addItem(text='Remove core tools',
                        onSelect=self.perform_action,
                        arguments=['remove_core'], shortcut='r')
        self.m2.addItem(text='Start core tools',
                        onSelect=self.perform_action,
                        arguments=['start_core'], shortcut='s')
        self.m2.addItem(text='Stop core tools',
                        onSelect=self.perform_action,
                        arguments=['stop_core'], shortcut='p')
        self.m2.addItem(text='Update core tools',
                        onSelect=self.perform_action,
                        arguments=['update_core'], shortcut='u')

        # Plugin Menu Items
        self.m3 = self.add_menu(name="Plugins", shortcut="p")
        self.m3.addItem(text='Add new plugin',
                        onSelect=self.perform_action,
                        arguments=['add'], shortcut='a')
        self.m3.addItem(text='Build plugin tools',
                        onSelect=self.perform_action,
                        arguments=['build'], shortcut='b')
        self.m3.addItem(text='Clean plugin tools',
                        onSelect=self.perform_action,
                        arguments=['clean'], shortcut='c')
        self.m3.addItem(text='Inventory of installed plugins',
                        onSelect=self.perform_action,
                        arguments=['inventory'], shortcut='i')
        self.m3.addItem(text='Remove plugins',
                        onSelect=self.perform_action,
                        arguments=['remove'], shortcut='r')
        self.m3.addItem(text='Start plugin tools',
                        onSelect=self.perform_action,
                        arguments=['start'], shortcut='s')
        self.m3.addItem(text='Stop plugin tools',
                        onSelect=self.perform_action,
                        arguments=['stop'], shortcut='p')
        self.m3.addItem(text='Update plugins',
                        onSelect=self.perform_action,
                        arguments=['update'], shortcut='u')

        # Log Menu Items
        self.m4 = self.add_menu(name="Logs", shortcut="l")
        self.m4.addItem(text='Get container logs', arguments=[],
                        onSelect=self.logs_form)

        # Services Menu Items
        self.m5 = self.add_menu(name="Services Running", shortcut='s')
        self.m5.addItem(text='Core Services', onSelect=self.services_form,
                        arguments=['core'], shortcut='c')
        self.m5.addItem(text='Plugin Services (To be implemented...)',
                        onSelect=self.services_form,
                        arguments=['plugins'], shortcut='p')

        # System Commands Menu Items
        self.m6 = self.add_menu(name="System Commands")
        self.m6.addItem(text='Factory reset', onSelect=self.system_commands,
                        arguments=['reset'], shortcut='r')
        self.m6.addItem(text='Upgrade (To Be Implemented...)',
                        onSelect=self.system_commands,
                        arguments=['upgrade'], shortcut='u')

        # Tutorial Menu Items
        self.m7 = self.add_menu(name="Tutorials", shortcut="t")
        self.s1 = self.m7.addNewSubmenu(name="About Vent", shortcut='v')
        self.s1.addItem(text="Background", onSelect=self.switch_tutorial,
                        arguments=['background'], shortcut='b')
        self.s1.addItem(text="Terminology", onSelect=self.switch_tutorial,
                        arguments=['terminology'], shortcut='t')
        self.s1.addItem(text="Getting Setup", onSelect=self.switch_tutorial,
                        arguments=['setup'], shortcut='s')
        self.s2 = self.m7.addNewSubmenu(name="Working with Cores",
                                        shortcut='c')
        self.s2.addItem(text="Building Cores", onSelect=self.switch_tutorial,
                        arguments=['building_cores'], shortcut='b')
        self.s2.addItem(text="Starting Cores", onSelect=self.switch_tutorial,
                        arguments=['starting_cores'], shortcut='c')
        self.s3 = self.m7.addNewSubmenu(name="Working with Plugins",
                                        shortcut='p')
        self.s3.addItem(text="Adding Plugins", onSelect=self.switch_tutorial,
                        arguments=['adding_plugins'], shortcut='a')
        self.s4 = self.m7.addNewSubmenu(name="Files", shortcut='f')
        self.s4.addItem(text="Adding Files", onSelect=self.switch_tutorial,
                        arguments=['adding_files'], shortcut='a')
        self.s5 = self.m7.addNewSubmenu(name="Services", shortcut='s')
        self.s5.addItem(text="Setting up Services",
                        onSelect=self.switch_tutorial,
                        arguments=['setting_up_services'], shortcut='s')

    def services_form(self, service_type):
        """ Change to the services form for core or plugins """
        # TODO break out services and add services from plugins
        if service_type == 'core':
            self.parentApp.change_form("SERVICES")
        elif service_type == 'plugins':
            self.parentApp.change_form("SERVICES")

    def logs_form(self, *args, **keywords):
        """ Toggles to logs """
        self.parentApp.change_form("LOGS")

    def help_form(self, *args, **keywords):
        """ Toggles to help """
        self.parentApp.change_form("HELP")
