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
            tools = None
            if self.action['cores'] and inventory['core']:
                tools = inventory['core']
            elif not self.action['cores'] and inventory['tools']:
                tools = inventory['tools']

            for repo in inventory['repos']:
                s_value = ''
                repo_name = repo.rsplit("/", 2)[1:]
                if len(repo_name) == 1:
                    repo_name = repo.split('/')
                if tools:
                    p_value = "\n  Plugin: " + repo + "\n"
                    for tool in tools:
                        t_name = tool.split(":")
                        if (t_name[0] == repo_name[0] and
                           t_name[1] == repo_name[1]):
                            s_value += "    " + tools[tool] + "\n      Built: "
                            s_value += inventory['built'][tool] + "\n"
                            s_value += "      Enabled: "
                            s_value += inventory['enabled'][tool] + "\n"
                            s_value += "      Image name: "
                            s_value += inventory['images'][tool] + "\n"
                            s_value += "      Status: "
                            s_value += inventory['running'][tool] + "\n"
                if s_value:
                    value += p_value + s_value
        else:
            value = "There was an issue with " + self.action['name']
            value += " retrieval:\n" + str(response[1])
            value += "\nPlease see vent.log for more details."
        self.add(npyscreen.Pager, values=value.split("\n"))
