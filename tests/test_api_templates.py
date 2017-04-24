from vent.api.templates Import Template

def test_options():
    """ Test the options function """
    instance = Template()
    instance.options('foo')

def test_option():
    instance = Template()
    instance.option('foo', 'bar')

def test_add_option():
    instance = Template()
    instance.add_option('foo', 'bar')

def test_del_section():
    instance = Template()
    instance.del_section('foo')
