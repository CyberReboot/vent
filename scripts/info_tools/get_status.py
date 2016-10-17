#!/usr/bin/env python2.7

import ConfigParser

import argparse
import os
import sys

from subprocess import call, check_output, PIPE, Popen

class PathDirs:
    """ Global path directories for parsing templates """
    def __init__(self,
                 base_dir="/var/lib/docker/data/",
                 collectors_dir="collectors",
                 core_dir="core",
                 plugins_dir="plugins/",
                 plugin_repos="plugin_repos",
                 template_dir="templates/",
                 vis_dir="visualization",
                 info_dir="/scripts/info_tools/",
                 data_dir="/vent/"
                 ):
        self.base_dir = base_dir
        self.collectors_dir = base_dir + collectors_dir
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        self.template_dir = base_dir + template_dir
        self.vis_dir = base_dir + vis_dir
        self.info_dir = info_dir
        self.data_dir = data_dir

def add_override_options(parser, path_dirs):
    """ Get arguments for overriding path_dirs"""
    parser.add_argument('-b', '--base_dir', default=path_dirs.base_dir, action='store', dest='base_dir', help='base directory to override')
    parser.add_argument('-i', '--info_dir', default=path_dirs.info_dir, action='store', dest='info_dir', help='info directory to override')
    parser.add_argument('-d', '--data_dir', default=path_dirs.data_dir, action='store', dest='data_dir', help='data directory to override')

def add_all_installed_options(subparsers, path_dirs):
    """ Subparser for get_all_installed """
    installed_parser = subparsers.add_parser('installed', help='all installed')
    add_override_options(installed_parser, path_dirs)

def add_core_config_options(subparsers, path_dirs):
    """ Subparser for get_core_config """
    config_parser = subparsers.add_parser('cconfig', help='configuration of core.template')
    add_override_options(config_parser, path_dirs)

def add_installed_collectors_options(subparsers, path_dirs):
    """ Subparser & mutEx group for get_installed_collectors by collector types """
    collector_parser = subparsers.add_parser('collectors', help='installed collectors')
    add_override_options(collector_parser, path_dirs)
    # Should only be able to pick all, passive, or active
    c_type = collector_parser.add_mutually_exclusive_group(required=False)
    c_type.add_argument('-all', '--all', default=False, action='store_true', dest='c_all', help='List all collectors')
    c_type.add_argument('-passive', '--passive', default=False, action='store_true', dest='c_passive', help='List passive collectors')
    c_type.add_argument('-active', '--active', default=False, action='store_true', dest='c_active', help='List active collectors')

def add_installed_cores_options(subparsers, path_dirs):
    """ Subparser for get_installed_cores """
    core_parser = subparsers.add_parser('cores', help='installed cores')
    add_override_options(core_parser, path_dirs)

def add_core_enabled_options(subparsers, path_dirs):
    """ Subparser for get_core_enabled """
    enabled_parser = subparsers.add_parser('cenabled', help='core enabled/disabled images')
    add_override_options(enabled_parser, path_dirs)

def add_enabled_options(subparsers, path_dirs):
    """ Subparser for get_enabled """
    enabled_parser = subparsers.add_parser('enabled', help='all enabled/disabled services')
    add_override_options(enabled_parser, path_dirs)

def add_mode_config_options(subparsers, path_dirs):
    config_parser = subparsers.add_parser('mconfig', help='configuration of modes.template')
    add_override_options(config_parser, path_dirs)

def add_mode_enabled_options(subparsers, path_dirs):
    """ Subparser for get_mode_enabled """
    enabled_parser = subparsers.add_parser('menabled', help='mode enabled images')
    add_override_options(enabled_parser, path_dirs)

def add_installed_plugins_options(subparsers, path_dirs):
    """ Subparser for get_installed_plugins """
    plugin_parser = subparsers.add_parser('plugins', help='installed plugins')
    add_override_options(plugin_parser,path_dirs)

def add_installed_vis_options(subparsers, path_dirs):
    """ Subparser for get_installed_vis """
    vis_parser = subparsers.add_parser('vis', help='installed visualizations')
    add_override_options(vis_parser, path_dirs)

def add_installed_repos_options(subparsers, path_dirs):
    """ Subparser for get_installed_plugins """
    plugin_parser = subparsers.add_parser('repos', help='installed plugin repos')
    add_override_options(plugin_parser,path_dirs)

def add_external_options(subparsers, path_dirs):
    """ Subparser for get_external """
    extconf_parser = subparsers.add_parser('external', help='services set to run externally')
    add_override_options(extconf_parser, path_dirs)

def add_status_options(subparsers, path_dirs):
    """ Subparser for get_status """
    status_parser = subparsers.add_parser('all', help='all status information')
    add_override_options(status_parser, path_dirs)

# Parses modes.template and returns a dict containing all specifically enabled containers
# Returns dict along the format of: {'namespace': ["all"], 'namespace2': [""], 'namespace3': ["plug1", "plug2"]}
def get_mode_config(path_dirs):
    # Parsing modes.template
    modes = {}
    try:
        config = ConfigParser.RawConfigParser()
        # needed to preserve case sensitive options
        config.optionxform=str
        config.read(path_dirs.template_dir+'modes.template')
        # Check if any runtime configurations
        if config.has_section("plugins"):
            plugin_array = config.options("plugins")
            # Check if there are any options
            if plugin_array:
                for plug in plugin_array:
                    modes[plug] = config.get("plugins", plug).replace(" ", "").split(",")
        # If not then there are no special runtime configurations and modes is empty
    except Exception as e: # pragma: no cover
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_mode_config")

    return modes

# Parses core.template to get all runtime configurations for enabling/disabling cores
# Returns dict along the format of: {'passive': "on", 'active': "on", 'aaa-redis': "off"}
def get_core_config(path_dirs):
    # Parsing core.template
    cores = {}
    try:
        config = ConfigParser.RawConfigParser()
        # needed to preserve case sensitive options
        config.optionxform=str
        config.read(path_dirs.template_dir+'core.template')
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
            if passive in ["on", "off"]:
                cores['passive'] = passive
            if active in ["on", "off"]:
                cores['active'] = active
        # If not then everything is enabled and cores is empty

        # Check if any run-time configurations for core
        if config.has_section("locally-active"):
            active_array = config.options("locally-active")
            # Check if there are any options
            if active_array:
                for option in active_array:
                    cores[option] = config.get("locally-active", option).replace(" ", "")
        # If not then everything is enabled and cores is empty
    except Exception as e: # pragma: no cover
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_core_config")

    return cores

# Retrieves installed cores
# Returns list: ["core1", "core2", "core3"]
def get_installed_cores(path_dirs):
    cores = []
    try:
        # Get all cores
        cores = [ core for core in os.listdir(path_dirs.core_dir) if os.path.isdir(os.path.join(path_dirs.core_dir, core)) ]
    except Exception as e:
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_installed_cores")

    return cores

# Retrieves installed collectors by category: active, passive, or both (all)
# Returns list: ["coll1", "coll2", "coll3"]
def get_installed_collectors(path_dirs, c_type):
    colls = []
    try:
        # Get all collectors
        collectors = [ collector for collector in os.listdir(path_dirs.collectors_dir) if os.path.isdir(os.path.join(path_dirs.collectors_dir, collector)) ]

        # Filter by passive/active/all
        if c_type == "passive":
            colls = [ collector for collector in collectors if "passive-" in collector ]
        elif c_type == "active":
            colls = [ collector for collector in collectors if "active-" in collector ]
        elif c_type == "all":
            colls = collectors
        else:
            with open("/tmp/error.log", "a+") as myfile:
                myfile.write("Error in get_installed_collectors\n" + "Invalid collector parameter: " + str(c_type))
            myfile.close()
    except Exception as e:
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_installed_collectors")

    return colls

# Retrieves installed visualizations
# Returns list: ["vis1", "vis2", "vis3"]
def get_installed_vis(path_dirs):
    vis = []
    try:
        # Get all visualizations
        vis = [ visualization for visualization in os.listdir(path_dirs.vis_dir) if os.path.isdir(os.path.join(path_dirs.vis_dir, visualization)) ]
    except Exception as e:
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_installed_vis")

    return vis

# Retrieves all plugins by namespace; e.g. - features/tcpdump || features/hexparser
# Note returns a dict of format: {'namespace': [p1, p2, p3, ...], 'namespace2': [p1, p2, p3, ...]}
def get_installed_plugins(path_dirs):
    p = {}
    try:
        # Get all namespaces
        namespaces = [ namespace for namespace in os.listdir(path_dirs.plugins_dir) if os.path.isdir(os.path.join(path_dirs.plugins_dir, namespace)) ]

        # For each namespace, retrieve all plugins and index by namespace
        for namespace in namespaces:
            p[namespace] = [ plugin for plugin in os.listdir(path_dirs.plugins_dir+namespace) if os.path.isdir(os.path.join(path_dirs.plugins_dir+namespace, plugin)) ]
    except Exception as e:
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_installed_plugins")

    return p

def get_installed_repos(path_dirs):
    try:
        return [ plugin_repo for plugin_repo in os.listdir(path_dirs.plugin_repos) if os.path.isdir(os.path.join(path_dirs.plugin_repos, plugin_repo)) ]
    except Exception as e:
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_installed_repos")

def get_all_installed(path_dirs):
    """
    Returns all installed containers as a dict, and each subset separately.
    {'cores':["core1", "core2"], 'collectors':["coll1", "coll2"]}
    """
    all_installed = {}
    try:
        # Get each set of containers by type
        all_cores = get_installed_cores(path_dirs)
        all_colls = get_installed_collectors(path_dirs, "all")
        all_vis = get_installed_vis(path_dirs)

        # Note - Dictionary
        all_plugins = get_installed_plugins(path_dirs)

        all_installed['core'] = all_cores
        all_installed['collectors'] = all_colls
        all_installed['visualization'] = all_vis

        # Check if all_plugins is empty
        if all_plugins:
            all_installed.update(all_plugins)
    except Exception as e: # pragma: no cover
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_all_installed")

    return all_installed, all_cores, all_colls, all_vis, all_plugins

def get_mode_enabled(path_dirs, mode_config):
    """ Returns all images enabled from modes.template """
    mode_enabled = {}
    try:
        all_installed, all_cores, all_colls, all_vis, all_plugins = get_all_installed(path_dirs)

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
                elif val in [["none"], [""]]:
                    core_enabled = []
                else:
                    core_enabled = val
            # if not, then no runtime config for core, use all
            else:
                core_enabled = all_cores

            # check if collectors has a specification in mode_config
            if "collectors" in mode_config.keys():
                val = mode_config['collectors']
                # val is either: ["all"] or ["none"]/[""] or ["coll1", "coll2", etc...]
                if val == ["all"]:
                    coll_enabled = all_colls
                elif val in [["none"], [""]]:
                    coll_enabled = []
                else:
                    coll_enabled = val
            # if not, then no runtime config for coll, use all
            else:
                coll_enabled = all_colls

            # check if visualizations has a specification in mode_config
            if "visualization" in mode_config.keys():
                val = mode_config['visualization']
                # val is either: ["all"] or ["none"]/[""] or ["coll1", "coll2", etc...]
                if val == ["all"]:
                    vis_enabled = all_vis
                elif val in [["none"], [""]]:
                    vis_enabled = []
                else:
                    vis_enabled = val
            # if not, then no runtime config for vis, use all
            else:
                vis_enabled = all_vis

            # plugins
            for namespace in mode_config.keys():
                if namespace not in ["visualization", "collectors", "core"]:
                    val = mode_config[namespace]
                    # val is either: ["all"] or ["none"]/[""] or ["some", "some2", etc...]
                    if val == ["all"]:
                        if namespace in all_plugins:
                            mode_enabled[namespace] = all_plugins[namespace]
                    elif val in [["none"], [""]]:
                        mode_enabled[namespace] = []
                    else:
                        mode_enabled[namespace] = val

            # if certain plugin namespaces have been omitted from the modes.template file
            # then no special runtime config and use all
            for namespace in all_plugins:
                if namespace not in mode_enabled:
                    mode_enabled[namespace] = all_plugins[namespace]

            mode_enabled['core'] = core_enabled
            mode_enabled['collectors'] = coll_enabled
            mode_enabled['visualization'] = vis_enabled
    except Exception as e:
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_mode_enabled")

    return mode_enabled

def get_core_enabled(path_dirs, core_config):
    """ Returns all enabled and disabled images from core.template """
    core_enabled = {}
    core_disabled = {}
    try:
        passive_colls = get_installed_collectors(path_dirs, "passive")
        active_colls = get_installed_collectors(path_dirs, "active")
        coll_enabled = []
        coll_disabled = []
        # only if not empty
        if core_config:
            ### Local-Collection ###
            # Check passive/active settings
            # Default all on
            p_colls = passive_colls
            a_colls = active_colls

            if 'passive' in core_config.keys() and core_config['passive'] == "off":
                    p_colls = []
            if 'active' in core_config.keys() and core_config['active'] == "off":
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

            ### Locally-Active ###
            # Check locally-active settings
            # Get all keys (containers) that are turned off
            locally_disabled = [ key for key in core_config if key not in ['passive', 'active'] and core_config[key] == "off" ]
            # Get all keys (containers) that are turned on
            locally_enabled = [ key for key in core_config if key not in ['passive', 'active'] and core_config[key] == "on" ]

            core_enabled['collectors'] = coll_enabled
            core_enabled['core'] = locally_enabled
            core_disabled['collectors'] = coll_disabled
            core_disabled['core'] = locally_disabled
    except Exception as e:
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_core_enabled")

    return core_enabled, core_disabled

def get_enabled(path_dirs):
    """ Returns containers that have been enabled/disabled by config """
    enabled = {}
    disabled = []
    try:
        # Retrieve configuration enablings/disablings for all containers
        mode_config = get_mode_config(path_dirs)
        core_config = get_core_config(path_dirs)

        # Retrieve containers enabled by mode
        # Note - mode_enabled and its complement form the complete set of containers
        mode_enabled = get_mode_enabled(path_dirs, mode_config)

        # Retrieve containers enabled/disabled by core
        # Note - the union of core_enabled and core_disabled DO NOT form the complete set of containers
        core_enabled, core_disabled = get_core_enabled(path_dirs, core_config)

        # The complete set of containers
        all_installed = get_all_installed(path_dirs)[0]

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
            if namespace in mode_enabled.keys() and namespace in core_enabled.keys():
                for container in all_installed[namespace]:
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
                            with open("/tmp/error.log", "a+") as myfile:
                                myfile.write("get_enabled error: Case 7 reached!\n")
            else:
            # For 'visualizations' & all plugin namespaces
                for container in all_installed[namespace]:
                    if namespace in mode_enabled:
                        # Case 5
                        if container in mode_enabled[namespace]:
                            all_enabled[namespace].append(container)
                        # Case 6
                        elif container not in mode_enabled[namespace]:
                            all_disabled[namespace].append(container)
                        # Case 7
                        else:
                            with open("/tmp/error.log", "a+") as myfile:
                                myfile.write("get_enabled error: Case 7 reached!\n")

        enabled = all_enabled
        disabled = all_disabled
    except Exception as e:
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_enabled")

    return enabled, disabled

def get_external(path_dirs):
    """ Returns all images that should be running externally """
    # returned in format {'elasticsearch': 'off', etc...}
    extconf = {}

    try:
        ### Parse core.template to find any services set to run externally ###
        config = ConfigParser.RawConfigParser()
        # needed to preserve case sensitive options
        config.optionxform=str
        config.read(path_dirs.template_dir+'core.template')
        # check section exists
        if config.has_section("external"):
            # check if there are any options
            if config.options("external"):
                for option in config.options("external"):
                    extconf[option] = config.get("external", option)
    except Exception as e:
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_external")

    return extconf

def get_status(path_dirs):
    """ Displays status of all running, not running/built, not built, and disabled plugins """
    plugins = {}

    try:
        ### Get All Installed Images (By Filewalk) ###
        all_installed, all_cores, all_colls, all_vis, all_plugins = get_all_installed(path_dirs)

        ### Get Enabled/Disabled Images ###
        # Retrieves all enabled images
        enabled, disabled = get_enabled(path_dirs)

        # Make a list of disabled images of format: namespace/image
        disabled_images = []

        for namespace in disabled:
            for image in disabled[namespace]:
                disabled_images.append(namespace+'/'+image)

        ### Get Disabled Containers ###
        # Need to cross reference with all installed containers to determine all disabled containers
        disabled_containers = []

        containers = check_output(" docker ps -a | grep '/' | awk \"{print \$NF}\" ", shell=True).split("\n")
        containers = [ container for container in containers if container != "" ]

        # Intersect the set of all containers with the set of all disabled images
        # Images form the basis for a container (in name especially), but there can be multiple containers per image
        for container in containers:
            for namespace in disabled:
                for image in disabled[namespace]:
                    if image in container:
                        disabled_containers.append(container)

        ### Get all Running Containers, not including disabled containers ###
        # Retrieves running or restarting docker containers and returns a list of container names
        running = check_output(" { docker ps -af status=running & docker ps -af status=restarting; } | grep '/' | awk \"{print \$NF}\" ", shell=True).split("\n")
        running = [ container for container in running if container != "" ]

        # Running containers should not intersect with disabled containers/images.
        # Containers should not exist/be running if disabled
        running_errors = [ container for container in running if container in disabled_containers ]
        running = [ container for container in running if container not in disabled_containers ]

        ### Get all NR Containers, not including disabled containers ###
        # Retrieves docker containers with status exited, paused, dead, created; returns as a list of container names
        nrcontainers = check_output(" { docker ps -af status=created & docker ps -af status=exited & docker ps -af status=paused & docker ps -af status=dead; } | grep '/' | awk \"{print \$NF}\" ", shell=True).split("\n")
        nrcontainers = [ container for container in nrcontainers if container != "" ]
        # Containers should not exist if disabled
        nr_errors = [ container for container in nrcontainers if container in disabled_containers ]
        nrbuilt = [ container for container in nrcontainers if container not in disabled_containers ]

        ### Get all Built Images, not including disabled images ###
        # Retrieve all built docker images
        built = check_output(" docker images | grep '/' | awk \"{print \$1}\" ", shell=True).split("\n")
        built = [ image for image in built if image != "" ]
        # Image *should* be removed if disabled
        built_errors = [ image for image in built if image in disabled_images ]

        ### Get all Not Built Images, not including disabled images ###
        # If image hasn't been disabled and isn't present in docker images then add
        notbuilt = []
        for namespace in all_installed:
            for image in all_installed[namespace]:
                if namespace in disabled and image not in disabled[namespace] and namespace+'/'+image not in built:
                    notbuilt.append(namespace+'/'+image)

        ### Get Externally Running Services ###
        external = {}
        external = get_external(path_dirs)

        plugins['Running'] = running
        plugins['Not Running'] = nrbuilt
        plugins['Built'] = built
        plugins['Disabled Containers'] = disabled_containers
        plugins['Disabled Images'] = disabled_images
        plugins['Not Built'] = notbuilt
        plugins['External'] = external
        plugins['Running Errors'] = running_errors
        plugins['Not Running Errors'] = nr_errors
        plugins['Built Errors'] = built_errors

    except Exception as e:
        with open('/tmp/error.log', 'a+') as myfile:
            myfile.write("Error - get_status.py: get_status")

    return plugins

def main(path_dirs, parser, args):
    """ Calls the appropriate function and prints to stdout """
    status = None

    try:
        # Set to whatever values are given in args
        if args.base_dir:
            path_dirs = PathDirs(base_dir=args.base_dir)
        if args.info_dir:
            path_dirs.info_dir = args.info_dir
        if args.data_dir:
            path_dirs.data_dir = args.data_dir

        if args.cmd == "all":
            status = get_status(path_dirs)
        elif args.cmd == "cconfig":
            status = get_core_config(path_dirs)
        elif args.cmd == "cenabled":
            core_config = get_core_config(path_dirs)
            status = get_core_enabled(path_dirs, core_config)
        elif args.cmd == "collectors":
            if args.c_all:
                status = get_installed_collectors(path_dirs, "all")
            elif args.c_passive:
                status = get_installed_collectors(path_dirs, "passive")
            elif args.c_active:
                status = get_installed_collectors(path_dirs, "active")
        elif args.cmd == "cores":
            status = get_installed_cores(path_dirs)
        elif args.cmd == "enabled":
            status = get_enabled(path_dirs)
        elif args.cmd == "installed":
            status = get_all_installed(path_dirs)
        elif args.cmd == "mconfig":
            status = get_mode_config(path_dirs)
        elif args.cmd == "menabled":
            mode_config = get_mode_config(path_dirs)
            status = get_mode_enabled(path_dirs, mode_config)
        elif args.cmd == "plugins":
            status = get_installed_plugins(path_dirs)
        elif args.cmd == "vis":
            status = get_installed_vis(path_dirs)
        elif args.cmd == "repos":
            status = get_installed_repos(path_dirs)
        elif args.cmd == "external":
            status = get_external(path_dirs)
        else:
            parser.print_help()

    except Exception as e:
        pass

    print(status)

if __name__ == "__main__":
    try:
        # Initiate default PathDirs
        path_dirs = PathDirs()

        """
        Argparse
        Options: all, cconfig, cenabled, collectors, cores,
                 enabled, installed, mconfig, menabled, plugins, vis
        """
        parser = argparse.ArgumentParser(prog='get_status')
        subparsers = parser.add_subparsers(help='Get status of: ', dest='cmd')
        add_status_options(subparsers, path_dirs)
        add_core_config_options(subparsers, path_dirs)
        add_core_enabled_options(subparsers, path_dirs)
        add_installed_collectors_options(subparsers, path_dirs)
        add_installed_cores_options(subparsers, path_dirs)
        add_enabled_options(subparsers, path_dirs)
        add_all_installed_options(subparsers, path_dirs)
        add_mode_config_options(subparsers, path_dirs)
        add_mode_enabled_options(subparsers, path_dirs)
        add_installed_plugins_options(subparsers, path_dirs)
        add_installed_repos_options(subparsers, path_dirs)
        add_installed_vis_options(subparsers, path_dirs)
        add_external_options(subparsers, path_dirs)


        args = parser.parse_args()
        # If no values provided, set get_status as default
        if not args:
            args.cmd = "all"
        else:
            # Collectors was called
            if "c_all" in args:
                # No args were passed, default to all collectors
                # Note if invalid flags are passive like --pass, this defaults to all
                if not args.c_all and not args.c_passive and not args.c_active:
                    args.c_all = True
        # After modifying args, call main
        main(path_dirs, parser, args)
    except Exception as e:
        pass
