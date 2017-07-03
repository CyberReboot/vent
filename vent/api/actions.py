import os
import shlex
import shutil

from ast import literal_eval
from subprocess import check_output, STDOUT

from vent.api.plugins import Plugin
from vent.api.plugin_helpers import PluginHelper
from vent.api.templates import Template
from vent.helpers.logs import Logger
from vent.helpers.meta import Containers
from vent.helpers.meta import Images
from vent.helpers.meta import Version


class Action:
    """ Handle actions in menu """
    def __init__(self, **kargs):
        self.plugin = Plugin(**kargs)
        self.d_client = self.plugin.d_client
        self.vent_config = os.path.join(self.plugin.path_dirs.meta_dir,
                                        "vent.cfg")
        self.p_helper = PluginHelper(**kargs)
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
        except Exception as e:  # pragma: no cover
            self.logger.error("add failed with error: " + str(e))
            status = (False, e)
        self.logger.info("Status of add: " + str(status[0]))
        self.logger.info("Finished: add")
        return status

    def add_image(self,
                  image,
                  link_name,
                  tag=None,
                  registry=None,
                  groups=None):
        """ Add a new image from a Docker registry """
        self.logger.info("Starting: add image")
        status = (True, None)
        try:
            status = self.plugin.add_image(image,
                                           link_name,
                                           tag=tag,
                                           registry=registry,
                                           groups=groups)
        except Exception as e:  # pragma: no cover
            self.logger.error("add image failed with error: " + str(e))
            status = (False, e)
        self.logger.info("Status of add image: " + str(status[0]))
        self.logger.info("Finished: add image")
        return status

    def remove(self, repo=None, namespace=None, name=None, groups=None,
               enabled="yes", branch="master", version="HEAD", built="yes"):
        """ Remove tools or a repo """
        self.logger.info("Starting: remove")
        status = (True, None)
        try:
            status = self.plugin.remove(name=name,
                                        repo=repo,
                                        namespace=namespace,
                                        groups=groups,
                                        enabled=enabled,
                                        branch=branch,
                                        version=version,
                                        built=built)
        except Exception as e:  # pragma: no cover
            self.logger.error("remove failed with error: " + str(e))
            status = (False, e)
        self.logger.info("Status of remove: " + str(status[0]))
        self.logger.info("Finished: remove")
        return status

    def _start_sections(self,
                        s,
                        files,
                        groups,
                        enabled,
                        branch,
                        version,
                        run_build):
        """ Run through sections for prep_start """
        tool_d = {}
        for section in s:
            # initialize needed vars
            template_path = os.path.join(s[section]['path'],
                                         'vent.template')
            c_name = s[section]['image_name'].replace(':', '-')
            c_name = c_name.replace('/', '-')
            image_name = s[section]['image_name']

            # checkout the right version and branch of the repo
            cwd = os.getcwd()
            self.logger.info("current directory is: " + str(cwd))
            os.chdir(os.path.join(s[section]['path']))
            status = self.p_helper.checkout(branch=branch, version=version)
            self.logger.info(status)
            os.chdir(cwd)

            if run_build:
                status = self.build(name=s[section]['name'],
                                    groups=groups,
                                    enabled=enabled,
                                    branch=branch,
                                    version=version)
                self.logger.info(status)

            # set docker settings for container
            vent_template = Template(template_path)
            status = vent_template.section('docker')
            self.logger.info(status)
            tool_d[c_name] = {'image': image_name,
                              'name': c_name}
            if status[0]:
                for option in status[1]:
                    options = option[1]
                    # check for commands to evaluate
                    if '`' in options:
                        cmds = options.split('`')
                        if len(cmds) > 2:
                            i = 1
                            while i < len(cmds):
                                try:
                                    cmds[i] = check_output(shlex.split(cmds[i]),
                                                           stderr=STDOUT,
                                                           close_fds=True).strip()
                                except Exception as e:  # pragma: no cover
                                    self.logger.error("unable to evaluate command specified in vent.template: " + str(e))
                                i += 2
                        options = "".join(cmds)
                    # store options set for docker
                    try:
                        tool_d[c_name][option[0]] = literal_eval(options)
                    except Exception as e:  # pragma: no cover
                        self.logger.error("unable to store the options set for docker: " + str(e))
                        tool_d[c_name][option[0]] = options

            # get temporary name for links, etc.
            status = vent_template.section('info')
            self.logger.info(status)
            plugin_c = Template(template=self.plugin.manifest)
            status, plugin_sections = plugin_c.sections()
            self.logger.info(status)
            for plugin_section in plugin_sections:
                status = plugin_c.option(plugin_section, "link_name")
                self.logger.info(status)
                image_status = plugin_c.option(plugin_section, "image_name")
                self.logger.info(image_status)
                if status[0] and image_status[0]:
                    cont_name = image_status[1].replace(':', '-')
                    cont_name = cont_name.replace('/', '-')
                    if cont_name not in tool_d:
                        tool_d[cont_name] = {'image': image_status[1],
                                             'name': cont_name,
                                             'start': False}
                    tool_d[cont_name]['tmp_name'] = status[1]

            # add extra labels
            if 'labels' not in tool_d[c_name]:
                tool_d[c_name]['labels'] = {}
            tool_d[c_name]['labels']['vent'] = Version()
            tool_d[c_name]['labels']['vent.namespace'] = s[section]['namespace']
            tool_d[c_name]['labels']['vent.branch'] = branch
            tool_d[c_name]['labels']['vent.version'] = version
            tool_d[c_name]['labels']['vent.name'] = s[section]['name']

            log_config = {'type': 'syslog',
                          'config': {'syslog-address': 'tcp://0.0.0.0:514',
                                     'syslog-facility': 'daemon',
                                     'tag': 'plugin'}}
            if 'groups' in s[section]:
                # add labels for groups
                tool_d[c_name]['labels']['vent.groups'] = s[section]['groups']
                # add restart=always to core containers
                if 'core' in s[section]['groups']:
                    tool_d[c_name]['restart_policy'] = {"Name": "always"}
                # send logs to syslog
                if 'syslog' not in s[section]['groups'] and 'core' in s[section]['groups']:
                    log_config['config']['tag'] = 'core'
                    tool_d[c_name]['log_config'] = log_config
                if 'syslog' not in s[section]['groups']:
                    tool_d[c_name]['log_config'] = log_config
                # mount necessary directories
                if 'files' in s[section]['groups']:
                    if 'volumes' in tool_d[c_name]:
                        tool_d[c_name]['volumes'][self.plugin.path_dirs.base_dir[:-1]] = {'bind': '/vent', 'mode': 'ro'}
                    else:
                        tool_d[c_name]['volumes'] = {self.plugin.path_dirs.base_dir[:-1]: {'bind': '/vent', 'mode': 'ro'}}
                    if files[0]:
                        tool_d[c_name]['volumes'][files[1]] = {'bind': '/files', 'mode': 'ro'}
            else:
                tool_d[c_name]['log_config'] = log_config

            # add label for priority
            status = vent_template.section('settings')
            self.logger.info(status)
            if status[0]:
                for option in status[1]:
                    if option[0] == 'priority':
                        tool_d[c_name]['labels']['vent.priority'] = option[1]

            # only start tools that have been built
            if s[section]['built'] != 'yes':
                del tool_d[c_name]
        return status, tool_d

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
        self.logger.info("Starting: prep_start")
        self.logger.info("Arguments: "+str(args))
        status = (False, None)
        try:
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
            s, _ = self.plugin.constraint_options(args, options)
            status, tool_d = self._start_sections(s,
                                                  files,
                                                  groups,
                                                  enabled,
                                                  branch,
                                                  version,
                                                  run_build)

            # check and update links, volumes_from, network_mode
            for container in tool_d.keys():
                if 'links' in tool_d[container]:
                    for link in tool_d[container]['links']:
                        for c in tool_d.keys():
                            if ('tmp_name' in tool_d[c] and
                               tool_d[c]['tmp_name'] == link):
                                tool_d[container]['links'][tool_d[c]['name']] = tool_d[container]['links'].pop(link)
                if 'volumes_from' in tool_d[container]:
                    tmp_volumes_from = tool_d[container]['volumes_from']
                    tool_d[container]['volumes_from'] = []
                    for volumes_from in list(tmp_volumes_from):
                        for c in tool_d.keys():
                            if ('tmp_name' in tool_d[c] and
                               tool_d[c]['tmp_name'] == volumes_from):
                                tool_d[container]['volumes_from'].append(tool_d[c]['name'])
                                tmp_volumes_from.remove(volumes_from)
                    tool_d[container]['volumes_from'] += tmp_volumes_from
                if 'network_mode' in tool_d[container]:
                    if tool_d[container]['network_mode'].startswith('container:'):
                        network_c_name = tool_d[container]['network_mode'].split('container:')[1]
                        for c in tool_d.keys():
                            if ('tmp_name' in tool_d[c] and
                               tool_d[c]['tmp_name'] == network_c_name):
                                tool_d[container]['network_mode'] = 'container:' + tool_d[c]['name']

            # remove tmp_names
            for c in tool_d.keys():
                if 'tmp_name' in tool_d[c]:
                    del tool_d[c]['tmp_name']

            # remove containers that shouldn't be started
            for c in tool_d.keys():
                if 'start' in tool_d[c] and not tool_d[c]['start']:
                    del tool_d[c]
            status = (True, tool_d)
        except Exception as e:  # pragma: no cover
            self.logger.error("prep_start failed with error: "+str(e))
            status = (False, e)

        self.logger.info("Status of prep_start: "+str(status[0]))
        self.logger.info("Finished: prep_start")
        return status

    def start(self, tool_d):
        """
        Start a set of tools that match the parameters given, if no parameters
        are given, start all installed tools on the master branch at verison
        HEAD that are enabled
        """
        self.logger.info("Starting: start")
        status = (True, None)
        try:
            # check start priorities (priority of groups alphabetical for now)
            group_orders = {}
            groups = []
            containers_remaining = []
            for container in tool_d:
                containers_remaining.append(container)
                if 'labels' in tool_d[container]:
                    if 'vent.groups' in tool_d[container]['labels']:
                        groups += tool_d[container]['labels']['vent.groups'].split(',')
                        if 'vent.priority' in tool_d[container]['labels']:
                            priorities = tool_d[container]['labels']['vent.priority'].split(',')
                            container_groups = tool_d[container]['labels']['vent.groups'].split(',')
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
                                    self.logger.info("started " +
                                                     str(container_tuple[1]) +
                                                     " with ID: " +
                                                     str(container.short_id))
                                except Exception as err:  # pragma: no cover
                                    self.logger.error(str(err))
                                    container_id = self.d_client.containers.run(detach=True,
                                                                                **tool_d[container_tuple[1]])
                                    self.logger.info("started " +
                                                     str(container_tuple[1]) +
                                                     " with ID: " +
                                                     str(container_id))
                            except Exception as e:  # pragma: no cover
                                self.logger.error("failed to start " +
                                                  str(container_tuple[1]) +
                                                  " because: " + str(e))

            # start the rest of the containers that didn't have any priorities
            for container in containers_remaining:
                try:
                    try:
                        c = self.d_client.containers.get(container)
                        c.start()
                        self.logger.info("started " + str(container) +
                                         " with ID: " + str(c.short_id))
                    except Exception as err:  # pragma: no cover
                        self.logger.error(str(err))
                        container_id = self.d_client.containers.run(detach=True,
                                                                    **tool_d[container])
                        self.logger.info("started " + str(container) +
                                         " with ID: " + str(container_id))
                except Exception as e:  # pragma: no cover
                    self.logger.error("failed to start " + str(container) +
                                      " because: " + str(e))
        except Exception as e:  # pragma: no cover
            self.logger.error("start failed with error: " + str(e))
            status = (False, e)

        self.logger.info("Status of start: " + str(status[0]))
        self.logger.info("Finished: start")
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
        self.logger.info("Starting: update")
        self.logger.info(args)
        status = (True, None)
        try:
            options = ['path', 'image_name', 'image_id']
            s, template = self.plugin.constraint_options(args, options)

            # get existing containers and images and states
            running_containers = Containers()
            built_images = Images()
            self.logger.info("running docker containers: " +
                             str(running_containers))
            self.logger.info("built docker images: " + str(built_images))

            # if repo, pull and build
            # if registry image, pull
            for section in s:
                try:
                    cwd = os.getcwd()
                    self.logger.info("current working directory: " + str(cwd))
                    os.chdir(s[section]['path'])
                    c_status = self.p_helper.checkout(branch=branch,
                                                      version=version)
                    self.logger.info(c_status)
                    try:
                        os.chdir(cwd)
                    except Exception as e:  # pragma: no cover
                        self.logger.error("unable to change directory: " +
                                          str(e))
                    template = self.plugin.builder(template,
                                                   s[section]['path'],
                                                   s[section]['image_name'],
                                                   section,
                                                   build=True,
                                                   branch=branch,
                                                   version=version)
                    self.logger.info(template)
                    # stop & remove old containers & images if image_id updated
                    # !! TODO

                    # start containers if they were running
                    # !! TODO

                    # TODO logging
                except Exception as e:  # pragma: no cover
                    self.logger.error("unable to update: " + str(section) +
                                      " because: " + str(e))

            template.write_config()
        except Exception as e:  # pragma: no cover
            self.logger.error("update failed with error: " + str(e))
            status = (False, e)

        self.logger.info("Status of update: " + str(status[0]))
        self.logger.info("Finished: update")
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
        args = locals()
        self.logger.info("Starting: stop")
        self.logger.info(args)
        status = (True, None)
        try:
            # !! TODO need to account for plugin containers that have random
            #         names, use labels perhaps
            options = ['name',
                       'namespace',
                       'built',
                       'groups',
                       'path',
                       'image_name',
                       'branch',
                       'version']
            s, _ = self.plugin.constraint_options(args, options)
            self.logger.info(s)
            for section in s:
                container_name = s[section]['image_name'].replace(':', '-')
                container_name = container_name.replace('/', '-')
                try:
                    container = self.d_client.containers.get(container_name)
                    container.stop()
                    self.logger.info("stopped " + str(container_name))
                except Exception as e:  # pragma: no cover
                    self.logger.error("failed to stop " + str(container_name) +
                                      " because: " + str(e))
        except Exception as e:  # pragma: no cover
            self.logger.error("stop failed with error: " + str(e))
            status = (False, e)
        self.logger.info("Status of stop: " + str(status[0]))
        self.logger.info("Finished: stop")
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
        args = locals()
        self.logger.info("Starting: clean")
        self.logger.info(args)
        status = (True, None)
        try:
            # !! TODO need to account for plugin containers that have random
            #         names, use labels perhaps
            options = ['name',
                       'namespace',
                       'built',
                       'groups',
                       'path',
                       'image_name',
                       'branch',
                       'version']
            s, _ = self.plugin.constraint_options(args, options)
            self.logger.info(s)
            for section in s:
                container_name = s[section]['image_name'].replace(':', '-')
                container_name = container_name.replace('/', '-')
                try:
                    container = self.d_client.containers.get(container_name)
                    container.remove(force=True)
                    self.logger.info("cleaned " + str(container_name))
                except Exception as e:  # pragma: no cover
                    self.logger.error("failed to clean " +
                                      str(container_name) +
                                      " because: " + str(e))
        except Exception as e:  # pragma: no cover
            self.logger.error("clean failed with error: " + str(e))
            status = (False, e)
        self.logger.info("Status of clean: " + str(status[0]))
        self.logger.info("Finished: clean")
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
        self.logger.info("Starting: build")
        self.logger.info(args)
        status = (True, None)
        try:
            options = ['image_name', 'path']
            s, template = self.plugin.constraint_options(args, options)
            self.logger.info(s)
            for section in s:
                self.logger.info("Building " + str(section) + " ...")
                template = self.plugin.builder(template,
                                               s[section]['path'],
                                               s[section]['image_name'],
                                               section,
                                               build=True,
                                               branch=branch,
                                               version=version)
            template.write_config()
        except Exception as e:  # pragma: no cover
            self.logger.error("build failed with error: " + str(e))
            status = (False, e)
        self.logger.info("Status of build: " + str(status[0]))
        self.logger.info("Finished: build")
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
    def upgrade():
        # TODO
        return

    def reset(self):
        """ Factory reset all of Vent's user data, containers, and images """
        status = (True, None)
        error_message = ''

        # remove containers
        try:
            c_list = self.d_client.containers.list(filters={'label': 'vent'},
                                                   all=True)
            for c in c_list:
                c.remove(force=True)
        except Exception as e:  # pragma: no cover
            error_message += "Error removing Vent containers: " + str(e) + "\n"

        # remove images
        try:
            i_list = self.d_client.images.list(filters={'label': 'vent'},
                                               all=True)
            for i in i_list:
                self.d_client.images.remove(image=i.id, force=True)
        except Exception as e:  # pragma: no cover
            error_message += "Error deleting Vent images: " + str(e) + "\n"

        # remove .vent folder
        try:
            shutil.rmtree(os.path.join(os.path.expanduser('~'), '.vent'))
        except Exception as e:  # pragma: no cover
            error_message += "Error deleting Vent data: " + str(e) + "\n"

        if error_message:
            status = (False, error_message)

        return status

    def logs(self, c_type=None, grep_list=None):
        """ Generically filter logs stored in log containers """
        def get_logs(logs, log_entries):
            try:
                for log in logs:
                    if str(container.name) in log_entries:
                        log_entries[str(container.name)].append(log)
                    else:
                        log_entries[str(container.name)] = [log]
            except Exception as e:  # pragma: no cover
                self.logger.error("Unable to get logs for " +
                                  str(container.name) +
                                  " because: " + str(e))
            return log_entries

        self.logger.info("Starting: logs")
        status = (True, None)
        log_entries = {}
        containers = self.d_client.containers.list(all=True,
                                                   filters={'label': 'vent'})
        self.logger.info("containers found: " + str(containers))
        comp_c = containers
        if c_type:
            try:
                comp_c = [c for c in containers
                          if (c_type
                              in c.attrs['Config']['Labels']['vent.groups'])]
            except Exception as e:  # pragma: no cover
                self.logger.error("Unable to limit containers by: " +
                                  str(c_type) + " because: " +
                                  str(e))

        if grep_list:
            for expression in grep_list:
                for container in comp_c:
                    try:
                        # 'logs' stores each line containing the expression
                        logs = [log for log in container.logs().split("\n")
                                if expression in log]
                        log_entries = get_logs(logs, log_entries)
                    except Exception as e:  # pragma: no cover
                        self.logger.info("Unable to get logs for " +
                                         str(container) +
                                         " because: " + str(e))
        else:
            for container in comp_c:
                try:
                    logs = container.logs().split("\n")
                    log_entries = get_logs(logs, log_entries)
                except Exception as e:  # pragma: no cover
                    self.logger.info("Unabled to get logs for " +
                                     str(container) +
                                     " because: " + str(e))

        status = (True, log_entries)
        self.logger.info("Status of logs: " + str(status[0]))
        self.logger.info("Finished: logs")
        return status

    @staticmethod
    def help():
        # TODO
        return

    def inventory(self, choices=None):
        """ Return a dictionary of the inventory items and status """
        self.logger.info("Starting: inventory")
        status = (True, None)
        self.logger.info("choices specified: " + str(choices))
        if not choices:
            return (False, "No choices made")
        try:
            # choices: repos, core, tools, images, built, running, enabled
            items = {'repos': [], 'core': [], 'tools': [], 'images': [],
                     'built': [], 'running': [], 'enabled': []}

            tools = self.plugin.list_tools()
            self.logger.info("found tools: " + str(tools))
            for choice in choices:
                for tool in tools:
                    try:
                        if choice == 'repos':
                            if 'repo' in tool:
                                if (tool['repo'] and
                                   tool['repo'] not in items[choice]):
                                    items[choice].append(tool['repo'])
                        elif choice == 'core':
                            if 'groups' in tool:
                                if 'core' in tool['groups']:
                                    items[choice].append((tool['section'],
                                                          tool['name']))
                        elif choice == 'tools':
                            items[choice].append((tool['section'],
                                                  tool['name']))
                        elif choice == 'images':
                            # TODO also check against docker
                            items[choice].append((tool['section'],
                                                  tool['name'],
                                                  tool['image_name']))
                        elif choice == 'built':
                            items[choice].append((tool['section'],
                                                  tool['name'],
                                                  tool['built']))
                        elif choice == 'running':
                            containers = Containers()
                            status = 'not running'
                            for container in containers:
                                image_name = tool['image_name'] \
                                             .rsplit(":" +
                                                     tool['version'], 1)[0]
                                image_name = image_name.replace(':', '-')
                                image_name = image_name.replace('/', '-')
                                if container[0] == image_name:
                                    status = container[1]
                            items[choice].append((tool['section'],
                                                  tool['name'],
                                                  status))
                        elif choice == 'enabled':
                            items[choice].append((tool['section'],
                                                  tool['name'],
                                                  tool['enabled']))
                        else:
                            # unknown choice
                            pass
                    except Exception as e:  # pragma: no cover
                        self.logger.error("unable to grab info about tool: " +
                                          str(tool) + " because: " + str(e))
            status = (True, items)
        except Exception as e:  # pragma: no cover
            self.logger.error("inventory failed with error: " + str(e))
            status = (False, str(e))
        self.logger.info("Status of inventory: " + str(status[0]))
        self.logger.info("Finished: inventory")
        return status
