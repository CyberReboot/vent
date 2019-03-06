from vent.api.tools import Tools
from vent.helpers.logs import Logger
from vent.menus.inventory import InventoryForm


class BaseInventoryForm(InventoryForm):
    """ Base form to inherit from """

    def __init__(self, action_dict=None, action_name=None, *args, **keywords):
        api_action = Tools()
        action = {'api_action': api_action}
        if action_dict:
            action.update(action_dict)
        logger = Logger(action_name)
        InventoryForm.__init__(self, action, logger, *args, **keywords)


class InventoryToolsForm(BaseInventoryForm):
    """ Inventory Tools form for the Vent CLI """

    def __init__(self, *args, **keywords):
        """ Initialize inventory tools form objects """
        action_name = 'inventory'
        action_dict = {'title': 'Inventory of tools:',
                       'name': 'inventory',
                       'cores': False}
        BaseInventoryForm.__init__(self,
                                   action_dict,
                                   action_name,
                                   *args,
                                   **keywords)
