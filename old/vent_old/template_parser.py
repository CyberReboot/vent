#!/usr/bin/env python2.7

import ast
import copy
import ConfigParser
import json
import os
import subprocess
import sys
import time

from helpers.paths import PathDirs

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
            f.write("|")
            if template_type not in ["visualization", "core", "active", "passive"]:
                f.write("1")
            else:
                f.write("0")
            f.write("\n")
    except Exception as e:
        pass
    return

def read_template_types(template_type, container_cmd, path_dirs):
    """ read in templates for plugins, core, and visualization """
    template_dir = path_dirs.template_dir
    plugins_dir = path_dirs.plugins_dir
    info_dir = path_dirs.info_dir

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
    # currently unimplemented
    delay_sections = {}

    try:
        # list of containers enabled by modes.template
        mode_enabled = ast.literal_eval(subprocess.check_output("python2.7 "+info_dir+"get_status.py menabled -b "+path_dirs.base_dir, shell=True))
        # filter out core_disabled containers from modes_enabled. For collectors, containers must be in mode_enabled and core_enabled to be enabled
        core_enabled, core_disabled = ast.literal_eval(subprocess.check_output("python2.7 "+info_dir+"get_status.py cenabled -b "+path_dirs.base_dir, shell=True))
        sections = []
        if template_type in ['active', 'passive']:
            if 'collectors' in mode_enabled and 'collectors' in core_enabled:
                mode_enabled = [container for container in mode_enabled['collectors'] if container.startswith(template_type+"-")]
                core_enabled = core_enabled['collectors']
                sections = [container for container in mode_enabled if container in core_enabled]
        elif template_type in mode_enabled:
            mode_enabled = mode_enabled[template_type]
            sections = mode_enabled
            if template_type in core_disabled:
                core_disabled = core_disabled[template_type]
                sections = [container for container in mode_enabled if not container in core_disabled]

        # start enabled containers. If a container is restarted from stopped to running, remove it from 'sections'
        stopped_containers = subprocess.check_output("docker ps -a --filter 'status=exited' --filter 'name="+template_type+"-' | awk '{print $NF}'", shell=True).split("\n")
        stopped_containers = sorted(stopped_containers)
        restarted_containers = []
        for sc in stopped_containers:
            for section in sections:
                if section in sc:
                    os.system("docker start "+sc)
                    restarted_containers.append(section)
        sections = [section for section in sections if not section in restarted_containers]

        # add sections that exist in the template, but are not enabled containers
        config = ConfigParser.RawConfigParser()
        # needed to preserve case sensitive options
        config.optionxform=str
        config.read(template_path)
        for s in config.sections():
            if s in ["info", "service", "locally-active", "external", "instances", "active-containers", "local-collection"]:
                sections.append(s)
    except Exception as e:
        sections = []

    try:
        core_config = ConfigParser.RawConfigParser()
        # needed to preserve case sensitive options
        core_config.optionxform=str
        core_config.read(template_dir+'core.template')
        # check dependencies like elasticsearch and rabbitmq
        external_options = core_config.options("external")
    except Exception as e:
        external_options = []

    public_network = "0.0.0.0"
    public_nic = None
    # check default route then if public_nic has been overridden
    try:
        public_nic = subprocess.check_output("route | grep default | awk '{print $NF}'", shell=True)
        core_config = ConfigParser.RawConfigParser()
        # needed to preserve case sensitive options
        core_config.optionxform=str
        core_config.read(template_dir+'core.template')
        # check dependencies like elasticsearch and rabbitmq
        service = core_config.options("service")
        public_nic = core_config.get("service", "public_nic")
    except Exception as e:
        pass
    if public_nic:
        try:
            response = subprocess.check_output(info_dir+"get_info.sh nics | grep "+public_nic, shell=True)
            public_network = response.split(":")[1].strip()
        except Exception as e:
            pass
    try:
        running_containers = []
        running_containers = subprocess.check_output("docker ps | awk \"{print \$NF}\"", shell=True).split("\n")
        t_sections = []
        # remove sections that represent running containers
        for section in sections:
            for container in running_containers:
                if section in container and template_type in container:
                    t_sections.append(section)
        sections = [x for x in sections if x not in t_sections]
        external_overrides = []
        external_hosts = {}
        instances = []
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
                intermediate_t = []
                if plugins == 'all':
                    tools = [ name for name in os.listdir(plugins_dir+template_type) if os.path.isdir(os.path.join(plugins_dir+template_type, name)) ]
                    for tool in tools:
                        t.append(tool)
                else:
                    for tool in plugins.split(","):
                        intermediate_t.append(tool)
                    sections = intermediate_t

                for tool in t:
                    if not tool in sections:
                        sections.append(tool)
            except Exception as e:
                pass
        # parse through each section of the template file, creating corresponding fields for the JSON file written in execute_template()
        for section in sections:
            external_overrides = []
            instances = []
            host_config_exists = False
            instructions = {}
            try:
                options = config.options(section)
            except Exception as e:
                options = []
            try:
                info_name = config.get("info", "name")
            except Exception as e:
                info_name = ""
            try:
                service_schedule[template_type] = json.loads(config.get("service", "schedule"))
            except Exception as e:
                service_schedule[template_type] = {}
            try:
                # !! TODO this is not correct, should be a dictionary of options and values
                instances = config.options("instances")
            except Exception as e:
                instances = []
            try:
                locally_active = config.options("locally-active")
                for l_a in locally_active:
                    if config.get("locally-active", l_a) == "off":
                        external_overrides.append(l_a)
            except Exception as e:
                external_overrides = []
            for option in options:
                if section not in ["info", "service", "locally-active", "external", "instances", "active-containers", "local-collection"] and section not in external_overrides:
                    option_val = config.get(section, option)
                    try:
                        option_val = int(option_val)
                    except Exception as e:
                        pass
                    if option == "HostConfig":
                        host_config_exists = True
                        try:
                            option_val = option_val.replace("true", "True")
                            option_val = option_val.replace("false", "False")
                            host_config = ast.literal_eval(option_val)
                            host_config_new = copy.deepcopy(host_config)
                            extra_hosts = []
                            # reconfigure exposing ports to the public_network only
                            if "PublishAllPorts" in host_config:
                                if host_config["PublishAllPorts"] in [True, "True"]:
                                    del host_config_new["PublishAllPorts"]
                                    if "PortBindings" in host_config:
                                        # !! TODO
                                        # not a valid configuration?
                                        pass
                                    else:
                                        ports = []
                                        # use docker inspect image
                                        try:
                                            if template_type in ["active", "passive"]:
                                                mapping = subprocess.check_output("docker inspect -f '{{.Config.ExposedPorts}}' collectors/"+section, shell=True)
                                            else:
                                                mapping = subprocess.check_output("docker inspect -f '{{.Config.ExposedPorts}}' "+template_type+"/"+section, shell=True)
                                            p = mapping.strip()[4:-1].split(" ")
                                            for port in p:
                                                ports.append(port[:-3])
                                        except Exception as e:
                                            pass
                                        port_dict = {}
                                        for port in ports:
                                            port_dict[port] = [{"HostPort":"", "HostIp":public_network}]
                                        host_config_new["PortBindings"] = port_dict
                            elif "PortBindings" in host_config:
                                # !! TODO temporary hack
                                pass
                                #new_port_dict = {}
                                #port_dict = host_config["PortBindings"]
                                #for port in port_dict:
                                #    intermediate = port_dict[port]
                                #    # !! TODO not necessarily always the first object in the array
                                #    intermediate[0]['HostIp'] = public_network
                                #    new_port_dict[port] = intermediate
                                #host_config_new["PortBindings"] = new_port_dict
                            if template_type == "core":
                                host_config_new["RestartPolicy"] = { "Name": "always" }
                            if template_type not in ["visualization", "core", "active", "passive"]:
                                # add link to rabbitmq
                                if "Links" in host_config:
                                    host_config_new["Links"].append("core-aaa-rabbitmq:rabbitmq")
                                else:
                                    host_config_new["Links"] = ["core-aaa-rabbitmq:rabbitmq"]
                                # add files volume
                                if "Binds" in host_config:
                                    host_config_new["Binds"].append("/files:/files:rw")
                                else:
                                    host_config_new["Binds"] = ["/files:/files:rw"]
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
                                                print("no local "+r_name+" but an external one wasn't specified.")
                                option_val = str(host_config_new).replace("'", '"')
                                if len(host_config_new["Links"]) == 0:
                                    del host_config_new["Links"]
                            # add syslog, don't log rmq-es-connector as it will loop itself
                            if section not in ["rmq-es-connector", "aaa-syslog", "aaa-redis", "aaa-rabbitmq"]:
                                try:
                                    # !! TODO temporary hack
                                    #syslog_host = public_network
                                    syslog_host = "localhost"
                                    for ext in external_overrides:
                                        if "aaa-syslog" == ext:
                                            if "aaa-syslog_host" in external_options:
                                                try:
                                                    syslog_host = core_config.get("external", "aaa-syslog_host")
                                                except Exception as e:
                                                    pass
                                            else:
                                                print("no local syslog but an external one wasn't specified.")
                                    host_config_new["LogConfig"] = { "Type": "syslog", "Config": {"tag":"\{\{.ImageName\}\}/\{\{.Name\}\}/\{\{.ID\}\}","syslog-address":"tcp://"+syslog_host} }
                                    option_val = str(host_config_new).replace("'", '"')
                                except Exception as e:
                                    pass
                            else:
                                option_val = str(host_config_new).replace("'", '"')
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
                        host_config["Binds"] = ["/files:/files:rw"]
                        try:
                            rabbitmq_host = "rabbitmq"
                            external_rabbit = False
                            for ext in external_overrides:
                                if "aaa-rabbitmq" == ext:
                                    external_rabbit = True
                                    if "aaa-rabbitmq_host" in external_options:
                                        try:
                                            rabbitmq_host = core_config.get("external", "aaa-rabbitmq_host")
                                            extra_hosts.append("rabbitmq:"+rabbitmq_host)
                                            host_config["ExtraHosts"] = extra_hosts
                                        except Exception as e:
                                            pass
                                    else:
                                        print("no local rabbitmq but an external one wasn't specified.")
                            if not external_rabbit:
                                host_config["Links"] = ["core-aaa-rabbitmq:rabbitmq"]
                        except Exception as e:
                            pass
                    # add syslog
                    if section not in ["rmq-es-connector", "aaa-syslog", "aaa-redis", "aaa-rabbitmq"]:
                        try:
                            # !! TODO temporary hack
                            #syslog_host = public_network
                            syslog_host = "localhost"
                            for ext in external_overrides:
                                if "aaa-syslog" == ext:
                                    if "aaa-syslog_host" in external_options:
                                        try:
                                            syslog_host = core_config.get("external", "aaa-syslog_host")
                                        except Exception as e:
                                            pass
                                    else:
                                        print("no local syslog but an external one wasn't specified.")
                            host_config["LogConfig"] = { "Type": "syslog", "Config": {"tag":"\{\{.ImageName\}\}/\{\{.Name\}\}/\{\{.ID\}\}","syslog-address":"tcp://"+syslog_host} }
                        except Exception as e:
                            pass
                    option_val = str(host_config).replace("'", '"')
                    option_val = option_val.replace("True", "true")
                    option_val = option_val.replace("False", "false")
                    if option_val != "{}":
                        instructions["HostConfig"] = option_val
                if container_cmd:
                    # set an environment variable in the container that has the
                    # vent hostname
                    hostname = container_cmd.split("_", 1)[0]
                    if "Env" in instructions:
                        if type(instructions['Env']) == list:
                            instructions['Env'].append("VENT_HOST="+hostname)
                        else:
                            temp_env = instructions['Env'][1:-1].split(",")
                            instructions['Env'] = []
                            for item in temp_env:
                                instructions['Env'].append(item.strip()[1:-1])
                    else:
                        instructions['Env'] = ["VENT_HOST="+hostname]
                    # override the container command to be what was passed in
                    # by the container_cmd minus the vent hostname
                    instructions['Cmd'] = container_cmd.split("_", 1)[1].replace("'", '"')
                if not section in external_overrides:
                    # !! TODO do we ever get here? i don't think so
                    #if "active" in section or "passive" in section:
                    #    if (template_type == "active" and "active" in section) or (template_type == "passive" and "passive" in section):
                    #        if section in instances:
                    #            try:
                    #                instance_count = config.get("instances", section)
                    #                for i in range(int(instance_count)):
                    #                    instructions['Image'] = 'core/'+section
                    #                    instructions['Volumes'] = {"/"+section+"-data": {}}
                    #                    tool_dict[section+str(i)] = instructions
                    #            except Exception as e:
                    #                pass
                    #        else:
                    #            instructions['Image'] = 'collectors/'+section
                    #            instructions['Volumes'] = {"/"+section+"-data": {}}
                    #            tool_dict[section] = instructions
                    #else:
                    if section in instances:
                        try:
                            instance_count = config.get("instances", section)
                            for i in range(int(instance_count)):
                                if template_type in ['active','passive']:
                                    instructions['Image'] = 'collectors/'+section
                                else:
                                    instructions['Image'] = template_type+'/'+section
                                instructions['Volumes'] = {"/"+section+"-data": {}}
                                if template_type == "core":
                                    tool_core[template_type+"-"+section+str(i)] = instructions
                                elif template_type in ['active', 'passive']:
                                    if template_type in section:
                                        tool_dict[section+str(i)] = instructions
                                else:
                                    tool_dict[template_type+"-"+section+str(i)] = instructions
                        except Exception as e:
                            pass
                    else:
                        if template_type in ['active','passive']:
                            instructions['Image'] = 'collectors/'+section
                        else:
                            instructions['Image'] = template_type+'/'+section
                        instructions['Volumes'] = {"/"+section+"-data": {}}
                        if template_type == "core":
                            tool_core[template_type+"-"+section] = instructions
                        elif template_type in ['active', 'passive']:
                            if template_type in section:
                                tool_dict[section] = instructions
                        else:
                            tool_dict[template_type+"-"+section] = instructions
    except Exception as e:
        pass
    return info_name, service_schedule, tool_core, tool_dict, delay_sections

def main(path_dirs, template_type, template_execution, container_cmd):
    """main method for template_parser. Based on the action argument given, performs the actions on the correct template files"""
    if template_execution == "stop":
        if template_type == "all":
            for x in ["visualization", "active", "passive", "core"]:
                os.system("docker ps -aqf name=\""+x+"\" | xargs docker stop 2> /dev/null")
        else:
            os.system("docker ps -aqf name=\""+template_type+"\" | xargs docker stop 2> /dev/null")
    elif template_execution == "clean":
        if template_type == "all":
            for x in ["visualization", "active", "passive", "core"]:
                os.system("docker ps -aqf name=\""+x+"\" | xargs docker kill 2> /dev/null")
                os.system("docker ps -aqf name=\""+x+"\" | xargs docker rm 2> /dev/null")
        else:
            os.system("docker ps -aqf name=\""+template_type+"\" | xargs docker kill 2> /dev/null")
            os.system("docker ps -aqf name=\""+template_type+"\" | xargs docker rm 2> /dev/null")
    elif template_execution == "start" and template_type == "all":
        for x in ["core", "visualization", "active", "passive"]:
            info_name, service_schedule, tool_core, tool_dict, delay_sections = read_template_types(x, container_cmd, path_dirs)
            execute_template(template_type, template_execution, info_name, service_schedule, tool_core, tool_dict, delay_sections)
    else:
        info_name, service_schedule, tool_core, tool_dict, delay_sections = read_template_types(template_type, container_cmd, path_dirs)
        execute_template(template_type, template_execution, info_name, service_schedule, tool_core, tool_dict, delay_sections)

if __name__ == "__main__": # pragma: no cover
    path_dirs = PathDirs()
    if len(sys.argv) < 3:
        sys.exit()
    else:
        template_type = sys.argv[1]
        template_execution = sys.argv[2]
        container_cmd = None
        if len(sys.argv) == 4:
            container_cmd = sys.argv[3]

    main(path_dirs, template_type, template_execution, container_cmd)
