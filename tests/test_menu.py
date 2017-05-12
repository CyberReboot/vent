import curses
import npyscreen

from vent.menu import VentApp
from vent.menus.add import AddForm
from vent.menus.help import HelpForm
from vent.menus.main import MainForm
from vent.menus.services import ServicesForm
from vent.menus.choose_tools import ChooseToolsForm
from vent.menus.add_options import AddOptionsForm

def test_menu():
    """ Test the menu """
    npyscreen.TEST_SETTINGS['TEST_INPUT'] = ['^X', '^T']
    npyscreen.TEST_SETTINGS['CONTINUE_AFTER_TEST_INPUT'] = True

    a = VentApp()
    try:
        a.run(fork=False)
    except Exception as e:
        pass

def test_add():
    """ Test the add form """
    a = VentApp()
    b = AddForm(a)
    b.create()
