#!/usr/bin/env python2.7

import ConfigParser
import sys

from subprocess import check_output

def url(service, service_type):
    """ Retrieves urls for external configurations of core services """
    url_str = "not running"
    locally_active = []
    try:
        config = ConfigParser.RawConfigParser()
        config.read("/var/lib/docker/data/templates/core.template")
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
                elif service_type == "marvel":
                    url_str = "http://"+external_host+":9200/_plugin/marvel"
            elif service == "aaa-rabbitmq":
                url_str = "http://"+external_host+":15672 login: guest/guest"
            elif service == "aaa-syslog":
                # !! TODO
                url_str = "external"
                pass
        else:
            if service == "elasticsearch":
                if service_type == "head":
                    url_str = check_output("/data/service_urls/get_elasticsearch_head_url.sh")
                elif service_type == "marvel":
                    url_str = check_output("/data/service_urls/get_elasticsearch_marvel_url.sh")
            elif service == "aaa-rabbitmq":
                url_str = check_output("/data/service_urls/get_rabbitmq_url.sh")
            elif service == "aaa-syslog":
                # !! TODO
                pass
            elif service == "rq-dashboard":
                url_str = check_output("/data/service_urls/get_rqdashboard_url.sh")
    except Exception as e:
        pass
    return url_str

if __name__ == "__main__": # pragma: no cover
    try:
        url_str = url(sys.argv[1], sys.argv[2])
        print url_str
    except Exception as e:
        pass
