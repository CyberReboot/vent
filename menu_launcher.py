#!/usr/bin/env python2.7

import ConfigParser
import curses
import os
import sys

from subprocess import call, check_output, PIPE, Popen

screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
screen.keypad(1)

curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE)
h = curses.color_pair(1)
n = curses.A_NORMAL

MENU = "menu"
COMMAND = "command"
EXITMENU = "exitmenu"
INFO = "info"
INFO2 = "info2"
SETTING = "setting"
INPUT = "input"

# path that exists on the iso
template_dir = "/var/lib/docker/data/templates/"
plugins_dir = "/var/lib/docker/data/plugins/"

def run_plugins(action):
    modes = []
    try:
        config = ConfigParser.RawConfigParser()
        config.read(template_dir+'modes.template')
        plugin_array = config.options("plugins")
        plugins = {}
        for plug in plugin_array:
            plugins[plug] = config.get("plugins", plug)

        for plugin in plugins:
            if plugin == "core" or plugin == "visualization":
                p = {}
                try:
                    config = ConfigParser.RawConfigParser()
                    config.read(template_dir+plugin+'.template')
                    plugin_name = config.get("info", "name")
                    p['title'] = plugin_name
                    p['type'] = COMMAND
                    p['command'] = 'python2.7 /data/template_parser.py '+plugin+' '+action
                    modes.append(p)
                except:
                    # if no name is provided, it doesn't get listed
                    pass
        try:
            config = ConfigParser.RawConfigParser()
            config.read(template_dir+'core.template')
            try:
                passive = config.get("local-collection", "passive")
                if passive == "on":
                    p = {}
                    p['title'] = "Local Passive Collection"
                    p['type'] = COMMAND
                    p['command'] = 'python2.7 /data/template_parser.py passive '+action
                    modes.append(p)
            except:
                pass
            try:
                active = config.get("local-collection", "active")
                if active == "on":
                    p = {}
                    p['title'] = "Local Active Collection"
                    p['type'] = COMMAND
                    p['command'] = 'python2.7 /data/template_parser.py active '+action
                    modes.append(p)
            except:
                pass
        except:
            pass
        if len(modes) > 1:
            p = {}
            p['title'] = "All"
            p['type'] = COMMAND
            p['command'] = 'python2.7 /data/template_parser.py all '+action
            modes.append(p)
    except:
        print "unable to get the configuration of modes from the templates.\n"

    # make sure that vent-management is running
    result = check_output('/bin/sh /data/bootlocal.sh'.split())
    print result

    return modes

def update_plugins():
    modes = []
    try:
        config = ConfigParser.RawConfigParser()
        config.read(template_dir+'modes.template')
        plugin_array = config.options("plugins")
        plugins = {}
        for plug in plugin_array:
            plugins[plug] = config.get("plugins", plug)

        for plugin in plugins:
            p = {}
            try:
                config = ConfigParser.RawConfigParser()
                config.read(template_dir+plugin+'.template')
                plugin_name = config.get("info", "name")
                p['title'] = plugin_name
                p['type'] = MENU
                p['subtitle'] = 'Please select a tool to configure...'
                p['options'] = []
                if plugin == 'core':
                    tools = [ name for name in os.listdir("/var/lib/docker/data/"+plugin) if os.path.isdir(os.path.join('/var/lib/docker/data/'+plugin, name)) ]
                    for tool in tools:
                        t = {}
                        t['title'] = tool
                        t['type'] = SETTING
                        t['command'] = ''
                        p['options'].append(t)
                elif plugins[plugin] == 'all':
                    tools = [ name for name in os.listdir(plugins_dir+plugin) if os.path.isdir(os.path.join(plugins_dir+plugin, name)) ]
                    for tool in tools:
                        t = {}
                        t['title'] = tool
                        t['type'] = SETTING
                        t['command'] = ''
                        p['options'].append(t)
                else:
                    for tool in plugins[plugin].split(","):
                        t = {}
                        t['title'] = tool
                        t['type'] = SETTING
                        t['command'] = ''
                        p['options'].append(t)
                modes.append(p)
            except:
                # if no name is provided, it doesn't get listed
                pass
    except:
        print "unable to get the configuration of modes from the templates.\n"
    return modes

def build_menu():
    modes = []
    # TODO
    return

def get_param(prompt_string):
     curses.echo()
     screen.clear()
     screen.border(0)
     screen.addstr(2, 2, prompt_string)
     screen.refresh()
     input = screen.getstr(10, 10, 150)
     curses.noecho()
     return input

def runmenu(menu, parent):
    if parent is None:
        lastoption = "Exit"
    else:
        lastoption = "Return to %s menu" % parent['title']

    optioncount = len(menu['options'])

    pos=0
    oldpos=None
    x = None

    while x != ord('\n'):
        if pos != oldpos:
            oldpos = pos
            screen.border(0)
            screen.addstr(2,2, menu['title'], curses.A_STANDOUT)
            screen.addstr(4,2, menu['subtitle'], curses.A_BOLD)

            for index in range(optioncount):
                textstyle = n
                if pos==index:
                    textstyle = h
                if menu['options'][index]['type'] == INFO:
                    if "|" in menu['options'][index]['command']:
                        cmds = menu['options'][index]['command'].split("|")
                        i = 0
                        while i < len(cmds):
                            c = cmds[i].split()
                            if i == 0:
                                cmd = Popen(c, stdout=PIPE)
                            elif i == len(cmds)-1:
                                result = check_output(c, stdin=cmd.stdout)
                                cmd.wait()
                            else:
                                cmd = Popen(c, stdin=cmd.stdout, stdout=PIPE)
                                cmd.wait()
                            i += 1
                    else:
                        result = check_output((menu['options'][index]['command']).split())
                    screen.addstr(5+index,4, "%s - %s" % (menu['options'][index]['title'], result), textstyle)
                elif menu['options'][index]['type'] == INFO2:
                    screen.addstr(5+index,4, "%s" % (menu['options'][index]['title']), textstyle)
                else:
                    screen.addstr(5+index,4, "%d - %s" % (index+1, menu['options'][index]['title']), textstyle)
            textstyle = n
            if pos==optioncount:
                textstyle = h
            screen.addstr(6+optioncount,4, "%d - %s" % (optioncount+1, lastoption), textstyle)
            screen.refresh()

        x = screen.getch()

        if x == 258: # down arrow
            if pos < optioncount:
                pos += 1
            else:
                pos = 0
        elif x == 259: # up arrow
            if pos > 0:
                pos += -1
            else:
                pos = optioncount
        elif x >= ord('1') and x <= ord(str(optioncount+1)):
            pos = x - ord('0') - 1
    return pos

def processmenu(menu, parent=None):
    optioncount = len(menu['options'])
    exitmenu = False
    while not exitmenu:
        getin = runmenu(menu, parent)
        if getin == optioncount:
            exitmenu = True
        elif menu['options'][getin]['type'] == COMMAND or menu['options'][getin]['type'] == INFO2:
            curses.def_prog_mode()
            os.system('reset')
            screen.clear()
            os.system(menu['options'][getin]['command'])
            screen.clear()
            curses.reset_prog_mode()
            curses.curs_set(1)
            curses.curs_set(0)
        # !! TODO
        elif menu['options'][getin]['type'] == INFO:
            pass
        # !! TODO
        elif menu['options'][getin]['type'] == SETTING:
            curses.def_prog_mode()
            os.system('reset')
            screen.clear()
            os.system(menu['options'][getin]['command'])
            screen.clear()
            curses.reset_prog_mode()
            curses.curs_set(1)
            curses.curs_set(0)
        elif menu['options'][getin]['type'] == INPUT:
            if menu['options'][getin]['title'] == "Add Plugins":
                plugin_url = get_param("Enter the HTTPS Git URL that contains the new plugins, e.g. https://github.com/CyberReboot/vent-network-plugins.git")
                curses.def_prog_mode()
                os.system('reset')
                screen.clear()
                os.system("python2.7 /data/plugin_parser.py add_plugins "+plugin_url)
                screen.clear()
                os.execl(sys.executable, sys.executable, *sys.argv)
            elif menu['options'][getin]['title'] == "Remove Plugins":
                plugin_url = get_param("Enter the HTTPS Git URL that contains the plugins you'd like to remove, e.g. https://github.com/CyberReboot/vent-network-plugins.git")
                curses.def_prog_mode()
                os.system('reset')
                screen.clear()
                os.system("python2.7 /data/plugin_parser.py remove_plugins "+plugin_url)
                screen.clear()
                os.execl(sys.executable, sys.executable, *sys.argv)
        elif menu['options'][getin]['type'] == MENU:
            screen.clear()
            processmenu(menu['options'][getin], menu)
            screen.clear()
        elif menu['options'][getin]['type'] == EXITMENU:
            exitmenu = True

def build_menu_dict():
    menu_data = {
      'title': "Vent", 'type': MENU, 'subtitle': "Please select an option...",
      'options':[
        { 'title': "Mode", 'type': MENU, 'subtitle': 'Please select an option...',
          'options': [
            { 'title': "Start", 'type': MENU, 'subtitle': '',
              'options': run_plugins("start")
            },
            { 'title': "Stop", 'type': MENU, 'subtitle': '',
              'options': run_plugins("stop")
            },
            { 'title': "Clean (Stop and Remove Containers)", 'type': MENU, 'subtitle': '',
              'options': run_plugins("clean")
            },
            { 'title': "Status", 'type': MENU, 'subtitle': '',
              'options': run_plugins("status")
            },
            { 'title': "Configure", 'type': MENU, 'subtitle': '',
              'options': update_plugins()
            }
          ]
        },
        { 'title': "Plugins", 'type': MENU, 'subtitle': 'Please select an option...',
          'options': [
            { 'title': "Add Plugins", 'type': INPUT, 'command': '' },
            { 'title': "Remove Plugins", 'type': INPUT, 'command': '' },
            { 'title': "Show Installed Plugins", 'type': INPUT, 'command': '' },
            { 'title': "Update Plugins", 'type': INPUT, 'command': '' },
          ]
        },
        { 'title': "System Info", 'type': MENU, 'subtitle': '',
          'options': [
            #{ 'title': "Visualization Endpoint Status", 'type': INFO, 'command': '/bin/sh /var/lib/docker/data/visualization/get_url.sh' },
            { 'title': "RabbitMQ Management Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py aaa-rabbitmq mgmt' },
            { 'title': "RQ Dashboard Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py rq-dashboard mgmt' },
            { 'title': "Elasticsearch Head Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py elasticsearch head' },
            { 'title': "Elasticsearch Marvel Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py elasticsearch marvel' },
            { 'title': "Containers Running", 'type': INFO, 'command': 'docker ps | sed 1d | wc -l' },
            { 'title': "Container Stats", 'type': INFO2, 'command': "docker ps | awk '{print $NF}' | grep -v NAMES | xargs docker stats" },
            { 'title': "Uptime", 'type': INFO, 'command': 'uptime' },
          ]
        },
        { 'title': "Build", 'type': MENU, 'subtitle': '',
          'options': [
            { 'title': "Build new plugins and core", 'type': COMMAND, 'command': '/bin/sh /data/build_images.sh' },
            { 'title': "Force rebuild all plugins and core", 'type': COMMAND, 'command': '/bin/sh /data/build_images.sh --no-cache' },
          ]
        },
        { 'title': "Help", 'type': COMMAND, 'command': 'less /data/help' },
        { 'title': "Shell Access", 'type': COMMAND, 'command': 'cat /etc/motd; /bin/sh /etc/profile.d/boot2docker.sh; /bin/sh' },
        { 'title': "Reboot", 'type': COMMAND, 'command': 'sudo reboot' },
        { 'title': "Shutdown", 'type': COMMAND, 'command': 'sudo shutdown -h now' },
      ]
    }
    return menu_data

def main():
    menu_data = build_menu_dict()
    processmenu(menu_data)
    curses.endwin()
    os.system('clear')

if __name__ == "__main__":
    # make sure that vent-management is running
    result = check_output('/bin/sh /data/bootlocal.sh'.split())
    print result
    main()
