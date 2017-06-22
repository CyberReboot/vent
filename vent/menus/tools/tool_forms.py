from vent.api.actions import Action
from vent.helpers.logs import Logger
from vent.menus.tools.tools import ToolForm


class BaseForm(ToolForm):
    """ Base form to inherit from """
    def __init__(self, action_dict=None, names=None, *args, **keywords):
        api_action = Action()
        action = {'api_action': api_action}
        if action_dict:
            action.update(action_dict)
        if names:
            i = 1
            for name in names:
                action['action_object'+str(i)] = getattr(api_action, name)
                i += 1
        logger = Logger(name[0])
        ToolForm.__init__(self, action, logger)


class BuildToolsForm(BaseForm):
    """ Build Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize building tools form objects """
        names = ['build']
        action_dict = {'action_name': 'build',
                       'present_tense': 'building images',
                       'past_tense': 'Built images',
                       'type': 'images',
                       'action': 'build (only plugin tools are shown)',
                       'cores': False}
        BaseForm.__init__(self, action_dict, names)


class BuildCoreToolsForm(BaseForm):
    """ Build Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize building core tools form objects """
        names = ['build']
        action_dict = {'action_name': 'build',
                       'present_tense': 'building core images',
                       'past_tense': 'Built core images',
                       'type': 'images',
                       'action': 'build (only core tools are shown)',
                       'cores': True}
        BaseForm.__init__(self, action_dict, names)


class CleanToolsForm(BaseForm):
    """ Clean Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize cleaning tools form objects """
        names = ['clean']
        action_dict = {'action_name': 'clean',
                       'present_tense': 'cleaning containers',
                       'past_tense': 'Cleaned containers',
                       'type': 'containers',
                       'action': 'clean (only plugin tools are shown)',
                       'cores': False}
        BaseForm.__init__(self, action_dict, names)


class CleanCoreToolsForm(BaseForm):
    """ Clean Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize cleaning core tools form objects """
        names = ['clean']
        action_dict = {'action_name': 'clean',
                       'present_tense': 'cleaning core containers',
                       'past_tense': 'Cleaned core containers',
                       'type': 'containers',
                       'action': 'clean (only core tools are shown)',
                       'cores': True}
        BaseForm.__init__(self, action_dict, names)


class RemoveToolsForm(BaseForm):
    """ Remove Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize removing tools form objects """
        names = ['remove']
        action_dict = {'action_name': 'remove',
                       'present_tense': 'removing containers',
                       'past_tense': 'Removed containers',
                       'type': 'containers',
                       'action': 'remove (only plugin tools are shown)',
                       'cores': False}
        BaseForm.__init__(self, action_dict, names)


class RemoveCoreToolsForm(BaseForm):
    """ Remove Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize removing core tools form objects """
        names = ['remove']
        action_dict = {'action_name': 'remove',
                       'present_tense': 'removing core containers',
                       'past_tense': 'Removed core containers',
                       'type': 'containers',
                       'action': 'remove (only core tools are shown)',
                       'cores': True}
        BaseForm.__init__(self, action_dict, names)


class StartToolsForm(BaseForm):
    """ Start Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize starting tools form objects """
        names = ['start', 'prep_start']
        action_dict = {'action_name': 'start',
                       'present_tense': 'starting containers',
                       'past_tense': 'Started containers',
                       'type': 'containers',
                       'action': 'start (only enabled, built, non-running plugin tools are shown)',
                       'cores': False}
        BaseForm.__init__(self, action_dict, names)


class StartCoreToolsForm(BaseForm):
    """ Start Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize starting core tools form objects """
        names = ['start', 'prep_start']
        action_dict = {'action_name': 'start',
                       'present_tense': 'starting core containers',
                       'past_tense': 'Started core containers',
                       'type': 'containers',
                       'action': 'start (only enabled, built, non-running plugin tools are shown)',
                       'cores': True}
        BaseForm.__init__(self, action_dict, names)


class StopToolsForm(BaseForm):
    """ Stop Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize stopping tools form objects """
        names = ['stop']
        action_dict = {'action_name': 'stop',
                       'present_tense': 'stopping containers',
                       'past_tense': 'Stopped containers',
                       'type': 'containers',
                       'action': 'stop (only plugin tools are shown)',
                       'cores': False}
        BaseForm.__init__(self, action_dict, names)


class StopCoreToolsForm(BaseForm):
    """ Stop Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize stopping core tools form objects """
        names = ['stop']
        action_dict = {'action_name': 'stop',
                       'present_tense': 'stopping core containers',
                       'past_tense': 'Stopped core containers',
                       'type': 'containers',
                       'action': 'stop (only core tools are shown)',
                       'cores': True}
        BaseForm.__init__(self, action_dict, names)


class UpdateToolsForm(BaseForm):
    """ Update Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize updating tools form objects """
        names = ['update']
        action_dict = {'action_name': 'update',
                       'present_tense': 'updating containers',
                       'past_tense': 'Updated containers',
                       'type': 'containers',
                       'action': 'update (only plugin tools are shown)',
                       'cores': False}
        BaseForm.__init__(self, action_dict, names)


class UpdateCoreToolsForm(BaseForm):
    """ Update Core Tools form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize updating core tools form objects """
        names = ['update']
        action_dict = {'action_name': 'update',
                       'present_tense': 'updating core containers',
                       'past_tense': 'Updated core containers',
                       'type': 'containers',
                       'action': 'update (only core tools are shown)',
                       'cores': True}
        BaseForm.__init__(self, action_dict, names)
