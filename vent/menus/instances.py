import json
import npyscreen

from vent.api.plugin_helpers import PluginHelper

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
        self.editor_args = keywords
        self.editor_args['next_tool'] = None
        self.p_helper = PluginHelper(plugins_dir='.internals/')
        keywords['name'] = 'New number of instances for ' + \
                keywords['tool_name']
        super(InstanceForm, self).__init__(*args, **keywords)

    def create(self):
        self.add(npyscreen.TitleText, name='How many instances:',
                 editable=False)
        self.num_instances = self.add(npyscreen.Textfield, rely=3)

    def change_screens(self):
        """ Change to the next tool to edit or back to MAIN form """
        if self.next_tool:
            self.parentApp.change_form(self.next_tool)
        else:
            self.parentApp.change_form("MAIN")

    def on_ok(self):
        # keep prompting user for an integer if not given
        try:
            new_val = int(self.num_instances.value)
        except:
            npyscreen.notify_confirm("You must enter a valid number.",
                                     title="Invalid input")
            return
        # get old number of instances
        constraints = {'name': self.tool_name,
                       'branch': self.branch,
                       'version': self.version}
        tool, manifest = self.p_helper.constraint_options(constraints, [])
        # only one tool should be returned
        section = tool.keys()[0]
        try:
            settings_dict = json.loads(manifest.option(section, 'settings')[1])
            old_val = int(settings_dict['instances'])
        except:
            # if no previous instance number defined, default is one
            old_val = 1
        d
        self.change_screens()

    def on_cancel(self):
        npyscreen.notify_confirm("No changes made")
        self.change_screens()
