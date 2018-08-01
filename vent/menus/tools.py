import json
import re
import time
from collections import deque
from threading import Thread

import npyscreen

from vent.api.actions import Action
from vent.api.menu_helpers import MenuHelper
from vent.api.templates import Template
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
        self.m_helper = MenuHelper()
        action = {'api_action': self.api_action}
        self.tools_tc = {}
        self.repo_widgets = {}
        if keywords['action_dict']:
            action.update(keywords['action_dict'])
        if keywords['names']:
            i = 1
            for name in keywords['names']:
                action['action_object'+str(i)] = getattr(self.api_action, name)
                i += 1
        self.action = action
        # get list of all possible group views to display
        self.views = deque()
        possible_groups = set()
        manifest = Template(self.api_action.plugin.manifest)
        if self.action['cores']:
            tools = self.api_action.inventory(choices=['core'])[1]['core']
        else:
            tools = self.api_action.inventory(choices=['tools'])[1]['tools']
        for tool in tools:
            groups = manifest.option(tool, 'groups')[1].split(',')
            for group in groups:
                # don't do core because that's the purpose of all in views
                if group != '' and group != 'core':
                    possible_groups.add(group)
        self.manifest = manifest
        self.views += possible_groups
        self.views.append('all groups')
        self.no_instance = ['build', 'remove']
        super(ToolForm, self).__init__(*args, **keywords)

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def toggle_view(self, *args, **kwargs):
        """ Toggles the view between different groups """
        group_to_display = self.views.popleft()
        self.cur_view.value = group_to_display
        for repo in self.tools_tc:
            for tool in self.tools_tc[repo]:
                t_groups = self.manifest.option(tool, 'groups')[1]
                if group_to_display not in t_groups and \
                        group_to_display != 'all groups':
                    self.tools_tc[repo][tool].value = False
                    self.tools_tc[repo][tool].hidden = True
                else:
                    self.tools_tc[repo][tool].value = True
                    self.tools_tc[repo][tool].hidden = False
        # redraw elements
        self.display()
        # add view back to queue
        self.views.append(group_to_display)

    def create(self, group_view=False):
        """ Update with current tools """
        self.add_handlers({'^T': self.quit, '^Q': self.quit})
        self.add(npyscreen.TitleText,
                 name='Select which tools to ' + self.action['action'] + ':',
                 editable=False)
        togglable = ['remove', 'enable', 'disable', 'build']
        if self.action['action_name'] in togglable:
            self.cur_view = self.add(npyscreen.TitleText,
                                     name='Group view:',
                                     value='all groups', editable=False,
                                     rely=3)
            self.add_handlers({'^V': self.toggle_view})
            i = 5
        else:
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
                if (repo.startswith('http')):
                    repo_name = repo.rsplit('/', 2)[1:]
                else:
                    repo_name = repo.split('/')

                # determine if enabled or disabled tools should be shown
                show_disabled = False
                if 'action_name' in self.action:
                    if self.action['action_name'] == 'enable':
                        show_disabled = True

                for tool in inventory['tools']:
                    tool_repo_name = tool.split(':')

                    # cross reference repo names
                    if (repo_name[0] == tool_repo_name[0] and
                            repo_name[1] == tool_repo_name[1]):
                        # check to ensure tool not set to locally active = no
                        # in vent.cfg
                        externally_active = False
                        vent_cfg_file = self.action['api_action'].vent_config
                        vent_cfg = Template(vent_cfg_file)
                        tool_pairs = vent_cfg.section('external-services')[1]
                        for ext_tool in tool_pairs:
                            if ext_tool[0].lower() == inventory['tools'][tool]:
                                try:
                                    ext_tool_options = json.loads(ext_tool[1])
                                    loc = 'locally_active'
                                    if (loc in ext_tool_options and
                                            ext_tool_options[loc] == 'no'):
                                        externally_active = True
                                except Exception as e:
                                    self.logger.error("Couldn't check ext"
                                                      ' because: ' + str(e))
                                    externally_active = False
                        # check to ensure not disabled
                        disabled = False
                        manifest = Template(self.api_action.plugin.manifest)
                        if manifest.option(tool, 'enabled')[1] == 'no':
                            disabled = True
                        if (not externally_active and not disabled and not
                                show_disabled):
                            instance_num = re.search(r'\d+$',
                                                     manifest.option(
                                                         tool, 'name')[1])
                            if not instance_num:
                                ncore_list.append(tool)
                            # multiple instances share same image
                            elif self.action['action_name'] not in self.no_instance:
                                ncore_list.append(tool)
                        elif (not externally_active and disabled and
                                show_disabled):
                            instance_num = re.search(r'\d+$',
                                                     manifest.option(
                                                         tool, 'name')[1])
                            if not instance_num:
                                ncore_list.append(tool)
                            # multiple instances share same image
                            elif self.action['action_name'] not in self.no_instance:
                                ncore_list.append(tool)

                for tool in inventory['core']:
                    tool_repo_name = tool.split(':')

                    # cross reference repo names
                    if (repo_name[0] == tool_repo_name[0] and
                            repo_name[1] == tool_repo_name[1]):
                        # check to ensure tool not set to locally active = no
                        # in vent.cfg
                        externally_active = False
                        vent_cfg_file = self.action['api_action'].vent_config
                        vent_cfg = Template(vent_cfg_file)
                        tool_pairs = vent_cfg.section('external-services')[1]
                        for ext_tool in tool_pairs:
                            if ext_tool[0].lower() == inventory['core'][tool]:
                                try:
                                    ext_tool_options = json.loads(ext_tool[1])
                                    loc = 'locally_active'
                                    if (loc in ext_tool_options and
                                            ext_tool_options[loc] == 'no'):
                                        externally_active = True
                                except Exception as e:
                                    self.logger.error("Couldn't check ext"
                                                      ' because: ' + str(e))
                                    externally_active = False
                        # check to ensure not disabled
                        disabled = False
                        manifest = Template(self.api_action.plugin.manifest)
                        if manifest.option(tool, 'enabled')[1] == 'no':
                            disabled = True
                        if (not externally_active and not disabled and not
                                show_disabled):
                            instance_num = re.search(r'\d+$',
                                                     manifest.option(
                                                         tool, 'name')[1])
                            if not instance_num:
                                core_list.append(tool)
                            # multiple instances share same image
                            elif self.action['action_name'] not in self.no_instance:
                                core_list.append(tool)
                        elif (not externally_active and disabled and
                                show_disabled):
                            instance_num = re.search(r'\d+$',
                                                     manifest.option(
                                                         tool, 'name')[1])
                            if not instance_num:
                                core_list.append(tool)
                            # multiple instances share same image
                            elif self.action['action_name'] not in self.no_instance:
                                core_list.append(tool)

                has_core[repo] = core_list
                has_non_core[repo] = ncore_list

            for repo in repos:
                self.tools_tc[repo] = {}

                if self.action['cores']:
                    # make sure only repos with core tools are displayed
                    if has_core.get(repo):
                        self.repo_widgets[repo] = self.add(npyscreen.TitleText,
                                                           name='Plugin: '+repo,
                                                           editable=False,
                                                           rely=i, relx=5)

                        for tool in has_core[repo]:
                            tool_name = tool.split(':', 2)[2].split('/')[-1]
                            if tool_name == '':
                                tool_name = '/'
                            self.tools_tc[repo][tool] = self.add(
                                npyscreen.CheckBox, name=tool_name,
                                value=True, relx=10)
                            i += 1
                        i += 3
                else:
                    # make sure only repos with non-core tools are displayed
                    if has_non_core.get(repo):
                        self.repo_widgets[repo] = self.add(npyscreen.TitleText,
                                                           name='Plugin: '+repo,
                                                           editable=False,
                                                           rely=i, relx=5)

                        for tool in has_non_core[repo]:
                            tool_name = tool.split(':', 2)[2].split('/')[-1]
                            if tool_name == '':
                                tool_name = '/'
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
            info_str = ''
            while thr.is_alive():
                if orig_type == 'containers':
                    info = diff(Containers(), original)
                elif orig_type == 'images':
                    info = diff(Images(), original)
                if info:
                    info_str = ''
                for entry in info:
                    info_str = entry[0] + ': ' + entry[1] + '\n' + info_str
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
                        r_str += container + ': successful\n'
                    for container in failed:
                        r_str += container + ': failed\n'
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
            reconfirmation_str = ''
            if self.action['cores']:
                reconfirmation_str = 'Are you sure you want to '
                reconfirmation_str += self.action['action_name']
                reconfirmation_str += ' core containers?'
            else:
                reconfirmation_str = 'Are you sure you want to '
                reconfirmation_str += self.action['action_name']
                reconfirmation_str += ' plugin containers?'

            perform = npyscreen.notify_ok_cancel(reconfirmation_str,
                                                 title='Confirm command')
            if not perform:
                return

        tools_to_configure = []
        for repo in self.tools_tc:
            for tool in self.tools_tc[repo]:
                self.logger.info(tool)
                if self.tools_tc[repo][tool].value:
                    t = tool.split(':', 2)[2].split('/')[-1]
                    if t.startswith('/:'):
                        t = ' '+t[1:]
                    t = t.split(':')
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
                        name = list(tool.keys())[0]
                        if tool[name]['type'] == 'registry':
                            registry_image = True
                        else:
                            registry_image = False
                        kargs = {'name': 'Configure ' + t[0],
                                 'tool_name': t[0],
                                 'branch': t[1],
                                 'version': t[2],
                                 'repo': repo,
                                 'next_tool': None,
                                 'get_configure': action.get_configure,
                                 'save_configure': action.save_configure,
                                 'restart_tools': action.restart_tools,
                                 'clean': action.clean,
                                 'prep_start': action.prep_start,
                                 'start_tools': action.start,
                                 'from_registry': registry_image}
                        if tools_to_configure:
                            kargs['next_tool'] = tools_to_configure[-1]
                        self.parentApp.addForm('EDITOR' + t[0], EditorForm,
                                               **kargs)
                        tools_to_configure.append('EDITOR' + t[0])
                    else:
                        kargs = {'name': t[0],
                                 'branch': t[1],
                                 'version': t[2]}
                        # add core recognition
                        if self.action['cores']:
                            kargs.update({'groups': 'core'})
                        # use latest version for update, not necessarily
                        # version in manifest
                        if self.action['action_name'] == 'update':
                            if t[2] != 'HEAD':
                                repo_commits = self.m_helper.repo_commits(repo)[
                                    1]
                                for branch in repo_commits:
                                    if branch[0] == t[1]:
                                        kargs.update(
                                            {'new_version': branch[1][0]})
                            else:
                                kargs.update({'new_version': 'HEAD'})
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
                npyscreen.notify_confirm('No tools selected, returning to'
                                         ' main menu',
                                         title='No action taken')
                self.quit()

    def on_cancel(self):
        """ When user clicks cancel, will return to MAIN """
        self.quit()
