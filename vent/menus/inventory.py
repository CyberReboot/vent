import npyscreen


class InventoryForm(npyscreen.FormBaseNew):
    """ Inventory form for the Vent CLI """
    def __init__(self, action=None, logger=None, *args, **keywords):
        """ Initialize inventory form objects """
        self.action = action
        self.logger = logger
        super(InventoryForm, self).__init__(*args, **keywords)

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.add(npyscreen.TitleFixedText, name=self.action['title'], value='')
        response = self.action['api_action'].inventory(choices=['repos',
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
                if (self.action['cores'] or
                   (not self.action['cores'] and
                   repo != "https://github.com/cyberreboot/vent")):
                    value += "\n  Plugin: "+repo+"\n"
                    repo_name = repo.rsplit("/", 2)[1:]
                    if len(repo_name) == 1:
                        repo_name = repo.split('/')
                    for tool in inventory['tools']:
                        is_core = False
                        for core in inventory['core']:
                            if core[0] == tool[0]:
                                is_core = True
                        if ((is_core and self.action['cores']) or
                           (not is_core and not self.action['cores'])):
                            r_name = tool[0].split(":")
                            if (repo_name[0] == r_name[0] and
                               repo_name[1] == r_name[1]):
                                value += "    " + tool[1] + "\n"
                                for built in inventory['built']:
                                    if built[0] == tool[0]:
                                        value += "      Built: " + built[2]
                                        value += "\n"
                                for enabled in inventory['enabled']:
                                    if enabled[0] == tool[0]:
                                        value += "      Enabled: " + enabled[2]
                                        value += "\n"
                                for image in inventory['images']:
                                    if image[0] == tool[0]:
                                        value += "      Image name: "
                                        value += image[2] + "\n"
                                for running in inventory['running']:
                                    if running[0] == tool[0]:
                                        value += "      Status: " + running[2]
                                        value += "\n"
                    if self.action['cores']:
                        tmp_value = value.split("\n")
                        if "Plugin: " in tmp_value[-2]:
                            value = "\n".join(value.split("\n")[:-2])
        else:
            value = "There was an issue with " + self.action['name']
            value += " retrieval:\n" + str(response[1])
            value += "\nPlease see vent.log for more details."
        self.add(npyscreen.Pager, values=value.split("\n"))
