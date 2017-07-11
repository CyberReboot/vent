import curses
import npyscreen

from vent.helpers.meta import Services


class ServicesForm(npyscreen.FormBaseNew):
    """ Services form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize service form objects """
        self.core = keywords['core']
        super(ServicesForm, self).__init__(*args, **keywords)

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        curses.mousemask(1)
        self.parentApp.switchForm('MAIN')

    def create(self):
        """ Override method for creating FormBaseNew form """
        # track the mouse cursor to allow highlighting
        curses.mousemask(0)

        self.add_handlers({"^T": self.quit, "^Q": self.quit})
        self.services_tft = self.add(npyscreen.TitleFixedText,
                                     name='No services running.',
                                     value="")
        services = Services(self.core)
        if services:
            self.services_tft.hidden = True
            for service in services:
                value = ""
                for val in service[1]:
                    value += val+", "
                self.add(npyscreen.TitleFixedText,
                         name=service[0],
                         value=value[:-2])
