import npyscreen
import os
import sys

class InventoryForm(npyscreen.FormBaseNew):
    """ Inventory form for the Vent CLI """
    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.change_forms,'^Q': self.exit})
        self.services_tft = self.add(npyscreen.TitleFixedText, name='No plugins in the inventory. (To be implemented.)', value="")

    def exit(self, *args, **keywords):
        os.system('reset')
        os.system('stty sane')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    def change_forms(self, *args, **keywords):
        """ Toggles back to main """
        change_to = "MAIN"

        # Tell the VentApp object to change forms.
        self.parentApp.change_form(change_to)
