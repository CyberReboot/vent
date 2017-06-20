import npyscreen
import threading
import time

from vent.helpers.meta import Containers
from vent.helpers.meta import Images


class ToolForm(npyscreen.ActionForm):
    """ Tools form for teh Vent CLI """
    def __init__(self, action=None, logger=None, *args, **keywords):
        """ Initialize tool form objects """
        self.action = action
        self.logger = logger
        self.tools_tc = {}
        super(ToolForm, self).__init__(*args, **keywords)

    def switch(self, *args, **kwargs):
        """ Wrapper that switches to MAIN form """
        self.parentApp.change_form("MAIN")

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def create(self):
        """ Update with current tools """
        self.add_handlers({"^T": self.switch, "^Q": self.quit})
        self.add(npyscreen.TitleText,
                 name='Select which tools to ' + self.action['action'] + ':',
                 editable=False)

        i = 4
        response = self.action['api_action'].inventory(choices=['core',
                                                                'repos',
                                                                'tools'])
        if response[0]:
            inventory = response[1]
            for repo in inventory['repos']:
                if (self.action['cores'] or
                   (not self.action['cores'] and
                   repo != 'https://github.com/cyberreboot/vent')):
                    repo_name = repo.rsplit("/", 2)[1:]
                    self.tools_tc[repo] = {}
                    title_text = self.add(npyscreen.TitleText,
                                          name='Plugin: '+repo,
                                          editable=False, rely=i, relx=5)
                    i += 1
                    for tool in inventory['tools']:
                        r_name = tool[0].split(":")
                        if (repo_name[0] == r_name[0] and
                           repo_name[1] == r_name[1]):
                            core = False
                            for item in inventory['core']:
                                if tool[0] == item[0]:
                                    core = True
                            t = tool[1]
                            if t == "":
                                t = "/"
                            if ((core and self.action['cores']) or
                               (not core and not self.action['cores'])):
                                t += ":" + ":".join(tool[0].split(":")[-2:])
                                self.tools_tc[repo][t] = self.add(npyscreen.CheckBox, name=t, value=True, relx=10)
                                i += 1
                    i += 2
        return

    def on_ok(self):
        """
        Take the tool selections and perform the provided action on them
        """
        def diff(first, second):
            """
            Get the elements that exist in the first list and not in the second
            """
            second = set(second)
            return [item for item in first if item not in second]

        def popup(original, orig_type, thr, title):
            """
            Start the thread and display a popup of info
            until the thread is finished
            """
            thr.start()
            info_str = ""
            while thr.is_alive():
                if orig_type == 'containers':
                    info = diff(Containers(), original)
                elif orig_type == 'images':
                    info = diff(Images(), original)
                if info:
                    info_str = ""
                for entry in info:
                    # TODO limit length of info_str to fit box
                    info_str += entry[0]+": "+entry[1]+"\n"
                npyscreen.notify_wait(info_str, title=title)
                time.sleep(1)
            return

        if self.action['type'] == 'images':
            originals = Images()
        else:
            originals = Containers()

        for repo in self.tools_tc:
            for tool in self.tools_tc[repo]:
                self.logger.info(tool)
                if self.tools_tc[repo][tool].value:
                    t = tool
                    if t.startswith('/:'):
                        t = " "+t[1:]
                    t = t.split(":")
                    thr = threading.Thread(target=self.action['action_object'],
                                           args=(),
                                           kwargs={'name': t[0],
                                                   'branch': t[1],
                                                   'version': t[2]})
                    popup(originals, self.action['type'], thr,
                          'Please wait, ' + self.action['present_tense'] + '...')
        npyscreen.notify_confirm('Done ' + self.action['present_tense'] + '.',
                                 title=self.action['past_tense'])
        self.quit()

    def on_cancel(self):
        """ When user clicks cancel, will return to MAIN """
        self.quit()
