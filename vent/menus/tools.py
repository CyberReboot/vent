import npyscreen
import time

from threading import Thread

from vent.api.actions import Action
from vent.helpers.logs import Logger
from vent.helpers.meta import Containers
from vent.helpers.meta import Images
from vent.menus.editor import EditorForm


class ToolForm(npyscreen.ActionForm):
    """ Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize tool form objects """
        self.logger = Logger(__name__)
        self.logger.info(str(keywords['names']))
        self.api_action = Action()
        action = {'api_action': self.api_action}
        self.tools_tc = {}
        if keywords['action_dict']:
            action.update(keywords['action_dict'])
        if keywords['names']:
            i = 1
            for name in keywords['names']:
                action['action_object'+str(i)] = getattr(self.api_action, name)
                i += 1
        self.action = action
        super(ToolForm, self).__init__(*args, **keywords)

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def create(self):
        """ Update with current tools """
        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.add(npyscreen.TitleText,
                 name='Select which tools to ' + self.action['action'] + ':',
                 editable=False)

        i = 4
        if self.action['action_name'] == 'start':
            response = self.action['api_action'].inventory(choices=['repos',
                                                                    'tools',
                                                                    'built',
                                                                    'enabled',
                                                                    'running',
                                                                    'core'])
        else:
            response = self.action['api_action'].inventory(choices=['core',
                                                                    'repos',
                                                                    'tools'])
        if response[0]:
            inventory = response[1]

            repos = inventory['repos']

            # dict has repo as key and list of core/non-core tools as values
            has_core = {}
            has_non_core = {}

            # find all tools that are in this repo
            # and list them if they are core
            for repo in repos:
                core_list = []
                ncore_list = []

                # splice the repo names for processing
                if (repo.startswith("http")):
                    repo_name = repo.rsplit("/", 2)[1:]
                else:
                    repo_name = repo.split("/")

                for tool in inventory['tools']:
                    tool_repo_name = tool.split(":")

                    # cross reference repo names
                    if (repo_name[0] == tool_repo_name[0] and
                       repo_name[1] == tool_repo_name[1]):
                        ncore_list.append(tool.split(":", 2)[2].split("/")[-1])

                for tool in inventory['core']:
                    tool_repo_name = tool.split(":")

                    # cross reference repo names
                    if (repo_name[0] == tool_repo_name[0] and
                       repo_name[1] == tool_repo_name[1]):
                        core_list.append(tool.split(":", 2)[2].split("/")[-1])

                has_core[repo] = core_list
                has_non_core[repo] = ncore_list

            for repo in repos:
                self.tools_tc[repo] = {}

                if self.action['cores']:
                    # make sure only repos with core tools are displayed
                    if has_core.get(repo):
                        self.add(npyscreen.TitleText,
                                 name='Plugin: '+repo,
                                 editable=False, rely=i, relx=5)

                        for tool in has_core[repo]:
                            tool_name = tool
                            if tool_name == "":
                                tool_name = "/"
                            self.tools_tc[repo][tool] = self.add(
                                    npyscreen.CheckBox, name=tool_name,
                                    value=True, relx=10)
                            i += 1
                        i += 3
                else:
                    # make sure only repos with non-core tools are displayed
                    if has_non_core.get(repo):
                        self.add(npyscreen.TitleText,
                                 name='Plugin: '+repo,
                                 editable=False, rely=i, relx=5)

                        for tool in has_non_core[repo]:
                            tool_name = tool
                            if tool_name == "":
                                tool_name = "/"
                            self.tools_tc[repo][tool] = self.add(
                                    npyscreen.CheckBox, name=tool_name,
                                    value=True, relx=10)
                            i += 1
                        i += 3
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
                    info_str = entry[0] + ": " + entry[1] + "\n" + info_str
                if self.action['action_name'] != 'configure':
                    npyscreen.notify_wait(info_str, title=title)
                    time.sleep(1)

            thr.join()
            try:
                result = self.api_action.queue.get(False)
                if isinstance(result, tuple) and isinstance(result[1], tuple):
                    running, failed = result[1]
                    r_str = ''
                    for container in running:
                        r_str += container + ": successful\n"
                    for container in failed:
                        r_str += container + ": failed\n"
                    npyscreen.notify_confirm(r_str)
            except Exception as e:  # pragma: no cover
                pass
            return

        if self.action['type'] == 'images':
            originals = Images()
        else:
            originals = Containers()

        tool_d = {}
        if self.action['action_name'] in ['clean', 'remove', 'stop', 'update']:
            reconfirmation_str = ""
            if self.action['cores']:
                reconfirmation_str = "Are you sure you want to "
                reconfirmation_str += self.action['action_name']
                reconfirmation_str += " core containers?"
            else:
                reconfirmation_str = "Are you sure you want to "
                reconfirmation_str += self.action['action_name']
                reconfirmation_str += " plugin containers?"

            perform = npyscreen.notify_ok_cancel(reconfirmation_str,
                                                 title="Confirm command")
            if not perform:
                return

        tools_to_configure = []
        for repo in self.tools_tc:
            for tool in self.tools_tc[repo]:
                self.logger.info(tool)
                if self.tools_tc[repo][tool].value:
                    t = tool
                    if t.startswith('/:'):
                        t = " "+t[1:]
                    t = t.split(":")
                    if self.action['action_name'] == 'start':
                        status = self.action['action_object2'](name=t[0],
                                                               branch=t[1],
                                                               version=t[2])
                        if status[0]:
                            tool_d.update(status[1])
                    elif self.action['action_name'] == 'configure':
                        constraints = {'name': t[0],
                                       'branch': t[1],
                                       'version': t[2],
                                       'repo': repo}
                        options = ['type']
                        action = self.action['api_action']
                        tool = action.p_helper.constraint_options(constraints,
                                                                  options)[0]
                        # only one tool should be returned
                        name = tool.keys()[0]
                        if tool[name]['type'] == 'registry':
                            registry_image = True
                        else:
                            registry_image = False
                        kargs = {'name': 'Configure ' + t[0],
                                 'tool_name': t[0],
                                 'branch': t[1],
                                 'version': t[2],
                                 'next_tool': None,
                                 'get_configure': self.action['action_object1'],
                                 'save_configure': self.action['action_object2'],
                                 'from_registry': registry_image,
                                 'registry_download': False}
                        if tools_to_configure:
                            kargs['next_tool'] = tools_to_configure[-1]
                        self.parentApp.addForm("EDITOR" + t[0], EditorForm,
                                               **kargs)
                        tools_to_configure.append("EDITOR" + t[0])
                    else:
                        kargs = {'name': t[0],
                                 'branch': t[1],
                                 'version': t[2]}
                        # add core recognition
                        if self.action['cores']:
                            kargs.update({'groups': 'core'})
                        thr = Thread(target=self.action['action_object1'],
                                     args=(),
                                     kwargs=kargs)
                        popup(originals, self.action['type'], thr,
                              'Please wait, ' + self.action['present_t'] +
                              '...')
        if self.action['action_name'] == 'start':
            thr = Thread(target=self.action['action_object1'],
                         args=(),
                         kwargs={'tool_d': tool_d})
            popup(originals, self.action['type'], thr,
                  'Please wait, ' + self.action['present_t'] + '...')

        if self.action['action_name'] != 'configure':
            npyscreen.notify_confirm('Done ' + self.action['present_t'] + '.',
                                     title=self.action['past_t'])
            self.quit()
        else:
            if len(tools_to_configure) > 0:
                self.parentApp.change_form(tools_to_configure[-1])
            else:
                npyscreen.notify_confirm("No tools selected, returning to"
                                         " main menu",
                                         title="No action taken")
                self.quit()

    def on_cancel(self):
        """ When user clicks cancel, will return to MAIN """
        self.quit()
