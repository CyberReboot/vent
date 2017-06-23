import npyscreen
import threading
import time

from vent.api.plugins import Plugin
from vent.menus.add_options import AddOptionsForm


class AddForm(npyscreen.ActionForm):
    """ For for adding a new repo """
    def create(self):
        """ Create widgets for AddForm """
        # !! TODO have option for image to pull from a registry with tag
        self.add_handlers({"^T": self.switch, "^Q": self.quit})
        self.repo = self.add(npyscreen.TitleText, name='Repository',
                             value='https://github.com/cyberreboot/vent-plugins')
        self.user = self.add(npyscreen.TitleText, name='Username')
        self.pw = self.add(npyscreen.TitlePassword, name='Password')
        self.repo.when_value_edited()

    def switch(self, *args, **kwargs):
        """ Wrapper that switches to HELP form """
        self.parentApp.change_form("HELP")

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
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
        self.parentApp.addForm("ADDOPTIONS", AddOptionsForm, name="Set options for new plugin\t\t\t\t\t\tPress ^Q to quit", color="CONTROL")
        self.parentApp.change_form('ADDOPTIONS')

    def on_cancel(self):
        """ When user clicks cancel, will return to MAIN """
        self.quit()
