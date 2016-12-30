#!/usr/bin/env python2.7

import curses

class Menu:
    def __init__(self, paths=None):
        # setup curses !! TODO
        # use default paths unless given !! TODO
        # version # !! TODO
        try:
            self.screen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.screen.keypard(1)
            self.screen.border(0)
            self.title_text = curses.A_STANDOUT
            self.subtitle_text = curses.A_BOLD
            self.normal_text = curses.A_NORMAL
            self.up = curses.KEY_UP
            self.down = curses.KEY_DOWN
            self.right = curses.KEY_RIGHT
            self.left = curses.KEY_LEFT
            self.esc = 27

            # check if terminal can support color
            if curses.has_colors():
                curses.start_color()
                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
                bold = curses.color_pair(1)

            self.horizontal_pad = 2
            self.vertical_pad = 2

            # Initial Menu defaults
            self.title = 'main'
            self.subtitle = None
            self.parent = None
            self.menu = ['Tools', 'Plugins', 'System Info', 'Troubleshooting']

            self.run()
        except Exception as e:
            return ('failed', e)

    @staticmethod
    def run():
        while True:
            self.display_menu(self.title)
            c = self.screen.getch()
            # !! TODO
            # if c == [up, down, left, right, enter, esc]
            # note if esc just return to parent menu (self.parent)
            # enter should build new menu

    def display_menu(self, title):
        """ Curses wrapper around dictionary that represents menu; handles user selection """
        # !! TODO
        return self.build_menu(title)

    def build_menu(self, title):
        """ Takes in a string that maps to the menu to build """
        menu = {}
        # !! TODO
        if title == 'main':
            menu = {}
        return menu

    def restore(self):
        curses.initscr()
        curses.endwin()

    def __del__(self):
        self.restore()

if __name__ == '__main__':
    menu = Menu()
