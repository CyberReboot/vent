import ast
import copy
import json
import npyscreen
import os
import re

from vent.api.plugin_helpers import PluginHelper


class EditorForm(npyscreen.ActionForm):
    """ Form that can be used as a pseudo text editor in npyscreen """
    def __init__(self, *args, **keywords):
        """ Initialize EditorForm objects """
        # default for any editor
        self.section_value = re.compile(r"""
        \#.*                        # comments
        | \w+\ *=\ *[\w,.:/#-]*$    # option-value pairs
        | \[[\w-]+\]$               # section headers
        """, re.VERBOSE)
        self.p_helper = PluginHelper()
        self.settings = keywords
        del self.settings['parentApp']
        self.tool_identifier = {'name': self.settings['tool_name'],
                                'branch': self.settings['branch'],
                                'version': self.settings['version']}

        # setup checks
        self.just_downloaded = ('just_downloaded' in self.settings and
                keywords['just_downloaded'])
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
        elif self.instance_cfg:
            path = self.manifest.option(section, 'path')[1]
            # defaults in .internals
            path = path.replace('.vent/plugins',
                                '.vent/.internals')
            multi_tool = self.manifest.option(section, 'multi_tool')
            if multi_tool[0] and multi_tool[1] == 'yes':
                name = self.manifest.option(section, 'name')[1]
                if name == 'unspecified':
                    name = 'vent'
                template_path = os.path.join(path,
                                             name + '.template')
            else:
                template_path = os.path.join(path, 'vent.template')
            with open(template_path) as vent_template:
                self.config_val = vent_template.read()
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
            self.parentApp.change_form(self.next_tool)
        else:
            self.parentApp.change_form("MAIN")

    def on_ok(self):
        """ Save changes made to vent.template """
       # # ensure user didn't have any syntactical errors
       # for entry in self.edit_space.value.split('\n'):
       #     if entry.strip() == '':
       #         continue
       #     match = self.section_value.match(entry)
       #     if not match:
       #         try:
       #             opt_val = entry.split('=', 1)
       #             if opt_val[0].strip() == '':
       #                 raise Exception("It appears you haven't written"
       #                                 " anything before an equals sign"
       #                                 " somewhere.")
       #             ast.literal_eval(opt_val[1].strip())
       #         except Exception as e:
       #             npyscreen.notify_confirm("You didn't type in your input in"
       #                                      " a syntactically correct format."
       #                                      " Double check to make sure you"
       #                                      " don't have extraneous"
       #                                      " characters, have closed your"
       #                                      " brackets, etc. Here's an error"
       #                                      " message that may be helpful: " +
       #                                      str(e), title="Invalid input")
       #             return
       # # get the number of instances and ensure user didn't malform that
       # if re.match(r"instances\ *=", self.edit_space.value):
       #     try:
       #         new_instances = int(re.split(r"instances\ *=\ *",
       #                                      self.edit_space.value)[1][0])
       #     except ValueError:
       #         npyscreen.notify_confirm("You didn't specify a valid number" 
       #                                  " for instances.")
       #         return
       #     # get old number of instances
       #     try:
       #         settings_dict = json.loads(self.manifest.option(self.section,
       #                                                         'settings'[1]))
       #         old_instances = int(settings_dict['instances'])
       #     except Exception:
       #         old_instances = 1
       # else:
       #     new_instances = 1
       #     old_instances = 1

        # save and restart tools, if necessary
        if self.vent_cfg:
            self.settings['save_configure'](main_cfg=True,
                                            config_val=self.edit_space.value)
        else:
            save_args = copy.deepcopy(self.tool_identifier)
            save_args.update({'config_val': self.edit_space.value})
            if self.registry_tool:
                save_args.update({'from_registry': True})
            self.settings['save_configure'](**save_args)
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
       # # check if you need to start new instances
       # elif self.instance_cfg:
       #     if hasattr(self, 'start_tools'):
       #         npyscreen.notify_wait("Starting new instances...",
       #                               title="Start")
       #         tool_d = {}
       #         t_identifier = {'name': self.tool_name,
       #                         'branch': self.branch,
       #                         'version': self.version}
       #         result = self.p_helper.constraint_options(t_identifier, [])
       #         tools, manifest = result
       #         section = tools.keys()[0]
       #         for i in range(self.old_instances + 1, self.instances + 1):
       #             i_section = section.rsplit(':', 2)
       #             i_section[0] += str(i)
       #             i_section = ':'.join(i_section)
       #             t_name = manifest.option(i_section, 'name')[1]
       #             t_branch = manifest.option(i_section, 'branch')[1]
       #             t_version = manifest.option(i_section, 'version')[1]
       #             t_id = {'name': t_name,
       #                     'branch': t_branch,
       #                     'version': t_version}
       #             tool_d.update(self.prep_start(**t_id)[1])
       #         if tool_d:
       #             self.start_tools(tool_d)
       # if new_instnaces > old_instances:
       #     try:
       #         res = npyscreen.notify_yes_no("You will be creating " +
       #                                       str(new_val - old_val) +
       #                                       " additional instance(s), is"
       #                                       " that okay?")
       #         if res:
       #             if manifest.option(section, 'built')[1] == 'yes':
       #                 run = npyscreen.notify_yes_no("Do you want to"
       #                                               " start these new"
       #                                               " tools upon"
       #                                               " creation?")
       #             else:
       #                 run = False
       #             if not run:
       #                 del self.editor_args['prep_start']
       #                 del self.editor_args['start_tools']
       #             npyscreen.notify_wait("Pulling up default settings"
       #                                   " for " + self.tool_name + "...",
       #                                   title="Gathering settings")
       #             self.p_helper.clone(self.repo)
       #             self.editor_args['instances'] = new_val
       #             self.editor_args['old_instances'] = old_val
       #             self.parentApp.addForm('EDITOR' + self.tool_name,
       #                                    EditorForm, **self.editor_args)
       #             self.parentApp.change_form('EDITOR' + self.tool_name)
       # elif new_instances < old_instances:
       #     try:
       #         res = npyscreen.notify_yes_no("You will be deleting " +
       #                                       str(old_val - new_val) +
       #                                       " instance(s), is"
       #                                       " that okay?")
       #         if res:
       #             form_name = 'Delete instances for ' + self.tool_name + \
       #                     '\t'*8 + '^E to exit configuration process'
       #             deleter_args = {'name': form_name,
       #                             'new_instances': new_val,
       #                             'old_instances': old_val,
       #                             'next_tool': self.next_tool,
       #                             'manifest': manifest,
       #                             'section': section,
       #                             'clean': self.clean,
       #                             'prep_start': self.prep_start,
       #                             'start_tools': self.start_tools}
       #             self.parentApp.addForm('DELETER' + self.tool_name,
       #                                    DeleteForm, **deleter_args)
       #             self.parentApp.change_form('DELETER' + self.tool_name)
       #     except Exception as e:
       #         npyscreen.notify_confirm("Trouble finding instances to"
       #                                  " delete because " + str(e))
       #         self.on_cancel()
       # else:
       #     pass
        npyscreen.notify_confirm("Done configuring " +
                                 self.settings['tool_name'],
                                 title="Configurations saved")
        self.change_screens()

    def on_cancel(self):
        """ Don't save changes made to vent.template """
        npyscreen.notify_confirm("No changes made to " + self.tool_name,
                                 title="Configurations not saved")
        self.change_screens()
