import os
import shlex

from datetime import datetime
from os import chdir
from subprocess import check_output, STDOUT

from vent.api.actions import Action
from vent.api.plugins import Plugin
from vent.api.plugin_helpers import PluginHelper
from vent.api.templates import Template
from vent.helpers.logs import Logger
from vent.helpers.meta import Tools_Status


class MenuHelper:
    """ Handle helper functions in the API for the Menu """
    def __init__(self, **kargs):
        self.api_action = Action(**kargs)
        self.plugin = Plugin(**kargs)
        self.p_helper = PluginHelper(**kargs)
        self.logger = Logger(__name__)

    def cores(self, action, branch="master", version='HEAD'):
        """
        Supply action (install, build, start, stop, clean) for core tools
        """
        self.logger.info("Starting: cores")
        status = (False, None)
        try:
            self.logger.info("action provided: " + str(action))
            core = Tools_Status(True, branch=branch, version=version)[1]
            if action in ["install", "build"]:
                tools = []
                plugins = Plugin(plugins_dir=".internals/plugins/")
                self.p_helper.apply_path('https://github.com/cyberreboot/vent')
                path = os.path.join(plugins.path_dirs.plugins_dir,
                                    'cyberreboot/vent')
                response = self.p_helper.checkout(branch=branch,
                                                  version=version)
                self.logger.info("status of plugin checkout " + str(response))
                matches = self.p_helper.available_tools(path, version=version,
                                                        groups='core')
                for match in matches:
                    tools.append((match[0], ''))
                status = plugins.add('https://github.com/cyberreboot/vent',
                                     tools=tools,
                                     branch=branch,
                                     build=False)
                self.logger.info("status of plugin add: " + str(status))
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
                                                tool + ":" + branch)
                plugin_c.write_config()
            if action == "build":
                plugin_c = Template(template=self.plugin.manifest)
                sections = plugin_c.sections()
                try:
                    for tool in core['normal']:
                        for section in sections[1]:
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
                                                          stderr=STDOUT)
                                    sha = "Digest: sha256:"
                                    for line in output.split('\n'):
                                        if line.startswith(sha):
                                            image_id = line.split(sha)[1][:12]
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
            branch_output = branch_output.split("\n")
            for branch in branch_output:
                b = branch.strip()
                if b.startswith('*'):
                    b = b[2:]
                if "/" in b:
                    branches.append(b.rsplit('/', 1)[1])
                elif b:
                    branches.append(b)

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

            try:
                chdir(cwd)
            except Exception as e:  # pragma: no cover
                self.logger.error("unable to change directory to: " +
                                  str(cwd) + "because: " + str(e))

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
                                                     .split("git rev-list " +
                                                            branch),
                                                     stderr=STDOUT,
                                                     close_fds=True)
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
            try:
                chdir(cwd)
            except Exception as e:  # pragma: no cover
                self.logger.error("unable to change directory to: " +
                                  str(cwd) + " because: " + str(e))

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

            status = self.p_helper.checkout(branch=branch, version=version)
            if status[0]:
                path, _, _ = self.p_helper.get_path(repo)
                tools = self.p_helper.available_tools(path, version=version)
            else:
                self.logger.info("checkout failed. Exiting repo_tools with"
                                 " status: " + str(status))
                return status
            try:
                chdir(cwd)
            except Exception as e:  # pragma: no cover
                self.logger.error("unable to change directory to: " +
                                  str(cwd) + " because: " + str(e))

            status = (True, tools)
        except Exception as e:  # pragma: no cover
            self.logger.error("repo_tools failed with error: " + str(e))
            status = (False, e)

        self.logger.info("Status of repo_tools: " + str(status))
        self.logger.info("Finished: repo_tools")
        return status
