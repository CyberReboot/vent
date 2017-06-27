import npyscreen

from vent.api.actions import Action


class LogsForm(npyscreen.FormBaseNew):
    """ Logs form for the Vent CLI """
    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.add(npyscreen.TitleFixedText, name='Logs:', value='')
        self.logs_mle = self.add(npyscreen.Pager,
                                 values=['Checking for container logs, please wait...'])
        self.action = Action()
        response = self.action.logs()
        if response[0]:
            value = "Logs for each Vent container found:\n"
            logs = response[1]
            for container in logs:
                value += "\n Container: "+container+"\n"
                for log in logs[container]:
                    value += "    "+log+"\n"
                value += "\n"
            self.logs_mle.values = value.split("\n")
        else:
            self.logs_mle.values = ["There was an issue retrieving logs for Vent containers: ",
                                    str(response[1]),
                                    "Please see vent.log for more details."]
