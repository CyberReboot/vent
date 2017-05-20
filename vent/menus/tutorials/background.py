import npyscreen

class TutorialBackgroundForm(npyscreen.ActionFormWithMenus):

    def switch(self, name):
        self.parentApp.change_form(name)

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm('MAIN')

    def create(self):
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
        self.quit()

    def on_ok(self):
        # !! TODO - Should point to next form
        self.switch("TUTORIALBACKGROUND")
