import npyscreen

class TutorialIntroForm(npyscreen.ActionFormWithMenus):
    """ Tutorial introduction landing form for the Vent CLI """

    def switch(self, name):
        """ Wrapper that switches to provided form """
        self.parentApp.change_form(name)

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def create(self):
        """ Overridden to add handlers and content """
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

        Navigating through our menus is simple! Directional arrow keys or TAB will
        let you interact with the page and move between the buttons. ENTER will
        select a button! At the top left you will notice additional keybindings: CTRL+Q
        will take you back to the main menu for this page. At the bottom right you
        will notice we have a menu for you to access. This menu is specific to the
        tutorial and will allow you to skip to material you want. Press CTRL+X to
        access the menu, up and down directional arrows to change between entries or
        to access additional content in menus that display - more -, ENTER to dive
        deeper into a submenu, and ESC to exit the menu and return to the current
        page! You can also use the shortcut letters to switch between entries quickly!

        We hope you enjoy using Vent!

        Click OK when you are ready to continue on with the tutorial.

        NEXT UP: About Vent - Background
        """)
        self.m2 = self.add_menu(name="About Vent", shortcut='v')
        self.m2.addItem(text="Background", onSelect=self.switch,
                        arguments=['TUTORIALBACKGROUND'], shortcut='b')
        self.m2.addItem(text="Terminology", onSelect=self.switch,
                        arguments=['TUTORIALTERMINOLOGY'], shortcut='t')
        self.m2.addItem(text="Getting Setup", onSelect=self.switch,
                        arguments=['TUTORIALGETTINGSETUP'], shortcut='s')
        self.m3 = self.add_menu(name="Working with Cores", shortcut='c')
        self.m3.addItem(text="Building Cores", onSelect=self.switch,
                        arguments=['TUTORIALBUILDINGCORES'], shortcut='b')
        self.m3.addItem(text="Starting Cores", onSelect=self.switch,
                        arguments=['TUTORIALSTARTINGCORES'], shortcut='c')
        self.m4 = self.add_menu(name="Working with Plugins", shortcut='p')
        self.m4.addItem(text="Adding Plugins", onSelect=self.switch,
                        arguments=['TUTORIALADDINGPLUGINS'], shortcut='a')
        self.m5 = self.add_menu(name="Files", shortcut='f')
        self.m5.addItem(text="Adding Files", onSelect=self.switch,
                        arguments=['TUTORIALADDINGFILES'], shortcut='a')
        self.m6 = self.add_menu(name="Services", shortcut='s')
        self.m6.addItem(text="Setting up Services", onSelect=self.switch,
                        arguments=['TUTORIALSETTINGUPSERVICES'], shortcut='s')

    def on_cancel(self):
        """ When user clicks cancel, will return to MAIN """
        npyscreen.NPSAppManaged.STARTING_FORM = "MAIN"
        self.quit()

    def on_ok(self):
        """ When user clicks ok, will proceed to next tutorial """
        npyscreen.NPSAppManaged.STARTING_FORM = "MAIN"
        self.switch("TUTORIALBACKGROUND")
