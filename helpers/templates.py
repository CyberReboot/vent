import ConfigParser

class Template:
    """ Handle parsing templates """
    def __init__(self, template=None):
        self.config = ConfigParser.RawConfigParser()
        self.config.optionxform=str
        if template:
            self.config.read(template)

    def get_sections(self):
        return

    def get_options(self, section):
        return

    def set_section(self, section):
        return

    def set_option(self, section, option):
        return

    def add_section(self, section):
        return

    def add_option(self, section, option):
        return

    def del_section(self, section):
        return

    def del_option(self, section, option):
        return
