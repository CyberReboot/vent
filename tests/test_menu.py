from vent.menu import HelpForm
from vent.menu import VentApp
from vent.menu import VentForm

app = VentApp()
app.onStart()
app.change_form("HELP")

form = HelpForm()
form = VentForm()
