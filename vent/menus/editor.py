import npyscreen

class EditorForm(npyscreen.ActionForm):
    def __init__(self, *args, **keywords):
        self.next_tool = keywords['next_tool']
        self.template_val = keywords['template_val']
        super(EditorForm, self).__init__(*args, **keywords)

    def create(self):
        self.m = self.add(npyscreen.MultiLineEdit, value=self.template_val)

    def change_screens(self):
        if self.next_tool:
            self.parentApp.change_form(self.next_tool)
        else:
            self.parentApp.change_form("MAIN")

    def on_ok(self):
        npyscreen.notify_confirm("Done configuring this tool")
        self.change_screens()

    def on_cancel(self):
        npyscreen.notify_confirm("No changes made to this tool")
        self.change_screens()
