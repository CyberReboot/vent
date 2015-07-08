#!/usr/bin/env python2.7

import ConfigParser
import json
import os
import sys
import time

template_dir = "/data/templates/"
plugins_dir = "/data/plugins/"

def execute_template(template_type, template_execution, info_name, service_schedule, tool_collectors, tool_dict):
    # note for plugin, also run collector
    # for visualization, make aware of where the data is
    try:
        # !! TODO consider creating a subdirectory
        with open('/tmp/vent_'+template_execution+'.txt', 'a') as f:
            f.write(info_name+"|")
            json.dump(service_schedule, f)
            f.write("|")
            json.dump(tool_collectors, f)
            f.write("|")
            json.dump(tool_dict, f)
            f.write("\n")
    except:
        pass
    return

def read_template_types(template_type):
    # read in templates for plugins, collectors, and visualization
    template_path = template_dir+template_type+'.template'
    info_name = ""
    d_path = 0
    service_schedule = {}
    tool_collectors = {}
    tool_dict = {}

    # special case for visualization
    viz_instructions = {}
    viz_instructions['Image'] = 'visualization/honeycomb'
    viz_instructions['Volumes'] = {"/honeycomb-data": {}}
    viz_instructions['HostConfig'] = {"PublishAllPorts": "true"}
    tool_dict["1visualization-honeycomb"] = viz_instructions

    try:
        if template_type != "visualization" and template_type != "collectors":
            config = ConfigParser.RawConfigParser()
            # needed to preserve case sensitive options
            config.optionxform=str
            config.read(template_dir+'modes.template')
            plugin_array = config.options("plugins")
            plugins = {}
            if template_type == "all":
                for plug in plugin_array:
                    plugins[plug] = config.get("plugins", plug)
            else:
                plugins[template_type] = config.get("plugins", template_type)

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
                keys = list(set(tool.keys()))
                for plugin in keys:
                    config = ConfigParser.RawConfigParser()
                    # needed to preserve case sensitive options
                    config.optionxform=str
                    config.read(template_dir+plugin+'.template')
                    sections = config.sections()
                    cmd = ["get_data.py", "/"+tool[plugin]+"-data"]
                    if template_type == plugin or template_type == "all":
                        if len(sections) > 0:
                            for section in sections:
                                instructions = {}
                                collector_instructions = {}
                                options = config.options(section)
                                for option in options:
                                    if section == "service" and option == "schedule":
                                        service_schedule[plugin] = json.loads(config.get(section, option))
                                    elif section != "info" and section != "service":
                                        if section == tool[plugin]:
                                            option_val = config.get(section, option)
                                            try:
                                                option_val = int(option_val)
                                            except:
                                                pass
                                            if option == 'data_path':
                                                if len(cmd) == 4:
                                                    cmd.insert(1, option_val)
                                                else:
                                                    cmd.append(option_val)
                                                d_path = 1
                                            elif option == 'site_path':
                                                if len(cmd) == 2:
                                                    cmd.append("")
                                                    cmd.append(option_val)
                                                else:
                                                    cmd.append(option_val)
                                            else:
                                                instructions[option] = option_val
                                            instructions['Image'] = plugin+'/'+tool[plugin]
                                            instructions['Volumes'] = {"/"+tool[plugin]+"-data": {}}
                                            tool_dict[plugin+"-"+tool[plugin]] = instructions
                                if d_path == 1:
                                    collector_instructions['Image'] = "visualization/honeycomb"
                                    collector_instructions['Cmd'] = cmd
                                    collector_instructions['HostConfig'] = {"VolumesFrom":[plugin+"-"+tool[plugin], '1visualization-honeycomb']}
                                    tool_collectors[plugin+"-"+tool[plugin]+"-collector"] = collector_instructions
                                    d_path = 0
                                if not (plugin+"-"+tool[plugin]) in tool_dict:
                                    instructions['Image'] = plugin+'/'+tool[plugin]
                                    instructions['Volumes'] = {"/"+tool[plugin]+"-data": {}}
                                    tool_dict[plugin+"-"+tool[plugin]] = instructions
                        else:
                            instructions = {}
                            instructions['Image'] = plugin+'/'+tool[plugin]
                            instructions['Volumes'] = {"/"+tool[plugin]+"-data": {}}
                            tool_dict[plugin+"-"+tool[plugin]] = instructions

        if template_type != "all":
            with open(template_path): pass
            config = ConfigParser.RawConfigParser()
            # needed to preserve case sensitive options
            config.optionxform=str
            config.read(template_path)
            sections = config.sections()
            for section in sections:
                instructions = {}
                options = config.options(section)
                cmd = ["get_data.py", "/"+section+"-data"]
                for option in options:
                    if section == "info" and option == "name":
                        info_name = config.get(section, option)
                    elif section == "service" and option == "schedule":
                        service_schedule[template_type] = json.loads(config.get(section, option))
                    elif section != "info" and section != "service":
                        option_val = config.get(section, option)
                        try:
                            option_val = int(option_val)
                        except:
                            pass
                        if option == 'data_path':
                            if len(cmd) == 4:
                                cmd.insert(1, option_val)
                            else:
                                cmd.append(option_val)
                            d_path = 1
                        elif option == 'site_path':
                            if len(cmd) == 2:
                                cmd.append("")
                                cmd.append(option_val)
                            else:
                                cmd.append(option_val)
                        else:
                            instructions[option] = option_val
                if d_path == 1:
                    collector_instructions['Image'] = "visualization/honeycomb"
                    collector_instructions['Cmd'] = cmd
                    collector_instructions['HostConfig'] = {"VolumesFrom":[template_type+"-"+section, '1visualization-honeycomb']}
                    tool_collectors[template_type+"-"+section+"-collector"] = collector_instructions
                    d_path = 0
                if section != "info" and section != "service":
                    instructions['Image'] = template_type+'/'+section
                    instructions['Volumes'] = {"/"+section+"-data": {}}
                    tool_dict[template_type+"-"+section] = instructions
        else:
            info_name = "\"all\""
    except:
        pass
    return info_name, service_schedule, tool_collectors, tool_dict

def main():
    if len(sys.argv) < 3:
        sys.exit()
    else:
        template_type = sys.argv[1]
        template_execution = sys.argv[2]
        info_name, service_schedule, tool_collectors, tool_dict = read_template_types(template_type)
        execute_template(template_type, template_execution, info_name, service_schedule, tool_collectors, tool_dict)

if __name__ == "__main__":
    main()
