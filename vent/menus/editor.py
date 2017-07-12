import npyscreen


class EditorForm(npyscreen.ActionForm):
    """ Form that can be used as a pseudo test editor in npyscreen """
    def __init__(self, *args, **keywords):
        """ Initialize EditorForm objects """
        self.save = keywords['save_configure']
        self.tool_name = keywords['tool_name']
        self.version = keywords['version']
        if not keywords['from_registry']:
            self.next_tool = keywords['next_tool']
            self.branch = keywords['branch']
            template = keywords['get_configure'](name=self.tool_name,
                                                 branch=self.branch,
                                                 version=self.version)
            if template[0]:
                self.config_val = template[1]
            else:
                npyscreen.notify_confirm("Couldn't find vent.template for " +
                                         keywords['tool_name'])
                self.change_screens()
            self.from_registry = False
        else:
            self.from_registry = True
        super(EditorForm, self).__init__(*args, **keywords)

    def create(self):
        """ Create multi-line widget for editing """
        if self.from_registry:
            initial_val = ""
        else:
            initial_val = self.config_val
        self.edit_space = self.add(npyscreen.MultiLineEdit,
                                   value=initial_val)

    def change_screens(self):
        """ Change to the next tool to edit or back to MAIN form """
        if self.next_tool:
            self.parentApp.change_form(self.next_tool)
        else:
            self.parentApp.change_form("MAIN")

    def on_ok(self):
        """ Save changes made to vent.template """
        save_args = {'config_val': self.edit_space.value,
                     'name': self.tool_name,
                     'version': self.version}
        if self.from_registry:
            save_args.update({'from_registry': True})
        else:
            save_args.update({'branch': self.branch})
        self.save(**save_args)
        npyscreen.notify_confirm("Done configuring this tool",
                                 title="Configurations saved")
        if self.from_registry:
            self.parentApp.change_form("MAIN")
        else:
            self.change_screens()

    def on_cancel(self):
        """ Don't save changes made to vent.template """
        npyscreen.notify_confirm("No changes made to this tool",
                                 title="Configurations not saved")
        if self.from_registry:
            self.parentApp.change_form("MAIN")
        else:
            self.change_screens()
