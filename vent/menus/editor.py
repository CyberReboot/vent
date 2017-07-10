import npyscreen

class EditorForm(npyscreen.ActionForm):
    def __init__(self, *args, **keywords):
        self.next_tool = None
        if keywords['next_tool']:
            self.next_tool = keywords['next_tool']
        super(EditorForm, self).__init__(*args, **keywords)

    def create(self):
        self.m = self.add(npyscreen.MultiLineEdit, value='test')

    def on_ok(self):
        npyscreen.notify_confirm("Done configuring this tool")
        if self.next_tool:
            self.parentApp.change_form(self.next_tool)
        else:
            self.parentApp.change_form("MAIN")
