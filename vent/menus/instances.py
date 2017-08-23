import json
import npyscreen
import re

from vent.api.plugin_helpers import PluginHelper
from vent.menus.editor import EditorForm

class InstanceSelect(npyscreen.MultiSelect):
    """
    A widget class for selecting an exact amount of instances to perform
    actions on
    """
    def __init__(self, *args, **kargs):
        """ Initialize an instance select object """
        self.instance_num = kargs['instance_num']
        super(InstanceSelect, self).__init__(*args, **kargs)

    def when_value_edited(self, *args, **kargs):
        """ Overrided to prevent user from selecting too many instances """
        if len(self.value) > self.instance_num:
            self.value.pop(-2)
            self.display()

    def safe_to_exit(self, *args, **kargs):
        """
        Overrided to prevent user from exiting selection until
        they have selected the right amount of instances
        """
        if len(self.value) == self.instance_num:
            return True
        return False

class InstanceForm(npyscreen.ActionForm):
    """ Form that deals with adding or removing instances of a tool """
    def __init__(self, *args, **keywords):
        """ Initialize an instance form object """
        self.next_tool = keywords['next_tool']
        self.tool_name = keywords['tool_name']
        self.branch = keywords['branch']
        self.version = keywords['version']
        self.repo = keywords['repo']
        self.clean = keywords['clean']
        self.prep_start = keywords['prep_start']
        self.start_tools = keywords['start_tools']
        self.editor_args = keywords
        self.editor_args['instance_cfg'] = True
        del self.editor_args['clean']
        del self.editor_args['restart_tools']
        self.p_helper = PluginHelper(plugins_dir='.internals/')
        keywords['name'] = 'New number of instances for ' + \
                keywords['tool_name']
        super(InstanceForm, self).__init__(*args, **keywords)
        del self.editor_args['parentApp']
        self.editor_args['name'] = 'Configure new instances for ' + \
                self.tool_name

    def create(self):
        self.title = self.add(npyscreen.Textfield, value='How many instances:',
                              editable=False, color="GOOD")
        self.num_instances = self.add(npyscreen.Textfield, rely=3)

    def change_screens(self):
        """ Change to the next tool to edit or back to MAIN form """
        if self.next_tool:
            self.parentApp.change_form(self.next_tool)
        else:
            self.parentApp.change_form("MAIN")

    def on_ok(self):
        # get manifest and section that will be used for finding instances
        constraints = {'name': self.tool_name,
                       'branch': self.branch,
                       'version': self.version}
        tools, manifest = self.p_helper.constraint_options(constraints, [])
        section = tools.keys()[0]

        # perform deletion function
        if hasattr(self, 'del_instances'):
            npyscreen.notify_wait("Deleting instances given...",
                                  title="In progress")
            # keep track of number for shifting instances down for alignment
            shift_num = 1
            to_update = []
            for i, val in enumerate(self.del_instances.values):
                # clean all tools for renmaing and relabeling purposes
                t = val.split(':')
                self.clean(name=t[0], branch=t[1], version=t[2])
                if i in self.del_instances.value:
                    manifest.del_section(self.display_to_section[':'.join(t)])
                else:
                    try:
                        # shift remaining containers down for naming purposes
                        val_arr = val.split(':')
                        i_section = self.display_to_section[val]
                        settings_dict = json.loads(manifest.option \
                                (i_section, 'settings')[1])
                        settings_dict['instances'] = self.remaining_instances
                        manifest.set_option(i_section, 'settings',
                                            json.dumps(settings_dict))
                        prev_name = manifest.option(i_section, 'name')[1]
                        # number to identify different sections and tools by
                        identifier = str(shift_num) if shift_num != 1 else ''
                        new_name = re.split(r'[0-9]', prev_name)[0] + \
                                identifier
                        manifest.set_option(i_section, 'name', new_name)
                        # copy new contents into shifted version
                        new_section = re.sub(r'[0-9]', identifier,
                                             i_section, 1)
                        manifest.add_section(new_section)
                        for val_pair in manifest.section(i_section)[1]:
                            manifest.set_option(new_section, val_pair[0],
                                                val_pair[1])
                        manifest.del_section(i_section)
                        to_update.append({'name': new_name,
                                          'branch': val_arr[1],
                                          'version': val_arr[2]})
                        shift_num += 1
                    except Exception as e:
                        npyscreen.notify_confirm("Trouble deleting tools"
                                                 " because " + str(e))
            manifest.write_config()
            tool_d = {}
            for tool in to_update:
                tool_d.update(self.prep_start(**tool)[1])
            if tool_d:
                self.start_tools(tool_d)
            npyscreen.notify_confirm("Done deleting instances.",
                                     title="Finished")
            self.change_screens()

        # perform instance gathering function
        else:
            # keep prompting user for an integer if not given
            try:
                new_val = int(self.num_instances.value)
            except:
                npyscreen.notify_confirm("You must enter a valid number.",
                                         title="Invalid input")
                return
            # get old number of instances
            try:
                settings_dict = json.loads(manifest.option(section,
                                                           'settings')[1])
                old_val = int(settings_dict['instances'])
            except:
                # if no previous instance number defined, default is one
                old_val = 1
            if new_val > old_val:
                try:
                    res = npyscreen.notify_yes_no("You will be creating " +
                                                  str(new_val - old_val) +
                                                  " additional instance(s), is"
                                                  " that okay?")
                    if res:
                        run = npyscreen.notify_yes_no("Do you want to start"
                                                      " these new tools upon"
                                                      " creation?")
                        if not run:
                            del self.editor_args['prep_start']
                            del self.editor_args['start_tools']
                        npyscreen.notify_wait("Pulling up default settings"
                                              " for " + self.tool_name + "...",
                                              title="Gathering settings")
                        self.p_helper.clone(self.repo)
                        self.editor_args['instances'] = new_val
                        self.editor_args['old_instances'] = old_val
                        self.parentApp.addForm('EDITOR' + self.tool_name,
                                               EditorForm, **self.editor_args)
                        self.parentApp.change_form('EDITOR' + self.tool_name)
                except Exception as e:
                    npyscreen.notify_confirm("Trouble getting information for"
                                             " tool " + self.tool_name +
                                             " because " + str(e),
                                             title="Error")
                    self.on_cacel()
            elif new_val < old_val:
                try:
                    res = npyscreen.notify_yes_no("You will be deleting " +
                                                  str(old_val - new_val) +
                                                  " instance(s), is"
                                                  " that okay?")
                    if res:
                        self.remaining_instances = new_val
                        self.display_to_section = {}
                        cur_instances = []
                        for i in range(1, old_val + 1):
                            i_section = section.rsplit(':', 2)
                            i_section[0] += str(i) if i != 1 else ''
                            i_section = ':'.join(i_section)
                            display = i_section.rsplit('/', 1)[-1]
                            cur_instances.append(display)
                            self.display_to_section[display] = i_section
                        self.title.value = 'Select which instances to delete'
                        self.num_instances.hidden = True
                        self.del_instances = self.add(InstanceSelect,
                                                      values=cur_instances,
                                                      scroll_exit=True, rely=3,
                                                      instance_num=new_val)
                except Exception as e:
                    npyscreen.notify_confirm("Trouble finding instances to"
                                             " delete because " + str(e))
                    self.on_cancel()
            else:
                res = npyscreen.notify_yes_no("This is the same number of"
                                              " instances you already have,"
                                              " do you want to exit?",
                                              title="Same number of instaces")
                if res:
                    self.on_cancel()

    def on_cancel(self):
        npyscreen.notify_confirm("No changes made")
        self.change_screens()
