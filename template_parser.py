#!/usr/bin/env python2.7

import ConfigParser
import json
import os
import sys
import time

template_dir = "/data/templates/"
plugins_dir = "/data/plugins/"

def execute_template(template_type, template_execution, info_name, service_schedule, tool_dict):
    # note for plugin, also run collector
    # for visualization, make aware of where the data is
    print info_name
    print service_schedule
    try:
        with open('/tmp/vent-'+template_execution+'.txt', 'a') as f:
            json.dump(tool_dict, f)
            f.write("\n")
    except:
        pass
    return

def read_template_types(template_type):
    # read in templates for plugins, collectors, and visualization
    template_path = template_dir+template_type+'.template'
    info_name = ""
    service_schedule = {}
    tool_dict = {}
    try:
        if template_type != "visualization" and template_type != "collectors":
            config = ConfigParser.RawConfigParser()
            config.read(template_dir+'modes.template')
            plugin_array = config.options("plugins")
            plugins = {}
            for plug in plugin_array:
                plugins[plug] = config.get("plugins", plug)

            t = []
            for plugin in plugins:
                if plugins[plugin] == 'all':
                    tools = [ name for name in os.listdir(plugins_dir+plugin) if os.path.isdir(os.path.join(plugins_dir+plugin, name)) ]
                    for tool in tools:
                        t.append({plugin:tool})
                else:
                    for tool in plugins[plugin].split(","):
                        t.append({plugin:tool})

            for tool in t:
                for plugin in tool:
                    if template_type == plugin or template_type == "all":
                        config = ConfigParser.RawConfigParser()
                        config.read(template_dir+plugin+'.template')
                        sections = config.sections()
                        for section in sections:
                            options = config.options(section)
                            for option in options:
                                if section == "service" and option == "schedule":
                                    service_schedule[plugin] = config.get(section, option)
                        tool_dict[plugin+"-"+tool[plugin]] = []
                        instructions = {}
                        instructions['Image'] = plugin+'/'+tool[plugin]
                        tool_dict[plugin+"-"+tool[plugin]].append(instructions)

        if template_type != "all":
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
                        service_schedule[template_type] = config.get(section, option)
                    elif section != "info" and section != "service":
                        instructions[option] = config.get(section, option)
                if template_type == "visualization" or template_type == "collectors":
                    if section != "info" and section != "service":
                        instructions['Image'] = template_type+'/'+section
                        if not template_type+"-"+section in tool_dict:
                            tool_dict[template_type+"-"+section] = []
                        tool_dict[template_type+"-"+section].append(instructions)
        else:
            info_name = "all"
    except:
        pass
    return info_name, service_schedule, tool_dict

def main():
    if len(sys.argv) < 3:
        sys.exit()
    else:
        template_type = sys.argv[1]
        template_execution = sys.argv[2]
        info_name, service_schedule, tool_dict = read_template_types(template_type)
        execute_template(template_type, template_execution, info_name, service_schedule, tool_dict)

if __name__ == "__main__":
    main()
