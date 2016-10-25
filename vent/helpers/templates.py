import ConfigParser


class Template:
    """ Handle parsing templates """
    def __init__(self, template=None):
        self.config = ConfigParser.RawConfigParser()
        self.config.optionxform = str
        if template:
            self.config.read(template)

    @staticmethod
    def get_sections():
        return

    @staticmethod
    def get_options(section):
        return

    @staticmethod
    def set_section(section):
        return

    @staticmethod
    def set_option(section, option):
        return

    @staticmethod
    def add_section(section):
        return

    @staticmethod
    def add_option(section, option):
        return

    @staticmethod
    def del_section(section):
        return

    @staticmethod
    def del_option(section, option):
        return
