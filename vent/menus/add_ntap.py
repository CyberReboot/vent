import ast
import docker
import json
import npyscreen
import urllib2


class AddNTap(npyscreen.ActionForm):
    """ For creating a new network tap """

    def create(self):
        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.add(npyscreen.Textfield,
                 value='Create a network tap that calls tcpdump and records '
                        'based on the parameters given.',
                 editable=False,
                 color="STANDOUT")
        self.add(npyscreen.Textfield,
                 value= 'Example format: {"nic": "eth0", '
                                         ' "id": "exmpId", '
                                         ' "interval": "60", '
                                         ' "filter": "", '
                                         ' "iters": "1"} ',
                editable=False,
                color="STANDOUT")
        self.create = self.add(npyscreen.TitleText, name='Create container:')

        self.nextrely += 1

        # delete fields
        self.add(npyscreen.Textfield,
                value='Delete containers based on container id.:',
                 editable=False,
                 color="STANDOUT")
        self.add(npyscreen.Textfield,
                 value='Example format: {"id": "123"}'
                       ' or {"id": ["123", "456"]}',
                 editable=False,
                 color="STANDOUT")
        self.delete = self.add(npyscreen.TitleText, name='Delete container '
                               'id(s): ')

        self.nextrely += 1

        # start fields
        self.add(npyscreen.Textfield,
                 value='Start containers based on container id.',
                 editable=False,
                 color="STANDOUT")
        self.add(npyscreen.Textfield,
                 value='Example format: {"id": "123"}'
                       ' or {"id": ["123", "456"]}',
                 editable=False,
                 color="STANDOUT")
        self.start = self.add(npyscreen.TitleText, name='Start container '
                              'id(s): ')

        self.nextrely += 1

        # stop fields
        self.add(npyscreen.Textfield,
                 value='Stop containers based on container id.',
                 editable=False,
                 color="STANDOUT")
        self.add(npyscreen.Textfield,
                 value='Example format: {"id": "123"}'
                       ' or {"id": ["123", "456"]}',
                 editable=False,
                 color="STANDOUT")
        self.stop = self.add(npyscreen.TitleText, name='Stop container '
                             'id(s): ')


    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm("MAIN")


    def send_request(self, network_port, json_data, action):
        """ Send a post/get request to the right port/url """
        try:
            url = "http://" + network_port
            data = ast.literal_eval(json_data)
            data = json.dumps(data)
            req = urllib2.Request(url,data)
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req, data)
            npyscreen.notify_confirm("Success: " + action + " " + json_data)
            return True
        except Exception as e:  # pragma: no cover
            npyscreen.notify_confirm("unsuccessful call to network tap " +
                                     action + ": " + str(e),
                                     form_color='CAUTION')
            return False


    def on_ok(self):
        """ Create, stop, start, delete network tap containers """
        d = docker.from_env()
        containers = d.containers.list(filters={'label': 'vent'}, all=True)

        # iterate through the containers to grab network tap and the port it's
        # listening to
        network_port = ''
        found = False
        for c in containers:
            if 'network-tap' in c.attrs['Name'] and \
                    'core' in c.attrs['Config']['Labels']['vent.groups']:
                # get a dictionary of ports
                network_port = c.attrs['NetworkSettings']['Ports']

                # iterate through the dict to avoid hard coding anything
                # is it safe to assume only 1 entry in the dict will exist?
                for port in network_port:
                    h_port = network_port[port][0]['HostPort']
                    h_ip = network_port[port][0]['HostIp']
                    network_port = str(h_ip) + ":" + str(h_port)
                    found = True
                    break
            # no need to cycle every single container if we found our ports
            if found:
                break

        # make the appropriate post requests if the textbox isnt blank
        if network_port:
            if self.create.value:
                # check to see if user input has the required fields
                valid = ["nic", "id", "interval", "filter", "iters"]
                not_in = [field for field in valid if field not in
                        str(self.create.value)]
                if not_in:
                    npyscreen.notify_confirm("please include all required fields. \
                                             missing: " + str(not_in))
                else:
                    url = network_port + '/create'
                    if self.send_request(url, self.create.value, "create"):
                        self.quit()

            if self.delete.value:
                url = network_port + '/delete'
                if self.send_request(url, self.delete.value, "delete"):
                    self.quit()

            if self.start.value:
                url = network_port + '/start'
                if self.send_request(url, self.start.value, "start"):
                    self.quit()

            if self.stop.value:
                url = network_port + '/stop'
                if self.send_request(url, self.stop.value, "stop"):
                    self.quit()

        else:
            npyscreen.notify_confirm("Please ensure network tap is running")
            self.quit()

        if not self.delete.value and not self.create.value and not \
        self.stop.value and not self.start.value:
            npyscreen.notify_confirm("Please fill out at least one field")

        return


    def on_cancel(self):
        """ when user cancels, return to MAIN """
        self.quit()
