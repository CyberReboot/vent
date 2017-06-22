import npyscreen
import os
import sys

from vent.api.actions import Action

class LogsForm(npyscreen.FormBaseNew):
    """ Logs form for the Vent CLI """
    action = None
    def while_waiting(self):
        """ Update the text with the logs from containers not logging to syslog """
        if self.action is None:
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
                self.logs_mle.values=value.split("\n")
                self.logs_mle.display()
            else:
                self.logs_mle.values=["There was an issue retrieving logs for Vent containers: ",
                                      str(response[1]),
                                      "Please see vent.log for more details."]
                self.logs_mle.display()
        return

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.add(npyscreen.TitleFixedText, name='Logs:', value='')
        self.logs_mle = self.add(npyscreen.Pager,
                                      values=['Checking for container logs, please wait...'])
