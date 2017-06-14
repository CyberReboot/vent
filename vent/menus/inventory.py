import npyscreen
import os
import sys

from vent.api.actions import Action


class InventoryForm(npyscreen.FormBaseNew):
    """ Inventory form for the Vent CLI """

    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.change_forms,"^Q": self.exit})
        self.add(npyscreen.TitleFixedText, name='Inventory items:', value='')
        self.action = Action()
        response = self.action.inventory(choices=['repos',
                                                  'core',
                                                  'tools',
                                                  'images',
                                                  'built',
                                                  'running',
                                                  'enabled'])
        if response[0]:
            inventory = response[1]
            if len(inventory['repos']) == 0:
                value = "No tools were found.\n"
            else:
                value = "Tools for each plugin found:\n"
            for repo in inventory['repos']:
                if repo != "https://github.com/cyberreboot/vent":
                    value += "\n  Plugin: "+repo+"\n"
                    repo_name = repo.rsplit("/", 2)[1:]
                    for tool in inventory['tools']:
                        is_core = False
                        for core in inventory['core']:
                            if core[0] == tool[0]:
                                is_core = True
                        if not is_core:
                            r_name = tool[0].split(":")
                            if repo_name[0] == r_name[0] and repo_name[1] == r_name[1]:
                                value += "    "+tool[1]+"\n"
                                for built in inventory['built']:
                                    if built[0] == tool[0]:
                                        value += "      Built: "+built[2]+"\n"
                                for enabled in inventory['enabled']:
                                    if enabled[0] == tool[0]:
                                        value += "      Enabled: "+enabled[2]+"\n"
                                for image in inventory['images']:
                                    if image[0] == tool[0]:
                                        value += "      Image name: "+image[2]+"\n"
                                for running in inventory['running']:
                                    if running[0] == tool[0]:
                                        value += "      Status: "+running[2]+"\n"
        else:
            value = "There was an issue with inventory retrieval:\n" + \
                    str(response[1]) + \
                    "\nPlease see vent.log for more details."
        self.add(npyscreen.Pager, values=value.split("\n"))

    def exit(self, *args, **keywords):
        self.parentApp.switchForm("MAIN")

    def change_forms(self, *args, **keywords):
        """ Toggles back to main """
        change_to = "MAIN"

        # Tell the VentApp object to change forms.
        self.parentApp.change_form(change_to)
