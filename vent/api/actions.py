import ast
import datetime
import json
import os
import shlex
import subprocess

from vent.api.plugins import Plugin
from vent.api.templates import Template
from vent.helpers.logs import Logger
from vent.helpers.meta import Containers
from vent.helpers.meta import Core
from vent.helpers.meta import Images
from vent.helpers.meta import Version

class Action:
    """ Handle actions in menu """
    def __init__(self, **kargs):
        self.plugin = Plugin(**kargs)
        self.d_client = self.plugin.d_client
        self.vent_config = os.path.join(self.plugin.path_dirs.meta_dir,
                                        "vent.cfg")
        self.logger = Logger(__name__)

    def add(self, repo, tools=None, overrides=None, version="HEAD",
            branch="master", build=True, user=None, pw=None, groups=None,
            version_alias=None, wild=None, remove_old=True, disable_old=True):
        """ Add a new set of tool(s) """
        self.logger.info("Starting: add")
        status = (True, None)
        try:
            status = self.plugin.add(repo,
                                     tools=tools,
                                     overrides=overrides,
                                     version=version,
                                     branch=branch,
                                     build=build,
                                     user=user,
                                     pw=pw,
                                     groups=groups,
                                     version_alias=version_alias,
                                     wild=wild,
                                     remove_old=remove_old,
                                     disable_old=disable_old)
        except Exception as e:
            self.logger.error(str(e))
            status = (False, e)
        self.logger.info(status)
        self.logger.info("Finished: add")
        return status

    def remove(self, repo=None, namespace=None, name=None, groups=None,
               enabled="yes", branch="master", version="HEAD", built="yes"):
        """ Remove tools or a repo """
        self.logger.info("Starting: remove")
        status = (True, None)
        status = self.plugin.remove(name=name,
                                    repo=repo,
                                    namespace=namespace,
                                    groups=groups,
                                    enabled=enabled,
                                    branch=branch,
                                    version=version,
                                    built=built)
        self.logger.info(status)
        self.logger.info("Finished: remove")
        return status

    def prep_start(self,
                   repo=None,
                   name=None,
                   groups=None,
                   enabled="yes",
                   branch="master",
                   version="HEAD",
                   run_build=False):
        """
        Start a set of tools that match the parameters given, if no parameters
        are given, start all installed tools on the master branch at verison
        HEAD that are enabled
        """
        args = locals()
        del args['run_build']
        options = ['name',
                   'namespace',
                   'built',
                   'groups',
                   'path',
                   'image_name',
                   'branch',
                   'version']
        vent_config = Template(template=self.vent_config)
        files = vent_config.option('main', 'files')
        sections, template = self.plugin.constraint_options(args, options)
        tool_dict = {}
        for section in sections:
            # initialize needed vars
            template_path = os.path.join(sections[section]['path'], 'vent.template')
            container_name = sections[section]['image_name'].replace(':','-')
            container_name = container_name.replace('/','-')
            image_name = sections[section]['image_name']

            # checkout the right version and branch of the repo
            self.plugin.branch = branch
            self.plugin.version = version
            cwd = os.getcwd()
            os.chdir(os.path.join(sections[section]['path']))
            status = self.plugin.checkout()
            self.logger.info(status)
            os.chdir(cwd)

            if run_build:
                status = self.build(name=sections[section]['name'],
                                    groups=groups,
                                    enabled=enabled,
                                    branch=branch,
                                    version=version)
                self.logger.info(status)

            # set docker settings for container
            vent_template = Template(template_path)
            status = vent_template.section('docker')
            self.logger.info(status)
            tool_dict[container_name] = {'image':image_name, 'name':container_name}
            if status[0]:
                for option in status[1]:
                    options = option[1]
                    # check for commands to evaluate
                    if '`' in options:
                        cmds = options.split('`')
                        # TODO this probably needs better error checking to handle mismatched ``
                        if len(cmds) > 2:
                            i = 1
                            while i < len(cmds):
                                try:
                                    cmds[i] = subprocess.check_output(shlex.split(cmds[i]), stderr=subprocess.STDOUT, close_fds=True).strip()
                                except Exception as e:
                                    self.logger.warn("Unable to evaluate command specified in vent.template: "+str(e))
                                i += 2
                        options = "".join(cmds)
                    # store options set for docker
                    try:
                        tool_dict[container_name][option[0]] = ast.literal_eval(options)
                    except Exception as e:
                        tool_dict[container_name][option[0]] = options

            # get temporary name for links, etc.
            status = vent_template.section('info')
            self.logger.info(status)
            plugin_config = Template(template=self.plugin.manifest)
            status, plugin_sections = plugin_config.sections()
            self.logger.info(status)
            for plugin_section in plugin_sections:
                status = plugin_config.option(plugin_section, "link_name")
                self.logger.info(status)
                image_status = plugin_config.option(plugin_section, "image_name")
                self.logger.info(image_status)
                if status[0] and image_status[0]:
                    cont_name = image_status[1].replace(':','-')
                    cont_name = cont_name.replace('/','-')
                    if cont_name not in tool_dict:
                        tool_dict[cont_name] = {'image':image_status[1], 'name':cont_name, 'start':False}
                    tool_dict[cont_name]['tmp_name'] = status[1]

            # add extra labels
            if 'labels' not in tool_dict[container_name]:
                tool_dict[container_name]['labels'] = {}
            tool_dict[container_name]['labels']['vent'] = Version()
            tool_dict[container_name]['labels']['vent.namespace'] = sections[section]['namespace']
            tool_dict[container_name]['labels']['vent.branch'] = branch
            tool_dict[container_name]['labels']['vent.version'] = version
            tool_dict[container_name]['labels']['vent.name'] = sections[section]['name']

            if 'groups' in sections[section]:
                # add labels for groups
                tool_dict[container_name]['labels']['vent.groups'] = sections[section]['groups']
                # send logs to syslog
                if 'syslog' not in sections[section]['groups'] and 'core' in sections[section]['groups']:
                    tool_dict[container_name]['log_config'] = {'type':'syslog', 'config': {'syslog-address':'tcp://0.0.0.0:514', 'syslog-facility':'daemon', 'tag':'core'}}
                if 'syslog' not in sections[section]['groups']:
                    tool_dict[container_name]['log_config'] = {'type':'syslog', 'config': {'syslog-address':'tcp://0.0.0.0:514', 'syslog-facility':'daemon', 'tag':'plugin'}}
                # mount necessary directories
                if 'files' in sections[section]['groups']:
                    if 'volumes' in tool_dict[container_name]:
                        tool_dict[container_name]['volumes'][self.plugin.path_dirs.base_dir[:-1]] = {'bind': '/vent', 'mode': 'ro'}
                    else:
                        tool_dict[container_name]['volumes'] = {self.plugin.path_dirs.base_dir[:-1]: {'bind': '/vent', 'mode': 'ro'}}
                    if files[0]:
                        tool_dict[container_name]['volumes'][files[1]] = {'bind': '/files', 'mode': 'ro'}
            else:
                tool_dict[container_name]['log_config'] = {'type':'syslog', 'config': {'syslog-address':'tcp://0.0.0.0:514', 'syslog-facility':'daemon', 'tag':'plugin'}}

            # add label for priority
            status = vent_template.section('settings')
            self.logger.info(status)
            if status[0]:
                for option in status[1]:
                    if option[0] == 'priority':
                        tool_dict[container_name]['labels']['vent.priority'] = option[1]

            # only start tools that have been built
            if sections[section]['built'] != 'yes':
                del tool_dict[container_name]

        # check and update links, volumes_from, network_mode
        for container in tool_dict.keys():
            if 'links' in tool_dict[container]:
                for link in tool_dict[container]['links']:
                    for c in tool_dict.keys():
                        if 'tmp_name' in tool_dict[c] and tool_dict[c]['tmp_name'] == link:
                            tool_dict[container]['links'][tool_dict[c]['name']] = tool_dict[container]['links'].pop(link)
            if 'volumes_from' in tool_dict[container]:
                tmp_volumes_from = tool_dict[container]['volumes_from']
                tool_dict[container]['volumes_from'] = []
                for volumes_from in list(tmp_volumes_from):
                    for c in tool_dict.keys():
                        if 'tmp_name' in tool_dict[c] and tool_dict[c]['tmp_name'] == volumes_from:
                            tool_dict[container]['volumes_from'].append(tool_dict[c]['name'])
                            tmp_volumes_from.remove(volumes_from)
                tool_dict[container]['volumes_from'] += tmp_volumes_from
            if 'network_mode' in tool_dict[container]:
                if tool_dict[container]['network_mode'].startswith('container:'):
                    network_c_name = tool_dict[container]['network_mode'].split('container:')[1]
                    for c in tool_dict.keys():
                        if 'tmp_name' in tool_dict[c] and tool_dict[c]['tmp_name'] == network_c_name:
                            tool_dict[container]['network_mode'] = 'container:'+tool_dict[c]['name']

        # remove tmp_names
        for c in tool_dict.keys():
            if 'tmp_name' in tool_dict[c]:
                del tool_dict[c]['tmp_name']

        # remove containers that shouldn't be started
        for c in tool_dict.keys():
            if 'start' in tool_dict[c] and not tool_dict[c]['start']:
                del tool_dict[c]

        return tool_dict

    def start(self, tool_dict):
        """
        Start a set of tools that match the parameters given, if no parameters
        are given, start all installed tools on the master branch at verison
        HEAD that are enabled
        """
        status = (True, None)
        # check start priorities (priority of groups is alphabetical for now)
        group_orders = {}
        groups = []
        containers_remaining = []
        for container in tool_dict:
            containers_remaining.append(container)
            if 'labels' in tool_dict[container]:
                if 'vent.groups' in tool_dict[container]['labels']:
                    groups += tool_dict[container]['labels']['vent.groups'].split(',')
                    if 'vent.priority' in tool_dict[container]['labels']:
                        priorities = tool_dict[container]['labels']['vent.priority'].split(',')
                        container_groups = tool_dict[container]['labels']['vent.groups'].split(',')
                        for i, priority in enumerate(priorities):
                            if container_groups[i] not in group_orders:
                                group_orders[container_groups[i]] = []
                            group_orders[container_groups[i]].append((int(priority), container))
                        containers_remaining.remove(container)

        # start containers based on priorities
        groups = sorted(set(groups))
        started_containers = []
        for group in groups:
            if group in group_orders:
                for container_tuple in sorted(group_orders[group]):
                    if container_tuple[1] not in started_containers:
                        started_containers.append(container_tuple[1])
                        try:
                            try:
                                container = self.d_client.containers.get(container_tuple[1])
                                container.start()
                                self.logger.info("started "+str(container_tuple[1])+" with ID: "+str(container.short_id))
                            except Exception as err:
                                container_id = self.d_client.containers.run(detach=True, **tool_dict[container_tuple[1]])
                                self.logger.info("started "+str(container_tuple[1])+" with ID: "+str(container_id))
                        except Exception as e:
                            self.logger.warning("failed to start "+str(container_tuple[1])+" because: "+str(e))

        # start the rest of the containers that didn't have any priorities set
        for container in containers_remaining:
            try:
                try:
                    c = self.d_client.containers.get(container)
                    c.start()
                    self.logger.info("started "+str(container)+" with ID: "+str(c.short_id))
                except Exception as err:
                    container_id = self.d_client.containers.run(detach=True, **tool_dict[container])
                    self.logger.info("started "+str(container)+" with ID: "+str(container_id))
            except Exception as e:
                self.logger.warning("failed to start "+str(container)+" because: "+str(e))

        return status

    def update(self,
               repo=None,
               name=None,
               groups=None,
               enabled="yes",
               branch="master",
               version="HEAD"):
        """
        Update a set of tools that match the parameters given, if no parameters
        are given, updated all installed tools on the master branch at verison
        HEAD that are enabled
        """
        args = locals()
        options = ['path', 'image_name', 'image_id']
        sections, template = self.plugin.constraint_options(args, options)
        status = (True, None)

        # get existing containers and images and states
        running_containers = Containers()
        built_images = Images()

        # if repo, pull and build
        # if registry image, pull
        for section in sections:
            try:
                cwd = os.getcwd()
                os.chdir(sections[section]['path'])
                self.plugin.version = version
                self.plugin.branch = branch
                self.plugin.checkout()
                try:
                    os.chdir(cwd)
                except Exception as e:
                    pass
                template = self.plugin.builder(template, sections[section]['path'], sections[section]['image_name'], section, build=True, branch=branch, version=version)
                # stop and remove old containers and images if image_id updated
                # !! TODO

                # start containers if they were running
                # !! TODO

                # TODO logging
            except Exception as e:
                self.logger.error("Unable to update: "+str(section))

        template.write_config()
        return status

    def stop(self,
             repo=None,
             name=None,
             groups=None,
             enabled="yes",
             branch="master",
             version="HEAD"):
        """
        Stop a set of tools that match the parameters given, if no parameters
        are given, stop all installed tools on the master branch at verison
        HEAD that are enabled
        """
        # !! TODO need to account for plugin containers that have random names, use labels perhaps
        args = locals()
        options = ['name',
                   'namespace',
                   'built',
                   'groups',
                   'path',
                   'image_name',
                   'branch',
                   'version']
        sections, template = self.plugin.constraint_options(args, options)
        status = (True, None)
        for section in sections:
            container_name = sections[section]['image_name'].replace(':','-')
            container_name = container_name.replace('/','-')
            try:
                container = self.d_client.containers.get(container_name)
                container.stop()
                self.logger.info("stopped "+str(container_name))
            except Exception as e:
                self.logger.warning("failed to stop "+str(container_name)+" because: "+str(e))
        return status

    def clean(self,
              repo=None,
              name=None,
              groups=None,
              enabled="yes",
              branch="master",
              version="HEAD"):
        """
        Clean (stop and remove) a set of tools that match the parameters given,
        if no parameters are given, clean all installed tools on the master
        branch at verison HEAD that are enabled
        """
        # !! TODO need to account for plugin containers that have random names, use labels perhaps
        args = locals()
        options = ['name',
                   'namespace',
                   'built',
                   'groups',
                   'path',
                   'image_name',
                   'branch',
                   'version']
        sections, template = self.plugin.constraint_options(args, options)
        status = (True, None)
        for section in sections:
            container_name = sections[section]['image_name'].replace(':','-')
            container_name = container_name.replace('/','-')
            try:
                container = self.d_client.containers.get(container_name)
                container.remove(force=True)
                self.logger.info("cleaned "+str(container_name))
            except Exception as e:
                self.logger.warning("failed to clean "+str(container_name)+" because: "+str(e))
        return status

    def build(self,
              repo=None,
              name=None,
              groups=None,
              enabled="yes",
              branch="master",
              version="HEAD"):
        """ Build a set of tools that match the parameters given """
        args = locals()
        options = ['image_name', 'path']
        status = (True, None)
        sections, template = self.plugin.constraint_options(args, options)
        for section in sections:
            self.logger.info("Building "+str(section)+" ...")
            template = self.plugin.builder(template, sections[section]['path'],
                                           sections[section]['image_name'],
                                           section, build=True, branch=branch,
                                           version=version)
        template.write_config()
        return status

    def cores(self, action, branch="master"):
        """ Supply action (install, build, start, stop, clean) for core tools """
        status = (True, None)
        core = Core(branch=branch)
        if action in ["install", "build"]:
            tools = []
            plugins = Plugin(plugins_dir=".internals/plugins")
            plugins.version = 'HEAD'
            plugins.branch = branch
            plugins.apply_path('https://github.com/cyberreboot/vent')
            response = plugins.checkout()
            matches = plugins._available_tools(groups='core')
            for match in matches:
                tools.append((match[0], ''))
            status = plugins.add('https://github.com/cyberreboot/vent', tools=tools, branch=branch, build=False)
            plugin_config = Template(template=self.plugin.manifest)
            sections = plugin_config.sections()
            for tool in core['normal']:
                for section in sections[1]:
                    name = plugin_config.option(section, "name")
                    orig_branch = plugin_config.option(section, "branch")
                    namespace = plugin_config.option(section, "namespace")
                    version = plugin_config.option(section, "version")
                    if name[1] == tool and orig_branch[1] == branch and namespace[1] == "cyberreboot/vent" and version[1] == "HEAD":
                        plugin_config.set_option(section, "image_name", "cyberreboot/vent-"+tool+":"+branch)
            plugin_config.write_config()
        if action == "build":
            plugin_config = Template(template=self.plugin.manifest)
            sections = plugin_config.sections()
            try:
                for tool in core['normal']:
                    for section in sections[1]:
                        image_name = plugin_config.option(section, "image_name")
                        if image_name[1] == "cyberreboot/vent-"+tool+":"+branch:
                            try:
                                # currently can't use docker-py because it
                                # returns a 404 on pull so no way to valid if it
                                # worked or didn't
                                #image_id = self.d_client.images.pull('cyberreboot/vent-'+tool, tag=branch)
                                image_id = None
                                output = subprocess.check_output(shlex.split("docker pull cyberreboot/vent-"+tool+":"+branch), stderr=subprocess.STDOUT)
                                for line in output.split('\n'):
                                    if line.startswith("Digest: sha256:"):
                                        image_id = line.split("Digest: sha256:")[1][:12]
                                if image_id:
                                    plugin_config.set_option(section, "built", "yes")
                                    plugin_config.set_option(section, "image_id", image_id)
                                    plugin_config.set_option(section, "last_updated", str(datetime.datetime.utcnow()) + " UTC")
                                    status = (True, "Pulled "+tool)
                                    self.logger.info(str(status))
                                else:
                                    plugin_config.set_option(section, "built", "failed")
                                    plugin_config.set_option(section, "last_updated", str(datetime.datetime.utcnow()) + " UTC")
                                    status = (False, "Failed to pull image "+str(output.split('\n')[-1]))
                                    self.logger.warning(str(status))
                            except Exception as e:
                                plugin_config.set_option(section, "built", "failed")
                                plugin_config.set_option(section, "last_updated", str(datetime.datetime.utcnow()) + " UTC")
                                status = (False, "Failed to pull image "+str(e))
                                self.logger.warning(str(status))
            except Exception as e:
                status = (False, "Failed to pull images "+str(e))
                self.logger.warning(str(status))
            plugin_config.write_config()
        elif action == "start":
            status = self.start(groups="core", branch=branch)
        elif action == "stop":
            status = self.stop(groups="core", branch=branch)
        elif action == "clean":
            status = self.clean(groups="core", branch=branch)
        return status

    @staticmethod
    def backup():
        # TODO
        return

    @staticmethod
    def restore():
        # TODO
        return

    @staticmethod
    def configure():
        # TODO
        # tools, core, etc.
        return

    @staticmethod
    def system_commands():
        # reset, upgrade, etc.
        return

    def logs(self, container_type=None, grep_list=None):
        """ generically filter logs stored in log containers """
        log_entries = {}
        containers = self.d_client.containers.list(all=True, filters={'label':'vent'})
        if grep_list:
            compare_containers = containers
            if container_type:
                try:
                    compare_containers = [c for c in containers if (container_type in c.attrs['Config']['Labels']['vent.groups'])]
                except Exception as e:
                    self.logger.warn("Unable to limit containers by container_type: "+str(container_type)+" because: "+str(e))

            for expression in grep_list:
                for container in compare_containers:
                    try:
                        # 'logs' stores each line which contains the expression
                        logs  = [log for log in container.logs().split("\n") if expression in log]
                        for log in logs:
                            if str(container.name) in log_entries:
                                log_entries[str(container.name)].append(log)
                            else:
                                log_entries[str(container.name)] = [log]
                    except Exception as e:
                        self.logger.warn("Unable to get logs for "+str(container.name)+" because: "+str(e))
        else:
            compare_containers = containers
            if container_type:
                try:
                    compare_containers = [c for c in containers if (container_type in c.attrs['Config']['Labels']['vent.groups'])]
                except Exception as e:
                    self.logger.warn("Unable to limit containers by container_type: "+str(container_type)+" because: "+str(e))
            for container in compare_containers:
                try:
                    logs = container.logs().split("\n")
                    for log in logs:
                        if str(container.name) in log_entries:
                            log_entries[str(container.name)].append(log)
                        else:
                            log_entries[str(container.name)] = [log]
                except Exception as e:
                    self.logger.warn("Unable to get logs for "+str(container.name)+" because: "+str(e))
        return log_entries

    @staticmethod
    def help():
        # TODO
        return

    def inventory(self, choices=None):
        """ Return a dictionary of the inventory items and status """
        # choices: repos, core, tools, images, built, running, enabled
        items = {'repos':[], 'core':[], 'tools':[], 'images':[],
                 'built':[], 'running':[], 'enabled':[]}

        tools = self.plugin.tools()
        for choice in choices:
            for tool in tools:
                try:
                    if choice == 'repos':
                        if 'repo' in tool:
                            if tool['repo'] and tool['repo'] not in items[choice]:
                                items[choice].append(tool['repo'])
                    elif choice == 'core':
                        if 'groups' in tool:
                            if 'core' in tool['groups']:
                                items[choice].append((tool['section'], tool['name']))
                    elif choice == 'tools':
                        items[choice].append((tool['section'], tool['name']))
                    elif choice == 'images':
                        # TODO also check against docker
                        images = Images()
                        items[choice].append((tool['section'], tool['name'], tool['image_name']))
                    elif choice == 'built':
                        items[choice].append((tool['section'], tool['name'], tool['built']))
                    elif choice == 'running':
                        containers = Containers()
                        status = 'not running'
                        for container in containers:
                            image_name = tool['image_name'].rsplit(":"+tool['version'], 1)[0]
                            image_name = image_name.replace(':', '-')
                            image_name = image_name.replace('/', '-')
                            if container[0] == image_name:
                                status = container[1]
                        items[choice].append((tool['section'], tool['name'], status))
                    elif choice == 'enabled':
                        items[choice].append((tool['section'], tool['name'], tool['enabled']))
                    else:
                        # unknown choice
                        pass
                except Exception as e: # pragma: no cover
                    pass

        return items
