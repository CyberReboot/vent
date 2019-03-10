import os
import sys
import time
from threading import Thread

import npyscreen
from docker.errors import DockerException
from npyscreen import notify_confirm

from vent.api.system import System
from vent.helpers.logs import Logger
from vent.helpers.meta import Containers
from vent.helpers.meta import Cpu
from vent.helpers.meta import DropLocation
from vent.helpers.meta import Gpu
from vent.helpers.meta import Timestamp
from vent.helpers.meta import Uptime
from vent.helpers.paths import PathDirs
from vent.menus.add import AddForm
from vent.menus.backup import BackupForm
from vent.menus.editor import EditorForm
from vent.menus.inventory_forms import InventoryToolsForm
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

        # if file drop location changes deal with it
        logger = Logger(__name__)
        if self.file_drop.value != DropLocation()[1]:
            logger.info('Starting: file drop restart')
            try:
                self.file_drop.value = DropLocation()[1]
                logger.info('Path given: ' + str(self.file_drop.value))
            except Exception as e:  # pragma no cover
                logger.error('file drop restart failed with error: ' + str(e))
            logger.info('Finished: file drop restart')
        self.file_drop.display()
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
        s_action = form_action = action.split('_')[0]
        form_name = s_action.title() + ' tools'
        cores = False
        a_type = 'containers'
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

        if s_action == 'configure':
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
        elif action == 'services':
            form = ServicesForm
            forms = ['SERVICES']
            form_args = {'color': 'STANDOUT',
                         'name': 'Plugin Services',
                         'core': True}
        elif action == 'services_external':
            form = ServicesForm
            forms = ['SERVICES']
            form_args = {'color': 'STANDOUT',
                         'name': 'External Services',
                         'core': True,
                         'external': True}
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
        elif action == 'starting_tools':
            self.parentApp.change_form('TUTORIALSTARTINGCORES')
        elif action == 'adding_tools':
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
        elif action == 'start':
            status = self.api_action.start()
            if status[0]:
                notify_confirm('System start complete. '
                               'Press OK.')
            else:
                notify_confirm(status[1])
        elif action == 'stop':
            status = self.api_action.stop()
            if status[0]:
                notify_confirm('System stop complete. '
                               'Press OK.')
            else:
                notify_confirm(status[1])
        elif action == 'configure':
            # TODO
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
        return

    def create(self):
        """ Override method for creating FormBaseNewWithMenu form """
        try:
            self.api_action = System()
        except DockerException as de:  # pragma: no cover
            notify_confirm(str(de),
                           title='Docker Error',
                           form_color='DANGER',
                           wrap=True)
            MainForm.exit()

        self.add_handlers({'^T': self.help_form, '^Q': MainForm.exit})
        # all forms that can toggle view by group
        self.view_togglable = ['inventory', 'remove']

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

        # Tool Menu Items
        self.m3 = self.add_menu(name='Tools', shortcut='p')
        self.m3.addItem(text='Add New Tool',
                        onSelect=self.perform_action,
                        arguments=['add'], shortcut='a')
        self.m3.addItem(text='Configure Tools',
                        onSelect=self.perform_action,
                        arguments=['configure'], shortcut='t')
        self.m3.addItem(text='Inventory',
                        onSelect=self.perform_action,
                        arguments=['inventory'], shortcut='i')
        self.m3.addItem(text='Remove Tools',
                        onSelect=self.perform_action,
                        arguments=['remove'], shortcut='r')
        self.m3.addItem(text='Start Tools',
                        onSelect=self.perform_action,
                        arguments=['start'], shortcut='s')
        self.m3.addItem(text='Stop Tools',
                        onSelect=self.perform_action,
                        arguments=['stop'], shortcut='p')

        # Services Menu Items
        self.m5 = self.add_menu(name='Services Running', shortcut='s')
        self.m5.addItem(text='External Services', onSelect=self.perform_action,
                        arguments=['services_external'], shortcut='e')
        self.m5.addItem(text='Tool Services',
                        onSelect=self.perform_action,
                        arguments=['services'], shortcut='t')

        # System Commands Menu Items
        self.m6 = self.add_menu(name='System Commands', shortcut='y')
        self.m6.addItem(text='Backup', onSelect=self.system_commands,
                        arguments=['backup'], shortcut='b')
        self.m6.addItem(text='Change Vent Configuration',
                        onSelect=self.system_commands, arguments=['configure'],
                        shortcut='c')
        self.m6.addItem(text='Detect GPUs', onSelect=self.system_commands,
                        arguments=['gpu'], shortcut='g')
        self.m6.addItem(text='Factory Reset', onSelect=self.system_commands,
                        arguments=['reset'], shortcut='r')
        self.m6.addItem(text='Restore (To Be Implemented...', onSelect=self.system_commands,
                        arguments=['restore'], shortcut='t')

        # TODO this should be either or depending on whether or not it's running already
        self.m6.addItem(text='Start', onSelect=self.system_commands,
                        arguments=['start'], shortcut='s')
        self.m6.addItem(text='Stop', onSelect=self.system_commands,
                        arguments=['stop'], shortcut='o')

        self.m6.addItem(text='Upgrade (To Be Implemented...)',
                        onSelect=self.system_commands,
                        arguments=['upgrade'], shortcut='u')

        # Tutorial Menu Items
        self.m7 = self.add_menu(name='Tutorials', shortcut='t')
        self.s1 = self.m7.addNewSubmenu(name='About Vent', shortcut='v')
        self.s1.addItem(text='Background', onSelect=self.switch_tutorial,
                        arguments=['background'], shortcut='b')
        self.s1.addItem(text='Terminology', onSelect=self.switch_tutorial,
                        arguments=['terminology'], shortcut='t')
        self.s1.addItem(text='Getting Setup', onSelect=self.switch_tutorial,
                        arguments=['setup'], shortcut='s')
        self.s2 = self.m7.addNewSubmenu(name='Working with Tools',
                                        shortcut='c')
        self.s2.addItem(text='Starting Tools', onSelect=self.switch_tutorial,
                        arguments=['starting_tools'], shortcut='s')
        self.s3 = self.m7.addNewSubmenu(name='Working with Plugins',
                                        shortcut='p')
        self.s3.addItem(text='Adding Tools', onSelect=self.switch_tutorial,
                        arguments=['adding_tools'], shortcut='a')
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
