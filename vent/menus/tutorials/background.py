import npyscreen

class TutorialBackgroundForm(npyscreen.ActionFormWithMenus):

    def switch(self, name):
        """ Wrapper that switches to provided form """
        self.parentApp.change_form(name)

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def create(self):
        """ Overridden to add handlers and content """
        self.add_handlers({"^Q": self.quit})
        self.add(npyscreen.TitleText, name='Vent Background', editable=False)
        self.m2 = self.add_menu(name="About Vent", shortcut="v")
        self.m2.addItem(text="Terminology", shortcut='t')
        self.m3 = self.add_menu(name="Interacting with the Menu", shortcut="i")
        self.m4 = self.add_menu(name="Working with Cores", shortcut="c")
        self.m5 = self.add_menu(name="Working with Plugins", shortcut="p")
        self.m6 = self.add_menu(name="Adding Files", shortcut="f")
        self.m7 = self.add_menu(name="Services", shortcut="s")

    def on_cancel(self):
        """ When user clicks cancel, will return to MAIN """
        self.quit()

    def on_ok(self):
        """ When user clicks ok, will proceed to next tutorial """
        # !! TODO - Should point to next form
        self.switch("TUTORIALBACKGROUND")
