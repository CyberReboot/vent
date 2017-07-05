import npyscreen
import os

from vent.api.actions import Action
from vent.api.templates import Template
from vent.helpers.logs import Logger

class TemplateForm(npyscreen.ActionForm):
    """ Template form for the Vent CLI """
    def __init__(self, *args, **kargs):
        """ Initialize template form objects """
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
        status, inventory = self.api_action.inventory(choices=['core'])
        if status:
            for tool in inventory['core']:
                self.tools[tool[0]] = self.add(npyscreen.CheckBox, name=tool[1], value=True)
