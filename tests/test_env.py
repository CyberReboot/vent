import ConfigParser
import os
import pytest

from vent import plugin_parser

class PathDirs:
    """ Global path directories for parsing templates """
    def __init__(self,
                 base_dir=os.getcwd()+"/",
                 collectors_dir="collectors",
                 core_dir="vent/core",
                 plugins_dir="vent/plugins/",
                 plugin_repos="plugin_repos",
                 template_dir="vent/templates/",
                 vis_dir="visualization",
                 info_dir="scripts/info_tools/",
                 data_dir=os.getcwd()+"/vent/",
                 scripts_dir=os.getcwd()+"/scripts/"):
        self.base_dir = base_dir
        self.collectors_dir = base_dir + collectors_dir
        if not os.path.exists(self.collectors_dir):
            os.makedirs(self.collectors_dir)
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        if not os.path.exists(self.plugin_repos):
            os.makedirs(self.plugin_repos)
        self.template_dir = base_dir + template_dir
        self.vis_dir = base_dir + vis_dir
        if not os.path.exists(self.vis_dir):
            os.makedirs(self.vis_dir)
        self.info_dir = info_dir
        self.data_dir = data_dir
        self.scripts_dir = scripts_dir

class TestEnv():
    """ Class to create the right env for testing - installing plugins, modifying modes.template/core.template, etc... """
    def __init__(self):
        # Create stubs if they don't already exist
        self.initconfigs(PathDirs(), True)

    @staticmethod
    def add_plugin(path_dirs, url):
        plugin_parser.add_plugins(path_dirs, url)

    @staticmethod
    def remove_plugin(path_dirs, url):
        plugin_parser.remove_plugins(path_dirs, url)

    @staticmethod
    def initconfigs(path_dirs, empty):
        """
        Initializes configs: either keeps existing configs & creates blanks if they don't exist or
        creates dummy configs with populated values
        """
        open(path_dirs.template_dir+"modes.template", "a+").close()
        open(path_dirs.template_dir+"core.template", "a+").close()
        open(path_dirs.template_dir+"visualization.template", "a+").close()
        if not empty:
            config = ConfigParser.RawConfigParser()

            # Write to modes.template
            config.add_section('plugins')
            config.set('plugins', 'core', 'all')

            with open(path_dirs.template_dir+'modes.template', 'wb') as configfile:
                config.write(configfile)

            # Write to core.template
            # Need to reset info stored in config stream so we don't write information for modes into core
            config = ConfigParser.RawConfigParser()
            config.add_section('info')
            config.set('info', 'name', 'Core')
            config.add_section('service')
            config.set('service', 'schedule', '{"all":"continuous"}')
            config.add_section('instances')
            config.set('instances', 'rq-worker', '2')
            config.add_section('active-containers')
            config.set('active-containers', 'count', '20')
            config.add_section('local-collection')
            config.set('local-collection', 'passive', 'on')
            config.set('local-collection', 'active', 'off')
            config.add_section('locally-active')
            config.set('locally-active', 'rmq-es-connector', 'off')
            config.set('locally-active', 'aaa-redis', 'on')

            with open(path_dirs.template_dir+'core.template', 'wb') as configfile:
                config.write(configfile)

            # Write to visualization.template
            # Reset stream
            config = ConfigParser.RawConfigParser()
            config.add_section('info')
            config.set('info', 'name', 'visualization')
            config.add_section('service')
            config.set('service', 'schedule', '{"all":"continuous"}')
            config.add_section('honeycomb')
            config.set('honeycomb', 'Cmd', '""')

    @staticmethod
    def modifyconfigs(path_dirs, new_conf):
        """
        Takes in paths to templates, and a dictionary indexed (by config name)
        list of tuples that describe the section name, option, and value.
        FORMAT: {'modes.template': [ (section, option, value), (section, option2, value)...] },
                {'core.template': [ (section, option, value), (section2, option, value)...] }
        """
        for template in new_conf:
            config = ConfigParser.RawConfigParser()
            config.read(path_dirs.template_dir+template)
            for (section, option, value) in new_conf[template]:
                if not config.has_section(section):
                    config.add_section(section)
                config.set(section, option, value)
            with open(path_dirs.template_dir+template, 'w') as configfile:
                config.write(configfile)
