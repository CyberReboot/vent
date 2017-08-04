import json
import npyscreen

from vent.api.actions import Action
from vent.api.templates import Template

class GroupForm(npyscreen.FormBaseNew):
    """ List tools by the groups they're in """
    def __init__(self, *args, **keywords):
        """ Initialize group form objects """
        self.core = keywords['core']
        if keywords['core']:
            self.title_val = 'Groups of core tools:' + '\n'
        else:
            self.title_val = 'Groups of tools:' + '\n'
        self.action = Action()
        super(GroupForm, self).__init__(*args, **keywords)

    def create(self):
        """ Override method for creating group form """
        self.add_handlers({"^T": self.quit})
        self.add(npyscreen.TitleFixedText, name=self.title_val, value='')
        manifest = Template(self.action.plugin.manifest)
        try:
            if self.core:
                tools = self.action.inventory(choices=['core'])[1]['core']
            else:
                tools = self.action.inventory(choices=['tools'])[1]['tools']
        except Exception:
            tools = []
        output_val = ''
        if tools:
            group_dict = {}
            # find all the groups that the tools are a part of
            for tool in tools:
                # will already know if tools are core so don't need to be redundant
                groups = manifest.option(tool, 'groups')[1].replace('core', '')
                if groups == '':
                    if 'no_group' not in group_dict:
                        group_dict['no_group'] = []
                    group_dict['no_group'].append(tools[tool])
                else:
                    groups = groups.split(',')
                    for group in groups:
                        if group != '':
                            if group not in group_dict:
                                group_dict[group] = []
                            group_dict[group].append(tools[tool])
            if group_dict:
                for group in group_dict:
                    if group != 'no_group':
                        output_val += '\t' + group + ':' + '\n'
                    else:
                        if self.core:
                            output_val += '\t' + 'no additional group' + \
                                    ' besides core:' + '\n'
                        else:
                            output_val += '\t' + 'no group defined:' + '\n'
                    for tool in group_dict[group]:
                        output_val += '\t'*3 + '-' + tool + '\n'
            else:
                output_val = "Tools installed don't belong to groups"
        else:
            output_val = 'No tools are installed yet'
        self.add(npyscreen.Pager, values=output_val.split('\n'))

    def quit(self, *args, **keywords):
        self.parentApp.change_form("MAIN")
