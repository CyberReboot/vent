#!/usr/bin/env python2.7

try:
    # python2
    import ConfigParser
except ImportError:
    # python3
    import configparser as ConfigParser

import ast
import curses
import os
import sys
import termios
import tty

from subprocess import call, check_output, CalledProcessError, PIPE, Popen
from helpers.paths import PathDirs

try:
    screen = curses.initscr()
    screen.keypad(1)
    curses.noecho()
    h = curses.A_BOLD
    n = curses.A_NORMAL
    # Check if terminal can support color
    if curses.has_colors(): # pragma: no cover
        curses.start_color()
        curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE)
        h = curses.color_pair(1)
except Exception as e: # pragma: no cover
    pass

# Curses Menu Types #

# menu indicates a type that expands to another menu.
# exitmenu is the type that returns to previous menu.
MENU = "menu"
EXITMENU = "exitmenu"

# command runs a simple command without user confirmation on selection.
# the command is in the 'command' index of the dictionary and runs on user selection.
COMMAND = "command"

# confirm is the same as command, however it waits for user confirmation before clearing results.
CONFIRM = "confirm"

# prompt is the same as command, however it waits for user confirmation prior to running.
PROMPT = "prompt"

# input is similar to confirm, but it requires manual user input prior to running.
INPUT = "input"

# display shows processed results on menu load but it does not use the 'command' index.
# this is because results of the display type require heavier processing.
DISPLAY = "display"

# info shows command results inline in menu without user confirmation.
# it does this by running the command stored in the 'command' index on menu load.
INFO = "info"

def get_container_menu(path_dirs):
    """get a list of containers, returns a menu with containers as options"""
    p = {}
    try:
        p['type'] = MENU
        command1 = "if [ ! -d /tmp/vent_logs ]; then mkdir /tmp/vent_logs; fi; "
        command2 = "python2.7 "+path_dirs.info_dir+"get_logs.py -c "
        command3 = " | tee /tmp/vent_logs/vent_container_"
        p['title'] = 'Service Logs'
        p['subtitle'] = 'Please select a service:'
        containers = check_output("/bin/sh "+path_dirs.info_dir+"get_info.sh installed containers | grep -v NAMES | grep -v Built\ Containers | grep -v Dead | awk \"{print \$1}\"", shell=True).split("\n")
        containers = filter(None, containers)
        if containers:
            p['options'] = [ {'title': name, 'type': COMMAND, 'command': '' } for name in containers ]
            for d in p['options']:
                d['command'] = command1+command2+d['title']+command3+d['title']+".log | less"
        else:
            p['options'] = [ {'title': "There are no services to show logs for.", 'type': DISPLAY, 'command': ''} ]
    except Exception as e: # pragma: no cover
        pass
    return p

def get_namespace_menu(path_dirs):
    """get a list of namespaces, returns a menu with namespaces as options"""
    p = {}
    try:
        p['type'] = MENU
        command1 = "if [ ! -d /tmp/vent_logs ]; then mkdir /tmp/vent_logs;fi; "
        command2 = "python2.7 "+path_dirs.info_dir+"get_logs.py -n "
        command3 = " | tee /tmp/vent_logs/vent_namespace_"
        p['title'] = 'Namespace Logs'
        p['subtitle'] = 'Please select a namespace:'
        namespaces = check_output("/bin/sh "+path_dirs.info_dir+"get_info.sh installed images | grep / | cut -f1 -d\"/\" | sort | uniq", shell=True).split("\n")
        namespaces = filter(None, namespaces)
        if namespaces:
            p['options'] = [ {'title': name, 'type': COMMAND, 'command': '' } for name in namespaces ]
            for d in p['options']:
                d['command'] = command1+command2+d['title']+command3+d['title']+".log | less"
        else:
            p['options'] = [ {'title': "There are no namespaces to show logs for.", 'type': DISPLAY, 'command': ''} ]
    except Exception as e: # pragma: no cover
        pass
    return p


# Allows for acceptance of single char before terminating
def getch():
    try:
        fd = sys.stdin.fileno()
        settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, settings)
        return ch
    except Exception as e: # pragma: no cover
        pass

def confirm():
    """wait for user input before clearing stdout"""
    os.system("echo")
    os.system("echo")
    os.system("echo ----------------------------")
    os.system("echo Operation complete. Press any key to continue...")
    while getch():
        break
        
def prompt():
    """wait for user confimation"""
    os.system('echo "Do you want to continue [Y/n]?"')
    char = getch()
    if char == "Y":
        return True
    else:
        return False

def get_plugin_status(path_dirs):
    """ Displays status of all running, not running/built, not built, and disabled plugins """
    p = {}
    try:
        ### Get Plugin Statuses ###
        status = {}
        running = []
        nrbuilt = []
        built = []
        disabled_containers = []
        disabled_images = []
        notbuilt = []
        running_errors = []
        nr_errors = []
        built_errors = []
        external = {}

        try:
            status = ast.literal_eval(check_output("python2.7 "+path_dirs.info_dir+'get_status.py all --base_dir '+path_dirs.base_dir, shell=True))
            running = status['Running']
            nrbuilt = status['Not Running']
            built = status['Built']
            disabled_containers = status['Disabled Containers']
            disabled_images = status['Disabled Images']
            notbuilt = status['Not Built']
            external = status['External']
            running_errors = status['Running Errors']
            nr_errors = status['Not Running Errors']
            built_errors = status['Built Errors']
        except Exception as e: # pragma: no cover
            with open('/tmp/error.log', 'a+') as myfile:
                myfile.write("Error - menu_launcher.py: Unable to get plugin status")

        ### Prepare Statuses for MENU ###
        p_running = [ {'title': x, 'type': DISPLAY, 'command': ''} for x in running ]
        p_nrbuilt = [ {'title': x, 'type': DISPLAY, 'command': ''} for x in nrbuilt ]
        p_disabled_cont = [ {'title': x, 'type': DISPLAY, 'command': ''} for x in disabled_containers ]
        p_disabled_images = [ {'title': x, 'type': DISPLAY, 'command': ''} for x in disabled_images ]
        p_built = [ {'title': x, 'type': DISPLAY, 'command': ''} for x in built ]
        p_notbuilt = [ {'title': x, 'type': DISPLAY, 'command': ''} for x in notbuilt ]
        # format for title is: 'elasticsearch @ 0.0.0.0'
        p_external = [ {'title': x+' @ '+external[x], 'type': DISPLAY, 'command': ''} for x in external ]

        ### Prepare Errors for MENU ###
        p_running_errors = [ {'title': x, 'type': DISPLAY, 'command': ''} for x in running_errors ]
        p_nr_errors = [ {'title': x, 'type': DISPLAY, 'command': ''} for x in nr_errors ]
        p_built_errors = [ {'title': x, 'type': DISPLAY, 'command': ''} for x in built_errors ]

        # Only add to p_error_menu if errors exist for that section
        p_error_menu = []
        if len(running_errors) > 0:
            p_error_menu.append({'title': "Running Errors", 'subtitle': "Services that should not be running because they are disabled...", 'type': MENU, 'options': p_running_errors})
        if len(nr_errors) > 0:
            p_error_menu.append({'title': "Not Running Errors", 'subtitle': "Services that should be removed because they are disabled...", 'type': MENU, 'options': p_nr_errors})
        if len(built_errors) > 0:
            p_error_menu.append({'title': "Built Errors", 'subtitle': "Images that should not be built because they are disabled...", 'type': MENU, 'options': p_built_errors})

        # If there is nothing populating a menu, notify the user.
        for menu in [p_running, p_nrbuilt, p_disabled_cont, p_disabled_images, p_built, p_notbuilt, p_external, p_error_menu]:
            if len(menu) == 0:
                if menu == p_running:
                    menu.append({'title': 'There are no services running.', 'type': DISPLAY, 'command': ''})
                elif menu == p_nrbuilt:
                    menu.append({'title': 'There are no services that are not running.', 'type': DISPLAY, 'command': ''})
                elif menu == p_disabled_cont:
                    menu.append({'title': 'There are no services that are disabled.', 'type': DISPLAY, 'command': ''})
                elif menu == p_disabled_images:
                    menu.append({'title': 'There are no images that are disabled.', 'type': DISPLAY, 'command': ''})
                elif menu == p_built:
                    menu.append({'title': 'There are no built images.', 'type': DISPLAY, 'command': ''})
                elif menu == p_notbuilt:
                    menu.append({'title': 'There are no unbuilt images.', 'type': DISPLAY, 'command': ''})
                elif menu == p_external:
                    menu.append({'title': 'There are no services set to run externally.', 'type': DISPLAY, 'command': ''})
                elif menu == p_error_menu:
                    menu.append({'title': 'There are no service/image errors.', 'type': DISPLAY, 'command': ''})

        ### Returned Menu Dictionary
        p['title'] = 'Plugin Status'
        p['subtitle'] = 'Please select a status to view:'
        p['options'] = [
                         { 'title': "Running Services", 'subtitle': "Currently running services...", 'type': MENU, 'options': p_running },
                         { 'title': "Not Running Services", 'subtitle': "Built but not currently running services...", 'type': MENU, 'options': p_nrbuilt },
                         { 'title': "Disabled Services", 'subtitle': "Currently disabled services; check the \'External\' menu...", 'type': MENU, 'options': p_disabled_cont },
                         { 'title': "Disabled Images", 'subtitle': "Currently disabled images; check the \'External\' menu...", 'type': MENU, 'options': p_disabled_images },
                         { 'title': "Built Images", 'subtitle': "Currently built images...", 'type': MENU, 'options': p_built },
                         { 'title': "Not Built Images", 'subtitle': "Currently not built (do not have images)...", 'type': MENU, 'options': p_notbuilt },
                         { 'title': "External", 'subtitle': "Current services and images set to run externally...", 'type': MENU, 'options': p_external },
                         { 'title': "Errors", 'subtitle': "Please select a runtime error option to view:", 'type': MENU, 'options': p_error_menu }
                        ]
    except Exception as e: # pragma: no cover
        pass

    return p

def get_installed_plugin_repos(path_dirs, m_type, command):
    """ Returns a dictionary of all installed plugin repos; e.g - vent-network """
    p = {}
    try:
        p['type'] = MENU
        if command=="remove":
            command1 = "python2.7 "+path_dirs.data_dir+"plugin_parser.py remove_plugins "
            p['title'] = 'Remove Plugins'
            p['subtitle'] = 'Please select a plugin to remove:'
            plugins = [ name for name in os.listdir(path_dirs.plugin_repos) if os.path.isdir(os.path.join(path_dirs.plugin_repos, name)) ]
            if plugins:
                p['options'] = [ {'title': name, 'type': m_type, 'command': '' } for name in plugins ]
                for d in p['options']:
                    with open(path_dirs.plugin_repos+"/"+d['title']+"/.git/config", "r") as myfile:
                        repo_name = ""
                        while not "url" in repo_name:
                            repo_name = myfile.readline()
                        repo_name = repo_name.split("url = ")[-1]
                        d['command'] = command1+repo_name+" "+path_dirs.base_dir+" "+path_dirs.data_dir
            else:
                p['options'] = [ {'title': 'You have no installed plugins to remove.', 'type': DISPLAY, 'command': ''} ]
        elif command=="update":
            command1 = "python2.7 "+path_dirs.data_dir+"plugin_parser.py update_plugins "
            p['title'] = 'Update Plugins'
            p['subtitle'] = 'Please select a plugin to update:'
            plugins = [ name for name in os.listdir(path_dirs.plugin_repos) if os.path.isdir(os.path.join(path_dirs.plugin_repos, name)) ]
            if plugins:
                p['options'] = [ {'title': name, 'type': m_type, 'command': '' } for name in plugins ]
                for d in p['options']:
                    with open(path_dirs.plugin_repos+"/"+d['title']+"/.git/config", "r") as myfile:
                        repo_name = ""
                        while not "url" in repo_name:
                            repo_name = myfile.readline()
                        repo_name = repo_name.split("url = ")[-1]
                        d['command'] = command1+repo_name+" "+path_dirs.base_dir+" "+path_dirs.data_dir
            else:
                p['options'] = [ {'title': 'You have no installed plugins to update.', 'type': DISPLAY, 'command': ''} ]
        else:
            p['title'] = 'Installed Plugins'
            p['subtitle'] = 'Installed Plugins...'
            plugins = [ name for name in os.listdir(path_dirs.plugin_repos) if os.path.isdir(os.path.join(path_dirs.plugin_repos, name)) ]
            if plugins:
                p['options'] = [ {'title': name, 'type': m_type, 'command': '' } for name in plugins ]
            else:
                p['options'] = [ {'title': 'You have no plugins installed.', 'type': DISPLAY, 'command': ''} ]
    except Exception as e: # pragma: no cover
        pass

    return p

def run_plugins(path_dirs, action):
    """creates menu to start plugin containers"""
    modes = []
    try:
        config = ConfigParser.RawConfigParser()
        # needed to preserve case sensitive options
        config.optionxform=str
        config.read(path_dirs.template_dir+'modes.template')
        plugin_array = config.options("plugins")
        plugins = {}
        for plug in plugin_array:
            plugins[plug] = config.get("plugins", plug)

        # Set Defaults
        cores = 0
        all_colls = 0
        passive_colls = 0
        active_colls = 0
        vis = 0
        try:
            # get number of installed cores
            cores = len(ast.literal_eval(check_output("python2.7 "+path_dirs.info_dir+'get_status.py cores --base_dir '+path_dirs.base_dir, shell=True)))

            # get number of installed collectors
            all_colls = len(ast.literal_eval(check_output("python2.7 "+path_dirs.info_dir+'get_status.py collectors --all --base_dir '+path_dirs.base_dir, shell=True)))
            passive_colls = len(ast.literal_eval(check_output("python2.7 "+path_dirs.info_dir+'get_status.py collectors --passive --base_dir '+path_dirs.base_dir, shell=True)))
            active_colls = len(ast.literal_eval(check_output("python2.7 "+path_dirs.info_dir+'get_status.py collectors --active --base_dir '+path_dirs.base_dir, shell=True)))

            # get number of installed visualizations
            vis = len(ast.literal_eval(check_output("python2.7 "+path_dirs.info_dir+'get_status.py vis --base_dir '+path_dirs.base_dir, shell=True)))
        except Exception as e: # pragma: no cover
            with open('/tmp/error.log', 'a+') as myfile:
                myfile.write("Unable to get installed cores/collectors/vis.")

        for plugin in plugins:
            # check if plugin is core or vis and the corresponding size is greater than 0
            if (plugin, cores > 0) == ("core", True) or (plugin, vis > 0) == ("visualization", True):
                p = {}
                try:
                    config = ConfigParser.RawConfigParser()
                    # needed to preserve case sensitive options
                    config.optionxform=str
                    config.read(path_dirs.template_dir+plugin+'.template')
                    plugin_name = config.get("info", "name")
                    p['title'] = plugin_name
                    p['type'] = CONFIRM
                    p['command'] = 'python2.7 '+path_dirs.data_dir+'template_parser.py '+plugin+' '+action
                    modes.append(p)
                except Exception as e: # pragma: no cover
                    # if no name is provided, it doesn't get listed
                    pass
        try:
            config = ConfigParser.RawConfigParser()
            # needed to preserve case sensitive options
            config.optionxform=str
            config.read(path_dirs.template_dir+'core.template')
            # check if we have any passive collectors to handle
            if passive_colls > 0:
                try:
                    passive = config.get("local-collection", "passive")
                    if passive == "on":
                        p = {}
                        p['title'] = "Local Passive Collection"
                        p['type'] = CONFIRM
                        p['command'] = 'python2.7 '+path_dirs.data_dir+'template_parser.py passive '+action
                        modes.append(p)
                except Exception as e:
                    pass
            # check if we have any active collectors to handle
            if active_colls > 0:
                try:
                    active = config.get("local-collection", "active")
                    if active == "on":
                        p = {}
                        p['title'] = "Local Active Collection"
                        p['type'] = CONFIRM
                        p['command'] = 'python2.7 '+path_dirs.data_dir+'template_parser.py active '+action
                        modes.append(p)
                except Exception as e:
                    pass
        except Exception as e: # pragma: no cover
            pass
        if len(modes) > 1:
            p = {}
            p['title'] = "All"
            p['type'] = CONFIRM
            p['command'] = 'python2.7 '+path_dirs.data_dir+'template_parser.py all '+action
            modes.append(p)
        elif len(modes) == 0:
            p = {'title': "You have no services to "+action+".", 'type': DISPLAY, 'command': ''}
            modes.append(p)
    except Exception as e:
        print("unable to get the configuration of modes from the templates.\n")

    # make sure that vent-management is running
    try:
        result = check_output('/bin/sh '+path_dirs.scripts_dir+'bootlocal.sh').split()
        print(result)
    except Exception as e:
        pass

    return modes

def visualizations(path_dirs):
    """adds visualizations endpoints to the menu"""
    modes = []
    try:
        results = check_output(path_dirs.info_dir+'get_visualization.sh').split("\n")
        for result in results:
            if result != "":
                p = {}
                p['title'] = result
                p['type'] = DISPLAY
                p['command'] = ''
                modes.append(p)
    except Exception as e:
        pass
    if len(modes) == 0:
        p = {'title': "You have no visualizations installed", 'type': DISPLAY, 'command': ''}
        modes.append(p)
    return modes

def update_plugins(path_dirs):
    """adds the plugins that can be updated to the menu"""
    modes = []
    try:
        for f in os.listdir(path_dirs.template_dir):
            if f.endswith(".template"):
                p = {}
                p['title'] = f
                p['type'] = COMMAND
                p['command'] = 'python2.7 '+path_dirs.vendor_dir+'suplemon/suplemon.py '+path_dirs.template_dir+f
                modes.append(p)
    except Exception as e:
        print("unable to get the configuration templates.\n")
    return modes

def get_param(prompt_string):
    """prompts user for input from keyboard, returns that input"""
    curses.echo()
    screen.clear()
    screen.border(0)
    screen.addstr(2, 2, prompt_string)
    screen.refresh()
    input = screen.getstr(10, 10, 150)
    curses.noecho()
    return input

def runmenu(menu, parent):
    """process menu options"""
    if parent is None:
        lastoption = "Exit"
    else:
        menu_name = parent['title']
        if "-" in menu_name:
            menu_name = menu_name.split("-")[0].strip()
        lastoption = "Return to {0!s} menu".format(menu_name)

    # last value on the screen by position
    optioncount = len(menu['options'])
    entries = []
    # get all valid entries (interactive entries)
    for index in range(optioncount):
        if menu['options'][index]['type'] not in [INFO, DISPLAY]:
            # append relative position of entry amongst entries
            entries.append(index)
    # add last option
    entries.append(optioncount)

    # set initial position to first valid entry
    pos = 0
    if entries:
        pos = entries[0]
    oldpos = None
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
                    # run piped commands individually else run single command
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
                    screen.addstr(5+index,4, "{0!s} - {1!s}".format(menu['options'][index]['title'], result), textstyle)
                elif menu['options'][index]['type'] == DISPLAY:
                    screen.addstr(5+index,4, "{0!s}".format(menu['options'][index]['title']), textstyle)
                else: # COMMAND, CONFIRM, INPUT, MENU
                    number = entries.index(index)
                    screen.addstr(5+index,4, "{0:d} - {1!s}".format(number+1, menu['options'][index]['title']), textstyle)
            textstyle = n
            if pos==optioncount:
                textstyle = h
            #
            number = entries.index(optioncount)
            screen.addstr(6+optioncount,4, "{0:d} - {1!s}".format(number+1, lastoption), textstyle)
            screen.refresh()

        x = screen.getch()

        # !! TODO hack for now, long term should probably take multiple character numbers and update on return
        num_options = len(entries)
        if len(entries) > 9:
            num_options = 9

        if x == 258: # down arrow
            # check that we aren't navigating through an empty menu or menu with no interactive items
            if entries:
                # check pos isn't at end of interactive entries
                if pos < entries[-1]:
                    # find current index and increment
                    pos = entries.index(pos)+1
                else:
                    pos = entries[0]
        elif x == 259: # up arrow
            # check that we aren't navigating through an empty menu or menu with no interactive items
            if entries:
                # check pos isn't at beginning of interactive entries
                if pos > entries[0]:
                    # find current index and decrement
                    pos = entries.index(pos)-1
                else:
                    pos = entries[-1]
        elif x == 27: # escape
            pos = entries[-1]
        elif ord('1') <= x <= ord(str(num_options)): # other typed input
            # calculate number to traverse to, get entries position
            pos = entries[x - ord('0') - 1]
    return pos

def processmenu(path_dirs, menu, parent=None):
    """ processes the execution of the interaction sent to the menu """
    optioncount = len(menu['options'])
    exitmenu = False
    while not exitmenu:
        getin = runmenu(menu, parent)
        if getin == optioncount:
            exitmenu = True
        elif menu['options'][getin]['type'] in [PROMPT]:
            curses.def_prog_mode()
            os.system('reset')
            screen.clear()
            if prompt():
                os.system(menu['options'][getin]['command'])

            screen.clear()
            curses.reset_prog_mode()
            try:
                curses.curs_set(1)
                curses.curs_set(0)
            except Exception as e:
                pass
        elif menu['options'][getin]['type'] in [COMMAND, CONFIRM]:
            curses.def_prog_mode()
            os.system('reset')
            screen.clear()
            os.system(menu['options'][getin]['command'])

            if menu['options'][getin]['type'] == CONFIRM:
                if menu['title'] == "Remove Plugins":
                    exitmenu = True
                confirm()

            screen.clear()
            curses.reset_prog_mode()
            try:
                curses.curs_set(1)
                curses.curs_set(0)
            except Exception as e:
                pass
        elif menu['options'][getin]['type'] in [INFO, DISPLAY]:
            pass
        elif menu['options'][getin]['type'] == INPUT:
            if menu['options'][getin]['title'] == "Add Plugins":
                plugin_url = get_param("Enter the HTTPS Git URL that contains the new plugins, e.g. https://github.com/CyberReboot/vent-plugins.git:")
                curses.def_prog_mode()
                os.system('reset')
                screen.clear()
                if not "https://" in plugin_url:
                    os.system("echo No plugins added, url is not formatted correctly.")
                    os.system("echo Please use a git url, e.g. https://github.com/CyberReboot/vent-plugins.git")
                else:
                    os.system("python2.7 "+path_dirs.data_dir+"plugin_parser.py add_plugins "+plugin_url+" "+path_dirs.base_dir+" "+path_dirs.data_dir)
                confirm()
                screen.clear()
                os.execl(sys.executable, sys.executable, *sys.argv)
            elif menu['options'][getin]['title'] == "Files":
                filename = get_param("Enter the name of the processed file to lookup logs for:")
                curses.def_prog_mode()
                os.system('reset')
                os.system("clear")
                screen.clear()
                try:
                    # ensure directory exists
                    os.system("if [ ! -d /tmp/vent_logs ]; then mkdir /tmp/vent_logs; fi;")
                    # check logs exist for that file
                    found = call("python2.7 "+path_dirs.info_dir+"get_logs.py -f "+filename+" | grep "+filename, shell=True)
                    if found == 0:
                        # print logs
                        os.system("python2.7 "+path_dirs.info_dir+"get_logs.py -f "+filename+" | tee /tmp/vent_logs/vent_file_"+filename+" | less")
                    else:
                        os.system("echo \"No logs found for that file.\" | less")
                except Exception as e:
                    os.system("echo \"Error retrieving logs for that file.\" | less")
                screen.clear()
                curses.reset_prog_mode()
                try:
                    curses.curs_set(1)
                    curses.curs_set(0)
                except Exception as e:
                    pass
        elif menu['options'][getin]['type'] == MENU:
            if menu['options'][getin]['title'] == "Remove Plugins":
                screen.clear()
                installed_plugins = get_installed_plugin_repos(path_dirs, CONFIRM, "remove")
                processmenu(path_dirs, installed_plugins, menu)
                screen.clear()
            elif menu['options'][getin]['title'] == "Show Installed Plugins":
                screen.clear()
                installed_plugins = get_installed_plugin_repos(path_dirs, DISPLAY, "")
                processmenu(path_dirs, installed_plugins, menu)
                screen.clear()
            elif menu['options'][getin]['title'] == "Update Plugins":
                screen.clear()
                installed_plugins = get_installed_plugin_repos(path_dirs, CONFIRM, "update")
                processmenu(path_dirs, installed_plugins, menu)
                screen.clear()
            elif menu['options'][getin]['title'] == "Status":
                screen.clear()
                plugins = get_plugin_status(path_dirs)
                processmenu(path_dirs, plugins, menu)
                screen.clear()
            elif menu['options'][getin]['title'] == "Services":
                screen.clear()
                containers = get_container_menu(path_dirs)
                processmenu(path_dirs, containers, menu)
                screen.clear()
            elif menu['options'][getin]['title'] == "Namespaces":
                screen.clear()
                namespaces = get_namespace_menu(path_dirs)
                processmenu(path_dirs, namespaces, menu)
                screen.clear()
            else:
                screen.clear()
                processmenu(path_dirs, menu['options'][getin], menu)
                screen.clear()
        elif menu['options'][getin]['type'] == EXITMENU:
            exitmenu = True

def build_menu_dict(path_dirs):
    """ builds the menu dictionary that gets populated in curses """
    v_version = ""
    try:
        with open(path_dirs.data_dir+"VERSION", 'r') as f:
            v_version = f.readline()
    except Exception as e:
        pass
    menu_data = {
      'title': "Vent - "+v_version, 'type': MENU, 'subtitle': "Please select an option:",
      'options':[
        { 'title': "Mode", 'type': MENU, 'subtitle': 'Please select an option:',
          'options': [
            { 'title': "Start", 'type': MENU, 'subtitle': 'Choose a set of services to start:',
              'options': run_plugins(path_dirs, "start")
            },
            { 'title': "Stop", 'type': MENU, 'subtitle': 'Choose a set of services to stop:',
              'options': run_plugins(path_dirs, "stop")
            },
            { 'title': "Clean (Stop and Remove Services)", 'type': MENU, 'subtitle': 'Choose a set of services to clean:',
              'options': run_plugins(path_dirs, "clean")
            },
            { 'title': "Status", 'type': MENU, 'subtitle': '',
              'command': ''
            },
            { 'title': "Configure", 'type': MENU, 'subtitle': 'Choose a template to configure:',
              'options': update_plugins(path_dirs)
            }
          ]
        },
        { 'title': "Plugins", 'type': MENU, 'subtitle': 'Please select an option:',
          'options': [
            { 'title': "Add Plugins", 'type': INPUT, 'command': '' },
            { 'title': "Remove Plugins", 'type': MENU, 'command': '' },
            { 'title': "Show Installed Plugins", 'type': MENU, 'command': '' },
            { 'title': "Update Plugins", 'type': MENU, 'command': '' },
          ]
        },
        { 'title': "System Info", 'type': MENU, 'subtitle': 'Some core service statuses...',
          'options': [
            { 'title': "RabbitMQ Management Status", 'type': INFO, 'command': 'python2.7 '+path_dirs.scripts_dir+'service_urls/get_urls.py aaa-rabbitmq mgmt' },
            { 'title': "RQ Dashboard Status", 'type': INFO, 'command': 'python2.7 '+path_dirs.scripts_dir+'service_urls/get_urls.py rq-dashboard mgmt' },
            { 'title': "Elasticsearch Head Status", 'type': INFO, 'command': 'python2.7 '+path_dirs.scripts_dir+'service_urls/get_urls.py elasticsearch head' },
            { 'title': "Containers Running", 'type': INFO, 'command': 'docker ps | sed 1d | wc -l' },
            { 'title': "Uptime", 'type': INFO, 'command': 'uptime' }
          ]
        },
        { 'title': "Build", 'type': MENU, 'subtitle': 'Please select a service group to build:',
          'options': [
            { 'title': "Build new plugins and core", 'type': CONFIRM, 'command': '/bin/sh '+path_dirs.scripts_dir+'build_images.sh --basedir '+path_dirs.base_dir[:-1] },
            { 'title': "Force rebuild all plugins and core", 'type': CONFIRM, 'command': '/bin/sh '+path_dirs.scripts_dir+'build_images.sh --basedir '+path_dirs.base_dir[:-1]+' --no-cache' },
          ]
        },
        { 'title': "System Commands", 'type': MENU, 'subtitle': 'Please select an option:',
            'options': [
                { 'title': "Logs", 'type': MENU, 'subtitle': 'Please select a group to view logs for:', 'command': '',
                    'options': [
                        {'title': "Services", 'type': MENU, 'subtitle': '', 'command': ''},
                        {'title': "Namespaces", 'type': MENU, 'subtitle': '', 'command': ''},
                        {'title': "Files", 'type': INPUT, 'command': ''},
                        {'title': "All", 'type': COMMAND, 'command': 'if [ ! -d /tmp/vent_logs ]; then mkdir /tmp/vent_logs; fi; python2.7 '+path_dirs.info_dir+'get_logs.py -a | tee /tmp/vent_logs/vent_all.log | less'},
                    ]
                },
                { 'title': "Service Stats", 'type': COMMAND, 'command': "sh "+path_dirs.info_dir+"get_stats.sh -r" },
                { 'title': "Shell Access", 'type': COMMAND, 'command': 'cat /etc/motd; cat /vent/VERSION; /bin/sh' },
                { 'title': "Reboot", 'type': PROMPT, 'command': 'sudo reboot' },
                { 'title': "Shutdown", 'type': PROMPT, 'command': 'sudo shutdown -h now' },
            ]
        },
        { 'title': "Help", 'type': COMMAND, 'command': 'less '+path_dirs.data_dir+'help' },
        { 'title': "Visualization Endpoints", 'type': MENU, 'subtitle': 'Status of visualization endpoints',
          'options': visualizations(path_dirs)
        },
      ]
    }
    return menu_data

def main(base_dir=None, info_dir=None, data_dir=None):
    """start menu, clears terminal after exiting menu"""
    path_dirs = PathDirs()
    if base_dir:
        path_dirs = PathDirs(base_dir=base_dir)
    if info_dir:
        path_dirs.info_dir = info_dir
    if data_dir:
        path_dirs.data_dir = data_dir
    menu_data = build_menu_dict(path_dirs)
    processmenu(path_dirs, menu_data)
    curses.endwin()
    os.system('clear')

def execute(cmd):
    """executes a subprocess command and iterates ... as the output is created"""
    popen = Popen(cmd, stdout=PIPE, shell=True, universal_newlines=True)
    stdout_lines = iter(popen.stdout.readline, "")
    for stdout_line in stdout_lines:
        yield "..."

    popen.stdout.close()
    return_code = popen.wait()
    if return_code != 0:
        raise CalledProcessError(return_code, cmd)

if __name__ == "__main__": # pragma: no cover
    # make sure that vent-management is running
    try:
        print("loading"),
        for result in execute('/bin/sh /scripts/bootlocal.sh'):
            print(result),
        print("")
    except Exception as e:
        pass

    # run main program
    if len(sys.argv) == 4:
        main(base_dir=sys.argv[1], info_dir=sys.argv[2], data_dir=sys.argv[3])
    else:
        main()
