from vent.menus.tutorials import TutorialForm


class TutorialAddingFilesForm(TutorialForm):
    """ Tutorial Adding Files form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize adding files tutorial form fields """
        title = "Adding Files"
        text = """TODO"""
        next_tutorial = "TUTORIALSETTINGUPSERVICES"
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)


class TutorialIntroForm(TutorialForm):
    """ Tutorial introduction landing form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize introduction landing tutorial form fields """
        title = "Tutorial Introduction"
        text = """
        Welcome to Vent!

        This tutorial is intended to help you get up to speed on Vent, some of
        the terminology we use, how to interact with this application, getting
        setup, and more.

        Please note the OK and CANCEL buttons on the bottom right of the
        screen. If at any point you wish to quit the tutorial, simply click
        CANCEL to be taken to the main menu. You can always find the tutorial
        menu again from the main menu.

        Navigating through our menus is simple. Directional arrow keys or TAB
        will let you interact with the page and move between the buttons. ENTER
        will select a button. At the top left you will notice additional
        keybindings: CTRL+Q will take you back to the main menu for this page.
        At the bottom left you will notice a menu for you to access. This menu
        is specific to the tutorial and will allow you to skip to material you
        want. Press CTRL+X to access the menu, up and down directional arrows
        to change between entries or to access additional content in menus that
        display - more -, ENTER to dive deeper into a submenu, and ESC to exit
        the menu and return to the current page. You can also use the shortcut
        letters to switch between entries quickly.

        Click OK when you are ready to continue on with the tutorial.

        NEXT UP: About Vent - Background
        """
        next_tutorial = "TUTORIALBACKGROUND"
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)


class TutorialAddingPluginsForm(TutorialForm):
    """ Tutorial Adding Plugins form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize adding plugins tutorial form fields """
        title = "Adding Plugins"
        text = """TODO"""
        next_tutorial = "TUTORIALADDINGFILES"
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)


class TutorialBackgroundForm(TutorialForm):
    """ Tutorial Background form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize background tutorial form fields """
        title = "Vent Background"
        text = """TODO"""
        next_tutorial = "TUTORIALTERMINOLOGY"
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)


class TutorialBuildingCoresForm(TutorialForm):
    """ Tutorial Building Cores form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize building cores tutorial form fields """
        title = "Building Cores"
        text = """TODO"""
        next_tutorial = "TUTORIALSTARTINGCORES"
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)


class TutorialGettingSetupForm(TutorialForm):
    """ Tutorial Getting Setup form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize getting setup tutorial form fields """
        title = "Getting Setup"
        text = """TODO"""
        next_tutorial = "TUTORIALBUILDINGCORES"
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)


class TutorialSettingUpServicesForm(TutorialForm):
    """ Tutorial Setting up Services form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize setting up services tutorial form fields """
        title = "Setting up Services"
        text = """TODO"""
        next_tutorial = "MAIN"
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)


class TutorialStartingCoresForm(TutorialForm):
    """ Tutorial Starting Cores form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize starting cores tutorial form fields """
        title = "Starting Cores"
        text = """TODO"""
        next_tutorial = "TUTORIALADDINGPLUGINS"
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)


class TutorialTerminologyForm(TutorialForm):
    """ Tutorial terminology form for the Vent CLI """
    def __init__(self, *args, **keywords):
        """ Initialize terminology tutorial form fields """
        title = "Vent Terminology"
        text = """TODO"""
        next_tutorial = "TUTORIALGETTINGSETUP"
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)
