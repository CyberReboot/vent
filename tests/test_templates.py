import pytest

from vent.helpers import templates

class TemplateTester:
    """ Tester class for Templates.py """
    section1 = "old"
    section2 = "new"
    option1 = "alpha"
    option2 = "beta"
    val1 = "text"
    val2 = "more text"

    def __init__(self):
        self.instance = templates.Template()

    def sections(self):
        return self.instance.sections()

    def section(self, section):
        return self.instance.section(section)

    def options(self, section):
        return self.instance.options(section)

    def option(self, section, option):
        return self.instance.option(section, option)

    def add_section(self, section):
        return self.instance.add_section(section)

    def add_option(self, section, option, value=None):
        return self.instance.add_option(section, option, value)

    def del_section(self, section):
        return self.instance.del_section(section)

    def del_option(self, section, option):
        return self.instance.del_option(section, option)

    def set_option(self, section, option, value):
        return self.instance.set_option(section, option, value)

    def rename_section(self, original, new):
        return self.instance.rename_section(original, new)

    def move_option(self, source, destination, option, overwrite=False):
        return self.instance.move_option(source, destination, option, overwrite)

def test_blank_template():
    """ Test negatives on blank template """
    test = TemplateTester()
    assert test.sections() == (True, [])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False
    assert test.option(test.section1, test.option1)[0] == False
    assert test.del_section(test.section1)[0] == False
    assert test.del_option(test.section1, test.option1)[0] == False
    assert test.set_option(test.section1, test.option1, test.val1)[0] == False
    assert test.rename_section(test.section1, test.section2)[0] == False
    assert test.move_option(test.section1, test.section2, test.option1)[0] == False

    # Should pass
    assert test.add_option(test.section1, test.option1) == (True, ['alpha'])

    # Should pass
    assert test.add_option(test.section2, test.option1, test.val1) == (True, ['alpha'])

def test_add_section():
    """ Test insert section that doesn't exist """
    test = TemplateTester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])
    assert test.option(test.section1, test.option1)[0] == False

def test_add_section_duplicate():
    """ Test insert section that already exists """
    test = TemplateTester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.add_section(test.section1)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])
    assert test.option(test.section1, test.option1)[0] == False

def test_add_option():
    """ Test insert option into section that doesn't exist """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1) == (True, ['alpha'])
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', None)])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, None)

def test_add_option_duplicate_section():
    """ Test insert option into section that already exists """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1) == (True, ['alpha'])
    assert test.add_option(test.section1, test.option2)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', None)])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, None)

def test_add_option_value_no_section():
    """ Test insert option with value into section that doesn't exist """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'text')

def test_add_option_value():
    """ Test insert option with value into section that exists """
    test = TemplateTester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.add_option(test.section1, test.option1, test.val1)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])
    assert test.option(test.section1, test.option1)[0] == False

def test_add_option_value_duplicate_section():
    """ Test insert option with different value into section that exists """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.add_option(test.section1, test.option1, test.val2)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'text')

def test_del_option():
    """ Test delete option that exists """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.del_option(test.section1, test.option1) == (True, [])
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])
    assert test.option(test.section1, test.option1)[0] == False

def test_del_option_negative():
    """ Test delete option that doesn't exist """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.del_option(test.section1, test.option2)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'text')
    assert test.option(test.section1, test.option2)[0] == False

def test_del_option_no_section():
    """ Test delete option from section that doesn't exist """
    test = TemplateTester()
    assert test.del_option(test.section1, test.option1)[0] == False
    assert test.sections() == (True, [])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False
    assert test.option(test.section1, test.option1)[0] == False

def test_move_option():
    """ Test move option from section to empty section """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.add_section(test.section2) == (True, ['old', 'new'])
    assert test.move_option(test.section1, test.section2, test.option1) == (True, ['alpha'])
    assert test.sections() == (True, ['old', 'new'])
    assert test.section(test.section1) == (True, [])
    assert test.section(test.section2) == (True, [('alpha', 'text')])
    assert test.options(test.section1) == (True, [])
    assert test.options(test.section2) == (True, ['alpha'])
    assert test.option(test.section1, test.option1)[0] == False
    assert test.option(test.section2, test.option1) == (True, 'text')

def test_move_option_duplicate():
    """ Test move duplicate option """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.add_option(test.section2, test.option1, test.val2) == (True, ['alpha'])
    assert test.move_option(test.section1, test.section2, test.option1)[0] == False
    assert test.sections() == (True, ['old', 'new'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.section(test.section2) == (True, [('alpha', 'more text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.options(test.section2) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'text')
    assert test.option(test.section2, test.option1) == (True, 'more text')

def test_move_option_overwrite():
    """ Test move duplicate option with overwrite """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.add_option(test.section2, test.option1, test.val2) == (True, ['alpha'])
    assert test.move_option(test.section1, test.section2, test.option1, overwrite=True) == (True, ['alpha'])
    assert test.sections() == (True, ['old', 'new'])
    assert test.section(test.section1) == (True, [])
    assert test.section(test.section2) == (True, [('alpha', 'text')])
    assert test.options(test.section1) == (True, [])
    assert test.options(test.section2) == (True, ['alpha'])
    assert test.option(test.section1, test.option1)[0] == False
    assert test.option(test.section2, test.option1) == (True, 'text')

def test_move_option_negative():
    """ Test move option that doesn't exist """
    test = TemplateTester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.add_option(test.section2, test.option1, test.val2) == (True, ['alpha'])
    assert test.move_option(test.section1, test.section2, test.option1)[0] == False
    assert test.sections() == (True, ['old', 'new'])
    assert test.section(test.section1) == (True, [])
    assert test.section(test.section2) == (True, [('alpha', 'more text')])
    assert test.options(test.section1) == (True, [])
    assert test.options(test.section2) == (True, ['alpha'])
    assert test.option(test.section1, test.option1)[0] == False
    assert test.option(test.section2, test.option1) == (True, 'more text')

def test_move_option_to_no_section():
    """ Test move option to section that doesn't exist """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.move_option(test.section1, test.section2, test.option1)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.section(test.section2)[0] == False
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.options(test.section2)[0] == False
    assert test.option(test.section1, test.option1) == (True, 'text')
    assert test.option(test.section2, test.option1)[0] == False

def test_move_option_from_no_section():
    """ Test move option from section that doesn't exist """
    test = TemplateTester()
    assert test.add_option(test.section2, test.option1, test.val1) == (True, ['alpha'])
    assert test.move_option(test.section1, test.section2, test.option1)[0] == False
    assert test.sections() == (True, ['new'])
    assert test.section(test.section1)[0] == False
    assert test.section(test.section2) == (True, [('alpha', 'text')])
    assert test.options(test.section1)[0] == False
    assert test.options(test.section2) == (True, ['alpha'])
    assert test.option(test.section1, test.option1)[0] == False
    assert test.option(test.section2, test.option1) == (True, 'text')

def test_set_option():
    """ Test set option into section that exists """
    test = TemplateTester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.set_option(test.section1, test.option1, test.val1) == (True, None)
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'text')

def test_set_option_negative():
    """ Test set option into section that doesn't exist """
    test = TemplateTester()
    assert test.set_option(test.section1, test.option1, test.val1)[0] == False
    assert test.sections() == (True, [])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False
    assert test.option(test.section1, test.option1)[0] == False

def test_set_option_duplicate():
    """ Test set duplicate option """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.set_option(test.section1, test.option1, test.val2) == (True, None)
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'more text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'more text')

def test_rename_section():
    """ Test rename empty section that exists """
    test = TemplateTester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.rename_section(test.section1, test.section2)
    assert test.sections() == (True, ['new'])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False
    assert test.section(test.section2) == (True, [])
    assert test.options(test.section2) == (True, [])

def test_rename_section_itself():
    """ Test rename empty section to itself """
    test = TemplateTester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.rename_section(test.section1, test.section1)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])

def test_rename_section_duplicate():
    """ Test rename empty section to duplicate section """
    test = TemplateTester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.add_option(test.section2, test.option1, test.val1) == (True, ['alpha'])
    assert test.rename_section(test.section1, test.section2)[0] == False
    assert test.sections() == (True, ['old', 'new'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])
    assert test.section(test.section2) == (True, [('alpha', 'text')])
    assert test.options(test.section2) == (True, ['alpha'])
    assert test.option(test.section2, test.option1) == (True, 'text')

def test_rename_section_values():
    """ Test rename nonempty section """
    test = TemplateTester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.rename_section(test.section1, test.section2) == (True, ['new'])
    assert test.sections() == (True, ['new'])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False
    assert test.section(test.section2) == (True, [('alpha', 'text')])
    assert test.options(test.section2) == (True, ['alpha'])
    assert test.option(test.section2, test.option1) == (True, 'text')

def test_del_section():
    """ Test delete section that exists """
    test = TemplateTester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.del_section(test.section1) == (True, [])
    assert test.sections() == (True, [])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False

def test_del_section_negative():
    """ Test delete section that doesn't exist """
    test = TemplateTester()
    assert test.del_section(test.section1)[0] == False
    assert test.sections() == (True, [])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False
