import npyscreen


class BackupForm(npyscreen.ActionForm):
    """ Form that can be used to select a backup file to restore """

    def __init__(self, *args, **keywords):
        """ Initialize backup form objects """
        self.restore = keywords['restore']
        self.dirs = keywords['dirs']
        self.display_vals = []
        for bdir in self.dirs:
            date_arr = bdir.split('-')[2:]
            self.display_vals.append('-'.join(date_arr[:3]) + ' at ' +
                                     ' '.join(date_arr[3:]))
        super(BackupForm, self).__init__(*args, **keywords)

    def create(self):
        """ Add backup files to select from """
        self.add_handlers({'^T': self.quit})
        self.add(npyscreen.Textfield, value='Pick a version to restore from: ',
                 editable=False, color='STANDOUT')
        self.dir_select = self.add(npyscreen.SelectOne,
                                   values=self.display_vals,
                                   scroll_exit=True, rely=4)

    def quit(self, *args, **kwargs):
        self.parentApp.change_form('MAIN')

    def on_ok(self):
        """ Perform restoration on the backup file selected """
        if self.dir_select.value:
            npyscreen.notify_wait('In the process of restoring',
                                  title='Restoring...')
            status = self.restore(self.dirs[self.dir_select.value[0]])
            if status[0]:
                npyscreen.notify_confirm('Status of restore:\n' +
                                         status[1])
            else:
                npyscreen.notify_confirm(status[1])
            self.quit()
        else:
            npyscreen.notify_confirm('Choose a version to restore from')

    def on_cancel(self):
        """ When user clicks cancel, will return to MAIN """
        self.quit()
