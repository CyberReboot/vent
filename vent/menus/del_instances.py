import json
import re

import npyscreen

from vent.helpers.meta import Dependencies


class InstanceSelect(npyscreen.MultiSelect):
    """
    A widget class for selecting an exact amount of instances to perform
    actions on
    """

    def __init__(self, *args, **kargs):
        """ Initialize an instance select object """
        self.instance_num = kargs['instance_num']
        super(InstanceSelect, self).__init__(*args, **kargs)

    def when_value_edited(self, *args, **kargs):
        """ Overrided to prevent user from selecting too many instances """
        if len(self.value) > self.instance_num:
            self.value.pop(-2)
            self.display()

    def safe_to_exit(self, *args, **kargs):
        """
        Overrided to prevent user from exiting selection until
        they have selected the right amount of instances
        """
        if len(self.value) == self.instance_num:
            return True
        return False


class DeleteForm(npyscreen.ActionForm):
    """ A form for selecting instances to delete and deleting them """

    def __init__(self, *args, **keywords):
        """ Initialize a delete form object """
        self.new_instances = int(keywords['new_instances'])
        self.next_tool = keywords['next_tool']
        self.manifest = keywords['manifest']
        self.clean = keywords['clean']
        self.prep_start = keywords['prep_start']
        self.start_tools = keywords['start_tools']
        self.cur_instances = []
        self.display_to_section = {}
        self.old_instances = int(keywords['old_instances'])
        section = keywords['section']
        for i in range(1, self.old_instances + 1):
            i_section = section.rsplit(':', 2)
            i_section[0] += str(i) if i != 1 else ''
            i_section = ':'.join(i_section)
            display = i_section.rsplit('/', 1)[-1]
            self.cur_instances.append(display)
            self.display_to_section[display] = i_section
        super(DeleteForm, self).__init__(*args, **keywords)

    def create(self):
        """ Creates the necessary display for this form """
        self.add_handlers({'^E': self.quit, '^Q': self.quit})
        to_delete = self.old_instances - self.new_instances
        self.add(npyscreen.Textfield, value='Select which instances to delete'
                 ' (you must select ' + str(to_delete) +
                 ' instance(s) to delete):', editable=False, color='GOOD')
        self.del_instances = self.add(InstanceSelect,
                                      values=self.cur_instances,
                                      scroll_exit=True, rely=3,
                                      instance_num=to_delete)

    def change_screens(self):
        """ Change to the next tool to edit or back to MAIN form """
        if self.next_tool:
            self.parentApp.change_form(self.next_tool)
        else:
            self.parentApp.change_form('MAIN')

    def quit(self, *args, **kargs):
        """ Quit without making any changes to the tool """
        npyscreen.notify_confirm('No changes made to instance(s)',
                                 title='Instance confiugration cancelled')
        self.change_screens()

    def on_ok(self):
        """ Delete the instances that the user chose to delete """
        npyscreen.notify_wait('Deleting instances given...',
                              title='In progress')
        # keep track of number for shifting instances down for alignment
        shift_num = 1
        to_update = []
        for i, val in enumerate(self.del_instances.values):
            # clean all tools for renmaing and relabeling purposes
            t = val.split(':')
            section = self.display_to_section[val]
            prev_running = self.manifest.option(section, 'running')
            run = prev_running[0] and prev_running[1] == 'yes'
            if i in self.del_instances.value:
                if run:
                    # grab dependencies of tools that linked to previous one
                    if i == 0:
                        dependent_tools = [self.manifest.option(
                            section, 'link_name')[1]]
                        for dependency in Dependencies(dependent_tools):
                            self.clean(**dependency)
                            to_update.append(dependency)
                    self.clean(name=t[0], branch=t[1], version=t[2])
                self.manifest.del_section(section)
            else:
                try:
                    # update instances for tools remaining
                    section = self.display_to_section[val]
                    settings_dict = json.loads(self.manifest.option
                                               (section, 'settings')[1])
                    settings_dict['instances'] = self.new_instances
                    self.manifest.set_option(section, 'settings',
                                             json.dumps(settings_dict))
                    # check if tool name doesn't need to be shifted because
                    # it's already correct
                    identifier = str(shift_num) if shift_num != 1 else ''
                    new_section = section.rsplit(':', 2)
                    new_section[0] = re.sub(r'\d+$', identifier,
                                            new_section[0])
                    new_section = ':'.join(new_section)
                    if section != new_section:
                        # clean tool so that we can rename its container and
                        # labels with new information
                        self.clean(name=t[0], branch=t[1], version=t[2])
                        prev_name = self.manifest.option(section, 'name')[1]
                        new_name = re.split(r'[0-9]', prev_name)[0] + \
                            identifier
                        self.manifest.set_option(section, 'name', new_name)
                        # copy new contents into shifted version
                        self.manifest.add_section(new_section)
                        for val_pair in self.manifest.section(section)[1]:
                            self.manifest.set_option(new_section, val_pair[0],
                                                     val_pair[1])
                        self.manifest.del_section(section)
                        if run:
                            to_update.append({'name': new_name,
                                              'branch': t[1],
                                              'version': t[2]})
                    shift_num += 1
                except Exception as e:
                    npyscreen.notify_confirm('Trouble deleting tools'
                                             ' because ' + str(e))
        self.manifest.write_config()
        tool_d = {}
        for tool in to_update:
            tool_d.update(self.prep_start(**tool)[1])
        if tool_d:
            self.start_tools(tool_d)
        npyscreen.notify_confirm('Done deleting instances.',
                                 title='Finished')
        self.change_screens()

    def on_cancel(self):
        """ Exits the form without performing any action """
        self.quit()
