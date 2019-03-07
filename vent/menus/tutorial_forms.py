from vent.menus.tutorials import TutorialForm


class TutorialAddingFilesForm(TutorialForm):
    """ Tutorial Adding Files form for the Vent CLI """

    def __init__(self, *args, **keywords):
        """ Initialize adding files tutorial form fields """
        title = 'Adding Files'
        text = """
        In the main Vent menu, there is a field labeled 'File Drop'. The
        provided directory is where Vent will be watching. Just add the
        desired file into the directory and Vent will automatically
        process those files with their respective plugins.

        To change the directory that Vent watches, on the main menu,
        there's a field labeled 'User Data'. Within that directory, there
        exists a file named 'vent.cfg'. Within the file, there is a
        section titled '[main]' with an option 'files'. Just change the
        value of 'files' to the desired directory.


        Example:
        Let's assume that all core tools have been added, built, and have
        been started. Let's also assume there's a plugin that deals with
        *.csv files. If a .csv file is placed into the File Drop
        directory, Vent will recognize the file extension and run the
        plugin. This also works for multiple plugins that deal with the
        same file type. If there were two plugins that dealt with .csv
        files, Vent would run both on the same .csv file.

        In addition, Vent also supports plugin pipelines.
        Let's say there are two plugins: Plugin A processes .csv files and
        Plugin B processes .csv2 files. A .csv file is added to the File
        Drop directory, so Vent will start Plugin A, which will process
        the file and output a .csv2 file in the same File Drop directory.
        This, in turn, will cause Plugin B to start and process the newly
        created .csv2 file.
        """
        next_tutorial = 'TUTORIALTROUBLESHOOTING'
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
        title = 'Tutorial Introduction'
        text = """
        Welcome to Vent!

        This tutorial is intended to help you get up to speed on Vent,
        some of the terminology we use, how to interact with this
        application, getting setup, and more.

        Please note the OK and CANCEL buttons on the bottom right of the
        screen. If at any point you wish to quit the tutorial, simply
        click CANCEL to be taken to the main menu. You can always find the
        tutorial menu again from the main menu.

        Navigating through our menus is simple. Directional arrow keys or
        TAB will let you interact with the page and move between the
        buttons. ENTER will select a button. At the top left you will
        notice additional keybindings: CTRL+Q will take you back to the
        main menu for this page. At the bottom left you will notice a menu
        for you to access. This menu is specific to the tutorial and will
        allow you to skip to material you want. Press CTRL+X to access the
        menu, up and down directional arrows to change between entries or
        to access additional content in menus that display - more -, ENTER
        to dive deeper into a submenu, and ESC to exit the menu and return
        to the current page. You can also use the shortcut letters to
        switch between entries quickly.

        Click OK when you are ready to continue on with the tutorial.

        NEXT UP: About Vent - Background
        """
        next_tutorial = 'TUTORIALBACKGROUND'
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
        title = 'Adding Plugins'
        text = """
        Adding custom Vent plugins is easy.
        From the main menu, hit '^X' to bring up the action menu.
        Highlight 'Plugins' and hit enter to bring up a new menu. From
        there, select 'Add new plugin' and hit 'Enter', which brings up
        another new form.

        It's possible to get plugins using Git or Docker.
        For Git: Specify the repository URL and credentials (if needed)
                 and hit OK. Vent will display all branches that the repo
                 currently has. Highlight the desired branch and press the
                 'Space' key to select it. By default, Vent will pull from
                 the latest commit but it is possible to select whatever
                 desired commit. Just highlight the commit ID, press
                 enter, and a menu will pop up with all commit IDs.
                 Highlight the desired commit ID and press 'Enter' to
                 select it. Next, if the image should also be built,
                 leave the value of 'Build' to 'True'. Otherwise, set it
                 to 'False' and press OK.

                 Now, select all desired plugins and hit 'OK' and Vent
                 will do the rest.

        For Docker: Give an image and name and hit OK.
        """
        next_tutorial = 'TUTORIALADDINGFILES'
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
        title = 'Vent Background'
        text = """TODO"""
        next_tutorial = 'TUTORIALTERMINOLOGY'
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
        title = 'Getting Setup'
        text = """
        Here's a quick setup guide to quickly get Vent up and running.

        First we need to add plugin tools to process files placed into File
        Drop.
        1) Hit '^X' to open the main action menu and go to the Tools
           submenu
        2) Add and build new tools using either Git or Docker
        3) Now, drop any files that the plugins process into the File Drop
           directory.

        Congrats! You have just started and processed files using Vent!
        """
        next_tutorial = 'TUTORIALSTARTINGCORES'
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
        title = 'Starting Cores'
        text = """
        Once a core tool has been added and built, the only thing left is
        to start it, so it can begin doing work.

        At the main menu, press '^X' to bring up the action menu.
        Highlight core tools and press 'Enter'.
        Now highlight 'Start core tools' and press 'Enter'.
        This will bring up a form with a list of core tools that are
        able to be started. By default, all tools are selected, but it is
        possible to select which tools to start using the arrow keys and
        the 'Space' key.

        Once the desired tools are selected, press OK and Vent will start
        up the core tools.
        """
        next_tutorial = 'TUTORIALADDINGPLUGINS'
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
        title = 'Vent Terminology'
        text = """
        Core Tool:   Main set of tools that Vent uses to do work. These
                     tools are the backbone of Vent.
        Plugin Tool: User added tools that process user defined file
                     types.
        User Data:   File directory that has meta data about Vent. The
                     most important files within User Data are:
                        plugin_manifest: meta data about all added tools
                        vent.log: logs concerning how Vent runs. Almost
                                  every function within Vent will write to
                                  this log.
                        vent.cfg: allows for the customization of certain
                                  functionality within vent. File Drop
                                  location can be set here. Certain GPU
                                  functionality can be set here.
        File Drop:   File directory that Vent watches. Drop files in here
                     so Vent can see and process them.

        Template Files: XXX TODO
        """
        next_tutorial = 'TUTORIALGETTINGSETUP'
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)


class TutorialTroubleshootingForm(TutorialForm):
    """ Tutorial troubleshooting form for the Vent CLI """

    def __init__(self, *args, **keywords):
        """ Initialize terminology tutorial form fields """
        title = 'Vent Troubleshooting'
        text = """
        Something not working as expected within Vent? Not a problem!

        Let's first get some basic possible errors out of the way.
        1) Is Docker daemon running? Vent uses Docker heavily so it is
           necessary to have the Docker daemon running.
        2) Is this the lastest version of Vent? Ways to get the latest
           Vent version:
              Using pip:    'pip3 install vent && vent'
              Using Docker: 'docker pull cyberreboot/vent'
                            'docker run -it vent_image_id'
              Using github: 'git clone https://github.com/CyberReboot/vent'
                            'cd vent && make && vent'

        Still not working? That's fine! Let's get into the nitty gritty
        and try to figure out what went wrong.

        Firstly, let's see if it's Vent that's causing the problems.
        Go to the 'User Data' file and open up 'vent.log' with your
        favorite text editor. Let's search the key term 'False'. Iterate
        through the search results and look for 'Status of some_function:
        False'. This tells us that one of Vent's core functions is not
        performing as expected. Next to it, there will be an error message
        explaining what went wrong. If it's something with Vent's
        implementation, please create an issue here:
        https://github.com/CyberReboot/vent/issues

        If there's no obvious error messages within 'vent.log', let's
        check any added plugin tools. Run the command 'docker logs
        syslog_container_id'. This will return all information about all
        plugin containers and any information regarding the error should
        be displayed here.
        """
        next_tutorial = 'MAIN'
        TutorialForm.__init__(self,
                              title,
                              text,
                              next_tutorial,
                              *args,
                              **keywords)
