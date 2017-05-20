import npyscreen

class TutorialIntroForm(npyscreen.ActionFormWithMenus):
    """ Tutorial introduction landing form for the Vent CLI """

    def switch(self, name):
        self.parentApp.change_form(name)

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm('MAIN')

    def create(self):
        self.add_handlers({"^Q": self.quit})
        self.add(npyscreen.TitleText, name="Tutorial Introduction", editable=False)
        self.multifield1 = self.add(npyscreen.MultiLineEdit, editable=False, value=
        """
        Welcome to Vent!

        We have created a tutorial to help you get up to speed on Vent, some of
        the terminology we use, how to interact with this application, getting
        setup, and more!

        Please note the OK and CANCEL buttons on the bottom right of the screen.
        If at any point you wish to quit the tutorial, simply click CANCEL to be
        taken to the main menu. You can always find the tutorial menu again from
        the main menu.

        Navigating through our menus is simple! Directional arrow keys will let
        you interact with the page and move between the buttons. ENTER will select
        a button! At the top left you will notice additional keybindings: CTRL+Q
        will take you back to the main menu for this page. At the bottom right you
        will notice we have a menu for you to access. This menu is specific to the
        tutorial and will allow you to skip to material you want. Press CTRL+X to
        access the menu, up and down directional arrows to change between entries,
        ENTER to dive deeper into a submenu, and ESC to exit the menu and return
        to the current page! You can also use the shortcut letters to switch
        between entries quickly!

        We hope you enjoy using Vent!

        Click OK when you are ready to continue on with the tutorial.

        NEXT UP: About Vent - Background
        """)
        self.m2 = self.add_menu(name="About Vent", shortcut='v')
        self.m2.addItem(text="Background", onSelect=self.switch,
                        arguments=['TUTORIALBACKGROUND'], shortcut='b')
        self.m2.addItem(text="Terminology", shortcut='t')
        self.m2.addItem(text="Getting Setup", shortcut='s')
        self.m3 = self.add_menu(name="Working with Cores", shortcut='c')
        self.m3.addItem(text="Building Cores", shortcut='b')
        self.m3.addItem(text="Starting Cores", shortcut='c')
        self.m4 = self.add_menu(name="Working with Plugins", shortcut='p')
        self.m4.addItem(text="Adding Plugins", shortcut='a')
        self.m5 = self.add_menu(name="Files", shortcut='f')
        self.m5.addItem(text="Adding Files", shortcut='a')
        self.m6 = self.add_menu(name="Services", shortcut='s')
        self.m6.addItem(text="Setting up Services", shortcut='s')

    def on_cancel(self):
        self.quit()

    def on_ok(self):
        self.switch("TUTORIALBACKGROUND")
