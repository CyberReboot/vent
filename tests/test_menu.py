import curses
import npyscreen

from vent.menu import AddForm
from vent.menu import HelpForm
from vent.menu import VentApp
from vent.menu import VentForm
from vent.menu import repo_tools
from vent.menu import repo_values

def test_menu():
    """ Test the menu """
    npyscreen.TEST_SETTINGS['TEST_INPUT'] = ['^X', '^T']
    npyscreen.TEST_SETTINGS['CONTINUE_AFTER_TEST_INPUT'] = True

    A = VentApp()
    try:
        A.run(fork=False)
    except Exception as e:
        pass

def test_repo_tools:
    a = VentApp()
    tools = repo_tools(a, 'master')
    assert type(tools) == list

def test_repo_values:
    a = VentApp()
    branches, commits = repo_values(a)
    assert type(branches) == list
    assert type(commits) == dict
