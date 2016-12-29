import ConfigParser

def ErrorHandler(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            print e
    return wrapper

class Template:
    """ Handle parsing templates """
    def __init__(self, template=None):
        self.config = ConfigParser.RawConfigParser()
        self.config.optionxform = str
        if template:
            self.config.read(template)

    """ Returns a list of sections """
    @ErrorHandler
    def sections(self):
        return (True, self.config.sections())

    """ Returns a list of tuples of (option, value) for the section """
    @ErrorHandler
    def section(self, section):
        # check if the named section exists
        if self.config.has_section(section):
            return (True, self.config.items(section))
        return (False, "Section: " + section + " does not exist")

    """ Returns a list of options for a section """
    @ErrorHandler
    def options(self, section):
        if self.config.has_section(section):
            return (True, self.config.options(section))
        return (False, "Section: " + section + " does not exist")

    """ Returns the value of the option """
    @ErrorHandler
    def option(self, section, option):
        if self.config.has_section(section):
            if self.config.has_option(section, option):
                return (True, self.config.get(section, option))
            return (False, "Option: " + option + " does not exist")
        return (False, "Section: " + section + " does not exist")

    """
    If section exists, returns log,
    otherwise adds section and returns list of sections.
    """
    @ErrorHandler
    def add_section(self, section):
        # check if section already exists
        if not self.config.has_section(section):
            self.config.add_section(section)
            # return updated sections
            return (True, self.config.sections())
        return (False, "Section: " + section + " already exists")

    """
    Creates an option for a section. If the section does
    not exist, it will create the section.
    """
    @ErrorHandler
    def add_option(self, section, option, value=None):
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

    """ Deletes a section if it exists """
    @ErrorHandler
    def del_section(self, section):
        if self.config.has_section(section):
            self.config.remove_section(section)
            return (True, self.config.sections())
        return (False, "Section: " + section + " does not exist")

    """ Deletes an option if the section and option exist """
    @ErrorHandler
    def del_option(self, section, option):
        if self.config.has_section(section):
            if self.config.has_option(section, option):
                self.config.remove_option(section, option)
                return (True, self.config.options(section))
            return (False, "Option: " + option + " does not exist")
        return (False, "Section: " + section + " does not exist")

    """
    Sets an option to a value in the given section. Option is created if it
    does not already exist
    """
    @ErrorHandler
    def set_option(self, section, option, value):
        if self.config.has_section(section):
            return (True, self.config.set(section, option, value))
        return (False, "Section: " + section + " does not exist")

    """ Renames a section by transferring all option-value pairs to a new section """
    @ErrorHandler
    def rename_section(self, original, new):
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

    """ Moves an option from one section to another """
    @ErrorHandler
    def move_option(self, source, destination, option, overwrite=False):
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
                            self.config.set(destination, option, self.config.get(source, option))
                            self.del_option(source, option)
                        else:
                            return (False, "Option: " + option + " already exists in " + destination + ". Did you want to overwrite?")
                    return (True, self.config.options(destination))
                return (False, "Option: " + option + " does not exist in " + source)
            return (False, "Section: " + destination + " does not exist")
        return (False, "Section: " + source + " does not exist")
