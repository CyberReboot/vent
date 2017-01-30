import ConfigParser

from vent.helpers.errors import ErrorHandler

class Template:
    """ Handle parsing templates """
    def __init__(self, template=None):
        self.config = ConfigParser.RawConfigParser()
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
        return (False, "Section: " + section + " does not exist")

    @ErrorHandler
    def options(self, section):
        """ Returns a list of options for a section """
        if self.config.has_section(section):
            return (True, self.config.options(section))
        return (False, "Section: " + section + " does not exist")

    @ErrorHandler
    def option(self, section, option):
        """ Returns the value of the option """
        if self.config.has_section(section):
            if self.config.has_option(section, option):
                return (True, self.config.get(section, option))
            return (False, "Option: " + option + " does not exist")
        return (False, "Section: " + section + " does not exist")

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
        return (False, "Section: " + section + " already exists")

    @ErrorHandler
    def add_option(self, section, option, value=None):
        """
        Creates an option for a section. If the section does
        not exist, it will create the section.
        """
        # if duplicate section, and return error message
        message = self.add_section(section)
        if not message[0]:
            return message
        # check if section exists
        if self.config.has_section(section):
            if not self.config.has_option(section, option):
                # if a value was provided, set to value
                if value:
                    self.config.set(section, option, value)
                else:
                    self.config.set(section, option)
                return (True, self.config.options(section))
            return (False, "Option: " + option + " already exists in " + section)
        return (False, "Section: " + section + " does not exist. Did you want to force it?")

    @ErrorHandler
    def del_section(self, section):
        """ Deletes a section if it exists """
        if self.config.has_section(section):
            self.config.remove_section(section)
            return (True, self.config.sections())
        return (False, "Section: " + section + " does not exist")

    @ErrorHandler
    def del_option(self, section, option):
        """ Deletes an option if the section and option exist """
        if self.config.has_section(section):
            if self.config.has_option(section, option):
                self.config.remove_option(section, option)
                return (True, self.config.options(section))
            return (False, "Option: " + option + " does not exist")
        return (False, "Section: " + section + " does not exist")

    @ErrorHandler
    def set_option(self, section, option, value):
        """
        Sets an option to a value in the given section. Option is created if it
        does not already exist
        """
        if self.config.has_section(section):
            self.config.set(section, option, value)
            return (True, self.config.options(section))
        return (False, "Section: " + section + " does not exist")

    @ErrorHandler
    def write_config(self):
        with open(self.template, 'wb') as configfile:
            self.config.write(configfile)
        return

    @ErrorHandler
    def rename_section(self, original, new):
        """
        Renames a section by transferring all option-value pairs to a new
        section
        """
        if self.config.has_section(original):
            if not self.config.has_section(new):
                values = self.section(original)[1]
                self.del_section(original)
                self.add_section(new)
                for value in values:
                    self.set_option(new, value[0], value[1])
                return (True, self.config.sections())
            return (False, "Section: " + new + " already exists")
        return (False, "Section: " + original + " does not exist")

    @ErrorHandler
    def move_option(self, source, destination, option, overwrite=False):
        """ Moves an option from one section to another """
        if self.config.has_section(source):
            if self.config.has_section(destination):
                if self.config.has_option(source, option):
                    # check that option does not exist at destination
                    if not self.config.has_option(destination, option):
                        self.set_option(destination, option, self.config.get(source, option))
                        self.del_option(source, option)
                    else:
                        # only overwrite if True
                        if overwrite:
                            self.set_option(destination, option, self.config.get(source, option))
                            self.del_option(source, option)
                        else:
                            return (False, "Option: " + option + " already exists in " + destination + ". Did you want to overwrite?")
                    return (True, self.config.options(destination))
                return (False, "Option: " + option + " does not exist in " + source)
            return (False, "Section: " + destination + " does not exist")
        return (False, "Section: " + source + " does not exist")

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
                if result[0] and constraint == 'groups' and constraints[constraint] in result[1]:
                    include = True
            if include:
                sections[a_section] = {}
                for option in options:
                    result = self.option(a_section, option)
                    if result[0]:
                        sections[a_section][option] = result[1]
        return sections
