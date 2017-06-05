import npyscreen
import threading
import time

from vent.api.plugins import Plugin

class AddForm(npyscreen.ActionForm):
    """ For for adding a new repo """
    def create(self):
        """ Create widgets for AddForm """
        # !! TODO have option for image to pull from a registry with tag
        self.add_handlers({"^T": self.change_forms, "^Q": self.quit})
        self.repo = self.add(npyscreen.TitleText, name='Repository',
                             value='https://github.com/cyberreboot/vent-plugins')
        self.user = self.add(npyscreen.TitleText, name='Username')
        self.pw = self.add(npyscreen.TitlePassword, name='Password')
        self.repo.when_value_edited()

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm("MAIN")

    def on_ok(self):
        """ Add the repository """
        self.parentApp.repo_value['repo'] = self.repo.value
        def popup(thr, title):
            """
            Start the thread and display a popup of the plugin being cloned
            until the thread is finished
            """
            thr.start()
            tool_str = "Cloning repository..."
            npyscreen.notify_wait(tool_str, title=title)
            while thr.is_alive():
                time.sleep(1)
            return

        api_plugin = Plugin()
        thr = threading.Thread(target=api_plugin.clone, args=(),
                               kwargs={'repo':self.repo.value,
                                       'user':self.user.value,
                                       'pw':self.pw.value})
        popup(thr, 'Please wait, adding repository...')
        self.parentApp.change_form('ADDOPTIONS')

    def on_cancel(self):
        self.quit()

    def change_forms(self, *args, **keywords):
        """ Toggles back and forth between help """
        change_to = "HELP"

        # Tell the VentApp object to change forms.
        self.parentApp.change_form(change_to)
