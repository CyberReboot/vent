import ast
import copy
import json
import npyscreen
import os
import re

from vent.api.plugin_helpers import PluginHelper
from vent.menus.del_instances import DeleteForm


class EditorForm(npyscreen.ActionForm):
    """ Form that can be used as a pseudo text editor in npyscreen """
    def __init__(self, repo='', tool_name='', branch='', version='',
                 next_tool=None, just_downloaded=False, vent_cfg=False,
                 from_registry=False, new_instance=False, *args, **keywords):
        """ Initialize EditorForm objects """
        # default for any editor
        self.settings = locals()
        self.settings.update(keywords)
        del self.settings['self']
        del self.settings['args']
        del self.settings['keywords']
        del self.settings['parentApp']
        self.section_value = re.compile(r"""
        \ *\#.*                        # comments
        | \w+\ *=\ *[\w,.:/#-]*$    # option-value pairs
        | \[[\w-]+\]$               # section headers
        """, re.VERBOSE)
        self.p_helper = PluginHelper(plugins_dir='.internals/')
        self.tool_identifier = {'name': tool_name,
                                'branch': branch,
                                'version': version}
        self.settings.update(self.tool_identifier)
        del self.settings['name']
        self.settings['tool_name'] = tool_name
        self.settings['next_tool'] = next_tool
        self.settings['repo'] = repo

        # setup checks
        self.just_downloaded = ('just_downloaded' in self.settings and
                self.settings['just_downloaded'])
        self.vent_cfg = ('vent_cfg' in self.settings and
                self.settings['vent_cfg'])
        self.registry_tool = ('from_registry' in self.settings and
                self.settings['from_registry'])
        self.instance_cfg = ('new_instance' in self.settings and
                self.settings['new_instance'])

        # get manifest info for tool that will be used throughout
        if not self.just_downloaded and not self.vent_cfg:
            result = self.p_helper.constraint_options(self.tool_identifier, [])
            tool, self.manifest = result
            self.section = tool.keys()[0]

        # get configuration information depending on type
        if self.just_downloaded:
            self.config_val = '[info]\n'
            self.config_val += 'name = ' + keywords['link_name'] + '\n'
            self.config_val += 'groups = ' + keywords['groups'] + '\n'
        elif self.vent_cfg:
            self.config_val = keywords['get_configure'](main_cfg=True)[1]
            self.settings['tool_name'] = 'vent configuration'
        elif self.instance_cfg:
            path = self.manifest.option(self.section, 'path')[1]
            # defaults in .internals
            path = path.replace('.vent/plugins',
                                '.vent/.internals')
            multi_tool = self.manifest.option(self.section, 'multi_tool')
            if multi_tool[0] and multi_tool[1] == 'yes':
                name = self.manifest.option(self.section, 'name')[1]
                if name == 'unspecified':
                    name = 'vent'
                template_path = os.path.join(path,
                                             name + '.template')
            else:
                template_path = os.path.join(path, 'vent.template')
            with open(template_path) as vent_template:
                self.config_val = vent_template.read()
            self.config_val = re.sub(r'instances\ *=\ *[0-9]+',
                                     'instances = ' +
                                     str(self.settings['new_instances']),
                                     self.config_val)
        else:
            self.config_val = keywords['get_configure'](**self.tool_identifier)[1]
        super(EditorForm, self).__init__(*args, **keywords)

    def create(self):
        """ Create multi-line widget for editing """
        # add various pointers to those editing vent_cfg
        if self.vent_cfg:
            self.add(npyscreen.Textfield,
                     value='# when configuring external'
                           ' services make sure to do so',
                     editable=False)
            self.add(npyscreen.Textfield,
                     value='# in the form of Service = {"setting": "value"}',
                     editable=False)
            self.add(npyscreen.Textfield,
                     value='# make sure to capitalize your service correctly'
                           ' (i.e. Elasticsearch vs. elasticsearch)',
                     editable=False)
            self.add(npyscreen.Textfield,
                     value='# and make sure to enclose all dict keys and'
                           ' values in double quotes ("")',
                     editable=False)
            self.add(npyscreen.Textfield,
                     value='',
                     editable=False)
        elif self.instance_cfg:
            self.add(npyscreen.Textfield,
                     value='# these settings will be used'
                           ' to configure the new instances',
                     editable=False)
        self.edit_space = self.add(npyscreen.MultiLineEdit,
                                   value=self.config_val)

    def change_screens(self):
        """ Change to the next tool to edit or back to MAIN form """
        if self.settings['next_tool']:
            self.parentApp.change_form(self.settings['next_tool'])
        else:
            self.parentApp.change_form("MAIN")

    def on_ok(self):
        """ Save changes made to vent.template """
        # ensure user didn't have any syntactical errors
        for entry in self.edit_space.value.split('\n'):
            if entry.strip() == '':
                continue
            match = self.section_value.match(entry)
            if not match:
                try:
                    opt_val = entry.split('=', 1)
                    if opt_val[0].strip() == '':
                        raise Exception("It appears you haven't written"
                                        " anything before an equals sign"
                                        " somewhere.")
                    ast.literal_eval(opt_val[1].strip())
                except Exception as e:
                    npyscreen.notify_confirm("You didn't type in your input in"
                                             " a syntactically correct format."
                                             " Double check to make sure you"
                                             " don't have extraneous"
                                             " characters, have closed your"
                                             " brackets, etc. Here's an error"
                                             " message that may be helpful: " +
                                             str(e), title="Invalid input")
                    return
        
        # get the number of instances and ensure user didn't malform that
        if re.search(r"instances\ *=", self.edit_space.value):
            try:
                new_instances = int(re.split(r"instances\ *=\ *",
                                             self.edit_space.value)[1][0])
            except ValueError:
                npyscreen.notify_confirm("You didn't specify a valid number" 
                                         " for instances.")
                return
            # user can't change instances when configuring new instnaces
            if (self.instance_cfg and
                    self.settings['new_instances'] != new_instances):
                npyscreen.notify_confirm("You can't change the number of"
                                         " instnaces while configuring new"
                                         " instances!", title="Illegal change")
                return
            # get old number of instances
            try:
                if 'old_instances' in self.settings:
                    old_instances = self.settings['old_instances']
                else:
                    settings_dict = json.loads(
                                        self.manifest.option(self.section,
                                                             'settings')[1])
                    old_instances = int(settings_dict['instances'])
            except Exception:
                old_instances = 1
        else:
            new_instances = 1
            old_instances = 1

        # save changes and update manifest we're looking at with changes
        if self.vent_cfg:
            save_args = {'main_cfg': True,
                         'config_val': self.edit_space.value}
            self.manifest = self.settings['save_configure'](**save_args)[1]
        else:
            save_args = copy.deepcopy(self.tool_identifier)
            save_args.update({'config_val': self.edit_space.value})
            if self.registry_tool:
                save_args.update({'from_registry': True})
            if self.instance_cfg:
                save_args.update({'instances': new_instances})
            self.manifest = self.settings['save_configure'](**save_args)[1]

        # restart tools, if necessary
        if not self.just_downloaded and not self.instance_cfg:
            restart_kargs = {'main_cfg': self.vent_cfg,
                             'old_val': self.config_val,
                             'new_val': self.edit_space.value}
            if self.vent_cfg:
                wait_str = "Restarting tools affected by changes..."
            else:
                wait_str = "Restarting this tool with new settings..."
                restart_kargs.update(self.tool_identifier)
            npyscreen.notify_wait(wait_str,
                                  title="Restarting with changes")
            self.settings['restart_tools'](**restart_kargs)

        # start new instances if user wanted to
        if self.instance_cfg and self.settings['start_new']:
            npyscreen.notify_wait("Starting new instances...",
                                  title="Start")
            tool_d = {}
            for i in range(self.settings['old_instances'] + 1,
                           self.settings['new_instances'] + 1):
                # create section by scrubbing instance number out of names
                # and adding new instance number
                i_section = self.section.rsplit(':', 2)
                i_section[0] = re.sub(r'[0-9]', '', i_section[0]) + str(i)
                i_section = ':'.join(i_section)
                t_name = self.manifest.option(i_section, 'name')[1]
                t_branch = self.manifest.option(i_section, 'branch')[1]
                t_version = self.manifest.option(i_section, 'version')[1]
                t_id = {'name': t_name,
                        'branch': t_branch,
                        'version': t_version}
                tool_d.update(self.settings['prep_start'](**t_id)[1])
            if tool_d:
                self.settings['start_tools'](tool_d)

        # prompt user for instance changes, as necessary
        if not self.instance_cfg and not self.vent_cfg:
            if new_instances > old_instances:
                try:
                    diff = str(new_instances - old_instances)
                    res = npyscreen.notify_yes_no("You will be creating " +
                                                  diff + " additional"
                                                  " instance(s) is that okay?",
                                                  title="Confirm new"
                                                  " instance(s)")
                    if res:
                        if self.manifest.option(self.section,
                                                'built')[1] == 'yes':
                            run = npyscreen.notify_yes_no("Do you want to"
                                                          " start these new"
                                                          " tools upon"
                                                          " creation?",
                                                          title="Run new"
                                                          " instance(s)")
                        else:
                            run = False
                        npyscreen.notify_wait("Pulling up default settings"
                                              " for " +
                                              self.settings['tool_name'] +
                                              "...",
                                              title="Gathering settings")
                        self.p_helper.clone(self.settings['repo'])
                        self.settings['new_instances'] = new_instances
                        self.settings['old_instances'] = old_instances
                        self.settings['start_new'] = run
                        self.settings['new_instance'] = True
                        self.settings['name'] = "Configure new instance(s)" + \
                                " for " + self.settings['tool_name']
                        self.parentApp.addForm('INSTANCEEDITOR' +
                                               self.settings['tool_name'],
                                               EditorForm, **self.settings)
                        self.parentApp.change_form('INSTANCEEDITOR' +
                                                   self.settings['tool_name'])
                    else:
                        return
                except Exception as e:
                    npyscreen.notify_confirm("Trouble finding tools to add,"
                                             " exiting" + str(e), title="Error")
                    self.on_cancel()
            elif new_instances < old_instances:
                try:
                    diff = str(old_instances - new_instances)
                    res = npyscreen.notify_yes_no("You will be deleting " +
                                                  diff + " instance(s), is"
                                                  " that okay?",
                                                  title="Confirm delete"
                                                  " instance(s)")
                    if res:
                        form_name = 'Delete instances for ' + \
                                self.settings['tool_name'] + '\t'*8 + \
                                '^E to exit configuration process'
                        deleter_args = {'name': form_name,
                                        'new_instances': new_instances,
                                        'old_instances': old_instances,
                                        'next_tool': self.settings['next_tool'],
                                        'manifest': self.manifest,
                                        'section': self.section,
                                        'clean': self.settings['clean'],
                                        'prep_start': self.settings['prep_start'],
                                        'start_tools': self.settings['start_tools']}
                        self.parentApp.addForm('DELETER' + self.settings['tool_name'],
                                               DeleteForm, **deleter_args)
                        self.parentApp.change_form('DELETER' +
                                                   self.settings['tool_name'])
                except Exception as e:
                    npyscreen.notify_confirm("Trouble finding instances to"
                                             " delete, exiting" + str(e), title="Error")
                    self.on_cancel()

        if (new_instances == old_instances or
                self.instance_cfg or self.vent_cfg):
            npyscreen.notify_confirm("Done configuring " +
                                     self.settings['tool_name'],
                                     title="Configurations saved")
            self.change_screens()

    def on_cancel(self):
        """ Don't save changes made to vent.template """
        npyscreen.notify_confirm("No changes made to " + self.settings['tool_name'],
                                 title="Configurations not saved")
        self.change_screens()
