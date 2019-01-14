import npyscreen


class TutorialForm(npyscreen.ActionFormWithMenus):
    """ Tutorial form for the Vent CLI """

    def __init__(self, title='', text='', next_tutorial='', *args, **keywords):
        """ Initialize tutorial form fields """
        self.title = title
        self.text = text
        self.next_tutorial = next_tutorial
        super(TutorialForm, self).__init__(*args, **keywords)

    def switch(self, name):
        """ Wrapper that switches to provided form """
        self.parentApp.change_form(name)

    def quit(self, *args, **kwargs):
        """ Overridden to switch back to MAIN form """
        self.parentApp.switchForm('MAIN')

    def create(self):
        """ Overridden to add handlers and content """
        self.add_handlers({'^Q': self.quit})
        self.add(npyscreen.TitleText, name=self.title, editable=False)
        self.add(npyscreen.MultiLineEdit, editable=False, value=self.text,
                 max_width=75, slow_scroll=True)
        self.m2 = self.add_menu(name='About Vent', shortcut='v')
        self.m2.addItem(text='Background', onSelect=self.switch,
                        arguments=['TUTORIALBACKGROUND'], shortcut='b')
        self.m2.addItem(text='Terminology', onSelect=self.switch,
                        arguments=['TUTORIALTERMINOLOGY'], shortcut='t')
        self.m2.addItem(text='Getting Setup', onSelect=self.switch,
                        arguments=['TUTORIALGETTINGSETUP'], shortcut='s')
        self.m3 = self.add_menu(name='Working with Cores', shortcut='c')
        self.m3.addItem(text='Starting Cores', onSelect=self.switch,
                        arguments=['TUTORIALSTARTINGCORES'], shortcut='c')
        self.m4 = self.add_menu(name='Working with Plugins', shortcut='p')
        self.m4.addItem(text='Adding Plugins', onSelect=self.switch,
                        arguments=['TUTORIALADDINGPLUGINS'], shortcut='a')
        self.m5 = self.add_menu(name='Files', shortcut='f')
        self.m5.addItem(text='Adding Files', onSelect=self.switch,
                        arguments=['TUTORIALADDINGFILES'], shortcut='a')
        self.m6 = self.add_menu(name='Help', shortcut='s')
        self.m6.addItem(text='Basic Troubleshooting', onSelect=self.switch,
                        arguments=['TUTORIALTROUBLESHOOTING'], shortcut='t')

    def on_cancel(self):
        """ When user clicks cancel, will return to MAIN """
        self.quit()

    def on_ok(self):
        """ When user clicks ok, will proceed to next tutorial """
        self.switch(self.next_tutorial)
