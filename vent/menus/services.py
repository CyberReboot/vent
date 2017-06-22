import npyscreen
import os
import sys

from vent.helpers.meta import Services

class ServicesForm(npyscreen.FormBaseNew):
    """ Services form for the Vent CLI """
    triggered = 0
    services_tft = None
    def while_waiting(self):
        """ Update with current services running """
        # !! TODO this should trigger and update regardless...
        if not self.triggered:
            self.triggered = 1
            services = Services()
            if services:
                self.services_tft.hidden = True
                self.services_tft.display()
                for service in services:
                    value = ""
                    for val in service[1]:
                        value += val+", "
                    title_text = self.add(npyscreen.TitleFixedText,
                                          name=service[0],
                                          value=value[:-2])
                    title_text.display()

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.services_tft = self.add(npyscreen.TitleFixedText, name='No services running.', value="")
