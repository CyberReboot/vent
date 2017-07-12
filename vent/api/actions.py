import json
import os
import shutil

from vent.api.plugins import Plugin
from vent.api.templates import Template
from vent.helpers.logs import Logger
from vent.helpers.meta import Containers
from vent.helpers.meta import Images


class Action:
    """ Handle actions in menu """
    def __init__(self, **kargs):
        self.plugin = Plugin(**kargs)
        self.d_client = self.plugin.d_client
        self.vent_config = os.path.join(self.plugin.path_dirs.meta_dir,
                                        "vent.cfg")
        self.p_helper = self.plugin.p_helper
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
            status = (False, str(e))
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
            status = (False, str(e))
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

    def prep_start(self,
                   repo=None,
                   name=None,
                   groups=None,
                   enabled="yes",
                   branch="master",
                   version="HEAD"):
        """ Prep a bunch of containers to be started to they can be ordered """
        args = locals()
        del args['self']
        self.logger.info("Starting: prep_start")
        status = self.p_helper.prep_start(**args)
        self.logger.info("Status of prep_start: " + str(status[0]))
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
            p_results = self.p_helper.start_priority_containers(groups,
                                                                group_orders,
                                                                tool_d)

            # start the rest of the containers that didn't have any priorities
            r_results = self.p_helper.start_remaining_containers(containers_remaining, tool_d)
            results = (p_results[0] + r_results[0],
                       p_results[1] + r_results[1])

            if len(results[1]) > 0:
                status = (False, results)
            else:
                status = (True, results)
        except Exception as e:  # pragma: no cover
            self.logger.error("start failed with error: " + str(e))
            status = (False, str(e))

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
            s, template = self.p_helper.constraint_options(args, options)

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
                    os.chdir(cwd)
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
            s, _ = self.p_helper.constraint_options(args, options)
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
            s, _ = self.p_helper.constraint_options(args, options)
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
            s, template = self.p_helper.constraint_options(args, options)
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
            cwd = os.getcwd()
            if cwd.startswith(os.path.join(os.path.expanduser('~'), '.vent')):
                os.chdir(os.path.expanduser('~'))
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

    def get_configure(self,
                      repo=None,
                      name=None,
                      groups=None,
                      enabled="yes",
                      branch="master",
                      version="HEAD"):
        """ Get the vent.template file for a given tool """
        self.logger.info("Starting: get_configure")
        constraints = locals()
        status = (True, None)
        options = ['path']
        tools = self.p_helper.constraint_options(constraints, options)[0]
        if tools:
            for tool in tools:
                template_path = os.path.join(tools[tool]['path'],
                                             'vent.template')
                try:
                    with open(template_path) as f:
                        status = (True, f.read())
                except Exception as e:
                    status = (False, str(e))
                    self.logger.error(str(e))
        else:
            status = (False, "Couldn't get vent.template")
        self.logger.info("Status of get_configure: " + str(status[0]))
        self.logger.info("Finished: get_configure")
        return status

    def save_configure(self,
                       repo=None,
                       name=None,
                       groups=None,
                       enabled="yes",
                       branch="master",
                       version="HEAD",
                       config_val=""):
        """
        Save changes made to vent.template through npyscreen to the template
        and to plugin_manifest
        """
        self.logger.info("Starting: save_configure")
        constraints = locals()
        del constraints['config_val']
        status = (True, None)
        options = ['path']
        tools, manifest = self.p_helper.constraint_options(constraints,
                                                           options)
        if tools:
            for tool in tools:
                template_path = os.path.join(tools[tool]['path'],
                                             'vent.template')
                # save in vent.template
                try:
                    with open(template_path, 'w') as f:
                        f.write(config_val)
                except Exception as e:
                    self.logger.error(str(e))
                    status = (False, str(e))
                    break
                # save in plugin_manifest
                try:
                    vent_template = Template(template_path)
                    sections = vent_template.sections()
                    if sections[0]:
                        for section in sections[1]:
                            section_dict = {}
                            options = vent_template.options(section)
                            if options[0]:
                                for option in options[1]:
                                    option_name = option
                                    if option == 'name':
                                        option_name = 'link_name'
                                    option_val = vent_template.option(section,
                                                                      option)[1]
                                    section_dict[option_name] = option_val
                            if section_dict:
                                manifest.set_option(tool, section,
                                                    json.dumps(section_dict))
                            elif manifest.option(tool, section)[0]:
                                manifest.del_option(tool, section)
                        manifest.write_config()
                except Exception as e:
                    self.logger.error(str(e))
                    status = (False, str(e))
        else:
            status = (False, "Couldn't save configuration")
        self.logger.info("Status of save_configure: " + str(status[0]))
        self.logger.info("Finished: save_configure")
        return status
