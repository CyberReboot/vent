import docker
import os
import shlex

from datetime import datetime
from os import chdir
from subprocess import check_output, STDOUT

from vent.api.actions import Action
from vent.api.plugin_helpers import PluginHelper
from vent.api.templates import Template
from vent.helpers.logs import Logger
from vent.helpers.meta import Tools


class MenuHelper:
    """ Handle helper functions in the API for the Menu """
    def __init__(self, **kargs):
        self.api_action = Action(**kargs)
        self.plugin = self.api_action.plugin
        self.p_helper = self.api_action.p_helper
        self.logger = Logger(__name__)

    def cores(self, action, branch="master", version='HEAD'):
        """
        Supply action (install, build, start, stop, clean) for core tools
        """
        self.logger.info("Starting: cores")
        status = (False, None)
        try:
            self.logger.info("action provided: " + str(action))
            core = self.tools_status(True, branch=branch, version=version)[1]
            if action in ["install", "build"]:
                tools = []
                core_repo = 'https://github.com/cyberreboot/vent'
                resp = self.p_helper.apply_path(core_repo)

                if resp[0]:
                    cwd = resp[1]
                else:
                    self.logger.info("apply_path failed. Exiting cores"
                                     " with status " + str(resp))
                    return resp

                path = os.path.join(self.plugin.path_dirs.plugins_dir,
                                    'cyberreboot/vent')

                # TODO commenting out for now, should use update_repo
                #response = self.p_helper.checkout(branch=branch,
                #                                  version=version)
                response = (True, None)

                self.logger.info("status of plugin checkout " +
                                 str(response))
                matches = self.p_helper.available_tools(path,
                                                        version=version,
                                                        groups='core')
                for match in matches:
                    name = match[0].rsplit('/')[-1]
                    constraints = {'name': name,
                                   'repo': core_repo}
                    prev_installed, _ = self.p_helper. \
                                        constraint_options(constraints, [])
                    if not prev_installed:
                        tools.append((match[0], ''))
                # only add stuff not already installed or repo specification
                if ((tools) or
                        (isinstance(matches, list) and len(matches) == 0)):
                    status = self.plugin.add(core_repo,
                                             tools=tools,
                                             branch=branch,
                                             build=False, core=True)
                    self.logger.info("status of plugin add: " + str(status))
                else:
                    self.logger.info("no new tools to install")
                    status = (True, "previously installed")
                plugin_c = Template(template=self.plugin.manifest)
                sections = plugin_c.sections()
                for tool in core['normal']:
                    for section in sections[1]:
                        name = plugin_c.option(section, "name")
                        orig_branch = plugin_c.option(section, "branch")
                        namespace = plugin_c.option(section, "namespace")
                        version = plugin_c.option(section, "version")
                        if (name[1] == tool and
                           orig_branch[1] == branch and
                           namespace[1] == "cyberreboot/vent" and
                           version[1] == "HEAD"):
                            plugin_c.set_option(section,
                                                "image_name",
                                                "cyberreboot/vent-" +
                                                tool.replace('_', '-') + ":" +
                                                branch)
                plugin_c.write_config()
                chdir(cwd)
            if action == "build":
                plugin_c = Template(template=self.plugin.manifest)
                sections = plugin_c.sections()
                try:
                    for tool in core['normal']:
                        for section in sections[1]:
                            tool = tool.replace('_', '-')
                            image_name = plugin_c.option(section,
                                                         "image_name")
                            check_image = "cyberreboot/vent-"
                            check_image += tool + ":" + branch
                            if image_name[1] == check_image:
                                timestamp = str(datetime.utcnow()) + " UTC"
                                try:
                                    # currently can't use docker-py because it
                                    # returns a 404 on pull so no way to valid
                                    # if it worked or didn't
                                    image_id = None
                                    cmd = "docker pull " + check_image
                                    output = check_output(shlex.split(cmd),
                                                          stderr=STDOUT).decode("utf-8")

                                    # image_name in format of (bool, image_name)
                                    name = image_name[1]

                                    d_client = docker.from_env()
                                    image_attrs = d_client.images.get(name)
                                    image_attrs = image_attrs.attrs
                                    image_id = image_attrs['Id'].split(':')[1][:12]

                                    if image_id:
                                        plugin_c.set_option(section,
                                                            "built",
                                                            "yes")
                                        plugin_c.set_option(section,
                                                            "image_id",
                                                            image_id)
                                        plugin_c.set_option(section,
                                                            "last_updated",
                                                            timestamp)
                                        status = (True, "Pulled " + tool)
                                        self.logger.info(str(status))
                                    else:
                                        plugin_c.set_option(section,
                                                            "built",
                                                            "failed")
                                        plugin_c.set_option(section,
                                                            "last_updated",
                                                            timestamp)
                                        status = (False,
                                                  "Failed to pull image " +
                                                  str(output.split('\n')[-1]))
                                        self.logger.error(str(status))
                                except Exception as e:  # pragma: no cover
                                    plugin_c.set_option(section,
                                                        "built",
                                                        "failed")
                                    plugin_c.set_option(section,
                                                        "last_updated",
                                                        timestamp)
                                    status = (False,
                                              "Failed to pull image " + str(e))
                                    self.logger.error(str(status))
                except Exception as e:  # pragma: no cover
                    status = (False, "Failed to pull images " + str(e))
                    self.logger.error(str(status))
                plugin_c.write_config()
            elif action == "start":
                status = self.api_action.prep_start(groups="core",
                                                    branch=branch)
                if status[0]:
                    tool_d = status[1]
                    status = self.api_action.start(tool_d)
            elif action == "stop":
                status = self.api_action.stop(groups="core", branch=branch)
            elif action == "clean":
                status = self.api_action.clean(groups="core", branch=branch)
        except Exception as e:  # pragma: no cover
            self.logger.info("core failed with error: " + str(e))
            status = (False, e)

        self.logger.info("Status of core: " + str(status[0]))
        self.logger.info("Finished: core")
        return status

    def repo_branches(self, repo):
        """ Get the branches of a repository """
        self.logger.info("Starting: repo_branches")
        self.logger.info("repo given: " + str(repo))
        branches = []
        try:
            # switch to directory where repo will be cloned to
            status = self.p_helper.apply_path(repo)
            if status[0]:
                cwd = status[1]
            else:
                self.logger.info("apply_path failed. Exiting repo_branches"
                                 " with status " + str(status))
                return status

            check_output(shlex.split("git pull --all"),
                         stderr=STDOUT,
                         close_fds=True)
            branch_output = check_output(shlex.split("git branch -a"),
                                         stderr=STDOUT,
                                         close_fds=True)
            branch_output = branch_output.split(b"\n")
            for branch in branch_output:
                br = branch.strip()
                if br.startswith(b'*'):
                    br = br[2:]
                if b"/" in br:
                    branches.append(br.rsplit(b'/', 1)[1].decode("utf-8"))
                elif br:
                    branches.append(br.decode("utf-8"))

            branches = list(set(branches))
            self.logger.info("branches found: " + str(branches))
            for branch in branches:
                try:
                    check_output(shlex.split("git checkout " + branch),
                                 stderr=STDOUT,
                                 close_fds=True)
                except Exception as e:  # pragma: no cover
                    self.logger.error("repo_branches failed with error: " +
                                      str(e) + " on branch: " + str(branch))
                    status = (False, e)
                    self.logger.info("Exiting repo_branches with status: " +
                                     str(status))
                    return status

            chdir(cwd)
            status = (True, branches)
        except Exception as e:  # pragma: no cover
            self.logger.error("repo_branches failed with error: " + str(e))
            status = (False, e)

        self.logger.info("Status of repo_branches: " + str(status))
        self.logger.info("Finished: repo_branches")
        return status

    def repo_commits(self, repo):
        """ Get the commit IDs for all of the branches of a repository """
        self.logger.info("Starting: repo_commits")
        self.logger.info("repo given: " + str(repo))
        commits = []
        try:
            status = self.p_helper.apply_path(repo)
            # switch to directory where repo will be cloned to
            if status[0]:
                cwd = status[1]
            else:
                self.logger.info("apply_path failed. Exiting repo_commits with"
                                 " status: " + str(status))
                return status

            status = self.repo_branches(repo)
            if status[0]:
                branches = status[1]
                for branch in branches:
                    try:
                        branch_output = check_output(shlex
                                                     .split("git rev-list origin/" +
                                                            branch),
                                                     stderr=STDOUT,
                                                     close_fds=True).decode("utf-8")
                        branch_output = branch_output.split("\n")[:-1]
                        branch_output += ['HEAD']
                        commits.append((branch, branch_output))
                    except Exception as e:  # pragma: no cover
                        self.logger.error("repo_commits failed with error: " +
                                          str(e) + " on branch: " +
                                          str(branch))
                        status = (False, e)
                        self.logger.info("Exiting repo_commits with status: " +
                                         str(status))
                        return status
            else:
                self.logger.info("repo_branches failed. Exiting repo_commits"
                                 " with status: " + str(status))
                return status

            chdir(cwd)
            status = (True, commits)
        except Exception as e:  # pragma: no cover
            self.logger.error("repo_commits failed with error: " + str(e))
            status = (False, e)

        self.logger.info("Status of repo_commits: " + str(status))
        self.logger.info("Finished: repo_commits")
        return status

    def repo_tools(self, repo, branch, version):
        """ Get available tools for a repository branch at a version """
        self.logger.info("Starting: repo_tools")
        self.logger.info("repo given: " + str(repo))
        self.logger.info("branch given: " + str(branch))
        self.logger.info("version given: " + str(version))
        try:
            tools = []
            status = self.p_helper.apply_path(repo)
            # switch to directory where repo will be cloned to
            if status[0]:
                cwd = status[1]
            else:
                self.logger.info("apply_path failed. Exiting repo_tools with"
                                 " status: " + str(status))
                return status

            # TODO commenting out for now, should use update_repo
            #status = self.p_helper.checkout(branch=branch, version=version)
            status = (True, None)

            if status[0]:
                path, _, _ = self.p_helper.get_path(repo)
                tools = self.p_helper.available_tools(path, version=version)
            else:
                self.logger.info("checkout failed. Exiting repo_tools with"
                                 " status: " + str(status))
                return status

            chdir(cwd)
            status = (True, tools)
        except Exception as e:  # pragma: no cover
            self.logger.error("repo_tools failed with error: " + str(e))
            status = (False, e)

        self.logger.info("Status of repo_tools: " + str(status))
        self.logger.info("Finished: repo_tools")
        return status

    def tools_status(self, core, branch="master", version="HEAD", **kargs):
        """
        Get tools that are currently installed/built/running and also the
        number of repos that those tools come from; can toggle whether looking
        for core tools or plugin tools
        """
        # !! TODO this might need to store namespaces/branches/versions
        all_tools = {'built': [], 'running': [], 'installed': [], 'normal': []}
        core_repo = 'https://github.com/cyberreboot/vent'
        repos = set()
        tools = Tools(**kargs)

        # get manifest file
        manifest = os.path.join(self.api_action.plugin.path_dirs.meta_dir,
                                "plugin_manifest.cfg")
        template = Template(template=manifest)
        tools = template.sections()

        # get repos
        if core:
            p_helper = PluginHelper(plugins_dir='.internals/plugins/')
            repos.add(core_repo)
        else:
            p_helper = PluginHelper(plugins_dir='plugins/')
            for tool in tools[1]:
                repo = template.option(tool, 'repo')
                if repo[0] and repo[1] != core_repo:
                    repos.add(repo[1])

        # get normal tools
        for repo in repos:
            status, _ = p_helper.clone(repo)
            if status:
                p_helper.apply_path(repo)

                # TODO commenting out for now, should use update_repo
                #p_helper.checkout(branch=branch, version=version)

                path, _, _ = p_helper.get_path(repo, core=core)
                matches = None
                if core:
                    matches = p_helper.available_tools(path, version=version,
                                                       groups='core')
                else:
                    matches = p_helper.available_tools(path, version=version)
                for match in matches:
                    if core:
                        all_tools['normal'].append(match[0].split('/')[-1].replace('_', '-'))
                    else:
                        all_tools['normal'].append(match[0].split('/')[-1])

        # get tools that have been installed
        for tool in tools[1]:
            repo = template.option(tool, "repo")
            if repo[0] and repo[1] in repos:
                name = template.option(tool, "name")
                if name[0]:
                    all_tools['installed'].append(name[1].replace('_', '-'))

        # get tools that have been built and/or are running
        try:
            d_client = docker.from_env()
            images = d_client.images.list(filters={'label': 'vent'})
            for image in images:
                try:
                    core_check = ("vent.groups" in image.attrs['Config']['Labels'] and
                                  'core' in image.attrs['Config']['Labels']['vent.groups'])
                    image_check = None
                    if core:
                        image_check = core_check
                    else:
                        image_check = not core_check
                    if image_check:
                        if ('vent.name' in image.attrs['Config']['Labels'] and
                           'hidden' not in image.attrs['Config']['Labels']['vent.groups']):
                            if core:
                                all_tools['built'].append(image.attrs['Config']['Labels']['vent.name'].replace('_', '-'))
                            else:
                                all_tools['built'].append(image.attrs['Config']['Labels']['vent.name'])
                except Exception as err:  # pragma: no cover
                    self.logger.error("image_check went wrong " + str(err))
            containers = d_client.containers.list(filters={'label': 'vent'})
            for container in containers:
                try:
                    core_check = ("vent.groups" in container.attrs['Config']['Labels'] and
                                  'core' in container.attrs['Config']['Labels']['vent.groups'])
                    container_check = None
                    if core:
                        container_check = core_check
                    else:
                        container_check = not core_check
                    if container_check:
                        if ('vent.name' in container.attrs['Config']['Labels'] and
                                'hidden' not in image.attrs['Config']['Labels']['vent.groups']):
                            if core:
                                all_tools['running'].append(container.attrs['Config']['Labels']['vent.name'].replace('_', '-'))
                            else:
                                all_tools['running'].append(container.attrs['Config']['Labels']['vent.name'])
                except Exception as err:  # pragma: no cover
                    self.logger.error("core_check went wrong " + str(err))
        except Exception as e:  # pragma: no cover
            self.logger.error("Something with docker went wrong " + str(e))
        return (len(repos), all_tools)
