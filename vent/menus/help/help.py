import npyscreen

class HelpForm(npyscreen.FormBaseNewWithMenus):
    """ Help form for the Vent CLI """
    def create(self):
        """ Override method for creating FormBaseNew form """
        self.add_handlers({"^T": self.change_forms,"^Q": self.exit})
        self.addfield = self.add(npyscreen.TitleFixedText, name="Vent",
                                 labelColor='DEFAULT', editable=False)
        self.multifield1 = self.add(npyscreen.MultiLineEdit, editable=False,
                                    value="""
        About Vent:
            Vent is a library that includes a CLI designed to serve as a general
            platform for analyzing network traffic. Built with some basic
            functionality, Vent serves as a user-friendly platform to build custom
            plugins on to perform user-defined processing on incoming network data.
            Vent supports any filetype, but only processes ones based on the types
            of plugins installed for that instance of Vent. Simply create your
            plugins, point vent to them & install them, and drop a file in vent to
            begin processing!

            For a detailed explanation of Vent Concepts, check out the General
            section in our Help Menu.

        Vent Concepts:
            Plugins - Plugins are user created software hosted on GitHub that Vent
            can install and run. Plugins are developed following a hybrid of requirements
            specified both by Docker and Vent. Vent uses Docker to run all plugins
            so all plugins should be designed to run as a system of containers.
            Knowledge of linking docker containers may be necessary for more
            complex tasks that require creating multiple containers for your plugin.
            For Help on building Plugins, check out the Plugin section in our Help Menu.

            Tools - Tools are the individual building blocks of a Plugin. Each tool should
            follow S.R.P, and over the entirety of the Plugin should be able accomplish any
            task desired! For Help on building Tools, check out the Plugin section in our Help Menu.

            Filetypes - The filetypes Vent can support are entirely based on the
            installed Plugins. Each plugin is ultimately responsible for doing
            some form of processing. Vent currently supports only PCAP files
            out of the box.

            Core - Core Tools are tools that Vent comes with out of the box. For more info on
            the Core Tools that Vent starts with please check out this link:
            https://github.com/CyberReboot/vent/blob/master/docs/images/core_plugins.png

            Status - You'll notice Vent offers several status types amongst tools/plugins.
                Built means that each tool has a Docker image successfully built based off
                the provided specs for that tool/plugin.

                Enabled/Disabled correspond to user defined settings to enable or disable
                a tool or set of tools (plugin).

                Installed means simply that the plugin has been cloned from GitHub and
                installed to the Vent filesystem. No Docker image has been created yet.

                Running means that a Docker container has successfully been created from
                the corresponding Docker image for a specific tool in a Plugin.
        """)
        self.m2 = self.add_menu(name="General", shortcut='g')
        self.m2.addItem(text="Concepts", onSelect=self.switch,
                        arguments=['HELPCONCEPTS'], shortcut='c')
        self.m2.addItem(text="Core Tools", onSelect=self.switch,
                        arguments=['HELPCORES'], shortcut='t')
        self.m2.addItem(text="Vent Statuses", onSelect=self.switch,
                        arguments=['HELPSTATUS'], shortcut='s')
        self.m2.addItem(text="Handling Filetypes", onSelect=self.switch,
                        arguments=['HELPFILETYPES'], shortcut='f')
        self.m3 = self.add_menu(name="Plugins", shortcut='p')
        self.m3.addItem(text="Building a Tool", onSelect=self.switch,
                        arguments=['HELPTOOLS'], shortcut='t')
        self.m3.addItem(text="Building a Plugin", onSelect=self.switch,
                        arguments=['HELPPLUGINS'], shortcut='p')

    def exit(self, *args, **keywords):
        self.parentApp.switchForm('MAIN')

    def change_forms(self, *args, **keywords):
        """ Checks which form is currently displayed and toggles it to the other one """
        # Returns to previous Form in history if there is a previous Form
        try:
            self.parentApp.switchFormPrevious()
        except Exception as e:
            self.parentApp.switchForm('MAIN')
