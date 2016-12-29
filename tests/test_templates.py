import pytest

from vent.helpers import templates

class Template_Tester:
    section1 = "old"
    section2 = "new"
    section3 = "small"
    section4 = "big"
    option1 = "alpha"
    option2 = "beta"
    val1 = "text"
    val2 = "more text"

    def __init__(self):
        self.instance = Template()

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

# Test negatives on blank template
def test_blank_template():
    test = Template_Tester()
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

# Test insert section that doesn't exist
def test_add_section():
    test = Template_Tester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])
    assert test.option(test.section1, test.option1)[0] == False

# Test insert section that already exists
def test_add_section_duplicate():
    test = Template_Tester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.add_section(test.section1)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])
    assert test.option(test.section1, test.option1)[0] == False

# Test insert option into section that doesn't exist
def test_add_option():
    test = Template_Tester()
    assert test.add_option(test.section1, test.option1) == (True, ['alpha'])
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', None)])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, None)

# Test insert option into section that already exists
def test_add_option_duplicate_section():
    test = Template_Tester()
    assert test.add_option(test.section1, test.option1) == (True, ['alpha'])
    assert test.add_option(test.section1, test.option2)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', None)])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, None)

# Test insert option with value into section that doesn't exist
def test_add_option_value_no_section():
    test = Template_Tester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'text')

# Test insert option with value into section that exists
def test_add_option_value():
    test = Template_Tester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.add_option(test.section1, test.option1, test.val1)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])
    assert test.option(test.section1, test.option1)[0] == False

# Test insert option with different value into section that exists
def test_add_option_value_duplicate_section():
    test = Template_Tester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.add_option(test.section1, test.option1, test.val2)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'text')

# Test delete option that exists
def test_del_option():
    test = Template_Tester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.del_option(test.section1, test.option1) == (True, [])
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])
    assert test.option(test.section1, test.option1)[0] == False

# Test delete option that doesn't exist
def test_del_option_negative():
    test = Template_Tester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.del_option(test.section1, test.option2)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'text')
    assert test.option(test.section1, test.option2)[0] == False

# Test delete option from section that doesn't exist
def test_del_option_no_section():
    test = Template_Tester()
    assert test.del_option(test.section1, test.option1)[0] == False
    assert test.sections() == (True, [])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False
    assert test.option(test.section1, test.option1)[0] == False

# Test move option from section to empty section
def test_move_option():
    test = Template_Tester()
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

# Test move duplicate option
def test_move_option_duplicate():
    test = Template_Tester()
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

# Test move duplicate option with overwrite
def test_move_option_overwrite():
    test = Template_Tester()
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

# Test move option that doesn't exist
def test_move_option_negative():
    test = Template_Tester()
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

# Test move option to section that doesn't exist
def test_move_option_to_no_section():
    test = Template_Tester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.move_option(test.section1, test.section2, test.option1)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.section(test.section2)[0] == False
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.options(test.section2)[0] == False
    assert test.option(test.section1, test.option1) == (True, 'text')
    assert test.option(test.section2, test.option1)[0] == False

# Test move option from section that doesn't exist
def test_move_option_from_no_section():
    test = Template_Tester()
    assert test.add_option(test.section2, test.option1, test.val1) == (True, ['alpha'])
    assert test.move_option(test.section1, test.section2, test.option1)[0] == False
    assert test.sections() == (True, ['new'])
    assert test.section(test.section1)[0] == False
    assert test.section(test.section2) == (True, [('alpha', 'text')])
    assert test.options(test.section1)[0] == False
    assert test.options(test.section2) == (True, ['alpha'])
    assert test.option(test.section1, test.option1)[0] == False
    assert test.option(test.section2, test.option1) == (True, 'text')

# Test set option into section that exists
def test_set_option():
    test = Template_Tester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.set_option(test.section1, test.option1, test.val1) == (True, None)
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'text')

# Test set option into section that doesn't exist
def test_set_option_negative():
    test = Template_Tester()
    assert test.set_option(test.section1, test.option1, test.val1)[0] == False
    assert test.sections() == (True, [])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False
    assert test.option(test.section1, test.option1)[0] == False

# Test set duplicate option
def test_set_option_duplicate():
    test = Template_Tester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.set_option(test.section1, test.option1, test.val2) == (True, None)
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [('alpha', 'more text')])
    assert test.options(test.section1) == (True, ['alpha'])
    assert test.option(test.section1, test.option1) == (True, 'more text')

# Test rename empty section that exists
def test_rename_section():
    test = Template_Tester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.rename_section(test.section1, test.section2)
    assert test.sections() == (True, ['new'])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False
    assert test.section(test.section2) == (True, [])
    assert test.options(test.section2) == (True, [])

# Test rename empty section to itself
def test_rename_section_itself():
    test = Template_Tester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.rename_section(test.section1, test.section1)[0] == False
    assert test.sections() == (True, ['old'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])

# Test rename empty section to duplicate section
def test_rename_section_duplicate():
    test = Template_Tester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.add_option(test.section2, test.option1, test.val1) == (True, ['alpha'])
    assert test.rename_section(test.section1, test.section2)[0] == False
    assert test.sections() == (True, ['old', 'new'])
    assert test.section(test.section1) == (True, [])
    assert test.options(test.section1) == (True, [])
    assert test.section(test.section2) == (True, [('alpha', 'text')])
    assert test.options(test.section2) == (True, ['alpha'])
    assert test.option(test.section2, test.option1) == (True, 'text')

# Test rename nonempty section
def test_rename_section_values():
    test = Template_Tester()
    assert test.add_option(test.section1, test.option1, test.val1) == (True, ['alpha'])
    assert test.rename_section(test.section1, test.section2) == (True, ['new'])
    assert test.sections() == (True, ['new'])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False
    assert test.section(test.section2) == (True, [('alpha', 'text')])
    assert test.options(test.section2) == (True, ['alpha'])
    assert test.option(test.section2, test.option1) == (True, 'text')

# Test delete section that exists
def test_del_section():
    test = Template_Tester()
    assert test.add_section(test.section1) == (True, ['old'])
    assert test.del_section(test.section1) == (True, [])
    assert test.sections() == (True, [])
    assert test.section(test.section1)[0] == False
    assert test.options(test.section1)[0] == False

# Test delete section that doesn't exist
def test_del_section_negative():
   test = Template_Tester()
   assert test.del_section(test.section1)[0] == False
   assert test.sections() == (True, [])
   assert test.section(test.section1)[0] == False
   assert test.options(test.section1)[0] == False
