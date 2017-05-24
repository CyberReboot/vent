import npyscreen

class HelpForm(npyscreen.FormBaseNew):
    """ Help form for the Vent CLI """
    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.change_forms,'^Q': self.exit})
        self.addfield = self.add(npyscreen.TitlePager, name="Vent", values="""To Be Implemented...""".split("\n"))

    def exit(self, *args, **keywords):
        self.parentApp.switchForm('MAIN')

    def change_forms(self, *args, **keywords):
        """ Checks which form is currently displayed and toggles it to the other one """
        # Returns to previous Form in history if there is a previous Form
        try:
            self.parentApp.switchFormPrevious()
        except Exception as e:
            self.parentApp.switchForm('MAIN')
