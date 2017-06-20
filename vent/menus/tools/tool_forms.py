from vent.api.actions import Action
from vent.helpers.logs import Logger
from vent.menus.tools.tools import ToolForm


class BuildToolsForm(ToolForm):
    """ Build Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize building tools form objects """
        api_action = Action()
        action = {'api_action': api_action,
                  'action_object': api_action.build,
                  'present_tense':'building images',
                  'past_tense': 'Built images',
                  'type': 'images',
                  'action': 'build (only plugin tools are shown)',
                  'cores': False}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)

class BuildCoreToolsForm(ToolForm):
    """ Build Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize building core tools form objects """
        api_action = Action()
        action = {'api_action': api_action,
                  'action_object': api_action.build,
                  'present_tense':'building core images',
                  'past_tense': 'Built core images',
                  'type': 'images',
                  'action': 'build (only core tools are shown)',
                  'cores': True}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)
