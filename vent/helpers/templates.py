import configparser

from vent.helpers.errors import ErrorHandler


class Template:
    """ Handle parsing templates """

    def __init__(self, template=None):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.optionxform = str
        if template:
            self.config.read(template)
            self.template = template

    @ErrorHandler
    def sections(self):
        """ Returns a list of sections """
        return (True, self.config.sections())

    @ErrorHandler
    def section(self, section):
        """ Returns a list of tuples of (option, value) for the section """
        # check if the named section exists
        if self.config.has_section(section):
            return (True, self.config.items(section))
        return (False, 'Section: ' + section + ' does not exist')

    @ErrorHandler
    def options(self, section):
        """ Returns a list of options for a section """
        if self.config.has_section(section):
            return (True, self.config.options(section))
        return (False, 'Section: ' + section + ' does not exist')

    @ErrorHandler
    def option(self, section, option):
        """ Returns the value of the option """
        if self.config.has_section(section):
            if self.config.has_option(section, option):
                return (True, self.config.get(section, option))
            return (False, 'Option: ' + option + ' does not exist')
        return (False, 'Section: ' + section + ' does not exist')

    @ErrorHandler
    def add_section(self, section):
        """
        If section exists, returns log,
        otherwise adds section and returns list of sections.
        """
        # check if section already exists
        if not self.config.has_section(section):
            self.config.add_section(section)
            # return updated sections
            return (True, self.config.sections())
        return (False, 'Section: ' + section + ' already exists')

    @ErrorHandler
    def add_option(self, section, option, value=None):
        """
        Creates an option for a section. If the section does
        not exist, it will create the section.
        """
        # check if section exists; create if not
        if not self.config.has_section(section):
            message = self.add_section(section)
            if not message[0]:
                return message

        if not self.config.has_option(section, option):
            if value:
                self.config.set(section, option, value)
            else:
                self.config.set(section, option)
            return(True, self.config.options(section))
        return(False, 'Option: {} already exists @ {}'.format(option, section))

    @ErrorHandler
    def del_section(self, section):
        """ Deletes a section if it exists """
        if self.config.has_section(section):
            self.config.remove_section(section)
            return (True, self.config.sections())
        return (False, 'Section: ' + section + ' does not exist')

    @ErrorHandler
    def del_option(self, section, option):
        """ Deletes an option if the section and option exist """
        if self.config.has_section(section):
            if self.config.has_option(section, option):
                self.config.remove_option(section, option)
                return (True, self.config.options(section))
            return (False, 'Option: ' + option + ' does not exist')
        return (False, 'Section: ' + section + ' does not exist')

    @ErrorHandler
    def set_option(self, section, option, value):
        """
        Sets an option to a value in the given section. Option is created if it
        does not already exist
        """
        if self.config.has_section(section):
            self.config.set(section, option, value)
            return (True, self.config.options(section))
        return (False, 'Section: ' + section + ' does not exist')

    @ErrorHandler
    def write_config(self):
        with open(self.template, 'w') as configfile:
            self.config.write(configfile)
        return

    @ErrorHandler
    def constrained_sections(self, constraints=None, options=None):
        """
        Takes a dictionary of option/values (constraints) that must be present
        in a section, and returns a dictionary of sections and optionally a
        dictionary of option/values defined by a list of options called options
        that match the constraints
        """
        sections = {}
        if not constraints:
            constraints = {}
        if not options:
            options = []
        all_sections = self.sections()
        for a_section in all_sections[1]:
            include = True
            for constraint in constraints:
                result = self.option(a_section, constraint)
                if not result[0] or result[1] != constraints[constraint]:
                    include = False
                # handle group membership
                if (result[0] and
                    constraint == 'groups' and
                        constraints[constraint] in result[1]):
                    include = True
            if include:
                sections[a_section] = {}
                for option in options:
                    result = self.option(a_section, option)
                    if result[0]:
                        sections[a_section][option] = result[1]
        return sections

    @ErrorHandler
    def constrain_opts(self, constraint_dict, options):
        """ Return result of constraints and options against a template """
        constraints = {}
        for constraint in constraint_dict:
            if constraint != 'self':
                if (constraint_dict[constraint] or
                        constraint_dict[constraint] == ''):
                    constraints[constraint] = constraint_dict[constraint]
        results = self.constrained_sections(constraints=constraints,
                                            options=options)
        return results, self.template

    @ErrorHandler
    def list_tools(self):
        """
        Return list of tuples of all tools
        """
        tools = []
        exists, sections = self.sections()
        if exists:
            for section in sections:
                options = {'section': section,
                           'built': None,
                           'version': None,
                           'repo': None,
                           'branch': None,
                           'name': None,
                           'groups': None,
                           'image_name': None}
                for option in list(options.keys()):
                    exists, value = self.option(section, option)
                    if exists:
                        options[option] = value
                if 'core' not in options['groups'] and 'hidden' not in options['groups']:
                    tools.append(options)
        return tools
