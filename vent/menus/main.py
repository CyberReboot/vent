import os
import re
import sys
import time
from threading import Thread

import npyscreen
from docker.errors import DockerException
from npyscreen import notify_confirm

from vent.api.actions import Action
from vent.api.menu_helpers import MenuHelper
from vent.helpers.logs import Logger
from vent.helpers.meta import Containers
from vent.helpers.meta import Cpu
from vent.helpers.meta import DropLocation
from vent.helpers.meta import Gpu
from vent.helpers.meta import Images
from vent.helpers.meta import Jobs
from vent.helpers.meta import Timestamp
from vent.helpers.meta import Uptime
from vent.helpers.paths import PathDirs
from vent.menus.add import AddForm
from vent.menus.backup import BackupForm
from vent.menus.editor import EditorForm
from vent.menus.inventory_forms import InventoryCoreToolsForm
from vent.menus.inventory_forms import InventoryToolsForm
from vent.menus.logs import LogsForm
from vent.menus.ntap import CreateNTap
from vent.menus.ntap import DeleteNTap
from vent.menus.ntap import ListNTap
from vent.menus.ntap import NICsNTap
from vent.menus.ntap import StartNTap
from vent.menus.ntap import StopNTap
from vent.menus.services import ServicesForm
from vent.menus.tools import ToolForm


class MainForm(npyscreen.FormBaseNewWithMenus):
    """ Main information landing form for the Vent CLI """

    @staticmethod
    def exit(*args, **kwargs):
        os.system('reset')
        os.system('stty sane')
        try:
            sys.exit(0)
        except SystemExit:  # pragma: no cover
            os._exit(0)

    @staticmethod
    def t_status(core):
        """ Get status of tools for either plugins or core """
        m_helper = MenuHelper()
        repos, tools = m_helper.tools_status(core)
        installed = 0
        custom_installed = 0
        built = 0
        custom_built = 0
        running = 0
        custom_running = 0
        normal = str(len(tools['normal']))
        # determine how many extra instances should be shown for running
        norm = set(tools['normal'])
        inst = set(tools['installed'])
        run_str = str(len(tools['normal']) + len(inst - norm))
        for tool in tools['running']:
            # check for multi instances too for running
            if tool in tools['normal']:
                running += 1
            elif re.sub(r'\d+$', '', tool) in tools['normal']:
                running += 1
            else:
                custom_running += 1
        for tool in tools['built']:
            if tool in tools['normal']:
                built += 1
            else:
                custom_built += 1
        for tool in tools['installed']:
            if tool in tools['normal']:
                installed += 1
            elif re.sub(r'\d+$', '', tool) not in tools['normal']:
                custom_installed += 1
        tools_str = str(running + custom_running) + '/' + run_str + ' running'
        if custom_running > 0:
            tools_str += ' (' + str(custom_running) + ' custom)'
        tools_str += ', ' + str(built + custom_built) + '/' + normal + ' built'
        if custom_built > 0:
            tools_str += ' (' + str(custom_built) + ' custom)'
        tools_str += ', ' + str(installed + custom_installed) + '/' + normal
        tools_str += ' installed'
        if custom_built > 0:
            tools_str += ' (' + str(custom_installed) + ' custom)'
        return tools_str, (running, custom_running, normal, repos)

    def while_waiting(self):
        """ Update fields periodically if nothing is happening """
        # give a little extra time for file descriptors to close
        time.sleep(0.1)

        self.addfield.value = Timestamp()
        self.addfield.display()
        self.addfield2.value = Uptime()
        self.addfield2.display()
        self.addfield3.value = str(len(Containers()))+' running'
        if len(Containers()) > 0:
            self.addfield3.labelColor = 'GOOD'
        else:
            self.addfield3.labelColor = 'DEFAULT'
        self.addfield3.display()

        # update core tool status
        self.addfield5.value, values = MainForm.t_status(True)
        if values[0] + values[1] == 0:
            color = 'DANGER'
            self.addfield4.labelColor = 'CAUTION'
            self.addfield4.value = 'Idle'
        elif values[0] >= int(values[2]):
            color = 'GOOD'
            self.addfield4.labelColor = color
            self.addfield4.value = 'Ready to start jobs'
        else:
            color = 'CAUTION'
            self.addfield4.labelColor = color
            self.addfield4.value = 'Ready to start jobs'
        self.addfield5.labelColor = color

        # update plugin tool status
        plugin_str, values = MainForm.t_status(False)
        plugin_str += ', ' + str(values[3]) + ' plugin(s) installed'
        self.addfield6.value = plugin_str

        # get jobs
        jobs = Jobs()

        # number of jobs, number of tool containers
        self.addfield7.value = str(jobs[0]) + ' jobs running (' + str(jobs[1])
        self.addfield7.value += ' tool containers), ' + str(jobs[2])
        self.addfield7.value += ' completed jobs'

        if jobs[0] > 0:
            self.addfield4.labelColor = 'GOOD'
            self.addfield4.value = 'Processing jobs'
            self.addfield7.labelColor = 'GOOD'
        else:
            self.addfield7.labelColor = 'DEFAULT'
        self.addfield4.display()
        self.addfield5.display()
        self.addfield6.display()
        self.addfield7.display()

        # if file drop location changes deal with it
        logger = Logger(__name__)
        status = (False, None)
        if self.file_drop.value != DropLocation()[1]:
            logger.info('Starting: file drop restart')
            try:
                self.file_drop.value = DropLocation()[1]
                logger.info('Path given: ' + str(self.file_drop.value))
                # restart if the path is valid
                if DropLocation()[0]:
                    status = self.api_action.clean(name='file_drop')
                    status = self.api_action.prep_start(name='file_drop')
                else:
                    logger.error('file drop path name invalid' +
                                 DropLocation()[1])
                if status[0]:
                    tool_d = status[1]
                    status = self.api_action.start(tool_d)
                    logger.info('Status of file drop restart: ' +
                                str(status[0]))
            except Exception as e:  # pragma no cover
                logger.error('file drop restart failed with error: ' + str(e))
            logger.info('Finished: file drop restart')
        self.file_drop.display()
        return

    @staticmethod
    def core_tools(action):
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
            info_str = ''
            while thr.is_alive():
                if orig_type == 'containers':
                    info = diff(Containers(), original)
                elif orig_type == 'images':
                    info = diff(Images(), original)
                if info:
                    info_str = ''
                for entry in info:
                    # TODO limit length of info_str to fit box
                    info_str += entry[0]+': '+entry[1]+'\n'
                npyscreen.notify_wait(info_str, title=title)
                time.sleep(1)
            return

        if action == 'install':
            original_images = Images()
            m_helper = MenuHelper()
            thr = Thread(target=m_helper.cores, args=(),
                         kwargs={'action': 'install'})
            popup(original_images, 'images', thr,
                  'Please wait, installing core containers...')
            notify_confirm('Done installing core containers (any'
                           ' already installed tools untouched).',
                           title='Installed core containers')
        return

    def add_form(self, form, form_name, form_args):
        """ Add new form and switch to it """
        self.parentApp.addForm(form_name, form, **form_args)
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
        form = ToolForm
        s_action = action.split('_')[0]
        if 'core' in action:
            form_action = s_action + ' (only core tools are shown)'
            form_name = s_action.title() + ' core tools'
            cores = True
        else:
            form_action = s_action + ' (only plugin tools are shown)'
            form_name = s_action.title() + ' tools'
            cores = False
        a_type = 'containers'
        if s_action in ['build']:
            a_type = 'images'
        forms = [action.upper() + 'TOOLS']
        form_args = {'color': 'CONTROL',
                     'names': [s_action],
                     'name': form_name,
                     'action_dict': {'action_name': s_action,
                                     'present_t': s_action + 'ing ' + a_type,
                                     'past_t': s_action.title() + ' ' + a_type,
                                     'action': form_action,
                                     'type': a_type,
                                     'cores': cores}}
        # grammar rules
        vowels = ['a', 'e', 'i', 'o', 'u']

        # consonant-vowel-consonant ending
        # Eg: stop -> stopping
        if s_action[-1] not in vowels and \
           s_action[-2] in vowels and \
           s_action[-3] not in vowels:
            form_args['action_dict']['present_t'] = s_action + \
                s_action[-1] + 'ing ' + a_type

        # word ends with a 'e'
        # eg: remove -> removing
        if s_action[-1] == 'e':
            form_args['action_dict']['present_t'] = s_action[:-1] \
                + 'ing ' + a_type

        if s_action == 'start':
            form_args['names'].append('prep_start')
        elif s_action == 'configure':
            form_args['names'].pop()
            form_args['names'].append('get_configure')
            form_args['names'].append('save_configure')
            form_args['names'].append('restart_tools')
        if action == 'add':
            form = AddForm
            forms = ['ADD', 'ADDOPTIONS', 'CHOOSETOOLS']
            form_args['name'] = 'Add plugins'
            form_args['name'] += '\t'*6 + '^Q to quit'
        elif action == 'inventory':
            form = InventoryToolsForm
            forms = ['INVENTORY']
            form_args = {'color': 'STANDOUT', 'name': 'Inventory of tools'}
        elif action == 'logs':
            form = LogsForm
            forms = ['LOGS']
            form_args = {'color': 'STANDOUT', 'name': 'Logs'}
        elif action == 'services_core':
            form = ServicesForm
            forms = ['SERVICES']
            form_args = {'color': 'STANDOUT',
                         'name': 'Core Services',
                         'core': True}
        elif action == 'services':
            form = ServicesForm
            forms = ['SERVICES']
            form_args = {'color': 'STANDOUT',
                         'name': 'Plugin Services',
                         'core': False}
        elif action == 'services_external':
            form = ServicesForm
            forms = ['SERVICES']
            form_args = {'color': 'STANDOUT',
                         'name': 'External Services',
                         'core': False,
                         'external': True}
        elif action == 'inventory_core':
            form = InventoryCoreToolsForm
            forms = ['COREINVENTORY']
            form_args = {'color': 'STANDOUT',
                         'name': 'Inventory of core tools'}
        form_args['name'] += '\t'*8 + '^T to toggle main'
        if s_action in self.view_togglable:
            form_args['name'] += '\t'*8 + '^V to toggle group view'
        try:
            self.remove_forms(forms)
            thr = Thread(target=self.add_form, args=(),
                         kwargs={'form': form,
                                 'form_name': forms[0],
                                 'form_args': form_args})
            thr.start()
            while thr.is_alive():
                npyscreen.notify('Please wait, loading form...',
                                 title='Loading')
                time.sleep(1)
        except Exception as e:  # pragma: no cover
            pass
        return

    def switch_tutorial(self, action):
        """ Tutorial forms """
        if action == 'background':
            self.parentApp.change_form('TUTORIALBACKGROUND')
        elif action == 'terminology':
            self.parentApp.change_form('TUTORIALTERMINOLOGY')
        elif action == 'setup':
            self.parentApp.change_form('TUTORIALGETTINGSETUP')
        elif action == 'building_cores':
            self.parentApp.change_form('TUTORIALBUILDINGCORES')
        elif action == 'starting_cores':
            self.parentApp.change_form('TUTORIALSTARTINGCORES')
        elif action == 'adding_plugins':
            self.parentApp.change_form('TUTORIALADDINGPLUGINS')
        elif action == 'adding_files':
            self.parentApp.change_form('TUTORIALADDINGFILES')
        elif action == 'basic_troubleshooting':
            self.parentApp.change_form('TUTORIALTROUBLESHOOTING')
        return

    def system_commands(self, action):
        """ Perform system commands """
        if action == 'backup':
            status = self.api_action.backup()
            if status[0]:
                notify_confirm('Vent backup successful')
            else:
                notify_confirm('Vent backup could not be completed')
        elif action == 'configure':
            form_args = {'name': 'Change vent configuration',
                         'get_configure': self.api_action.get_configure,
                         'save_configure': self.api_action.save_configure,
                         'restart_tools': self.api_action.restart_tools,
                         'vent_cfg': True}
            add_kargs = {'form': EditorForm,
                         'form_name': 'CONFIGUREVENT',
                         'form_args': form_args}
            self.add_form(**add_kargs)
        elif action == 'reset':
            okay = npyscreen.notify_ok_cancel(
                "This factory reset will remove ALL of Vent's user data, "
                'containers, and images. Are you sure?',
                title='Confirm system command')
            if okay:
                status = self.api_action.reset()
                if status[0]:
                    notify_confirm('Vent reset complete. '
                                   'Press OK to exit Vent Manager console.')
                else:
                    notify_confirm(status[1])
                MainForm.exit()
        elif action == 'gpu':
            gpu = Gpu(pull=True)
            if gpu[0]:
                notify_confirm('GPU detection successful. '
                               'Found: ' + gpu[1])
            else:
                if gpu[1] == 'Unknown':
                    notify_confirm('Unable to detect GPUs, try `make gpu` '
                                   'from the vent repository directory. '
                                   'Error: ' + str(gpu[2]))
                else:
                    notify_confirm('No GPUs detected.')
        elif action == 'restore':
            backup_dir_home = os.path.expanduser('~')
            backup_dirs = [f for f in os.listdir(backup_dir_home) if
                           f.startswith('.vent-backup')]
            form_args = {'restore': self.api_action.restore,
                         'dirs': backup_dirs,
                         'name': 'Pick a version to restore from' + '\t'*8 +
                                 '^T to toggle main',
                         'color': 'CONTROL'}
            add_kargs = {'form': BackupForm,
                         'form_name': 'CHOOSEBACKUP',
                         'form_args': form_args}
            self.add_form(**add_kargs)
        elif action == 'swarm':
            # !! TODO
            # add notify_cancel_ok popup once implemented
            pass
        elif action == 'upgrade':
            # !! TODO
            # add notify_cancel_ok popup once implemented
            pass
        # deal with all network tap actions
        elif 'ntap' in action:
            # check if the tool is installed, built, and running
            output = self.api_action.tool_status_output('network_tap')

            # create a dict with substring as keys and forms as values
            ntap_form = {'create': CreateNTap,
                         'delete': DeleteNTap,
                         'list': ListNTap,
                         'nics': NICsNTap,
                         'start': StartNTap,
                         'stop': StopNTap}
            if output[0]:
                if output[1]:
                    notify_confirm(output[1])
                else:
                    # action regarding ntap come in the form of 'ntapcreate'
                    # 'ntapdelete', etc
                    tap_action = action.split('ntap')[1]
                    form_args = {'color': 'CONTROL',
                                 'name': 'Network Tap Interface ' +
                                         tap_action + '\t'*6 +
                                         '^T to toggle main'}
                    self.add_form(ntap_form[tap_action], 'Network Tap ' +
                                  tap_action.title(), form_args)

        return

    def create(self):
        """ Override method for creating FormBaseNewWithMenu form """
        try:
            self.api_action = Action()

        except DockerException as de:  # pragma: no cover
            notify_confirm(str(de),
                           title='Docker Error',
                           form_color='DANGER',
                           wrap=True)
            MainForm.exit()

        self.add_handlers({'^T': self.help_form, '^Q': MainForm.exit})
        # all forms that can toggle view by group
        self.view_togglable = ['inventory', 'remove', 'update', 'enable',
                               'disable', 'build']

        #######################
        # MAIN SCREEN WIDGETS #
        #######################

        self.addfield = self.add(npyscreen.TitleFixedText, name='Date:',
                                 labelColor='DEFAULT', value=Timestamp())
        self.addfield2 = self.add(npyscreen.TitleFixedText, name='Uptime:',
                                  labelColor='DEFAULT', value=Uptime())
        self.cpufield = self.add(npyscreen.TitleFixedText,
                                 name='Logical CPUs:',
                                 labelColor='DEFAULT', value=Cpu())
        self.gpufield = self.add(npyscreen.TitleFixedText, name='GPUs:',
                                 labelColor='DEFAULT', value=Gpu()[1])
        self.location = self.add(npyscreen.TitleFixedText,
                                 name='User Data:',
                                 value=PathDirs().meta_dir,
                                 labelColor='DEFAULT')
        self.file_drop = self.add(npyscreen.TitleFixedText,
                                  name='File Drop:',
                                  value=DropLocation()[1],
                                  labelColor='DEFAULT')
        self.addfield3 = self.add(npyscreen.TitleFixedText, name='Containers:',
                                  labelColor='DEFAULT',
                                  value='0 '+' running')
        self.addfield4 = self.add(npyscreen.TitleFixedText, name='Status:',
                                  labelColor='CAUTION',
                                  value='Idle')
        self.addfield5 = self.add(npyscreen.TitleFixedText,
                                  name='Core Tools:', labelColor='DANGER',
                                  value='Not built')
        self.addfield6 = self.add(npyscreen.TitleFixedText,
                                  name='Plugin Tools:', labelColor='DEFAULT',
                                  value='Not built')
        self.addfield7 = self.add(npyscreen.TitleFixedText, name='Jobs:',
                                  value='0 jobs running (0 tool containers),'
                                  ' 0 completed jobs', labelColor='DEFAULT')
        self.multifield1 = self.add(npyscreen.MultiLineEdit, max_height=22,
                                    editable=False, value="""

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
        self.m2 = self.add_menu(name='Core Tools', shortcut='c')
        self.m2.addItem(text='Add all latest core tools',
                        onSelect=MainForm.core_tools,
                        arguments=['install'], shortcut='i')
        self.m2.addItem(text='Build core tools',
                        onSelect=self.perform_action,
                        arguments=['build_core'], shortcut='b')
        self.m2.addItem(text='Clean core tools',
                        onSelect=self.perform_action,
                        arguments=['clean_core'], shortcut='c')
        self.m2.addItem(text='Configure core tools',
                        onSelect=self.perform_action,
                        arguments=['configure_core'], shortcut='t')
        self.m2.addItem(text='Disable core tools',
                        onSelect=self.perform_action,
                        arguments=['disable_core'], shortcut='d')
        self.m2.addItem(text='Enable core tools',
                        onSelect=self.perform_action,
                        arguments=['enable_core'], shortcut='e')
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
        self.m3 = self.add_menu(name='Plugins', shortcut='p')
        self.m3.addItem(text='Add new plugin',
                        onSelect=self.perform_action,
                        arguments=['add'], shortcut='a')
        self.m3.addItem(text='Build plugin tools',
                        onSelect=self.perform_action,
                        arguments=['build'], shortcut='b')
        self.m3.addItem(text='Clean plugin tools',
                        onSelect=self.perform_action,
                        arguments=['clean'], shortcut='c')
        self.m3.addItem(text='Configure plugin tools',
                        onSelect=self.perform_action,
                        arguments=['configure'], shortcut='t')
        self.m3.addItem(text='Disable plugin tools',
                        onSelect=self.perform_action,
                        arguments=['disable'], shortcut='d')
        self.m3.addItem(text='Enable plugin tools',
                        onSelect=self.perform_action,
                        arguments=['enable'], shortcut='e')
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
        self.m4 = self.add_menu(name='Logs', shortcut='l')
        self.m4.addItem(text='Get container logs', arguments=['logs'],
                        onSelect=self.perform_action)

        # Services Menu Items
        self.m5 = self.add_menu(name='Services Running', shortcut='s')
        self.m5.addItem(text='Core Services', onSelect=self.perform_action,
                        arguments=['services_core'], shortcut='c')
        self.m5.addItem(text='External Services', onSelect=self.perform_action,
                        arguments=['services_external'], shortcut='e')
        self.m5.addItem(text='Plugin Services',
                        onSelect=self.perform_action,
                        arguments=['services'], shortcut='p')

        # System Commands Menu Items
        self.m6 = self.add_menu(name='System Commands', shortcut='y')
        self.m6.addItem(text='Backup', onSelect=self.system_commands,
                        arguments=['backup'], shortcut='b')
        self.m6.addItem(text='Change vent configuration',
                        onSelect=self.system_commands, arguments=['configure'],
                        shortcut='c')
        self.m6.addItem(text='Detect GPUs', onSelect=self.system_commands,
                        arguments=['gpu'], shortcut='g')
        self.m6.addItem(text='Enable Swarm Mode (To Be Implemented...)',
                        onSelect=self.system_commands,
                        arguments=['swarm'], shortcut='s')
        self.m6.addItem(text='Factory reset', onSelect=self.system_commands,
                        arguments=['reset'], shortcut='r')
        self.s6 = self.m6.addNewSubmenu(name='Network Tap Interface',
                                        shortcut='n')
        self.m6.addItem(text='Restore', onSelect=self.system_commands,
                        arguments=['restore'], shortcut='t')
        self.m6.addItem(text='Upgrade (To Be Implemented...)',
                        onSelect=self.system_commands,
                        arguments=['upgrade'], shortcut='u')
        self.s6.addItem(text='Create', onSelect=self.system_commands,
                        shortcut='c', arguments=['ntapcreate'])
        self.s6.addItem(text='Delete', onSelect=self.system_commands,
                        shortcut='d', arguments=['ntapdelete'])
        self.s6.addItem(text='List', onSelect=self.system_commands,
                        shortcut='l', arguments=['ntaplist'])
        self.s6.addItem(text='NICs', onSelect=self.system_commands,
                        shortcut='n', arguments=['ntapnics'])
        self.s6.addItem(text='Start', onSelect=self.system_commands,
                        shortcut='s', arguments=['ntapstart'])
        self.s6.addItem(text='Stop', onSelect=self.system_commands,
                        shortcut='t', arguments=['ntapstop'])

        # Tutorial Menu Items
        self.m7 = self.add_menu(name='Tutorials', shortcut='t')
        self.s1 = self.m7.addNewSubmenu(name='About Vent', shortcut='v')
        self.s1.addItem(text='Background', onSelect=self.switch_tutorial,
                        arguments=['background'], shortcut='b')
        self.s1.addItem(text='Terminology', onSelect=self.switch_tutorial,
                        arguments=['terminology'], shortcut='t')
        self.s1.addItem(text='Getting Setup', onSelect=self.switch_tutorial,
                        arguments=['setup'], shortcut='s')
        self.s2 = self.m7.addNewSubmenu(name='Working with Cores',
                                        shortcut='c')
        self.s2.addItem(text='Building Cores', onSelect=self.switch_tutorial,
                        arguments=['building_cores'], shortcut='b')
        self.s2.addItem(text='Starting Cores', onSelect=self.switch_tutorial,
                        arguments=['starting_cores'], shortcut='c')
        self.s3 = self.m7.addNewSubmenu(name='Working with Plugins',
                                        shortcut='p')
        self.s3.addItem(text='Adding Plugins', onSelect=self.switch_tutorial,
                        arguments=['adding_plugins'], shortcut='a')
        self.s4 = self.m7.addNewSubmenu(name='Files', shortcut='f')
        self.s4.addItem(text='Adding Files', onSelect=self.switch_tutorial,
                        arguments=['adding_files'], shortcut='a')
        self.s5 = self.m7.addNewSubmenu(name='Help', shortcut='s')
        self.s5.addItem(text='Basic Troubleshooting',
                        onSelect=self.switch_tutorial,
                        arguments=['basic_troubleshooting'], shortcut='t')

    def help_form(self, *args, **keywords):
        """ Toggles to help """
        self.parentApp.change_form('HELP')
