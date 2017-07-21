import npyscreen

class BackupForm(npyscreen.ActionForm):
    """ Form that can be used to select a backup file to restore """
    def __init__(self, *args, **keywords):
        self.restore = keywords['restore']
        self.files = keywords['files']
        self.display_vals = []
        for f in self.files:
            date_arr = f.replace('.cfg', '').split('-')[2:]
            self.display_vals.append('-'.join(date_arr[:3]) + ' at ' +
                                     ' '.join(date_arr[3:]))
        super(BackupForm, self).__init__(*args, **keywords)

    def create(self):
        self.add(npyscreen.Textfield, value='Pick a version to restore from: ',
                 editable=False, color="STANDOUT")
        self.file_select = self.add(npyscreen.SelectOne, values=self.display_vals,
                                    scroll_exit=True, rely=4)

    def on_ok(self):
        if self.file_select.value:
            npyscreen.notify_wait("In the process of restoring", title="Restoring...")
            status = self.restore(self.files[self.file_select.value[0]])
            if status[0]:
                npyscreen.notify_confirm("Status of restore:\n" +
                                         status[1])
            else:
                npyscreen.notify_confirm(status[1])
            self.parentApp.change_form("MAIN")
        else:
            npyscreen.notify_confirm("Choose a file to restore from")

    def on_cancel(self):
        self.parentApp.change_form("MAIN")
