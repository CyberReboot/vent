import npyscreen


class EditorForm(npyscreen.ActionForm):
    """ Form that can be used as a pseudo test editor in npyscreen """
    def __init__(self, *args, **keywords):
        """ Initialize EditorForm objects """
        self.save = keywords['save_configure']
        if 'vent_cfg' in keywords and keywords['vent_cfg']:
            self.vent_cfg = True
            self.config_val = keywords['get_configure'](main_cfg=True)[1]
            self.next_tool = None
            self.tool_name = 'vent configuration'
        else:
            self.tool_name = keywords['tool_name']
            self.branch = keywords['branch']
            self.version = keywords['version']
            if not keywords['registry_download']:
                self.next_tool = keywords['next_tool']
                self.from_registry = keywords['from_registry']
                # get vent.template settings
                template = keywords['get_configure'](name=self.tool_name,
                                                     branch=self.branch,
                                                     version=self.version)
                if template[0]:
                    self.config_val = template[1]
                else:
                    npyscreen.notify_confirm("Couldn't find vent.template"
                                             " for " + keywords['tool_name'])
            else:
                self.next_tool = None
                self.from_registry = True
                # populate editor with known fields of registry image
                self.config_val = "[info]\n"
                self.config_val += "name = " + keywords['link_name'] + "\n"
                self.config_val += "groups = " + keywords['groups'] + "\n"
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
        if self.vent_cfg:
            self.save(main_cfg=True, config_val=self.edit_space.value)
        else:
            save_args = {'config_val': self.edit_space.value,
                         'name': self.tool_name,
                         'branch': self.branch,
                         'version': self.version}
            if self.from_registry:
                save_args.update({'from_registry': True})
            self.save(**save_args)
        npyscreen.notify_confirm("Done configuring " + self.tool_name,
                                 title="Configurations saved")
        self.change_screens()

    def on_cancel(self):
        """ Don't save changes made to vent.template """
        npyscreen.notify_confirm("No changes made to " + self.tool_name,
                                 title="Configurations not saved")
        self.change_screens()
