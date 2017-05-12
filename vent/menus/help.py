import npyscreen

class HelpForm(npyscreen.FormBaseNew):
    """ Help form for the Vent CLI """
    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.change_forms,'^Q': self.quit})
        self.addfield = self.add(npyscreen.TitlePager, name="Vent", values="""Help\nmore\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more\nand more""".split("\n"))

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)

    def change_forms(self, *args, **keywords):
        """ Checks which form is currently displayed and toggles it to the other one """
        if self.name == "Help\t\t\t\t\t\t\t\tPress ^T to toggle main":
            change_to = "MAIN"
        else:
            change_to = "HELP"

        # Tell the VentApp object to change forms.
        self.parentApp.change_form(change_to)
