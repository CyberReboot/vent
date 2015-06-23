#!/usr/bin/env python2.7

import ConfigParser
import json
import sys
import time

def execute_template(template_type, template_execution, info_name, service_schedule, tool_dict):

    return

def read_template_types(template_type):
    template_path = '/data/templates/'+template_type+'.template'
    info_name = ""
    service_schedule = ""
    tool_dict = {}
    try:
       with open(template_path): pass
       config = ConfigParser.RawConfigParser()
       config.read(template_path)
       sections = config.sections()
       for section in sections:
           instructions = {}
           options = config.options(section)
           for option in options:
               if section == "info" and option == "name":
                   info_name = config.get(section, option)
               elif section == "service" and option == "schedule":
                   service_schedule = config.get(section, option)
               elif section != "info" and section != "service":
                   instructions[option] = config.get(section, option)
           if section != "info" and section != "service":
               tool_dict[section] = []
               tool_dict[section].append(instructions)
    except:
       pass
    print json.dumps(tool_dict)
    return info_name, service_schedule, tool_dict

def main():
    print sys.argv
    # read in templates for plugins, collectors, and visualization
    if len(sys.argv) < 3:
        sys.exit()
    else:
        template_type = sys.argv[1]
        template_execution = sys.argv[2]
        info_name, service_schedule, tool_dict = read_template_types(template_type)
        execute_template(template_type, template_execution, info_name, service_schedule, tool_dict)

if __name__ == "__main__":
    main()
