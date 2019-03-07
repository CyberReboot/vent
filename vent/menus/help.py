import npyscreen


class HelpForm(npyscreen.ActionFormWithMenus):
    """ Help form for the Vent CLI """

    @staticmethod
    def switch(page):
        def popup(page):
            info_str = ''
            if page == 'Menu':
                info_str = """
                Menu interactions are simple! Here is a quick guide to get you
                familiar.

                Navigation of a page: Up, Down, Left, Right, or TAB. Note that
                SHIFT+TAB can be used to reverse cycle!

                Editing a page: Simply navigating to an editable field and
                typing should be enough to edit most pages. ENTER can you be
                used to select or deselect options, or to open drop down menus.

                CTRL+T: Will toggle between two pages.
                CTRL+Q: Will take you back to main. Or from main, will exit the
                application.
                CTRL+X: Can be used to open up menus on certain pages.
                """
            elif page == 'Plugins':
                info_str = """
                Plugins are user created software hosted on GitHub that Vent
                can install and run. Plugins are developed following a hybrid
                of requirements specified both by Docker and Vent. Vent uses
                Docker to run all plugins so all plugins should be designed to
                run as a system of containers. Knowledge of linking docker
                containers may be necessary for more complex tasks that require
                creating multiple containers for your plugin. For Help on
                building Plugins, check out the Working with Plugins section in
                our Help Menu."""
            elif page == 'Tools':
                info_str = """
                Tools are the individual building blocks of a Plugin. Each tool
                should follow S.R.P, and over the entirety of the Plugin should
                be able accomplish any task desired! For Help on building
                Tools, check out the Working with Plugins section in our Help
                Menu."""
            elif page == 'Filetypes':
                info_str = """
                The filetypes Vent can support are entirely based on the
                installed Plugins. Each plugin is ultimately responsible for
                doing some form of processing."""
            elif page == 'Status':
                info_str = """
                You'll notice Vent offers several status types amongst
                tools/plugins. Built means that each tool has a Docker image
                successfully built based off the provided specs for that
                tool/plugin. Enabled/Disabled correspond to user defined
                settings to enable or disable a tool or set of tools (plugin).
                Installed means simply that the plugin has been cloned from
                GitHub and installed to the Vent filesystem. No Docker image
                has been created yet. Running means that a Docker container has
                successfully been created from the corresponding Docker image
                for a specific tool in a Plugin."""
            elif page == 'Plugin Adding':
                info_str = """
                To add a plugin that you've created, simply open up the Menu
                from the main page using ^X. After, press "p" to open up the
                Plugin menu and then "a" to drop down into our Plugin
                installation screen. To add a Plugin, we require a valid
                GitHub repository. If your repository is private, you will
                need to enter a username and password. Once you have finished
                that, select OK. If we are successfully able to connect, you
                should see your repositories branches listed in our Plugin
                options menu. From here, press TAB to cycle between the
                options, and ENTER to select different branches to install and
                build from. You can even choose a specific commit if you like!
                Once you've selected those tools and selected OK, Vent will
                notify you about all tools it has detected. For more
                information about how Vent detects tools, see our "Building a
                Plugin" section. You may select or deselect the tools you wish
                to install as part of your Plugin. When you are done, select
                OK. If everything works you should get a successful Add. Select
                OK, to be returned to the main screen!"""
            elif page == 'Plugin Building':
                # !! TODO
                info_str = """Stay tuned!"""
            npyscreen.notify_confirm(info_str,
                                     title='About Vent ' + page,
                                     wide=True)
        popup(page)

    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({'^T': self.change_forms, '^Q': self.exit})
        self.addfield = self.add(npyscreen.TitleFixedText, name='Vent',
                                 labelColor='DEFAULT', editable=False)
        self.multifield1 = self.add(npyscreen.MultiLineEdit, editable=False,
                                    value="""
        About Vent

        Vent is a library that includes a CLI designed to serve as a general
        platform for analyzing network traffic. Built with some basic
        functionality, Vent serves as a user-friendly platform to build custom
        plugins on to perform user-defined processing on incoming network data.
        Vent supports any filetype, but only processes ones based on the types
        of plugins installed for that instance of Vent. Simply create your
        plugins, point vent to them & install them, and drop a file in vent to
        begin processing!

        For a detailed explanation of Vent Concepts, check out the General
        section in our Help Menu. Topics include: Vent Plugins, Tools,
        Filetypes, and Statuses! Use ^X to access the menu and ESC to
        close it.

        Select CANCEL or ^Q to return to the Main Menu. Select OK or ^T to
        return to your previous menu.

        PRO TIP: You can use TAB to cycle through options.
        """)
        self.m2 = self.add_menu(name='Vent Basics', shortcut='b')
        self.m2.addItem(text='Menu Interactions', onSelect=HelpForm.switch,
                        arguments=['Menu'], shortcut='m')
        self.m2.addItem(text='Plugins', onSelect=HelpForm.switch,
                        arguments=['Plugins'], shortcut='p')
        self.m2.addItem(text='Tools', onSelect=HelpForm.switch,
                        arguments=['Tools'], shortcut='t')
        self.m2.addItem(text='Filetypes', onSelect=HelpForm.switch,
                        arguments=['Filetypes'], shortcut='f')
        self.m2.addItem(text='Statuses', onSelect=HelpForm.switch,
                        arguments=['Status'], shortcut='s')
        self.m3 = self.add_menu(name='Working with Plugins', shortcut='p')
        self.m3.addItem(text='Adding a Plugin', onSelect=HelpForm.switch,
                        arguments=['Plugin Adding'], shortcut='a')
        self.m3.addItem(text='Building a Plugin', onSelect=HelpForm.switch,
                        arguments=['Plugin Building'], shortcut='b')

    def exit(self, *args, **keywords):
        self.parentApp.switchForm('MAIN')

    def on_cancel(self):
        self.exit()

    def on_ok(self):
        self.change_forms()

    def change_forms(self, *args, **keywords):
        """
        Checks which form is currently displayed and toggles to the other one
        """
        # Returns to previous Form in history if there is a previous Form
        try:
            self.parentApp.switchFormPrevious()
        except Exception as e:  # pragma: no cover
            self.parentApp.switchForm('MAIN')
