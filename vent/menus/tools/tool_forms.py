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
                  'present_tense': 'building images',
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
                  'present_tense': 'building core images',
                  'past_tense': 'Built core images',
                  'type': 'images',
                  'action': 'build (only core tools are shown)',
                  'cores': True}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)


class CleanToolsForm(ToolForm):
    """ Clean Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize cleaning tools form objects """
        api_action = Action()
        action = {'api_action': api_action,
                  'action_object': api_action.clean,
                  'present_tense': 'cleaning containers',
                  'past_tense': 'Cleaned containers',
                  'type': 'containers',
                  'action': 'clean (only plugin tools are shown)',
                  'cores': False}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)


class CleanCoreToolsForm(ToolForm):
    """ Clean Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize cleaning core tools form objects """
        api_action = Action()
        action = {'api_action': api_action,
                  'action_object': api_action.clean,
                  'present_tense': 'cleaning core containers',
                  'past_tense': 'Cleaned core containers',
                  'type': 'containers',
                  'action': 'clean (only core tools are shown)',
                  'cores': True}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)


class RemoveToolsForm(ToolForm):
    """ Remove Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize removing tools form objects """
        api_action = Action()
        action = {'api_action': api_action,
                  'action_object': api_action.remove,
                  'present_tense': 'removing containers',
                  'past_tense': 'Removed containers',
                  'type': 'containers',
                  'action': 'remove (only plugin tools are shown)',
                  'cores': False}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)


class RemoveCoreToolsForm(ToolForm):
    """ Remove Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize removing core tools form objects """
        api_action = Action()
        action = {'api_action': api_action,
                  'action_object': api_action.remove,
                  'present_tense': 'removing core containers',
                  'past_tense': 'Removed core containers',
                  'type': 'containers',
                  'action': 'remove (only core tools are shown)',
                  'cores': True}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)


class StopToolsForm(ToolForm):
    """ Stop Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize stopping tools form objects """
        api_action = Action()
        action = {'api_action': api_action,
                  'action_object': api_action.stop,
                  'present_tense': 'stopping containers',
                  'past_tense': 'Stopped containers',
                  'type': 'containers',
                  'action': 'stop (only plugin tools are shown)',
                  'cores': False}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)


class StopCoreToolsForm(ToolForm):
    """ Stop Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize stopping core tools form objects """
        api_action = Action()
        action = {'api_action': api_action,
                  'action_object': api_action.stop,
                  'present_tense': 'stopping core containers',
                  'past_tense': 'Stopped core containers',
                  'type': 'containers',
                  'action': 'stop (only core tools are shown)',
                  'cores': True}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)


class UpdateToolsForm(ToolForm):
    """ Update Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize updating tools form objects """
        api_action = Action()
        action = {'api_action': api_action,
                  'action_object': api_action.update,
                  'present_tense': 'updating containers',
                  'past_tense': 'Updated containers',
                  'type': 'containers',
                  'action': 'update (only plugin tools are shown)',
                  'cores': False}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)


class UpdateCoreToolsForm(ToolForm):
    """ Update Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize updating core tools form objects """
        api_action = Action()
        action = {'api_action': api_action,
                  'action_object': api_action.update,
                  'present_tense': 'updating core containers',
                  'past_tense': 'Updated core containers',
                  'type': 'containers',
                  'action': 'update (only core tools are shown)',
                  'cores': True}
        logger = Logger(__name__)
        ToolForm.__init__(self, action, logger)
