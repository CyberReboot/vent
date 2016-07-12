#!/usr/bin/env python2.7

import ast
import copy
import ConfigParser
import json
import os
import subprocess
import sys
import time

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
                 info_dir="/data/info_tools/"
                 ):
        self.base_dir = base_dir
        self.collectors_dir = base_dir + collectors_dir
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        self.template_dir = base_dir + template_dir
        self.vis_dir = base_dir + vis_dir
        self.info_dir = info_dir

def execute_template(template_type, template_execution, info_name, service_schedule, tool_core, tool_dict, delay_sections, template_dir, plugins_dir):
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
            f.write("|")
            if template_type not in ["visualization", "core", "active", "passive"]:
                f.write("1")
            else:
                f.write("0")
            f.write("\n")
    except Exception as e:
        pass
    return

def read_template_types(template_type, container_cmd, template_dir, plugins_dir):
    """ read in templates for plugins, core, and visualization """
    template_path = template_dir+template_type+'.template'
    if template_type in ["active", "passive"]:
        template_path = template_dir+'collectors.template'

    # search for eval string and replace with sh evaluation
    # note only checks for first occurance per line
    try:
        orig_str = None
        repl_str = None
        with open(template_path, 'r') as f:
            for line in f:
                if "`" in line:
                    a = line.split('`', 1)[1]
                    if "`" in a:
                        cmd = a.split('`', 1)[0]
                        cmd_output = subprocess.check_output(cmd.split())
                        repl_str = cmd_output.strip()
                        orig_str = "`"+cmd+"`"
        if orig_str is not None and repl_str is not None:
            filedata = None
            with open(template_path, 'r') as f:
                filedata = f.read()
            filedata = filedata.replace(orig_str, repl_str)
            with open(template_path, 'w') as f:
                f.write(filedata)
    except Exception as e:
        pass

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
        if template_type != "all":
            try:
                # get list of sections per template file
                with open(template_path): pass
                config = ConfigParser.RawConfigParser()
                # needed to preserve case sensitive options
                config.optionxform=str
                config.read(template_path)
                sections = config.sections()
            except Exception as e:
                sections = []
            running_containers = subprocess.check_output("docker ps | awk \"{print \$NF}\"", shell=True).split("\n")
            t_sections = []
            # remove sections that represent running containers
            for section in sections:
                for container in running_containers:
                    if section in container and template_type in container:
                        t_sections.append(section)
                        print section
            sections = [x for x in sections if x not in t_sections]
            external_overrides = []
            external_hosts = {}
            instances = []
            try:
                core_config = ConfigParser.RawConfigParser()
                # needed to preserve case sensitive options
                core_config.optionxform=str
                core_config.read(template_dir+'core.template')
                # check dependencies like elasticsearch and rabbitmq
                external_options = core_config.options("external")
            except Exception as e:
                external_options = []
            host_config_exists = False

            # plugin template file
            if template_type not in ["visualization", "core", "active", "passive"]:
                try:
                    # add tools that don't have sections
                    modes_config = ConfigParser.RawConfigParser()
                    # needed to preserve case sensitive options
                    modes_config.optionxform=str
                    modes_config.read(template_dir+'modes.template')
                    plugins = modes_config.get("plugins", template_type)

                    t = []
                    if plugins == 'all':
                        tools = [ name for name in os.listdir(plugins_dir+template_type) if os.path.isdir(os.path.join(plugins_dir+template_type, name)) ]
                        for tool in tools:
                            t.append(tool)
                    else:
                        for tool in plugins.split(","):
                            t.append(tool)

                    for tool in t:
                        if not tool in sections:
                            sections.append(tool)
                except Exception as e:
                    pass

            # parse through each section of the template file, creating corresponding fields for the JSON file written in execute_template()
            for section in sections:
                instructions = {}
                try:
                    options = config.options(section)
                except Exception as e:
                    options = []
                cmd = ["get_data.py", "none", "/"+section+"-data"]
                for option in options:
                    if section == "info" and option == "name":
                        info_name = config.get(section, option)
                    elif section == "service" and option == "schedule":
                        service_schedule[template_type] = json.loads(config.get(section, option))
                    elif section == "instances":
                        instances = config.options(section)
                    elif section == "locally-active" and config.get(section, option) == "off":
                        external_overrides.append(option)
                    elif section not in ["info", "service", "locally-active", "external", "instances", "active-containers", "local-collection"] and section not in external_overrides:
                        option_val = config.get(section, option)
                        try:
                            option_val = int(option_val)
                        except Exception as e:
                            pass
                        # legacy
                        if option == 'data_path':
                            if len(cmd) == 4:
                                cmd.insert(1, option_val)
                            else:
                                cmd.append(option_val)
                            d_path = 1
                        # legacy
                        elif option == 'site_path':
                            if len(cmd) == 2:
                                cmd.append("")
                                cmd.append(option_val)
                            else:
                                cmd.append(option_val)
                        # unimplemented as of 7-12-16
                        elif option == 'delay':
                            try:
                                delay_sections[section] = option_val
                            except Exception as e:
                                pass
                        else:
                            if option == "HostConfig":
                                host_config_exists = True
                                try:
                                    option_val = option_val.replace("true", "True")
                                    option_val = option_val.replace("false", "False")
                                    host_config = ast.literal_eval(option_val)
                                    host_config_new = copy.deepcopy(host_config)
                                    extra_hosts = []
                                    host_config_new["RestartPolicy"] = { "Name": "always" }
                                    if template_type not in ["visualization", "core", "active", "passive"]:
                                        # add link to rabbitmq
                                        if "Links" in host_config:
                                            host_config_new["Links"].append("core-aaa-rabbitmq:rabbitmq")
                                        else:
                                            host_config_new["Links"] = ["core-aaa-rabbitmq:rabbitmq"]
                                        # add files volume
                                        if "Binds" in host_config:
                                            host_config_new["Binds"].append("/files:/files:ro")
                                        else:
                                            host_config_new["Binds"] = ["/files:/files:ro"]
                                    if "Links" in host_config:
                                        for rec in host_config["Links"]:
                                            r = rec.split(":")
                                            r_name = r[1]
                                            r_name_full = r[0].split("core-")
                                            if len(r_name_full) > 1:
                                                r_name_full = r_name_full[1]
                                            else:
                                                r_name_full = r_name_full[0]
                                            for ext in external_overrides:
                                                if r_name_full == ext:
                                                    host_config_new["Links"].remove(rec)
                                                    # add external_overrides to extrahosts
                                                    if r_name_full+"_host" in external_options:
                                                        try:
                                                            extra_hosts.append(r_name+":"+core_config.get("external", r_name_full+"_host"))
                                                            host_config_new["ExtraHosts"] = extra_hosts
                                                        except Exception as e:
                                                            pass
                                                    else:
                                                        print "no local "+r_name+" but an external one wasn't specified."
                                        option_val = str(host_config_new).replace("'", '"')
                                        if len(host_config_new["Links"]) == 0:
                                            del host_config_new["Links"]
                                    # add syslog, don't log rmq-es-connector as it will loop itself
                                    if section not in ["rmq-es-connector", "aaa-syslog", "aaa-redis", "aaa-rabbitmq"]:
                                        try:
                                            syslog_host = "localhost"
                                            for ext in external_overrides:
                                                if "aaa_syslog" == ext:
                                                    if "aaa_syslog_host" in external_options:
                                                        try:
                                                            syslog_host = core_config.get("external", "aaa_syslog_host")
                                                        except Exception as e:
                                                            pass
                                                    else:
                                                        print "no local syslog but an external one wasn't specified."
                                            host_config_new["LogConfig"] = { "Type": "syslog", "Config": {"tag":"\{\{.ImageName\}\}/\{\{.Name\}\}/\{\{.ID\}\}","syslog-address":"tcp://"+syslog_host} }
                                            option_val = str(host_config_new).replace("'", '"')
                                        except Exception as e:
                                            pass
                                except Exception as e:
                                    pass
                            option_val = option_val.replace("True", "true")
                            option_val = option_val.replace("False", "false")
                            if option_val != "{}":
                                instructions[option] = option_val
                if section not in ["info", "service", "locally-active", "external", "instances", "active-containers", "local-collection"]:
                    if template_type not in ["visualization", "core", "active", "passive"]:
                        # add tty/interactive
                        if not "Tty" in instructions:
                            instructions["Tty"] = "true"
                        if not "OpenStdin" in instructions:
                            instructions["OpenStdin"] = "true"
                        # add pythonunbuffered env
                        if not "Env" in instructions:
                            instructions["Env"] = ["PYTHONUNBUFFERED=0"]
                    if not host_config_exists:
                        host_config = {}
                        if template_type not in ["visualization", "core", "active", "passive"]:
                            host_config["Binds"] = ["/files:/files:ro"]
                            try:
                                rabbitmq_host = "rabbitmq"
                                external_rabbit = False
                                for ext in external_overrides:
                                    if "aaa_rabbitmq" == ext:
                                        external_rabbit = True
                                        if "aaa_rabbitmq_host" in external_options:
                                            try:
                                                rabbitmq_host = core_config.get("external", "aaa_rabbitmq_host")
                                                extra_hosts.append("rabbitmq:"+rabbitmq_host)
                                                host_config["ExtraHosts"] = extra_hosts
                                            except Exception as e:
                                                pass
                                        else:
                                            print "no local rabbitmq but an external one wasn't specified."
                                if not external_rabbit:
                                    host_config["Links"] = ["core-aaa-rabbitmq:rabbitmq"]
                            except Exception as e:
                                pass
                        # add syslog
                        try:
                            syslog_host = "localhost"
                            for ext in external_overrides:
                                if "aaa_syslog" == ext:
                                    if "aaa_syslog_host" in external_options:
                                        try:
                                            syslog_host = core_config.get("external", "aaa_syslog_host")
                                        except Exception as e:
                                            pass
                                    else:
                                        print "no local syslog but an external one wasn't specified."
                            host_config["LogConfig"] = { "Type": "syslog", "Config": {"tag":"\{\{.ImageName\}\}/\{\{.Name\}\}/\{\{.ID\}\}","syslog-address":"tcp://"+syslog_host} }
                        except Exception as e:
                            pass
                        option_val = str(host_config).replace("'", '"')
                        option_val = option_val.replace("True", "true")
                        option_val = option_val.replace("False", "false")
                        if option_val != "{}":
                            instructions["HostConfig"] = option_val
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
                    if container_cmd:
                        instructions['Cmd'] = container_cmd.replace("'", '"')
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
                                    except Exception as e:
                                        pass
                                else:
                                    instructions['Image'] = 'collectors/'+section
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
                                except Exception as e:
                                    pass
                            else:
                                instructions['Image'] = template_type+'/'+section
                                instructions['Volumes'] = {"/"+section+"-data": {}}
                                tool_dict[template_type+"-"+section] = instructions
        else:
            pass
    except Exception as e:
        print e
        pass
    return info_name, service_schedule, tool_core, tool_dict, delay_sections

def main():
    """main method for template_parser. Based on the action argument given, performs the actions on the correct template files"""
    path_dirs = PathDirs()
    template_dir = path_dirs.template_dir
    plugins_dir = path_dirs.plugins_dir

    if len(sys.argv) < 3:
        sys.exit()
    else:
        template_type = sys.argv[1]
        template_execution = sys.argv[2]
        if template_execution == "stop":
            if template_type == "all":
                for x in ["visualization", "core", "active", "passive"]:
                    os.system("docker ps | grep "+x+" | awk '{print $1}' | xargs docker stop")                
            else:
                os.system("docker ps | grep "+template_type+" | awk '{print $1}' | xargs docker stop")
        elif template_execution == "clean":
            if template_type == "all":
                for x in ["visualization", "core", "active", "passive"]:
                    os.system("docker ps -aqf name=\""+x+"\" | xargs docker kill")
                    os.system("docker ps -aqf name=\""+x+"\" | xargs docker rm")
            else:
                os.system("docker ps -a | grep "+template_type+" | awk '{print $1}' | xargs docker kill")
                os.system("docker ps -a | grep "+template_type+" | awk '{print $1}' | xargs docker rm")
        elif template_execution == "start" and template_type == "all":
            container_cmd = None
            if len(sys.argv) == 4:
                container_cmd = sys.argv[3]
            for x in ["visualization", "core", "active", "passive"]:
                info_name, service_schedule, tool_core, tool_dict, delay_sections = read_template_types(x, container_cmd, template_dir, plugins_dir)
                execute_template(template_type, template_execution, info_name, service_schedule, tool_core, tool_dict, delay_sections, template_dir, plugins_dir)
        else:
            container_cmd = None
            if len(sys.argv) == 4:
                container_cmd = sys.argv[3]
            info_name, service_schedule, tool_core, tool_dict, delay_sections = read_template_types(template_type, container_cmd, template_dir, plugins_dir)
            execute_template(template_type, template_execution, info_name, service_schedule, tool_core, tool_dict, delay_sections, template_dir, plugins_dir)

if __name__ == "__main__": # pragma: no cover
    main()
