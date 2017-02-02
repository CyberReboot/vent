from vent.menu import VentForm
from vent.menu import HelpForm
from vent.menu import VentApp

def test_onStart():
    """ Test the onStart function """
    instance = VentApp()
    instance.onStart()
