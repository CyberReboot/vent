import npyscreen
import os

from vent.api.actions import Action
from vent.api.templates import Template
from vent.helpers.logs import Logger

class TemplateForm(npyscreen.ActionForm):
    """ Template form for the Vent CLI """
    def __init__(self, *args, **kargs):
        """ Initialize template form objects """
        if kargs['action_dict']:
            if kargs['action_dict']['cores']:
                self.core = True
            else:
                self.core = False
        self.logger = Logger(__name__)
        self.api_action = Action()
        self.manifest = os.path.join(self.api_action.plugin.path_dirs.meta_dir,
                                     "plugin_manifest.cfg")
        self.tools = {}
        super(TemplateForm, self).__init__(*args, **kargs)

    def quit(self, *args, **kwargs):
        """ Overriden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def create(self):
        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.add(npyscreen.TitleText, name="Select which tools' template(s) to update",
                 editable=False)
        if self.core:
            successful, inventory = self.api_action.inventory(choices=['core'])
            if successful:
                for tool in inventory['core']:
                    self.tools[tool[0]] = self.add(npyscreen.CheckBox, name=tool[0].split('/')[-1], value=True)
        else:
            successful, inventory = self.api_action.inventory(choices=['core', 'tools'])
            if successful:
                for tool in inventory['tools']:
                    if tool not in inventory['core']:
                        self.tools[tool[0]] = self.add(npyscreen.CheckBox, name=tool[1], value=True)

    def on_cancel(self):
        """ When user clicks cancel, will return to MAIN """
        self.quit()
