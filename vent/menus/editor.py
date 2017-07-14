import npyscreen


class EditorForm(npyscreen.ActionForm):
    """ Form that can be used as a pseudo test editor in npyscreen """
    def __init__(self, *args, **keywords):
        """ Initialize EditorForm objects """
        self.next_tool = keywords['next_tool']
        self.tool_name = keywords['tool_name']
        self.branch = keywords['branch']
        self.version = keywords['version']
        template = keywords['get_configure'](name=self.tool_name,
                                             branch=self.branch,
                                             version=self.version)
        if template[0]:
            self.config_val = template[1]
        else:
            npyscreen.notify_confirm("Couldn't find vent.template for " +
                                     keywords['tool_name'])
            self.change_screens()
        self.save = keywords['save_configure']
        super(EditorForm, self).__init__(*args, **keywords)

    def create(self):
        """ Create multi-line widget for editing """
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
        self.save(name=self.tool_name, branch=self.branch,
                  version=self.version, config_val=self.edit_space.value)
        npyscreen.notify_confirm("Done configuring this tool",
                                 title="Configurations saved")
        self.change_screens()

    def on_cancel(self):
        """ Don't save changes made to vent.template """
        npyscreen.notify_confirm("No changes made to this tool",
                                 title="Configurations not saved")
        self.change_screens()
