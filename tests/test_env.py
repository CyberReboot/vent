import ConfigParser
import os
import pytest

from .. import plugin_parser

class TestEnv():
    """ Class to create the right env for testing - installing plugins, modifying modes.template/core.template, etc... """
    def __init__(self):
        # Create stubs if they don't already exist
        self.initconfigs(menu_launcher.PathDirs(), True)

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
    def modifyconfigs(path_dirs, template, new_conf):
        """
        Takes in paths to templates, specific template to modify, and
        a list of tuples that describe the section name, option, and value.
        FORMAT: [ (section, option, value), (section, option2, value)...]
        """
        config = ConfigParser.RawConfigParser()
        config.read(path_dirs.template_dir+template)   
        for (section, option, value) in new_conf:
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, option, value)
        with open(path_dirs.template_dir+template, 'w') as configfile:
            config.write(configfile)