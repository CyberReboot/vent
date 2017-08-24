import json
import npyscreen

from vent.api.plugin_helpers import PluginHelper
from vent.menus.del_instances import DeleteForm
from vent.menus.editor import EditorForm


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
        super(InstanceForm, self).__init__(*args, **keywords)
        del self.editor_args['parentApp']
        editor_name = 'Configure new instances for ' + self.tool_name
        self.editor_args['name'] = editor_name

    def create(self):
        """ Creates the necessary display for this form """
        self.add_handlers({"^E": self.quit})
        # get old number of instances for displaying
        constraints = {'name': self.tool_name,
                       'branch': self.branch,
                       'version': self.version}
        tools, manifest = self.p_helper.constraint_options(constraints, [])
        section = tools.keys()[0]
        try:
            settings_dict = json.loads(manifest.option(section,
                                                       'settings')[1])
            prev_val = settings_dict['instances']
        except:
            # if no previous instance number defined, default is one
            prev_val = '1'
        self.add(npyscreen.Textfield, value='How many instances'
                 ' (for reference, there are ' + str(prev_val) +
                 ' instance(s) of this tool already):',
                 editable=False, color="GOOD")
        self.num_instances = self.add(npyscreen.Textfield, rely=3)

    def change_screens(self):
        """ Change to the next tool to edit or back to MAIN form """
        if self.next_tool:
            self.parentApp.change_form(self.next_tool)
        else:
            self.parentApp.change_form("MAIN")

    def quit(self, *args, **kargs):
        """ Quit without making any changes to the tool """
        npyscreen.notify_confirm("No changes made")
        self.change_screens()

    def on_ok(self):
        """ Takes the input the user gave and performs necessary actions """
        # get manifest and section that will be used for finding instances
        constraints = {'name': self.tool_name,
                       'branch': self.branch,
                       'version': self.version}
        tools, manifest = self.p_helper.constraint_options(constraints, [])
        section = tools.keys()[0]

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
                    if manifest.option(section, 'built')[1] == 'yes':
                        run = npyscreen.notify_yes_no("Do you want to"
                                                      " start these new"
                                                      " tools upon"
                                                      " creation?")
                    else:
                        run = False
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
                self.quit()
        elif new_val < old_val:
            try:
                res = npyscreen.notify_yes_no("You will be deleting " +
                                              str(old_val - new_val) +
                                              " instance(s), is"
                                              " that okay?")
                if res:
                    form_name = 'Delete instances for ' + self.tool_name + \
                            '\t'*8 + '^E to exit configuration process'
                    deleter_args = {'name': form_name,
                                    'new_instances': new_val,
                                    'old_instances': old_val,
                                    'next_tool': self.next_tool,
                                    'manifest': manifest,
                                    'section': section,
                                    'clean': self.clean,
                                    'prep_start': self.prep_start,
                                    'start_tools': self.start_tools}
                    self.parentApp.addForm('DELETER' + self.tool_name,
                                           DeleteForm, **deleter_args)
                    self.parentApp.change_form('DELETER' + self.tool_name)
            except Exception as e:
                npyscreen.notify_confirm("Trouble finding instances to"
                                         " delete because " + str(e))
                self.quit()
        else:
            res = npyscreen.notify_yes_no("This is the same number of"
                                          " instances you already have,"
                                          " do you want to exit?",
                                          title="Same number of instaces")
            if res:
                self.quit()

    def on_cancel(self):
        """ Exits the form without performing any action """
        self.quit()
