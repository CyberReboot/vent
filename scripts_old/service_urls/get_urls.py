#!/usr/bin/env python2.7

import ConfigParser
import sys

from subprocess import check_output

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
                 info_dir="/scripts/info_tools/"
                 ):
        self.base_dir = base_dir
        self.collectors_dir = base_dir + collectors_dir
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        self.template_dir = base_dir + template_dir
        self.vis_dir = base_dir + vis_dir
        self.info_dir = info_dir

def url(path_dirs, service, service_type):
    """ Retrieves urls for external configurations of core services """
    url_str = "not running"
    locally_active = []
    try:
        config = ConfigParser.RawConfigParser()
        # needed to preserve case sensitive options
        config.optionxform=str
        config.read(path_dirs.template_dir + "core.template")
        # Check if section exists in config, and if there are any options
        if config.has_section("locally-active") and config.options("locally-active"):
            locally_active = config.options("locally-active")
        local_off_set = False
        for s in locally_active:
            if s == service:
                local_off_set = True
        local_off = None
        if local_off_set:
            local_off = config.get("locally-active", service)
        if local_off == "off":
            external_host = config.get("external", service+"_host")
            if service == "elasticsearch":
                if service_type == "head":
                    url_str = "http://"+external_host+":9200/_plugin/head"
            elif service == "aaa-rabbitmq":
                url_str = "http://"+external_host+":15672 login: guest/guest"
            elif service == "aaa-syslog":
                # !! TODO
                url_str = "external"
                pass
        else:
            if service == "elasticsearch":
                if service_type == "head":
                    url_str = check_output("/scripts/service_urls/get_elasticsearch_head_url.sh")
            elif service == "aaa-rabbitmq":
                url_str = check_output("/scripts/service_urls/get_rabbitmq_url.sh")
            elif service == "aaa-syslog":
                # !! TODO
                pass
            elif service == "rq-dashboard":
                url_str = check_output("/scripts/service_urls/get_rqdashboard_url.sh")
    except Exception as e:
        pass
    return url_str

if __name__ == "__main__": # pragma: no cover
    path_dirs = PathDirs()
    try:
        url_str = url(path_dirs, sys.argv[1], sys.argv[2])
        print(url_str)
    except Exception as e:
        pass
