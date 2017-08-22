import ast
import npyscreen
import os
import re

from vent.api.plugin_helpers import PluginHelper


class EditorForm(npyscreen.ActionForm):
    """ Form that can be used as a pseudo text editor in npyscreen """
    def __init__(self, *args, **keywords):
        """ Initialize EditorForm objects """
        self.section_value = re.compile(r"""
        \w+\ *=\ *[\w,-]*$      # option-value pairs
        | \[\w+\]$              # section headers
        """, re.VERBOSE)
        self.save = keywords['save_configure']
        self.instance_cfg = False
        if 'restart_tools' in keywords:
            self.restart_tools = keywords['restart_tools']
        if 'vent_cfg' in keywords and keywords['vent_cfg']:
            self.vent_cfg = True
            self.config_val = keywords['get_configure'](main_cfg=True)[1]
            self.next_tool = None
            self.tool_name = 'vent configuration'
        else:
            self.vent_cfg = False
            self.tool_name = keywords['tool_name']
            self.branch = keywords['branch']
            self.version = keywords['version']
            if keywords['registry_download']:
                self.next_tool = None
                self.from_registry = True
                # populate editor with known fields of registry image
                self.config_val = "[info]\n"
                self.config_val += "name = " + keywords['link_name'] + "\n"
                self.config_val += "groups = " + keywords['groups'] + "\n"
            else:
                self.next_tool = keywords['next_tool']
                self.from_registry = keywords['from_registry']
                # get vent.template settings for specific tool
                if ('instance_cfg' not in keywords or
                        keywords['instance_cfg'] == False):
                    template = keywords['get_configure'](name=self.tool_name,
                                                         branch=self.branch,
                                                         version=self.version)
                    if template[0]:
                        self.config_val = template[1]
                    else:
                        npyscreen.notify_confirm("Couldn't find vent.template"
                                                 " for " +
                                                 keywords['tool_name'])
                # get default vent.template settings for a tool
                else:
                    try:
                        self.instance_cfg = True
                        self.instances = keywords['instances']
                        p_helper = PluginHelper()
                        constraints = {'name': keywords['tool_name'],
                                       'branch': keywords['branch'],
                                       'version': keywords['version']}
                        tool, manifest = p_helper.constraint_options(constraints, [])
                        # only one tool should be returned
                        section = tool.keys()[0]
                        path = manifest.option(section, 'path')[1]
                        # sending defaults to internals so it doesn't mess with
                        # installed plugins
                        path = path.replace('.vent/plugins', '.vent/.internals')
                        multi_tool = manifest.option(section, 'multi_tool')
                        if multi_tool[0] and multi_tool[1] == 'yes':
                            name = manifest.option(section, 'name')[1]
                            if name == 'unspecified':
                                name == 'vent'
                            template_path = os.path.join(path,
                                                         name + '.template')
                        else:
                            template_path = os.path.join(path, 'vent.template')
                        with open(template_path) as vent_template:
                            self.config_val = vent_template.read()
                    except:
                        self.config_val = ''
                        npyscreen.notify_confirm("Couldn't get default"
                                                 " settings for tool because " + str(e) + ", you can"
                                                 " still enter in settings you"
                                                 " want", title="Unsuccessful"
                                                 " default")
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
        if self.next_tool:
            self.parentApp.change_form(self.next_tool)
        else:
            self.parentApp.change_form("MAIN")

    def on_ok(self):
        """ Save changes made to vent.template """
        # ensure user input is valid before proceeding
        # ensure user didn't try to manually define instances
        if 'instances =' in self.edit_space.value:
            npyscreen.notify_confirm("You can't define instances manually in"
                                     " editing, use the built-in instance"
                                     " editor instead.", title="Invalid input")
            return
        # ensure user didn't have any syntactical errors
        for entry in self.edit_space.value.split('\n'):
            if entry.strip() == '':
                continue
            match = self.section_value.match(entry)
            with open('/Users/bpagon/Desktop/random.txt', 'a') as f:
                f.write(entry + ' || ' + str(match) + '\n')
            if not match:
                try:
                    opt_val = entry.split('=', 1)
                    assert(opt_val[0].strip() != '')
                    ast.literal_eval(opt_val[1].strip())
                except:
                    npyscreen.notify_confirm("You didn't type in your input in"
                                             " a syntactically correct format."
                                             " You may be missing spaces"
                                             " between the equal sign, have"
                                             " non-alphanumeric characters,"
                                             " have extraneous characters,"
                                             " etc.", title="Invalid input")
                    return

        instances = 1
        def instance_num(config_val):
            """ Get the instance number from a given config string """
            instance_loc = config_val.find('instances')
            if instance_loc >= 0:
                next_line = config_val.find('\n', instance_loc)
                if next_line < 0:
                    next_line = len(config_val)
                instance = config_val[instance_loc+12:next_line]
            else:
                # default instance value
                instance = '1'
            return instance

        if self.vent_cfg:
            self.save(main_cfg=True, config_val=self.edit_space.value)
        else:
            save_args = {'config_val': self.edit_space.value,
                         'name': self.tool_name,
                         'branch': self.branch,
                         'version': self.version}
            if self.from_registry:
                save_args.update({'from_registry': True})
            if hasattr(self, 'instances'):
                save_args.update({'instances': self.instances})
            self.save(**save_args)
        if hasattr(self, 'restart_tools'):
            restart_kargs = {'main_cfg': self.vent_cfg,
                             'old_val': self.config_val,
                             'new_val': self.edit_space.value}
            if not self.vent_cfg:
                restart_kargs.update({'name': self.tool_name,
                                      'version': self.version,
                                      'branch': self.branch,
                                      'instances': instances})
            npyscreen.notify_wait("Restarting tools affected by changes...",
                                  title="Restart")
            self.restart_tools(**restart_kargs)
        npyscreen.notify_confirm("Done configuring " + self.tool_name,
                                 title="Configurations saved")
        self.change_screens()

    def on_cancel(self):
        """ Don't save changes made to vent.template """
        npyscreen.notify_confirm("No changes made to " + self.tool_name,
                                 title="Configurations not saved")
        self.change_screens()
