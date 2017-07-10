import npyscreen

class EditorForm(npyscreen.ActionForm):
    def __init__(self, *args, **keywords):
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
        self.m = self.add(npyscreen.MultiLineEdit, value=self.config_val)

    def change_screens(self):
        if self.next_tool:
            self.parentApp.change_form(self.next_tool)
        else:
            self.parentApp.change_form("MAIN")

    def on_ok(self):
        self.save(name=self.tool_name, branch=self.branch, version=self.version,
                  config_val=self.m.value)
        npyscreen.notify_confirm("Done configuring this tool")
        self.change_screens()

    def on_cancel(self):
        npyscreen.notify_confirm("No changes made to this tool")
        self.change_screens()
