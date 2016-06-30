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
    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, settings)
    return ch

# Will wait for user input before clearing stdout
def confirm():
    while getch():
        break

# Parses modes.template and returns a dict containing all specifically enabled containers
# Returns dict along the format of: {'namespace': ["all"], 'namespace2': [""], 'namespace3': ["plug1", "plug2"]}
def get_mode_configs():
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
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Exception in get_enabled_plugins: modes.template parsing...", sys.exc_info())
        myfile.close()
        pass

    return modes

# Parses core.template to get all runtime configurations for enabling/disabling cores
# Returns dict along the format of: {'passive': "on", 'active': "on", 'aaa-redis': "off"}
def get_core_configs():
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
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Exception in get_enabled_plugins: core.template parsing...", sys.exc_info())
        myfile.close()
        pass

    return cores

def get_collector_configs():
    # Parsing collectors.templates
    collectors = {}
    try:
        config = ConfigParser.RawConfigParser()
        passive = None
        active = None
        exists = check_output("ls "+template_dir+" | grep collectors.template", shell=True).rstrip('\n')
        with open("/tmp/enabled-collectors.log", "a+") as myfile:
            myfile.write(exists+"\n")
        myfile.close()
        # Bash output was not empty
        if exists == "collectors.template":
            config.read(template_dir+'collectors.template')
            # Check if any run-time configurations for collectors
            if config.has_section("local-collection"):
                # Check for passive collector configs
                if config.has_option("local-collection", "passive"):
                    passive = config.get("local-collection", "passive").replace(" ", "")
                # Check for active collector configs
                if config.has_option("local-collection", "active"):
                    active = config.get("local-collection", "active").replace(" ", "")
                if passive == "on" or passive == "off":
                    collectors['passive'] = passive
                    with open("/tmp/enabled-collectors.log", "a+") as myfile:
                        myfile.write("'passive': "+collectors['passive']+"\n")
                    myfile.close()
                if active == "on" or active == "off":
                    collectors['active'] = active
                    with open("/tmp/enabled-collectors.log", "a+") as myfile:
                        myfile.write("'active': "+collectors['active']+"\n")
                    myfile.close()
            # If not then everything is enabled and collectors is empty

            # Check if any run-time configurations for collector-related services
            if config.has_section("locally-active"):
                active_array = config.options("locally-active")
                if active_array:
                    with open("/tmp/enabled-collectors.log", "a+") as myfile:
                        for option in active_array:
                            collectors[option] = config.get("locally-active", option).replace(" ", "")
                            myfile.write("'"+option+"': "+collectors[option]+'\n')
                    myfile.close()
            # If not then everything is enabled and collectors is empty
        # If it was empty then the file doesn't exist and nothing needs to be done
    except:
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Exception in get_enabled_plugins: collectors.template parsing...", sys.exc_info())
        myfile.close()
        pass

    return collectors

def get_plugin_configs():
    # Parsing *.template (plugins)
    plugins = {}
    try:
        config = ConfigParser.RawConfigParser()
        # All .template files; Rstrip for trailing newline char
        all_templates = check_output("ls "+template_dir+" | grep .template", shell=True).rstrip('\n').split('\n')
        if all_templates != [""]: 
            # Remove modes.template and core.template and visualization.template and collectors.template
            templates = [ template for template in all_templates if template != "modes.template" and template != "core.template" and template != "visualization.template" and template != "collectors.template" ] 
            with open("/tmp/enabled-plugins.log", "a+") as myfile:
                for t in templates:
                    myfile.write(t+'\n')
            myfile.close()
            for template in templates:
                config.read(template_dir+template)
                # Check if any runtime configurations
                if config.has_section("plugins"):
                    plugin_array = config.options("plugins")
                    # Check if there are any options
                    if plugin_array:
                        with open("/tmp/enabled-plugins.log", "a+") as myfile:
                            myfile.write(template+"\n")
                            for plug in plugin_array:
                                plugins[plug] = config.get("plugins", plug).replace(" ", "").split(",")
                                for pl in plugins[plug]:
                                    myfile.write("'"+plug+"': "+pl+'\n')
                        myfile.close()
                # If not then everything is enabled and *_enabled is empty
        # If not then there are no plugins installed
    except:
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Exception in get_enabled_plugins: *.template parsing...", sys.exc_info())
        myfile.close()
        pass

    return plugins

#!! TODO - Finish implementation
def get_visualization_configs():
    # Parsing visualization.template
    vis = {}
    try:
        config = ConfigParser.RawConfigParser()
        exists = check_output("ls "+template_dir+" | grep visualization.template", shell=True).rstrip('\n')
        with open("/tmp/enabled-vis.log", "a+") as myfile:
                myfile.write("visualization.template\n")
        myfile.close()
        # Bash output was not empty
        if exists == "visualization.template":
            config.read(template_dir+'visualization.template')
            # !! TODO - What sections in a visualization.template will affect enable?
            # If not then everything is enabled and vis_enabled is empty
        # If it was empty then the file doesn't exist and nothing needs to be done
    except:
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Exception in get_enabled_plugins: visualization.template parsing...", sys.exc_info())
        myfile.close()
        pass

    return vis

# Retrieves installed cores by category: active, passive, or both (all)
# Returns list: ["core1", "core2", "core3"]
def get_installed_cores(c_type):
    cores = []
    try:
        # Get all cores
        c = [ core for core in os.listdir(core_dir) if os.path.isdir(os.path.join(core_dir, core)) ]

        # Filter by passive/active/all
        if c_type == "passive":
            cores = [ core for core in c if "passive-" in core ]
        elif c_type == "active":
            cores = [ core for core in c if "active-" in core ]
        elif c_type == "all":
            cores = c
        else:
            with open("/tmp/error.log", "a+") as myfile:
                myfile.write("Error in get_installed_cores: ", "Invalid core parameter: ", c_type)
            myfile.close()
    except:
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Error in get_installed_cores: ", sys.exc_info())
        myfile.close()
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
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Error in get_installed_collectors: ", sys.exc_info())
        myfile.close()
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
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Error in get_installed_vis: ", sys.exc_info())
        myfile.close()
        pass

# Retrieves all plugins by namespace; e.g. - features/tcpdump || features/hexparser
# Note returns a dict of format: {'namespace': [p1, p2, p3, ...], 'namespace2': [p1, p2, p3, ...]}
# !! TODO - Namespace conflicts are possible and might result in some issues here.
def get_installed_plugins():
    p = {}
    try:
        # Get all namespaces
        namespaces = [ namespace for namespace in os.listdir(plugins_dir) if os.path.isdir(os.path.join(plugins_dir, namespace)) ]

        # For each namespace, retrieve all plugins and index by namespace
        for namespace in namespaces:
            p[namespace] = [ plugin for plugin in os.listdir(plugins_dir+namespace) if os.path.isdir(os.path.join(plugins_dir+namespace, plugin)) ]
    except:
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Error in get_installed_plugins: ", sys.exc_info())
        myfile.close()
        pass

    return p

# Retrieves enabled cores
# Returns dict of format: {'core': ["core1", "core2"]}
def get_enabled_cores(mode_config, core_config):
    p = {}
    try:
        ### Enabled Core Containers ###
        # if mode_config is empty, no special runtime configuration
        if not mode_config:
            # if core_config is empty, no special runtime configuration
            if not core_config:
                # Every core is enabled
                p['core'] = get_installed_cores("all")
            else:
                # Check passive/active settings
                # Default all on
                passive_cores = get_installed_cores("passive")
                active_cores = get_installed_cores("active")

                enabled_cores = []
                disabled_cores = []
                if 'passive' in core_config.keys():
                    if core_config['passive'] == "off":
                        passive_cores = []
                if 'active' in core_config.keys():
                    if core_config['active'] == "off":
                        active_cores = []

                # Check locally-active settings
                # Default all on
                # Get all keys (containers) that are turned off
                locally_disabled = [ key for key in core_config if key != 'passive' and key != 'active' and core_config[key] == "off" ]
                # Get all keys (containers) that are turned on
                locally_enabled = [ key for key in core_config if key != 'passive' and key != 'active' and core_config[key] == "on" ]

                # Add all passively enabled cores
                if passive_cores:
                    enabled_cores.extend(passive_cores)
                else:
                    disabled_cores.extend(get_installed_cores("passive"))
                # Add all actively enabled cores
                if active_cores:
                    enabled_cores.extend(active_cores)
                else:
                    disabled_cores.extend(get_installed_cores("active"))
                # Add all locally enabled cores
                # Note - could be duplicates from passive/active
                enabled_cores = list(set(enabled_cores.extend(locally_enabled)))
                disabled_cores = list(set(disabled_cores.extend(locally_disabled)))


                # Removes any duplicates
                p['core'] = enabled_cores
        # mode_config has special runtime configs
        else:
            # if core_config is empty, can focus only on mode_config
            if not core_config:
                # check if core has a specification in mode_config
                if "core" in mode_config.keys():
                    val = mode_config['core']
                    # val is either: ["all"] or ["none"]/[""] or ["core1", "core2", etc...]
                    if val == ["all"]:
                        p['core'] = get_installed_cores("all")
                    elif val == ["none"] or val == [""]:
                        p['core'] = []
                    else:
                        p['core'] = val
                    with open("/tmp/mode-core-enable.log", "a+") as myfile:
                        for core in val:
                            myfile.write("MODE_CONFIG VAL FOR CORE IS: "+core+"\n")
                    myfile.close()
                # if not, then no runtime config for core, use all
                else:
                    p['core'] = get_installed_cores("all")
            # we have core_config and mode_config and need to deal with priority
            else:
                ### Get list of enabled_cores from core_config ###
                # Check passive/active settings
                # Default all on
                passive_cores = get_installed_cores("passive")
                active_cores = get_installed_cores("active")
                all_cores = get_installed_cores("all")

                core_enabled_cores = []
                core_disabled_cores = []
                if 'passive' in core_config.keys():
                    if core_config['passive'] == "off":
                        passive_cores = []
                if 'active' in core_config.keys():
                    if core_config['active'] == "off":
                        active_cores = []

                # Check locally-active settings
                # Get all keys (containers) that are turned off
                locally_disabled = [ key for key in core_config if key != 'passive' and key != 'active' and core_config[key] == "off" ]
                # Get all keys (containers) that are turned on
                locally_enabled = [ key for key in core_config if key != 'passive' and key != 'active' and core_config[key] == "on" ]

                # Add all passively enabled cores
                if passive_cores:
                    core_enabled_cores = core_enabled_cores + passive_cores
                else:
                    core_disabled_cores = core_disabled_cores + get_installed_cores("passive")
                # Add all actively enabled cores
                if active_cores:
                    core_enabled_cores = core_enabled_cores + active_cores
                else:
                    core_disabled_cores = core_disabled_cores + get_installed_cores("active")
                # Add all locally enabled cores
                # Note - could be duplicates from passive/active: convert to set and back
                core_enabled_cores = list(set(core_enabled_cores + locally_enabled))
                core_disabled_cores = list(set(core_disabled_cores + locally_disabled))

                ### Get list of enabled_cores from mode_config ###
                mode_enabled_cores = []
                # check if core has a specification in mode_config
                if "core" in mode_config.keys():
                    val = mode_config['core']
                    # val is either: ["all"] or ["none"]/[""] or ["core1", "core2", etc...]
                    if val == ["all"]:
                        mode_enabled_cores = all_cores
                    elif val == ["none"] or val == [""]:
                        mode_enabled_cores = []
                    else:
                        mode_enabled_cores = val
                    with open("/tmp/mode-core-enable.log", "a+") as myfile:
                        for core in val:
                            myfile.write("MODE_CONFIG VAL FOR CORE IS: "+core+"\n")
                    myfile.close()
                # if not, then no runtime config for core, use all
                else:
                    mode_enabled_cores = all_cores

                with open("/tmp/test.log", "a+") as myfile:
                    for core in mode_enabled_cores:
                        myfile.write("MODE_ENABLED_CORE: "+core+"\n")
                    for core in core_enabled_cores:
                        myfile.write("CORE_ENABLE_CORE: "+core+"\n")
                myfile.close()

                ### Logic by Case: ###
                # Case 1: core is in mode_enabled and in core_enabled -> enabled
                # Case 2: core is in mode_enabled and not in core_enabled-> disabled
                # Case 3: core is not in mode_enabled and in core_enabled -> enabled
                # Case 4: core is not in mode_enabled and not in core_enabled -> disabled
                # Case 5: core is in mode_enabled and not in core_enabled or disabled -> enabled
                # Case 6: core is not in mode_enabled and not in core_enabled or disabled -> disabled
                # Case 7: None of the other cases -> Something went grievously wrong...
                # Note - mode_enabled_cores and !mode_enabled_cores form a complete set of all cores
                # Note - core_enabled_cores and core_disabled_cores DO NOT form a complete set of all cores.
                all_enabled_cores = []
                all_disabled_cores = []
                for core in all_cores:
                    # Case 1
                    if core in mode_enabled_cores and core in core_enabled_cores:
                        all_enabled_cores.append(core)
                    # Case 2
                    elif core in mode_enabled_cores and core in core_disabled_cores:
                        all_disabled_cores.append(core)
                    # Case 3
                    elif core not in mode_enabled_cores and core in core_enabled_cores:
                        all_enabled_cores.append(core)
                    # Case 4
                    elif core not in mode_enabled_cores and core in core_disabled_cores:
                        all_disabled_cores.append(core)
                    # Case 5
                    elif core in mode_enabled_cores:
                        all_enabled_cores.append(core)
                    # Case 6
                    elif core not in mode_enabled_cores:
                        all_disabled_cores.append(core)
                    # Case 7
                    else:
                        with open("/tmp/error.log", "a+") as myfile:
                            myfile.write("error in get_enabled_plugins > something went grievously wrong in calculating all_enabled_cores\n")
                        myfile.close()
                for core in all_enabled_cores:
                    with open("/tmp/mode-core-enable.log", "a+") as myfile:
                        myfile.write("Enabled_Core: "+core+"\n")
                    myfile.close()
                for core in all_disabled_cores:
                    with open("/tmp/mode-core-enable.log", "a+") as myfile:
                        myfile.write("Disabled_Core: "+core+"\n")
                    myfile.close()

                p['core'] = all_enabled_cores
    except:
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Exception in get_enabled_cores", sys.exc_info())
        myfile.close()
    return p

# Retrieves enabled collectors
# Returns dict of format: {'collector': ["coll1", "coll2"]}
def get_enabled_collectors(mode_config, coll_config):
    p = {}
    try:
        ### Enabled Collector Containers ###
        # if mode_config is empty, no special runtime configuration
        if not mode_config:
            # if coll_config is empty, no special runtime configuration
            if not coll_config:
                # Every coll is enabled
                p['collector'] = get_installed_collectors("all")
            else:
                # Check passive/active settings
                # Default all on
                passive_colls = get_installed_collectors("passive")
                active_colls = get_installed_collectors("active")

                enabled_colls = []
                disabled_colls = []
                if 'passive' in coll_config.keys():
                    if coll_config['passive'] == "off":
                        passive_coll = []
                if 'active' in coll_config.keys():
                    if coll_config['active'] == "off":
                        active_colls = []

                # Check locally-active settings
                # Default all on
                # Get all keys (containers) that are turned off
                locally_disabled = [ key for key in coll_config if key != 'passive' and key != 'active' and coll_config[key] == "off" ]
                # Get all keys (containers) that are turned on
                locally_enabled = [ key for key in coll_config if key != 'passive' and key != 'active' and coll_config[key] == "on" ]

                # Add all passively enabled collectors
                if passive_colls:
                    enabled_colls.extend(passive_colls)
                else:
                    disabled_colls.extend(get_installed_collectors("passive"))
                # Add all actively enabled collectors
                if active_colls:
                    enabled_colls.extend(active_colls)
                else:
                    disabled_colls.extend(get_installed_collectors("active"))
                # Add all locally enabled collectors
                # Note - could be duplicates from passive/active
                enabled_colls = list(set(enabled_colls.extend(locally_enabled)))
                disabled_colls = list(set(disabled_colls.extend(locally_disabled)))


                # Removes any duplicates
                p['collector'] = enabled_colls
        # mode_config has special runtime configs
        else:
            # if coll_config is empty, can focus only on mode_config
            if not coll_config:
                # check if collectors has a specification in mode_config
                if "collectors" in mode_config.keys():
                    val = mode_config['collectors']
                    # val is either: ["all"] or ["none"]/[""] or ["coll1", "coll2", etc...]
                    if val == ["all"]:
                        p['collector'] = get_installed_collectors("all")
                    elif val == ["none"] or val == [""]:
                        p['collector'] = []
                    else:
                        p['collector'] = val
                    with open("/tmp/mode-collector-enable.log", "a+") as myfile:
                        for collector in val:
                            myfile.write("MODE_CONFIG VAL FOR COLL IS: "+collector+"\n")
                    myfile.close()
                # if not, then no runtime config for collector, use all
                else:
                    p['collector'] = get_installed_collectors("all")
            # we have coll_config and mode_config and need to deal with priority
            else:
                ### Get list of enabled_colls from coll_config ###
                # Check passive/active settings
                # Default all on
                passive_colls = get_installed_collectors("passive")
                active_colls = get_installed_collectors("active")
                all_colls = get_installed_collectors("all")

                coll_enabled_colls = []
                coll_disabled_colls = []
                if 'passive' in coll_config.keys():
                    if coll_config['passive'] == "off":
                        passive_colls = []
                if 'active' in coll_config.keys():
                    if coll_config['active'] == "off":
                        active_colls = []

                # Check locally-active settings
                # Get all keys (containers) that are turned off
                locally_disabled = [ key for key in coll_config if key != 'passive' and key != 'active' and coll_config[key] == "off" ]
                # Get all keys (containers) that are turned on
                locally_enabled = [ key for key in coll_config if key != 'passive' and key != 'active' and coll_config[key] == "on" ]

                # Add all passively enabled collectors
                if passive_colls:
                    coll_enabled_colls = coll_enabled_colls + passive_colls
                else:
                    coll_disabled_colls = coll_disabled_colls + get_installed_collectors("passive")
                # Add all actively enabled collectors
                if active_colls:
                    coll_enabled_colls = coll_enabled_colls + active_colls
                else:
                    coll_disabled_colls = coll_disabled_colls + get_installed_collectors("active")
                # Add all locally enabled collectors
                # Note - could be duplicates from passive/active: convert to set and back
                coll_enabled_colls = list(set(coll_enabled_colls + locally_enabled))
                coll_disabled_colls = list(set(coll_disabled_colls + locally_disabled))

                ### Get list of enabled_collectors from mode_config ###
                mode_enabled_colls = []
                # check if collectors has a specification in mode_config
                if "collectors" in mode_config.keys():
                    val = mode_config['collectors']
                    # val is either: ["all"] or ["none"]/[""] or ["coll1", "coll2", etc...]
                    if val == ["all"]:
                        mode_enabled_colls = all_colls
                    elif val == ["none"] or val == [""]:
                        mode_enabled_colls = []
                    else:
                        mode_enabled_colls = val
                    with open("/tmp/mode-collector-enable.log", "a+") as myfile:
                        for collector in val:
                            myfile.write("MODE_CONFIG VAL FOR COLL IS: "+collector+"\n")
                    myfile.close()
                # if not, then no runtime config for collector, use all
                else:
                    mode_enabled_colls = all_colls

                with open("/tmp/test-collector.log", "a+") as myfile:
                    for collector in mode_enabled_colls:
                        myfile.write("MODE_ENABLED_COLL: "+collector+"\n")
                    for collector in coll_enabled_colls:
                        myfile.write("COLL_ENABLE_COLL: "+collector+"\n")
                myfile.close()

                ### Logic by Case: ###
                # Case 1: coll is in mode_enabled and in coll_enabled -> enabled
                # Case 2: coll is in mode_enabled and not in coll_enabled-> disabled
                # Case 3: coll is not in mode_enabled and in coll_enabled -> enabled
                # Case 4: coll is not in mode_enabled and not in coll_enabled -> disabled
                # Case 5: coll is in mode_enabled and not in coll_enabled or disabled -> enabled
                # Case 6: coll is not in mode_enabled and not in coll_enabled or disabled -> disabled
                # Case 7: None of the other cases -> Something went grievously wrong...
                # Note - mode_enabled_colls and !mode_enabled_colls form a complete set of all colls.
                # Note - coll_enabled_colls and coll_disabled_colls DO NOT form a complete set of all colls.
                all_enabled_colls = []
                all_disabled_colls = []
                for coll in all_colls:
                    # Case 1
                    if coll in mode_enabled_colls and coll in coll_enabled_colls:
                        all_enabled_colls.append(coll)
                    # Case 2
                    elif coll in mode_enabled_colls and coll in coll_disabled_colls:
                        all_disabled_colls.append(coll)
                    # Case 3
                    elif coll not in mode_enabled_colls and coll in coll_enabled_colls:
                        all_enabled_colls.append(coll)
                    # Case 4
                    elif coll not in mode_enabled_colls and coll in coll_disabled_colls:
                        all_disabled_colls.append(coll)
                    # Case 5
                    elif coll in mode_enabled_colls:
                        all_enabled_colls.append(coll)
                    # Case 6
                    elif coll not in mode_enabled_colls:
                        all_disabled_colls.append(coll)
                    # Case 7
                    else:
                        with open("/tmp/error.log", "a+") as myfile:
                            myfile.write("error in get_enabled_plugins > something went grievously wrong in calculating all_enabled_colls\n")
                        myfile.close()
                for coll in all_enabled_colls:
                    with open("/tmp/mode-collector-enable.log", "a+") as myfile:
                        myfile.write("Enabled_Coll: "+coll+"\n")
                    myfile.close()
                for coll in all_disabled_colls:
                    with open("/tmp/mode-collector-enable.log", "a+") as myfile:
                        myfile.write("Disabled_Coll: "+coll+"\n")
                    myfile.close()

                p['collector'] = all_enabled_colls
    except:
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Exception in get_enabled_collectors", sys.exc_info())
        myfile.close()
    return p

# Retrieves plugins that have been enabled in config
# Priority is namespace.template, then modes.template
def get_enabled():
    p = {}
    try:
        # Retrieve configuration enablings/disablings for all containers
        mode_config = get_mode_configs()
        core_config = get_core_configs()
        coll_config = get_collector_configs()
        vis_config = get_visualization_configs()
        plugin_config = get_plugin_configs()

        # Retrieve enabled containers
        enabled_cores = get_enabled_cores(mode_config, core_config)
        enabled_collectors = get_enabled_collectors(mode_config, coll_config)

        ### Enabled Collector Containers ###
        # !! TODO - Mode x Collector

        # !! TODO - Mode x Visualization

        # !! TODO - Mode x Plugin
    except:
        with open("/tmp/error.log", "a+") as myfile:
            myfile.write("Exception in get_enabled_plugins", sys.exc_info())
        myfile.close()
        pass

    return p

"""
Takes in a dict of all installed plugins (see get_installed_plugins())
and a dict of all enabled_plugins (see get_enabled_plugins()).
Returns a MENU dict of plugins that have not been built.
"""
def get_unbuilt_plugins(installed_plugins, enabled_plugins):
    # TODO
    return

# Displays status of all running, not running/built, not built, and disabled plugins
def get_plugin_status():
    running = []
    nrbuilt = []
    notbuilt = []
    disabled = []
    installed = {}
    p = {}

    try:
        # Retrieves running or restarting docker containers and returns a list of "containeridimagename"; i.e. - running
        running = check_output(" { docker ps -a -f status=running & docker ps -a -f status=restarting; } | grep '/' | awk \"{print \$2\$1}\" ", shell=True).split("\n")

        # Retrieves docker containers with status exited, paused, dead, created as "containeridimagename"; i.e. - not running
        nrbuilt = check_output(" { docker ps -a -f status=created & docker ps -a -f status=exited & docker ps -a -f status=paused & docker ps -a -f status=dead; } | grep '/' | awk \"{print \$2\$1}\" ", shell=True).split("\n")
        # !! TODO - Append get_installed_plugins("all"), convert to dict first?
        installed = get_installed_plugins()
        enabled = get_enabled()

        # with open("/tmp/installed.log", "a+") as myfile:
        #     for namespace in installed:
        #         myfile.write("Namespace: "+namespace+" = [")
        #         for plugin in installed[namespace]:
        #             myfile.write(plugin+", ")
        #         myfile.write("]")
        # myfile.close()

        # !! TODO - Enabled/Disabled Plugins
        # !! TODO - Not built plugins
        p['title'] = 'Plugin Status'
        p['subtitle'] = 'Choose a category...'
        p_running = [ {'title': x, 'type': 'INFO', 'command': '' } for x in running if x != ""]
        p_nrbuilt = [ {'title': x, 'type': 'INFO', 'command': '' } for x in nrbuilt if x != ""]
        p['options'] = [ { 'title': "Running", 'subtitle': "Currently running...", 'type': MENU, 'options': p_running },
                         { 'title': "Not Running/Built", 'subtitle': "Built but not currently running...", 'type': MENU, 'options': p_nrbuilt }
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
        config = ConfigParser.RawConfigParser()
        config.read(template_dir+'modes.template')
        plugin_array = config.options("plugins")
        plugins = {}
        for plug in plugin_array:
            plugins[plug] = config.get("plugins", plug)

        p = {}
        p['title'] = 'Vent Settings'
        p['type'] = MENU
        p['subtitle'] = 'Please select a section to configure...'
        p['options'] = [
            { 'title': "Service", 'type': INPUT, 'command': '' },
            { 'title': "Instances", 'type': INPUT, 'command': '' },
            { 'title': "Active Containers", 'type': INPUT, 'command': '' },
            { 'title': "Local Collection", 'type': INPUT, 'command': '' },
            { 'title': "Locally Active", 'type': INPUT, 'command': '' },
            { 'title': "External", 'type': INPUT, 'command': '' },
        ]
        modes.append(p)
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
                confirm()
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
            confirm()
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
                os.system("python2.7 /data/plugin_parser.py add_plugins "+plugin_url)
                os.system("/bin/sh /data/build_images.sh")
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
            { 'title': "RabbitMQ Management Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py aaa-rabbitmq mgmt' },
            { 'title': "RQ Dashboard Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py rq-dashboard mgmt' },
            { 'title': "Elasticsearch Head Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py elasticsearch head' },
            { 'title': "Elasticsearch Marvel Status", 'type': INFO, 'command': 'python2.7 /data/service_urls/get_urls.py elasticsearch marvel' },
            { 'title': "Containers Running", 'type': INFO, 'command': 'docker ps | sed 1d | wc -l' },
            { 'title': "Container Stats", 'type': COMMAND, 'command': "docker ps | awk '{print $NF}' | grep -v NAMES | xargs docker stats" },
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
