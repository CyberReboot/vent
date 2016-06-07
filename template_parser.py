#!/usr/bin/env python2.7

import ast
import copy
import ConfigParser
import json
import os
import sys
import time

template_dir = "/var/lib/docker/data/templates/"
plugins_dir = "/var/lib/docker/data/plugins/"

def execute_template(template_type, template_execution, info_name, service_schedule, tool_core, tool_dict, delay_sections):
    # note for plugin, also run core
    # for visualization, make aware of where the data is
    try:
        # !! TODO consider creating a subdirectory
        with open('/tmp/vent_'+template_execution+'.txt', 'a') as f:
            f.write(info_name+"|")
            json.dump(service_schedule, f)
            f.write("|")
            json.dump(tool_core, f)
            f.write("|")
            json.dump(tool_dict, f)
            f.write("|")
            json.dump(delay_sections, f)
            f.write("\n")
    except:
        pass
    return

def read_template_types(template_type):
    # read in templates for plugins, core, and visualization
    template_path = template_dir+template_type+'.template'
    if template_type == "active" or template_type == "passive":
        template_path = template_dir+'collectors.template'

    info_name = ""
    d_path = 0
    service_schedule = {}
    tool_core = {}
    tool_dict = {}

    # special case for visualization
    if template_type == "visualization":
        viz_instructions = {}
        viz_instructions['Image'] = 'visualization/honeycomb'
        viz_instructions['Volumes'] = {"/honeycomb-data": {}}
        viz_instructions['HostConfig'] = {"PublishAllPorts": "true"}
        tool_dict["1visualization-honeycomb"] = viz_instructions

    try:
        delay_sections = {}
        if template_type != "visualization" and template_type != "core" and template_type != "active" and template_type != "passive":
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
                    cmd = ["get_data.py", "none", "/"+tool[plugin]+"-data"]
                    if template_type == plugin or template_type == "all":
                        if len(sections) > 0:
                            for section in sections:
                                instructions = {}
                                core_instructions = {}
                                options = config.options(section)
                                for option in options:
                                    if section == "service" and option == "schedule":
                                        service_schedule[plugin] = json.loads(config.get(section, option))
                                    elif section != "info" and section != "service" and section != "locally-active" and section != "external" and section != "instances" and section != "active-containers" and section != "local-collection":
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
                                            elif option == 'delay':
                                                try:
                                                    delay_sections[section] = option_val
                                                except:
                                                    pass
                                            else:
                                                instructions[option] = option_val
                                            instructions['Image'] = plugin+'/'+tool[plugin]
                                            instructions['Volumes'] = {"/"+tool[plugin]+"-data": {}}
                                            tool_dict[plugin+"-"+tool[plugin]] = instructions
                                if d_path == 1:
                                    core_instructions['Image'] = "visualization/honeycomb"
                                    core_instructions['Cmd'] = cmd
                                    core_instructions['HostConfig'] = {"VolumesFrom":[plugin+"-"+tool[plugin], '1visualization-honeycomb']}
                                    tool_core[plugin+"-"+tool[plugin]+"-core"] = core_instructions
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
            external_overrides = []
            external_hosts = {}
            instances = []
            for section in sections:
                instructions = {}
                options = config.options(section)
                cmd = ["get_data.py", "none", "/"+section+"-data"]
                for option in options:
                    if section == "info" and option == "name":
                        info_name = config.get(section, option)
                    elif section == "service" and option == "schedule":
                        service_schedule[template_type] = json.loads(config.get(section, option))
                    elif section == "instances":
                        instances = config.options(section)
                    elif section == "locally-active":
                        if config.get(section, option) == "off":
                            external_overrides.append(option)
                    elif section != "info" and section != "service" and section != "locally-active" and section != "external" and section != "instances" and section != "active-containers" and section != "local-collection":
                        if not section in external_overrides:
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
                            elif option == 'delay':
                                try:
                                    delay_sections[section] = option_val
                                except:
                                    pass
                            else:
                                # check dependencies like elasticsearch and rabbitmq
                                external_options = config.options("external")
                                if option == "HostConfig":
                                    try:
                                        option_val = option_val.replace("true", "True")
                                        option_val = option_val.replace("false", "False")
                                        host_config = ast.literal_eval(option_val)
                                        host_config_new = copy.deepcopy(host_config)
                                        extra_hosts = []
                                        host_config_new["RestartPolicy"] = { "Name": "always" }
                                        if "Links" in host_config:
                                            for rec in host_config["Links"]:
                                                r = rec.split(":")
                                                for ext in external_overrides:
                                                    if r[1] == ext:
                                                        host_config_new["Links"].remove(rec)
                                                        # add external_overrides to extrahosts
                                                        if r[1]+"_host" in external_options:
                                                            extra_hosts.append(r[1]+":"+config.get("external", r[1]+"_host"))
                                                            host_config_new["ExtraHosts"] = extra_hosts
                                                        else:
                                                            print "no local "+r[1]+" but an external one wasn't specified."
                                            option_val = str(host_config_new).replace("'", '"')
                                            if len(host_config_new["Links"]) == 0:
                                                del host_config_new["Links"]
                                        # add syslog, don't log rmq-es-connector as it will loop itself
                                        if section != "rmq-es-connector" and section != "aaa-syslog" and section != "aaa-redis" and section != "aaa-rabbitmq":
                                            try:
                                                syslog_host = "localhost"
                                                for ext in external_overrides:
                                                    if "aaa_syslog" == ext:
                                                        if "aaa_syslog_host" in external_options:
                                                            syslog_host = config.get("external", "aaa_syslog_host")
                                                        else:
                                                            print "no local syslog but an external one wasn't specified."
                                                host_config_new["LogConfig"] = { "Type": "syslog", "Config": {"tag":"\{\{.ImageName\}\}/\{\{.Name\}\}/\{\{.ID\}\}","syslog-address":"tcp://"+syslog_host} }
                                                option_val = str(host_config_new).replace("'", '"')
                                            except:
                                                pass
                                    except:
                                        pass
                                option_val = option_val.replace("True", "true")
                                option_val = option_val.replace("False", "false")
                                if option_val != "{}":
                                    instructions[option] = option_val
                if d_path == 1:
                    core_instructions = {}
                    core_instructions['Image'] = "visualization/honeycomb"
                    core_instructions['Cmd'] = cmd
                    if "active" in section or "passive" in section:
                        core_instructions['HostConfig'] = {"VolumesFrom":[section, '1visualization-honeycomb']}
                    else:
                        core_instructions['HostConfig'] = {"VolumesFrom":[template_type+"-"+section, '1visualization-honeycomb']}
                    tool_core[template_type+"-"+section+"-core"] = core_instructions
                    d_path = 0
                if section != "info" and section != "service" and section != "locally-active" and section != "external" and section != "instances" and section != "active-containers" and section != "local-collection":
                    if not section in external_overrides:
                        if "active" in section or "passive" in section:
                            if (template_type == "active" and "active" in section) or (template_type == "passive" and "passive" in section):
                                if section in instances:
                                    try:
                                        instance_count = config.get("instances", section)
                                        for i in range(int(instance_count)):
                                            instructions['Image'] = 'core/'+section
                                            instructions['Volumes'] = {"/"+section+"-data": {}}
                                            tool_dict[section+str(i)] = instructions
                                    except:
                                        pass
                                else:
                                    instructions['Image'] = 'core/'+section
                                    instructions['Volumes'] = {"/"+section+"-data": {}}
                                    tool_dict[section] = instructions
                        else:
                            if section in instances:
                                try:
                                    instance_count = config.get("instances", section)
                                    for i in range(int(instance_count)):
                                        instructions['Image'] = template_type+'/'+section
                                        instructions['Volumes'] = {"/"+section+"-data": {}}
                                        tool_dict[template_type+"-"+section+str(i)] = instructions
                                except:
                                    pass
                            else:
                                instructions['Image'] = template_type+'/'+section
                                instructions['Volumes'] = {"/"+section+"-data": {}}
                                tool_dict[template_type+"-"+section] = instructions
        else:
            info_name = "\"all\""
    except:
        pass
    return info_name, service_schedule, tool_core, tool_dict, delay_sections

def main():
    if len(sys.argv) < 3:
        sys.exit()
    else:
        template_type = sys.argv[1]
        template_execution = sys.argv[2]
        if template_execution == "stop":
            os.system("docker ps -a | grep "+template_type+" | awk '{print $1}' | xargs docker kill")
            os.system("docker ps -a | grep "+template_type+" | awk '{print $1}' | xargs docker rm")
        else:
            info_name, service_schedule, tool_core, tool_dict, delay_sections = read_template_types(template_type)
            execute_template(template_type, template_execution, info_name, service_schedule, tool_core, tool_dict, delay_sections)

if __name__ == "__main__":
    main()
