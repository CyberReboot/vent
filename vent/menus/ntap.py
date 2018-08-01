import ast

import npyscreen

from vent.api.actions import Action


class CreateNTap(npyscreen.ActionForm):
    """ For creating a new network tap container """

    def create(self):
        self.add_handlers({'^T': self.quit, '^Q': self.quit})
        self.add(npyscreen.Textfield,
                 value='Create a network tap that calls tcpdump and records '
                       'based on the parameters given ',
                 editable=False,
                 color='STANDOUT')
        self.add(npyscreen.Textfield,
                 value='via a POST request '
                 'to the url of the core network tap tool. ',
                 editable=False,
                 color='STANDOUT')
        self.add(npyscreen.Textfield,
                 value='An example payload: ',
                 editable=False,
                 color='STANDOUT')
        self.add(npyscreen.Textfield,
                 value=' {"nic": "eth0", "id": "testId", "interval": "60" '
                       '"filter": "", "iters": "1"} ',
                 editable=False,
                 color='STANDOUT')

        self.nextrely += 1

        self.nic = self.add(npyscreen.TitleText, name='nic')
        self.id = self.add(npyscreen.TitleText, name='id')
        self.interval = self.add(npyscreen.TitleText, name='interval')
        self.filter = self.add(npyscreen.TitleText, name='filter')
        self.iters = self.add(npyscreen.TitleText, name='iters')

    def on_ok(self):
        # error check to make sure all fields were filled out
        if not self.nic.value or not self.id.value or not self.interval.value \
           or not self.iters.value:
            npyscreen.notify_confirm('Please fill out all fields',
                                     form_color='CAUTION')
            return

        # create a dictionary with user entered data
        payload = {}
        payload[self.nic.name] = self.nic.value
        payload[self.id.name] = self.id.value
        payload[self.interval.name] = self.interval.value
        payload[self.filter.name] = self.filter.value
        payload[self.iters.name] = self.iters.value

        # create an action object and have it do the work
        self.api_action = Action()
        try:
            url = self.api_action.get_vent_tool_url('network-tap')[1] + \
                '/create'
            request = self.api_action.post_request(url, str(payload))

            if request[0]:
                npyscreen.notify_confirm('Success: ' + str(request[1]))
                self.quit()

            else:
                npyscreen.notify_confirm('Failure: ' + str(request[1]))
        except Exception as e:  # pragma: no cover
            npyscreen.notify_confirm('Failure: ' + str(e))

        return

    def quit(self, *args, **kwargs):
        """ Overriden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def on_cancel(self):
        """ When user cancels, return to MAIN """
        self.quit()


class NICsNTap(npyscreen.ActionForm):
    """ For listing all available network interfaces """

    def create(self):
        self.add_handlers({'^T': self.quit, '^Q': self.quit})
        self.add(npyscreen.Textfield,
                 value='List all avilable network interfaces',
                 editable=False,
                 color='STANDOUT')

        self.nextrely += 1

        try:
            self.api_action = Action()
            url = self.api_action.get_vent_tool_url('network-tap')[1] + '/nics'
            request = self.api_action.get_request(url)

            if request[0]:
                box = self.add(npyscreen.BoxTitle,
                               name='Available Network Interfaces',
                               max_height=40)
                request = ast.literal_eval(str(request[1]))
                data = [d for d in request[1].split('\n')]
                box.values = data
            else:
                npyscreen.notify_confirm('Failure: ' + request[1])

        except Exception as e:  # pragma no cover
            npyscreen.notify_confirm('Failure: ' + str(e))

    def quit(self, *args, **kwargs):
        """ Overriden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def on_cancel(self):
        """ When user cancels, return to MAIN """
        self.quit()

    def on_ok(self):
        self.quit()


class ListNTap(npyscreen.ActionForm):
    """ For listing all network tap capture containers """

    def create(self):
        self.add_handlers({'^T': self.quit, '^Q': self.quit})
        self.add(npyscreen.Textfield,
                 value='List all network tap capture containers',
                 editable=False,
                 color='STANDOUT')

        self.nextrely += 1

        try:
            self.api_action = Action()
            url = self.api_action.get_vent_tool_url('network-tap')[1] + '/list'
            request = self.api_action.get_request(url)

            if request[0]:
                box = self.add(npyscreen.BoxTitle,
                               name='Network Tap Capture Containers',
                               max_height=40)
                request = ast.literal_eval(str(request[1]))
                data = [d for d in list(request[1])]
                box.values = data
            else:
                npyscreen.notify_confirm('Failure: ' + request[1])

        except Exception as e:  # pragma no cover
            npyscreen.notify_confirm('Failure: ' + str(e))

    def quit(self, *args, **kwargs):
        """ Overriden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def on_cancel(self):
        """ When user cancels, return to MAIN """
        self.quit()

    def on_ok(self):
        self.quit()


class ActionNTap(npyscreen.ActionForm):
    """ Base class to inherit from. """

    def __init__(self, n_action=None, *args, **kwargs):
        self.n_action = n_action
        super(ActionNTap, self).__init__(*args, **kwargs)

    def create(self):
        self.add_handlers({'^T': self.quit, '^Q': self.quit})
        self.add(npyscreen.Textfield,
                 value=self.n_action + ' a network tap capture container.',
                 editable=False,
                 color='STANDOUT')
        self.add(npyscreen.Textfield,
                 value='Choose a container to ' + self.n_action,
                 editable=False,
                 color='STANDOUT')

        self.nextrely += 1

        try:
            self.api_action = Action()

            # display all containers by sending a get request to ntap/list
            # nlist returns tuple and get_request returns tuple
            url = self.api_action.get_vent_tool_url('network-tap')[1] + '/list'
            request = self.api_action.get_request(url)

            # create selection for containers
            if request[0]:
                request = ast.literal_eval(str(request[1]))
                data = [d for d in list(request[1])]
                self.ms = self.add(npyscreen.TitleMultiSelect, max_height=20,
                                   name='Choose one or more containers to ' +
                                   self.n_action,
                                   values=data)

            else:
                npyscreen.notify_confirm('Failure: ' + str(request[1]))

        except Exception as e:  # pragma: no cover
            npyscreen.notify_confirm('Failure: ' + str(e))

    def on_ok(self):
        # error check to make sure at least one box was selected
        if not self.ms.value:
            npyscreen.notify_confirm('Please select at least one container.',
                                     form_color='CAUTION')

        # format the data into something ncontrol likes
        else:
            payload = {'id': list(x['id'] for x in
                                  self.ms.get_selected_objects())}

        # grab the url that network-tap is listening to
        try:
            npyscreen.notify_wait('Please wait. Currently working')
            self.api_action = Action()
            url = self.api_action.get_vent_tool_url('network-tap')[1] + '/' \
                + self.n_action
            request = self.api_action.post_request(url, payload)

            if request[0]:
                npyscreen.notify_confirm('Success: ' + str(request[1]))
                self.quit()

            else:
                npyscreen.notify_confirm('Failure: ' + str(request[1]))

        except Exception as e:  # pragma: no cover
            npyscreen.notify_confirm('Failure: ' + str(e))

    def quit(self, *args, **kwargs):
        """ Overriden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def on_cancel(self):
        """ When user cancels, return to MAIN """
        self.quit()


class DeleteNTap(ActionNTap):
    """ Delete inheritance """

    def __init__(self, *args, **kwargs):
        ActionNTap.__init__(self, 'delete')


class StartNTap(ActionNTap):
    """ Delete inheritance """

    def __init__(self, *args, **kwargs):
        ActionNTap.__init__(self, 'start')


class StopNTap(ActionNTap):
    """ Delete inheritance """

    def __init__(self, *args, **kwargs):
        ActionNTap.__init__(self, 'stop')
