import docker
import json
import npyscreen
import urllib2


class AddNTap(npyscreen.ActionForm):
    """ For creating a new network tap """

    def create(self):
        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.add(npyscreen.Textfield,
                 value='Create a network tap that calls tcpdump and records \
                        based on the parameters given.',
                 editable=False,
                 color="STANDOUT")
        self.nic = self.add(npyscreen.TitleText, name='nic')
        self.id = self.add(npyscreen.TitleText, name='id')
        self.interval = self.add(npyscreen.TitleText, name='interval')
        self.filter = self.add(npyscreen.TitleText, name='filter')
        self.iters = self.add(npyscreen.TitleText, name='iters')

        self.nextrely += 1

        # delete fields
        self.add(npyscreen.Textfield,
                 value='Delete containers based on container id. Example \
                        format: {"id": "123"} or {"id": ["123", "456"]}',
                 editable=False,
                 color="STANDOUT")
        self.delete = self.add(npyscreen.TitleText, name='Delete container id(s)')

        self.nextrely += 1

        # start fields
        self.add(npyscreen.Textfield,
                 value='Start containers based on container id. Example \
                        format: {"id": "123"} or {"id": ["123", "456"]}',
                 editable=False,
                 color="STANDOUT")
        self.start = self.add(npyscreen.TitleText, name='Start container id(s)')

        self.nextrely += 1

        # stop fields
        self.add(npyscreen.Textfield,
                 value='Delete containers based on container id. Example \
                        format: {"id": "123"} or {"id": ["123", "456"]}',
                 editable=False,
                 color="STANDOUT")
        self.stop = self.add(npyscreen.TitleText, name='Stop container id(s)')

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm("MAIN")

    def on_ok(self):
        """ Create, stop, start, delete network tap containers """
        d = docker.from_env()
        containers = d.containers.list(filters={'label': 'vent'}, all=True)

        # iterate through the containers to grab network tap and the port it's
        # listening to
        network_port = ''
        found = False
        for c in containers:
            if c.attrs['Config']['Label']['name'] == 'network_tap' and \
                    'core' in c.attrs['Config']['Label']['vent.groups']:
                # get a dictionary of ports
                network_port = container.attrs['NetworkSettings']['Ports']

                # iterate through the dict to avoid hard coding anything
                # is it safe to assume only 1 entry in the dict will exist?
                for port in network_port:
                    h_port = network_port[port]['HostPort']
                    h_ip = network_port[port]['HostIp']
                    network_port = str(h_ip) + str(h_port)
                    found = True
                    break
            # no need to cycle every single container if we found our ports
            if found:
                break

        # make the appropriate post requests if the textbox isnt blank

        if self.delete:
            try:
                url = network_port + '/delete'
                req = urllib2.Request(url)
                req.add_header('Content-Type','application/json')
                data = json.dumps(self.delete)
                response = urllib2.urlopen(req, data)
            except Exception as e:  # pragma: no cover
                return "unsuccessful call to network tap delete: " + str(e)

        if self.start:
            try:
                url = network_port + '/start'
                req = urllib2.Request(url)
                req.add_header('Content-Type','application/json')
                data = json.dumps(self.start)
                response = urllib2.urlopen(req, data)
            except Exception as e:  # pragma: no cover
                return "unsuccessful call to network tap start: " + str(e)

        if self.stop:
            try:
                url = network_port + '/stop'
                req = urllib2.Request(url)
                req.add_header('Content-Type','application/json')
                data = json.dumps(self.stop)
                response = urllib2.urlopen(req, data)
            except Exception as e:  # pragma: no cover
                return "unsuccessful call to network tap stop: " + str(e)
