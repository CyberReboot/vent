import curses
import npyscreen

from vent.menu import AddForm
from vent.menu import HelpForm
from vent.menu import VentApp
from vent.menu import VentForm
from vent.menu import ServicesForm
from vent.menu import ChooseToolsForm
from vent.menu import AddOptionsForm

def test_menu():
    """ Test the menu """
    npyscreen.TEST_SETTINGS['TEST_INPUT'] = ['^X', '^T']
    npyscreen.TEST_SETTINGS['CONTINUE_AFTER_TEST_INPUT'] = True

    A = VentApp()
    try:
        A.run(fork=False)
    except Exception as e:
        pass
