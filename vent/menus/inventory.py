from collections import deque

import npyscreen

from vent.helpers.templates import Template


class InventoryForm(npyscreen.FormBaseNew):
    """ Inventory form for the Vent CLI """

    def __init__(self, action=None, logger=None, *args, **keywords):
        """ Initialize inventory form objects """
        self.action = action
        self.logger = logger
        self.api_action = self.action['api_action']
        # get list of all possible group views to display
        self.views = deque()
        possible_groups = set()
        manifest = Template(self.api_action.manifest)
        tools = self.api_action.inventory(choices=['tools'])[1]['tools']
        for tool in tools:
            groups = manifest.option(tool, 'groups')[1].split(',')
            for group in groups:
                # don't do core because that's the purpose of all in views
                if group != '' and group != 'core':
                    possible_groups.add(group)
        self.views += possible_groups
        self.views.append('all groups')
        super(InventoryForm, self).__init__(*args, **keywords)

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def toggle_view(self, *args, **kwargs):
        group = self.views.popleft()
        new_display = []
        new_display.append('Tools for group ' + group + ' found:')
        manifest = Template(self.api_action.manifest)
        cur_repo = ''
        for i in range(1, len(self.all_tools) - 1):
            val = self.all_tools[i]
            # get repo val
            if val.startswith('  Plugin:'):
                new_display.append(val)
                cur_repo = val.split(':', 1)[1].strip()
            # determine if tool should be displayed in this group
            elif val.startswith('    ') and not val.startswith('      '):
                name = val.strip()
                constraints = {'repo': cur_repo, 'name': name}
                t_section = manifest.constrain_opts(constraints, [])[0]
                t_section = list(t_section.keys())[0]
                if group in manifest.option(t_section, 'groups')[1].split(','):
                    new_display += self.all_tools[i:i+4]
            elif val == '':
                new_display.append(val)
        # if all groups display all groups
        if group == 'all groups':
            self.display_val.values = self.all_tools
        else:
            self.display_val.values = new_display
        # redraw
        self.display()
        # add group back into cycle
        self.views.append(group)

    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({'^T': self.quit, '^Q': self.quit,
                           '^V': self.toggle_view})
        self.add(npyscreen.TitleFixedText, name=self.action['title'], value='')
        response = self.action['api_action'].inventory(choices=['repos',
                                                                'tools',
                                                                'images',
                                                                'built',
                                                                'running'])
        if response[0]:
            inventory = response[1]
            if len(inventory['repos']) == 0:
                value = 'No tools were found.\n'
            else:
                value = 'Tools for all groups found:\n'
            tools = None
            if inventory['tools']:
                tools = inventory['tools']

            for repo in inventory['repos']:
                s_value = ''
                repo_name = repo.rsplit('/', 2)[1:]
                if len(repo_name) == 1:
                    repo_name = repo.split('/')
                if tools:
                    p_value = '\n  Plugin: ' + repo + '\n'
                    for tool in tools:
                        t_name = tool.split(':')
                        if (t_name[0] == repo_name[0] and
                                t_name[1] == repo_name[1]):
                            s_value += '    ' + tools[tool] + '\n      Built: '
                            s_value += inventory['built'][tool] + '\n'
                            s_value += '      Image name: '
                            s_value += inventory['images'][tool] + '\n'
                            s_value += '      Status: '
                            s_value += inventory['running'][tool] + '\n'
                if s_value:
                    value += p_value + s_value
        else:
            value = 'There was an issue with ' + self.action['name']
            value += ' retrieval:\n' + str(response[1])
            value += '\nPlease see vent.log for more details.'
        self.all_tools = value.split('\n')
        self.display_val = self.add(npyscreen.Pager, values=value.split('\n'))
