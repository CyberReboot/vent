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
            logs = self.action.logs()
            value = "Logs for each Vent container found:\n"
            for container in logs:
                value += "\n Container: "+container+"\n"
                for log in logs[container]:
                    value += "    "+log+"\n"
                value += "\n"
            self.logs_mle.values=value.split("\n")
            self.logs_mle.display()
        return

    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.change_forms,"^Q": self.exit})
        self.add(npyscreen.TitleFixedText, name='Logs:', value='')
        self.logs_mle = self.add(npyscreen.Pager,
                                      values=['Checking for container logs, please wait...'])

    def exit(self, *args, **keywords):
        self.parentApp.switchForm("MAIN")

    def change_forms(self, *args, **keywords):
        """ Toggles back to main """
        change_to = "MAIN"

        # Tell the VentApp object to change forms.
        self.parentApp.change_form(change_to)
