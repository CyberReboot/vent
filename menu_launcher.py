#!/usr/bin/env python2.7

import ConfigParser
import curses
import os
import sys
import termios
import tty


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
DISPLAY = "display"

# path that exists on the iso
collectors_dir = "/var/lib/docker/data/collectors"
core_dir = "/var/lib/docker/data/core"
plugins_dir = "/var/lib/docker/data/plugins/"
template_dir = "/var/lib/docker/data/templates/"
vis_dir = "/var/lib/docker/data/visualization"

# Update images for removed plugins
def update_images():
    images = check_output(" docker images | awk \"{print \$1}\" | grep / ", shell=True).split("\n")
    for image in images:
        image = image.split("  ")[0]
        if "core/" in image or "visualization/" in image or "collectors/" in image:
            if not os.path.isdir("/var/lib/docker/data/"+image):
                os.system("docker rmi "+image)
        else:
            if not os.path.isdir("/var/lib/docker/data/plugins/"+image):
                os.system("docker rmi "+image)

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
    except:
        pass

# Will wait for user input before clearing stdout
def confirm():
    while getch():
        break

# Parses modes.template and returns a dict containing all specifically enabled containers
# Returns dict along the format of: {'namespace': ["all"], 'namespace2': [""], 'namespace3': ["plug1", "plug2"]}
def get_mode_config():
    # Parsing modes.template
    modes = {}
    try:
        config = ConfigParser.RawConfigParser()
        config.read(template_dir+'modes.template')
        # Check if any runtime configurations
        if config.has_section("plugins"):
            plugin_array = config.options("plugins")
            # Check if there are any options
            if plugin_array:
                with open("/tmp/enabled-modes.log", "a+") as myfile:
                    myfile.write("modes.template\n")
                    for plug in plugin_array:
                        modes[plug] = config.get("plugins", plug).replace(" ", "").split(",")
                        for pl in modes[plug]:
                            myfile.write("'"+plug+"': "+pl+'\n')
                myfile.close()
        # If not then there are no special runtime configurations and modes is empty
    except:
        pass

    return modes

# Parses core.template to get all runtime configurations for enabling/disabling cores
# Returns dict along the format of: {'passive': "on", 'active': "on", 'aaa-redis': "off"}
def get_core_config():
    # Parsing core.template
    cores = {}
    try:
        config = ConfigParser.RawConfigParser()
        config.read(template_dir+'core.template')
        passive = None
        active = None
        # Check if any run-time configurations for core-collectors
        if config.has_section("local-collection"):
            # Check for passive collector configs
            if config.has_option("local-collection", "passive"):
                passive = config.get("local-collection", "passive").replace(" ", "")
            # Check for active collector configs
            if config.has_option("local-collection", "active"):
                active = config.get("local-collection", "active").replace(" ", "")
            if passive == "on" or passive == "off":
                cores['passive'] = passive
                with open("/tmp/enabled-core.log", "a+") as myfile:
                    myfile.write("'passive': "+cores['passive']+"\n")
                myfile.close()
            if active == "on" or active == "off":
                cores['active'] = active
                with open("/tmp/enabled-core.log", "a+") as myfile:
                    myfile.write("'active': "+cores['active']+"\n")
                myfile.close()
        # If not then everything is enabled and cores is empty

        # Check if any run-time configurations for core
        if config.has_section("locally-active"):
            active_array = config.options("locally-active")
            # Check if there are any options
            if active_array:
                with open("/tmp/enabled-core.log", "a+") as myfile:
                    for option in active_array:
                        cores[option] = config.get("locally-active", option).replace(" ", "")
                        myfile.write("'"+option+"': "+cores[option]+"\n")
                myfile.close()
        # If not then everything is enabled and cores is empty
    except:
        pass

    return cores

# Retrieves installed cores
# Returns list: ["core1", "core2", "core3"]
def get_installed_cores():
    cores = []
    try:
        # Get all cores
        cores = [ core for core in os.listdir(core_dir) if os.path.isdir(os.path.join(core_dir, core)) ]
    except:
        pass

    return cores

# Retrieves installed collectors by category: active, passive, or both (all)
# Returns list: ["coll1", "coll2", "coll3"]
def get_installed_collectors(c_type):
    colls = []
    try:
        # Get all collectors
        collectors = [ collector for collector in os.listdir(collectors_dir) if os.path.isdir(os.path.join(collectors_dir, collector)) ]

        # Filter by passive/active/all
        if c_type == "passive":
            colls = [ collector for collector in collectors if "passive-" in collector ]
        elif c_type == "active":
            colls = [ collector for collector in collectors if "active-" in collector ]
        elif c_type == "all":
            colls = collectors
        else:
            with open("/tmp/error.log", "a+") as myfile:
                myfile.write("Error in get_installed_collectors: ", "Invalid collector parameter: ", c_type)
            myfile.close()
    except:
        pass

    return colls

# Retrieves installed visualizations
# Returns list: ["vis1", "vis2", "vis3"]
def get_installed_vis():
    vis = []
    try:
        # Get all visualizations
        vis = [ visualization for visualization in os.listdir(vis_dir) if os.path.isdir(os.path.join(vis_dir, visualization)) ]
    except:
        pass

    return vis

# Retrieves all plugins by namespace; e.g. - features/tcpdump || features/hexparser
# Note returns a dict of format: {'namespace': [p1, p2, p3, ...], 'namespace2': [p1, p2, p3, ...]}
def get_installed_plugins():
    p = {}
    try:
        # Get all namespaces
        namespaces = [ namespace for namespace in os.listdir(plugins_dir) if os.path.isdir(os.path.join(plugins_dir, namespace)) ]

        # For each namespace, retrieve all plugins and index by namespace
        for namespace in namespaces:
            p[namespace] = [ plugin for plugin in os.listdir(plugins_dir+namespace) if os.path.isdir(os.path.join(plugins_dir+namespace, plugin)) ]
    except:
        pass

    return p

# Retrieves all installed containers
# Returns a dict indexed by container type: 
# {'cores':["core1", "core2"], 'collectors':["coll1", "coll2"]}
# Also returns a list of all containers, and list by category
def get_all_installed():
    all_installed = {}
    list_installed = {}
    try:
        # Get each set of containers by type
        all_cores = get_installed_cores()
        all_colls = get_installed_collectors("all")
        all_vis = get_installed_vis()

        # Note - Dictionary
        all_plugins = get_installed_plugins()

        all_installed['core'] = all_cores
        all_installed['collectors'] = all_colls
        all_installed['visualization'] = all_vis

        with open("/tmp/installed.log", "a+") as myfile:
            myfile.write("Cores: ")
            for val in all_cores:
                myfile.write(val+" ")
            myfile.write("\n")
            myfile.write("Colls: ")
            for val in all_colls:
                myfile.write(val+" ")
            myfile.write("\n")
            myfile.write("Vis: ")
            for val in all_vis:
                myfile.write(val+" ")
            myfile.write("\n")
            for key in all_plugins.keys():
                myfile.write(key+": ")
                for val in all_plugins[key]:
                    myfile.write(val+" ")
                myfile.write("\n")
        myfile.close()

        # Check if all_plugins is empty
        if all_plugins:
            all_installed.update(all_plugins)
    except:
        pass

    return all_installed, all_cores, all_colls, all_vis, all_plugins

def get_mode_enabled(mode_config):
    mode_enabled = {}
    try:
        all_installed, all_cores, all_colls, all_vis, all_plugins = get_all_installed()
        with open("/tmp/installed.log", "a+") as myfile:
            myfile.write("====ALL_INSTALLED====\n")
            for key in all_installed.keys():
                myfile.write(key+": ")
                for val in all_installed[key]:
                    myfile.write(val+" ")
                myfile.write("\n")
        myfile.close()

        # if mode_config is empty, no special runtime configuration
        if not mode_config:
            mode_enabled = all_installed
        # mode_config has special runtime configs
        else:
            # Containers by Category
            core_enabled = []
            coll_enabled = []
            vis_enabled = []

            # check if core has a specification in mode_config
            if "core" in mode_config.keys():
                val = mode_config['core']
                # val is either: ["all"] or ["none"]/[""] or ["core1", "core2", etc...]
                if val == ["all"]:
                    core_enabled = all_cores
                elif val == ["none"] or val == [""]:
                    core_enabled = []
                else:
                    core_enabled = val
                with open("/tmp/mode-core-enable.log", "a+") as myfile:
                    for core in val:
                        myfile.write("MODE_CONFIG VAL FOR CORE IS: "+core+"\n")
                myfile.close()
            # if not, then no runtime config for core, use all
            else:
                core_enabled = all_cores

            # check if collectors has a specification in mode_config
            if "collectors" in mode_config.keys():
                val = mode_config['collectors']
                # val is either: ["all"] or ["none"]/[""] or ["coll1", "coll2", etc...]
                if val == ["all"]:
                    coll_enabled = all_colls
                elif val == ["none"] or val == [""]:
                    coll_enabled = []
                else:
                    coll_enabled = val
                with open("/tmp/mode-coll-enable.log", "a+") as myfile:
                    for coll in val:
                        myfile.write("MODE_CONFIG VAL FOR COLL IS: "+coll+"\n")
                myfile.close()
            # if not, then no runtime config for coll, use all
            else:
                coll_enabled = all_colls

            # check if visualizations has a specification in mode_config
            if "visualization" in mode_config.keys():
                val = mode_config['visualization']
                # val is either: ["all"] or ["none"]/[""] or ["coll1", "coll2", etc...]
                if val == ["all"]:
                    vis_enabled = all_vis
                elif val == ["none"] or val == [""]:
                    vis_enabled = []
                else:
                    vis_enabled = val
                with open("/tmp/mode-vis-enable.log", "a+") as myfile:
                    for vis in val:
                        myfile.write("MODE_CONFIG VAL FOR VIS IS: "+vis+"\n")
                myfile.close()
            # if not, then no runtime config for vis, use all
            else:
                vis_enabled = all_vis

            # plugins
            for namespace in mode_config.keys():
                if namespace != "visualization" and namespace != "collectors" and namespace != "core":
                    val = mode_config[namespace]
                    # val is either: ["all"] or ["none"]/[""] or ["some", "some2", etc...]
                    if val == ["all"]:
                        mode_enabled[namespace] = all_plugins[namespace]
                    elif val == ["none"] or val == [""]:
                        mode_enabled[namespace] = []
                    else:
                        mode_enabled[namespace] = val
                    with open("/tmp/mode-plugin-enable.log", "a+") as myfile:
                        myfile.write("MODE_CONFIG VAL FOR "+namespace+" IS: ")
                        for plug in val:
                            myfile.write(plug)
                        myfile.write("\n")
                    myfile.close()

            # if certain plugin namespaces have been omitted from the modes.template file
            # then no special runtime config and use all
            for namespace in all_plugins.keys():
                if namespace not in mode_enabled.keys():
                    mode_enabled[namespace] = all_plugins[namespace]

            mode_enabled['core'] = core_enabled
            mode_enabled['collectors'] = coll_enabled
            mode_enabled['visualization'] = vis_enabled
    except:
        pass

    return mode_enabled

def get_core_enabled(core_config):
    core_enabled = {}
    core_disabled = {}
    try:
        passive_colls = get_installed_collectors("passive")
        active_colls = get_installed_collectors("active")
        coll_enabled = []
        coll_disabled = []
        # only if not empty
        if core_config:
            ### Local-Collection ###
            # Check passive/active settings
            # Default all on
            p_colls = passive_colls
            a_colls = active_colls

            if 'passive' in core_config.keys():
                if core_config['passive'] == "off":
                    p_colls = []
            if 'active' in core_config.keys():
                if core_config['active'] == "off":
                    a_colls = []

            # Add all passively enabled collectors
            if p_colls:
                coll_enabled = coll_enabled + p_colls
            else:
                coll_disabled = coll_disabled + passive_colls
            # Add all actively enabled collectors
            if a_colls:
                coll_enabled = coll_enabled + a_colls
            else:
                coll_disabled = coll_disabled + active_colls

            with open("/tmp/core-enable.log", "a+") as myfile:
                for x in p_colls:
                    myfile.write(x)
                myfile.write("\n")
                for x in a_colls:
                    myfile.write(x)
                myfile.write("\n")
                myfile.write("ENABLED: ")
                for x in coll_enabled:
                    myfile.write(x)
                myfile.write("\n")
                myfile.write("DISABLED: ")
                for x in coll_disabled:
                    myfile.write(x)
                myfile.write("\n")
            myfile.close()
            ### Locally-Active ###
            # Check locally-active settings
            # Get all keys (containers) that are turned off
            locally_disabled = [ key for key in core_config if key != 'passive' and key != 'active' and core_config[key] == "off" ]
            # Get all keys (containers) that are turned on
            locally_enabled = [ key for key in core_config if key != 'passive' and key != 'active' and core_config[key] == "on" ]

            with open("/tmp/core-enable.log", "a+") as myfile:
                myfile.write("LOCALLY-DISABLED: ")
                for x in locally_disabled:
                    myfile.write(x)
                myfile.write("\n")
                myfile.write("LOCALLY-ENABLED: ")
                for x in locally_enabled:
                    myfile.write(x)
                myfile.write("\n")
            myfile.close()

            core_enabled['collectors'] = coll_enabled
            core_enabled['core'] = locally_enabled
            core_disabled['collectors'] = coll_disabled
            core_disabled['core'] = locally_disabled
    except:
        pass

    return core_enabled, core_disabled

# Retrieves containers that have been enabled in config
# Priority is namespace.template, then modes.template
def get_enabled():
    enabled = {}
    disabled = []
    try:
        # Retrieve configuration enablings/disablings for all containers
        mode_config = get_mode_config()
        core_config = get_core_config()

        # Retrieve containers enabled by mode
        # Note - mode_enabled and its complement form the complete set of containers
        mode_enabled = get_mode_enabled(mode_config)

        # Retrieve containers enabled/disabled by core
        # Note - the union of core_enabled and core_disabled DO NOT form the complete set of containers
        core_enabled, core_disabled = get_core_enabled(core_config)

        # The complete set of containers
        all_installed = get_all_installed()[0]
        with open("/tmp/all_installed.log", "a+") as myfile:
            for key in all_installed:
                myfile.write(key+": ")
                for val in all_installed[key]:
                    myfile.write("val = "+val+", ")
                myfile.write("\n")
        myfile.close()

        ### Intersection Logic by Case: ###
        # Case 1: container is in mode_enabled and in core_enabled -> enabled
        # Case 2: container is in mode_enabled and in core_disabled-> disabled
        # Case 3: container is not in mode_enabled and in core_enabled -> disabled
        # Case 4: container is not in mode_enabled and not in core_enabled -> disabled
        # Case 5: container is in mode_enabled and not in core_enabled or disabled -> enabled
        # Case 6: container is not in mode_enabled and not in core_enabled or disabled -> disabled
        # Case 7: None of the other cases -> Something went grievously wrong...

        # Get keys from all_installed, and initialize values to empty list
        all_enabled = {}
        all_disabled = {}
        for namespace in all_installed:
            all_enabled[namespace] = []
            all_disabled[namespace] = []

        for namespace in all_installed.keys():
            # For 'cores' & 'collectors'
            with open("/tmp/statusout.log", "a+") as myfile:
                myfile.write(namespace+": ")
                if namespace in mode_enabled.keys() and namespace in core_enabled.keys():
                    for container in all_installed[namespace]:
                            myfile.write(container+", ")
                            # Case 1
                            if container in mode_enabled[namespace] and container in core_enabled[namespace]:
                                all_enabled[namespace].append(container)
                            # Case 2
                            elif container in mode_enabled[namespace] and container in core_disabled[namespace]:
                                all_disabled[namespace].append(container)
                            # Case 3
                            elif container not in mode_enabled[namespace] and container in core_enabled[namespace]:
                                all_disabled[namespace].append(container)
                            # Case 4
                            elif container not in mode_enabled[namespace] and container in core_disabled[namespace]:
                                all_disabled[namespace].append(container)
                            # Case 5
                            elif container in mode_enabled[namespace]:
                                all_enabled[namespace].append(container)
                            # Case 6
                            elif container not in mode_enabled[namespace]:
                                all_disabled[namespace].append(container)
                            # Case 7
                            else:
                                with open("/tmp/error.log", "a+") as file:
                                    file.write("get_enabled error: Case 7 reached!\n")
                                file.close()
                    myfile.write("\n")
                else:
                # For 'visualizations' & all plugin namespaces
                    for container in all_installed[namespace]:
                        myfile.write(container+", ")
                        # Case 5
                        if container in mode_enabled[namespace]:
                            all_enabled[namespace].append(container)
                        # Case 6
                        elif container not in mode_enabled[namespace]:
                            all_disabled[namespace].append(container)
                        # Case 7
                        else:
                            with open("/tmp/error.log", "a+") as file:
                                file.write("get_enabled error: Case 7 reached!\n")
                            file.close()            
                    myfile.write("\n")
            myfile.close()

        for key in all_enabled:
            with open("/tmp/final.log", "a+") as myfile:
                myfile.write("ENABLED "+key+": ")
                for val in all_enabled[key]:
                    myfile.write(val+" ")
                myfile.write("\n")
            myfile.close()

        for key in all_disabled:
            with open("/tmp/final.log", "a+") as myfile:
                myfile.write("DISABLED "+key+": ")
                for val in all_disabled[key]:
                    myfile.write(val+" ")
                myfile.write("\n")
            myfile.close()

        enabled = all_enabled
        disabled = all_disabled
    except:
        pass

    return enabled, disabled

# Displays status of all running, not running/built, not built, and disabled plugins
def get_plugin_status():
    notbuilt = []
    p = {}

    try:
        # Retrieves all installed containers
        all_installed, all_cores, all_colls, all_vis, all_plugins = get_all_installed()

        # Retrieves all enabled images
        enabled, disabled = get_enabled()

        # Need to cross reference with all installed containers to determine all disabled containers
        containers = check_output(" docker ps -a | grep '/' | awk \"{print \$NF}\" ", shell=True).split("\n")
        containers = [ container for container in containers if container != "" ]
        for container in containers:
            with open("/tmp/pruning.log", "a+") as myfile:
                myfile.write(container+"\n")
            myfile.close()

        disabled_containers = []

        for namespace in disabled:
            for container in disabled[namespace]:
                with open("/tmp/pruning.log", "a+") as myfile:
                    myfile.write("Disabled: "+container+"\n")
                myfile.close()

        # Intersect the set of all containers with the set of all disabled images
        # Images form the basis for a container (in name especially), but there can be multiple containers per image
        for container in containers:
            for namespace in disabled:
                for image in disabled[namespace]:
                    if image in container:
                        disabled_containers.append(container)
                        with open("/tmp/pruning.log", "a+") as myfile:
                            myfile.write(image + ": " + container + "...disabled!\n")
                        myfile.close()

        # Retrieves running or restarting docker containers and returns a list of container names
        running = check_output(" { docker ps -af status=running & docker ps -af status=restarting; } | grep '/' | awk \"{print \$NF}\" ", shell=True).split("\n")

        # Retrieves docker containers with status exited, paused, dead, created; returns as a list of container names
        nrcontainers = check_output(" { docker ps -af status=created & docker ps -af status=exited & docker ps -af status=paused & docker ps -af status=dead; } | grep '/' | awk \"{print \$NF}\" ", shell=True).split("\n")
        nrcontainers = [ container for container in nrcontainers if container != "" ]
        nrbuilt = [ container for container in nrcontainers if container not in disabled_containers ]

        # Retrieve all built docker images
        built = check_output(" docker images | grep '/' | awk \"{print \$1}\" ", shell=True).split("\n")
        built = [ image for image in built if image != "" ]

        # If image hasn't been disabled and isn't present in docker images then add
        notbuilt = []
        for namespace in all_installed:
            for image in all_installed[namespace]:
                if image not in disabled[namespace] and namespace+'/'+image not in built:
                    notbuilt.append(namespace+'/'+image)

        for container in nrcontainers:
            with open("/tmp/nrbuilt.log", "a+") as myfile:
                myfile.write("NR: "+container+"\n")
            myfile.close()
        for container in disabled_containers:
            with open("/tmp/nrbuilt.log", "a+") as myfile:
                myfile.write("DIS: "+container+"\n")
            myfile.close()
        for container in nrbuilt:
            with open("/tmp/nrbuilt.log", "a+") as myfile:
                myfile.write("NRB: "+container+"\n")
            myfile.close()
        for container in notbuilt:
            with open("/tmp/built.log", "a+") as myfile:
                myfile.write("NB: "+container+"\n")
            myfile.close()

        # Format disabled dict for menu processing
        p_disabled = []
        for namespace in disabled:
            for image in disabled[namespace]:
                p_disabled.append(namespace+'/'+image)

        p['title'] = 'Plugin Status'
        p['subtitle'] = 'Choose a category...'
        p_running = [ {'title': x, 'type': 'INFO', 'command': '' } for x in running if x != "" ]
        p_nrbuilt = [ {'title': x, 'type': 'INFO', 'command': '' } for x in nrbuilt ]
        p_disabled_cont = [ {'title': x, 'type': 'INFO', 'command': '' } for x in disabled_containers ]
        p_disabled_images = [ {'title': x, 'type': 'INFO', 'command': '' } for x in p_disabled ]
        p_built = [ {'title': x, 'type': 'INFO', 'command': '' } for x in built ]
        p_notbuilt = [ {'title': x, 'type': 'INFO', 'command': ''} for x in notbuilt ]
        p['options'] = [ { 'title': "Running Containers", 'subtitle': "Currently running...", 'type': MENU, 'options': p_running },
                         { 'title': "Not Running Containers", 'subtitle': "Built but not currently running...", 'type': MENU, 'options': p_nrbuilt },
                         { 'title': "Disabled Containers", 'subtitle': "Currently disabled by config...", 'type': MENU, 'options': p_disabled_cont },
                         { 'title': "Disabled Images", 'subtitle': "Currently disabled images...", 'type': MENU, 'options': p_disabled_images },
                         { 'title': "Built Images", 'subtitle': "Currently built images...", 'type': MENU, 'options': p_built },
                         { 'title': "Not Built Images", 'subtitle': "Currently not built (do not have images)...", 'type': MENU, 'options': p_notbuilt }
                        ]
    except:
        pass

    return p

# Retrieves all installed plugin repos; e.g - vent-network
def get_installed_plugin_repos(m_type, command):
    try:
        p = {}
        p['type'] = MENU
        if command=="remove":
            command1 = "python2.7 /data/plugin_parser.py remove_plugins "
            p['title'] = 'Remove Plugins'
            p['subtitle'] = 'Please select a plugin to remove...'
            p['options'] = [ {'title': name, 'type': m_type, 'command': '' } for name in os.listdir("/var/lib/docker/data/plugin_repos") if os.path.isdir(os.path.join('/var/lib/docker/data/plugin_repos', name)) ]
            for d in p['options']:
                with open("/var/lib/docker/data/plugin_repos/"+d['title']+"/.git/config", "r") as myfile:
                    repo_name = ""
                    while not "url" in repo_name:
                        repo_name = myfile.readline()
                    repo_name = repo_name.split("url = ")[-1]
                    d['command'] = command1+repo_name
        elif command=="update":
            command1 = "python2.7 /data/plugin_parser.py remove_plugins "
            command2 = " && python2.7 /data/plugin_parser.py add_plugins "
            p['title'] = 'Update Plugins'
            p['subtitle'] = 'Please select a plugin to update...'
            p['options'] = [ {'title': name, 'type': m_type, 'command': '' } for name in os.listdir("/var/lib/docker/data/plugin_repos") if os.path.isdir(os.path.join('/var/lib/docker/data/plugin_repos', name)) ]
            for d in p['options']:
                with open("/var/lib/docker/data/plugin_repos/"+d['title']+"/.git/config", "r") as myfile:
                    repo_name = ""
                    while not "url" in repo_name:
                        repo_name = myfile.readline()
                    repo_name = repo_name.split("url = ")[-1]
                    d['command'] = command1+repo_name+command2+repo_name
        else:
            p['title'] = 'Installed Plugins'
            p['subtitle'] = 'Installed Plugins:'
            p['options'] = [ {'title': name, 'type': m_type, 'command': '' } for name in os.listdir("/var/lib/docker/data/plugin_repos") if os.path.isdir(os.path.join('/var/lib/docker/data/plugin_repos', name)) ]
        return p

    except:
        pass

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
                    p['type'] = INFO2
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
                    p['type'] = INFO2
                    p['command'] = 'python2.7 /data/template_parser.py passive '+action
                    modes.append(p)
            except:
                pass
            try:
                active = config.get("local-collection", "active")
                if active == "on":
                    p = {}
                    p['title'] = "Local Active Collection"
                    p['type'] = INFO2
                    p['command'] = 'python2.7 /data/template_parser.py active '+action
                    modes.append(p)
            except:
                pass
        except:
            pass
        if len(modes) > 1:
            p = {}
            p['title'] = "All"
            p['type'] = INFO2
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
        for f in os.listdir(template_dir):
            if f.endswith(".template"):
                p = {}
                p['title'] = f
                p['type'] = SETTING
                p['command'] = 'python2.7 /data/suplemon/suplemon.py '+template_dir+f
                modes.append(p)
    except:
        print "unable to get the configuration templates.\n"
    return modes

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

        # !! TODO hack for now, long term should probably take multiple character numbers and update on return
        num_options = optioncount
        if optioncount > 8:
            num_options = 8

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
        elif x >= ord('1') and x <= ord(str(num_options+1)):
            pos = x - ord('0') - 1
    return pos

def processmenu(menu, parent=None):
    optioncount = len(menu['options'])
    exitmenu = False
    while not exitmenu:
        getin = runmenu(menu, parent)
        if getin == optioncount:
            exitmenu = True
        elif menu['options'][getin]['type'] == COMMAND:
            curses.def_prog_mode()
            os.system('reset')
            screen.clear()
            if "&&" in menu['options'][getin]['command']:
                commands = menu['options'][getin]['command'].split("&&")
                for c in commands:
                    success = os.system(c)
                    if success == 0:
                        continue
                    else:
                        print "FAILED command: " + c
                        break
            else:
                os.system(menu['options'][getin]['command'])
            screen.clear()
            curses.reset_prog_mode()
            curses.curs_set(1)
            curses.curs_set(0)
        elif menu['options'][getin]['type'] == INFO2:
            curses.def_prog_mode()
            os.system('reset')
            screen.clear()
            if "&&" in menu['options'][getin]['command']:
                commands = menu['options'][getin]['command'].split("&&")
                for c in commands:
                    success = os.system(c)
                    if success == 0:
                        continue
                    else:
                        print "FAILED command: " + c
                        break
            else:
                os.system(menu['options'][getin]['command'])
            if menu['title'] == "Remove Plugins":
                update_images()
                exitmenu = True
            elif menu['title'] == "Update Plugins":
                update_images()
                os.system("/bin/sh /data/build_images.sh")
            confirm()
            screen.clear()
            curses.reset_prog_mode()
            curses.curs_set(1)
            curses.curs_set(0)
        # !! TODO
        elif menu['options'][getin]['type'] == INFO:
            pass
        elif menu['options'][getin]['type'] == DISPLAY:
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
                plugin_url = get_param("Enter the HTTPS Git URL that contains the new plugins, e.g. https://github.com/CyberReboot/vent-plugins.git")
                curses.def_prog_mode()
                os.system('reset')
                screen.clear()
                if not "https://" in plugin_url:
                    os.system("echo No plugins added, url is not formatted correctly.")
                    os.system("echo Please use a git url, e.g. https://github.com/CyberReboot/vent-plugins.git")
                else:
                    os.system("python2.7 /data/plugin_parser.py add_plugins "+plugin_url)                    
                confirm()
                screen.clear()
                os.execl(sys.executable, sys.executable, *sys.argv)
        elif menu['options'][getin]['type'] == MENU:
            if menu['options'][getin]['title'] == "Remove Plugins":
                screen.clear()
                installed_plugins = get_installed_plugin_repos(INFO2, "remove")
                processmenu(installed_plugins, menu)
                screen.clear()
            elif menu['options'][getin]['title'] == "Show Installed Plugins":
                screen.clear()
                installed_plugins = get_installed_plugin_repos(DISPLAY, "")
                processmenu(installed_plugins, menu)
                screen.clear()
            elif menu['options'][getin]['title'] == "Update Plugins":
                screen.clear()
                installed_plugins = get_installed_plugin_repos(INFO2, "update")
                processmenu(installed_plugins, menu)
                screen.clear()
            elif menu['options'][getin]['title'] == "Status":
                screen.clear()
                plugins = get_plugin_status()
                processmenu(plugins, menu)
                screen.clear()
            else:
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
              'command': ''
            },
            { 'title': "Configure", 'type': MENU, 'subtitle': '',
              'options': update_plugins()
            }
          ]
        },
        { 'title': "Plugins", 'type': MENU, 'subtitle': 'Please select an option...',
          'options': [
            { 'title': "Add Plugins", 'type': INPUT, 'command': '' },
            { 'title': "Remove Plugins", 'type': MENU, 'command': '' },
            { 'title': "Show Installed Plugins", 'type': MENU, 'command': '' },
            { 'title': "Update Plugins", 'type': MENU, 'command': '' },
          ]
        },
        { 'title': "System Info", 'type': MENU, 'subtitle': '',
          'options': [
            #{ 'title': "Visualization Endpoint Status", 'type': INFO, 'command': '/bin/sh /var/lib/docker/data/visualization/get_url.sh' },
            { 'title': "Container Stats", 'type': COMMAND, 'command': "docker ps | awk '{print $NF}' | grep -v NAMES | xargs docker stats" },
            { 'title': "", 'type': INFO, 'command': 'echo'},
            { 'title': "RabbitMQ Management Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py aaa-rabbitmq mgmt' },
            { 'title': "RQ Dashboard Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py rq-dashboard mgmt' },
            { 'title': "Elasticsearch Head Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py elasticsearch head' },
            { 'title': "Elasticsearch Marvel Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py elasticsearch marvel' },
            { 'title': "Containers Running", 'type': INFO, 'command': 'docker ps | sed 1d | wc -l' },
            { 'title': "Uptime", 'type': INFO, 'command': 'uptime' },
          ]
        },
        { 'title': "Build", 'type': MENU, 'subtitle': '',
          'options': [
            { 'title': "Build new plugins and core", 'type': INFO2, 'command': '/bin/sh /data/build_images.sh' },
            { 'title': "Force rebuild all plugins and core", 'type': INFO2, 'command': '/bin/sh /data/build_images.sh --no-cache' },
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
