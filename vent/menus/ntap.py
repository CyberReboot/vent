import ast
import json
import npyscreen
import urllib2

from vent.api.actions import Action


class CreateNTap(npyscreen.ActionForm):
    """ For creating a new network tap container """

    def create(self):
        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.add(npyscreen.Textfield,
                 value='Create a network tap that calls tcpdump and records '
                       'based on the parameters given ',
                 editable=False,
                 color="STANDOUT")
        self.add(npyscreen.Textfield,
                value = 'via a POST request '
                        'to the url of the core network tap tool. ',
                editable=False,
                color="STANDOUT")
        self.add(npyscreen.Textfield,
                 value = 'An example payload: ',
                 editable=False,
                 color="STANDOUT")
        self.add(npyscreen.Textfield,
                 value = '  {"nic": "eth0", "id": "testId", "interval": "60" '
                         '"filter": "", "iters": "1"} ',
                 editable=False,
                 color="STANDOUT")

        self.nextrely += 1

        self.nic = self.add(npyscreen.TitleText, name = 'nic')
        self.id = self.add(npyscreen.TitleText, name  = 'id')
        self.interval = self.add(npyscreen.TitleText, name = 'interval')
        self.filter = self.add(npyscreen.TitleText, name = 'filter')
        self.iters = self.add(npyscreen.TitleText, name = 'iters')

    def on_ok(self):
        # error check to make sure all fields were filled out
        if not self.nic or not self.id or not self.interval or not self.filter\
        or not self.iters:
            npyscreen.notify_confirm("Please fill out all fields",
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
            url = self.api_action.get_vent_tool_url('network-tap') + '/create'
            request = self.api_action.post_request(url, payload)

            if request[0]:
                npyscreen.notify_confirm("Success: " + str(request[1]))

            else:
                npyscreen.notify_confirm("Failure: " + str(request[1]))
        except Exception as e:  # pragma: no cover
            npyscreen.notify_confirm("Failure: " + str(e))

        return

    def quit(self, *args, **kwargs):
        """ Overriden to switch back to MAIN form """
        self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        """ When user cancels, return to MAIN """
        self.quit()

class SSDNTap(npyscreen.ActionForm):
    """ For deleting/starting/stopping network tap capture containers """
    #  def __init__(self, n_action):
    #      self.n_action = n_action

    def create(self):
        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.add(npyscreen.Textfield,
                 value= self.n_action + ' a network tap capture container.',
                 editable=False,
                 color="STANDOUT")
        self.add(npyscreen.Textfield,
                 value='Choose a container to ' + self.n_action,
                 editable=False,
                 color="STANDOUT")

        self.nextrely += 1

        try:
            self.api_action = Action()
            # display all containers by sending a get request to ntap/list
            url = self.api_action.get_vent_tool_url('network-tap') + '/list'
            request = self.api_action.get_request(url)

            # create selection for containers
            if request[0]:
                self.ms = self.add(npyscreen.TitleMultiSelect, max_height = 5,
                              name = 'Choose one or more containers to ' +
                                     self.n_action,
                              values = request[1])

                # allow user to interact with form
                self.ms.edit()

        except Exception as e:  # pragma: no cover
            npyscreen.notify_confirm("Failure: " + str(e))

    def on_on(self):
        # error check to make sure at least one box was selected
        if not self.ms.get_selected_objects:
            npyscreen.notify_confirm("Please select at least one container",
                                     form_color='CAUTION')

        # format the data into something ncontrol likes
        else:
            payload = {'id': ms.get_selected_objects}

        # grab the url that network-tap is listening to
        try:
            npyscreen.notify_wait("Please wait. Currently working")
            self.api_action = Action()
            url = self.api_action.get_vent_tool_url + "/" + self.n_action
            request = self.api_action.post_request(url, payload)

            if request[0]:
                npyscreen.notify_confirm("Success: " + str(request[1]))

            else:
                npyscreen.notify_confirm("Failure: " + str(request[1]))

        except Exception as e:  # pragma: no cover
            npyscreen.notify_confirm("Failure: " + str(e))

    def quit(self, *args, **kwargs):
        """ Overriden to switch back to MAIN form """
        self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        """ When user cancels, return to MAIN """
        self.quit()
