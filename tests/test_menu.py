import curses
import npyscreen

from vent.menu import HelpForm
from vent.menu import VentApp
from vent.menu import VentForm

npyscreen.TEST_SETTINGS['TEST_INPUT'] = ['^X', '^T', '^C']
npyscreen.TEST_SETTINGS['CONTINUE_AFTER_TEST_INPUT'] = True

app = VentApp()

try:
    app.run(fork=False)
except Exception as e:
    pass
