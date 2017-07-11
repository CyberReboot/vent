import docker
import json
import os
import shlex

from datetime import datetime
from os import chdir, getcwd
from os.path import join
from subprocess import check_output, STDOUT

from vent.api.plugin_helpers import PluginHelper
from vent.api.templates import Template
from vent.helpers.errors import ErrorHandler
from vent.helpers.logs import Logger
from vent.helpers.paths import PathDirs


class Plugin:
    """ Handle Plugins """
    def __init__(self, **kargs):
        self.path_dirs = PathDirs(**kargs)
        self.manifest = join(self.path_dirs.meta_dir,
                             "plugin_manifest.cfg")
        self.p_helper = PluginHelper(**kargs)
        self.d_client = docker.from_env()
        self.logger = Logger(__name__)

    def add(self, repo, tools=None, overrides=None, version="HEAD",
            branch="master", build=True, user=None, pw=None, groups=None,
            version_alias=None, wild=None, remove_old=True, disable_old=True,
            limit_groups=None, core=False):
        """
        Adds a plugin of tool(s)
        tools is a list of tuples, where the pair is a tool name (path to
        Dockerfile) and version
          tools are for explicitly limiting which tools and versions
          (if version in tuple is '', then defaults to version)
        overrides is a list of tuples, where the pair is a tool name (path to
        Dockerfile) and a version
          overrides are for explicitly removing tools and overriding versions
          of tools (if version in tuple is '', then tool is removed, otherwise
          that tool is checked out at the specific version in the tuple)
        if tools and overrides are left as empty lists, then all tools in the
          repo are pulled down at the version and branch specified or defaulted
          to
        version is globally set for all tools, unless overridden in tools or
          overrides
        branch is globally set for all tools
        build is a boolean of whether or not to build the tools now
        user is the username for a private repo if needed
        pw is the password to go along with the username for a private repo
        groups is globally set for all tools
        version_alias is globally set for all tools and is a mapping from a
          friendly version tag to the real version commit ID
        wild lets you specify individual overrides for additional values in the
          tuple of tools or overrides.  wild is a list containing one or more
          of the following: branch, build, groups, version_alias
          the order of the items in the wild list will expect values to be
          tacked on in the same order to the tuple for tools and overrides in
          additional to the tool name and version
        remove_old lets you specify whether or not to remove previously found
          tools that match to ones being added currently (note does not stop
          currently running instances of the older version)
        disable_old lets you specify whether or not to disable previously found
          tools that match to ones being added currently (note does not stop
          currently running instances of the older version)
        limit_groups is a list of groups to build tools for that match group
          names in vent.template of each tool if exists
        Examples:
          repo=fe
            (get all tools from repo 'fe' at version 'HEAD' on branch 'master')
          repo=foo, version="3d1f", branch="foo"
            (get all tools from repo 'foo' at verion '3d1f' on branch 'foo')
          repo=foo, tools=[('bar', ''), ('baz', '1d32')]
            (get only 'bar' from repo 'foo' at version 'HEAD' on branch
            'master' and 'baz' from repo 'foo' at version '1d32' on branch
            'master', ignore all other tools in repo 'foo')
          repo=foo overrides=[('baz/bar', ''), ('.', '1c4e')], version='4fad'
            (get all tools from repo 'foo' at verion '4fad' on branch 'master'
            except 'baz/bar' and for tool '.' get version '1c4e')
          repo=foo tools=[('bar', '1a2d')], overrides=[('baz', 'f2a1')]
            (not a particularly useful example, but get 'bar' from 'foo' at
            version '1a2d' and get 'baz' from 'foo' at version 'f2a1' on branch
            'master', ignore all other tools)
        """
        # initialize and store class objects
        self.repo = repo.lower()
        self.tools = tools
        if (isinstance(self.tools, list) and
                len(self.tools) == 0):
            self.tools = None
        self.overrides = overrides
        self.version = version
        self.branch = branch
        self.build = build
        self.groups = groups
        self.core = core
        self.path, self.org, self.name = self.p_helper.get_path(repo,
                                                                core=core)

        # TODO these need to be implemented
        self.version_alias = version_alias
        self.wild = wild
        self.remove_old = remove_old
        self.disable_old = disable_old
        self.limit_groups = limit_groups

        status = (True, None)
        status_code, _ = self.p_helper.clone(self.repo, user=user, pw=pw)
        self.p_helper.apply_path(self.repo)
        status = self._build_tools(status_code)

        return status

    @ErrorHandler
    def add_image(self,
                  image,
                  link_name,
                  tag=None,
                  registry=None,
                  groups=None):
        """
        Add an image with a tag from a Docker registry, defaults to the Docker
        Hub if not specified
        """
        status = (True, None)
        try:
            org = ''
            name = image
            if '/' in image:
                org, name = image.split('/')
            else:
                org = "official"
            if not tag:
                tag = "latest"
            if not registry:
                registry = "docker.io"
            full_image = registry + "/" + image + ":" + tag
            image = self.d_client.images.pull(full_image)
            section = ':'.join([registry, org, name, '', tag])
            namespace = org + '/' + name

            # set template section and options for tool at version and branch
            template = Template(template=self.manifest)
            template.add_section(section)
            template.set_option(section, "name", name)
            template.set_option(section, "namespace", namespace)
            template.set_option(section, "path", "")
            template.set_option(section, "repo", registry + '/' + org)
            template.set_option(section, "enabled", "yes")
            template.set_option(section, "branch", "")
            template.set_option(section, "version", tag)
            template.set_option(section, "last_updated",
                                image.attrs['Created'])
            template.set_option(section, "image_name",
                                image.attrs['RepoTags'][0])
            template.set_option(section, "type", "registry")
            template.set_option(section, "link_name", link_name)
            template.set_option(section, "commit_id", "")
            template.set_option(section, "built", "yes")
            template.set_option(section, "image_id",
                                image.attrs['Id'].split(':')[1][:12])
            if groups:
                template.set_option(section, "groups", groups)

            # write out configuration to the manifest file
            template.write_config()
            status = (True, "Successfully added " + full_image)
        except Exception as e:  # pragma: no cover
            status = (False, str(e))
        return status

    @ErrorHandler
    def builder(self,
                template,
                match_path,
                image_name,
                section,
                build=None,
                branch=None,
                version=None):
        """ Build tools """
        self.logger.info("Starting: builder")
        self.logger.info("install path: " + str(match_path))
        self.logger.info("image name: " + str(image_name))
        self.logger.info("build: " + str(build))
        self.logger.info("branch: " + str(branch))
        self.logger.info("version: " + str(version))

        if build:
            self.build = build
        elif not hasattr(self, 'build'):
            self.build = True

        if branch:
            self.branch = branch
        elif not hasattr(self, 'branch'):
            self.branch = 'master'

        if version:
            self.version = version
        elif not hasattr(self, 'version'):
            self.version = 'HEAD'

        cwd = getcwd()
        self.logger.info("current working directory: " + str(cwd))
        try:
            chdir(match_path)
        except Exception as e:  # pragma: no cover
            self.logger.error("unable to change to directory: " +
                              str(match_path) + " because: " + str(e))
            return None

        template = self._build_image(template, match_path, image_name, section)
        chdir(cwd)

        # remove untagged images
        untagged = self.d_client.images.list(filters={"label": "vent",
                                                      "dangling": "true"})
        if untagged:
            deleted_images = ""
            for image in untagged:
                deleted_images = '\n'.join([deleted_images, image.id])
                self.d_client.images.remove(image.id, force=True)
            self.logger.info("removed dangling images:" + deleted_images)

        self.logger.info("template of builder: " + str(template))
        self.logger.info("Finished: builder")
        return template

    def _build_tools(self, status):
        """
        Create list of tools, paths, and versions to be built and sends them to
        build_manifest
        """
        response = (True, None)
        # TODO implement features: wild, remove_old, disable_old, limit_groups

        # check result of clone, ensure successful or that it already exists
        if status:
            response = self.p_helper.checkout(branch=self.branch,
                                              version=self.version)
            if response[0]:
                search_groups = None
                if self.core:
                    search_groups = 'core'
                matches = []
                if self.tools is None and self.overrides is None:
                    # get all tools
                    matches = self.p_helper.available_tools(self.path, version=self.version,
                                                            groups=search_groups)
                elif self.tools is None:
                    # there's only something in overrides
                    # grab all the tools then apply overrides
                    matches = self.p_helper.available_tools(self.path, version=self.version,
                                                            groups=search_groups)
                    # !! TODO apply overrides to matches
                elif self.overrides is None:
                    # there's only something in tools
                    # only grab the tools specified
                    matches = PluginHelper.tool_matches(tools=self.tools,
                                                        version=self.version)
                else:
                    # both tools and overrides were specified
                    # grab only the tools specified, with the overrides applied
                    o_matches = PluginHelper.tool_matches(tools=self.tools,
                                                          version=self.version)
                    matches = o_matches
                    for override in self.overrides:
                        override_t = None
                        if override[0] == '.':
                            override_t = ('', override[1])
                        else:
                            override_t = override
                        for match in o_matches:
                            if override_t[0] == match[0]:
                                matches.remove(match)
                                matches.append(override_t)
                if len(matches) > 0:
                    self._build_manifest(matches)
        else:
            response = (False, status)
        return response

    def _build_manifest(self, matches):
        """ Builds and writes the manifest for the tools being added """
        # !! TODO check for pre-existing that conflict with request and
        #         disable and/or remove image
        for match in matches:
            template = Template(template=self.manifest)
            # TODO check for special settings here first for the specific match
            self.version = match[1]
            response = self.p_helper.checkout(branch=self.branch,
                                              version=self.version)
            if response[0]:
                section = self.org + ":" + self.name + ":" + match[0] + ":"
                section += self.branch + ":" + self.version
                match_path = self.path + match[0]
                image_name = self.org + "-" + self.name + "-"
                if match[0] != '':
                    # if tool is in a subdir, add that to the name of the image
                    image_name += '-'.join(match[0].split('/')[1:]) + "-"
                image_name += self.branch + ":" + self.version

                # check if the section already exists
                exists, options = template.section(section)
                previous_commit = None
                previous_commits = None
                head = False
                if exists:
                    for option in options:
                        # TODO check if tool name but a different version
                        #      exists - then disable/remove if set
                        if option[0] == 'version' and option[1] == 'HEAD':
                            head = True
                        if option[0] == 'built' and option[1] == 'yes':
                            # !! TODO remove pre-existing image
                            pass
                        if option[0] == 'commit_id':
                            previous_commit = option[1]
                        if option[0] == 'previous_versions':
                            previous_commits = option[1]

                # !! TODO
                # check if section should be removed from config i.e. all tools
                # but new commit removed one that was in a previous commit

                # set template section & options for tool at version and branch
                template.add_section(section)
                template.set_option(section, "name", match[0].split('/')[-1])
                template.set_option(section, "namespace", self.org + '/' +
                                    self.name)
                template.set_option(section, "path", match_path)
                template.set_option(section, "repo", self.repo)
                template.set_option(section, "enabled", "yes")
                template.set_option(section, "branch", self.branch)
                template.set_option(section, "version", self.version)
                template.set_option(section, "last_updated",
                                    str(datetime.utcnow()) + " UTC")
                template.set_option(section, "image_name", image_name)
                template.set_option(section, "type", "repository")
                # save settings in vent.template to plugin_manifest
                vent_template = Template(template=join(match_path,
                                                       'vent.template'))
                sections = vent_template.sections()
                if sections[0]:
                    for header in sections[1]:
                        section_dict = {}
                        options = vent_template.options(header)
                        if options[0]:
                            for option in options[1]:
                                option_name = option
                                if option == 'name':
                                    option_name = 'link_name'
                                option = vent_template.option(header, option)
                                option_val = option[1]
                                section_dict[option_name] = option_val
                        if section_dict:
                            template.set_option(section, header,
                                                json.dumps(section_dict))
                # TODO do we need this if we save as a dictionary?
                vent_status, response = vent_template.option("info", "name")
                if vent_status:
                    template.set_option(section, "link_name", response)
                else:
                    template.set_option(section,
                                        "link_name",
                                        match[0].split('/')[-1])
                commit_id = None
                if self.version == 'HEAD':
                    chdir(match_path)
                    cmd = "git rev-parse --short HEAD"
                    commit_id = check_output(shlex.split(cmd),
                                             stderr=STDOUT,
                                             close_fds=True).strip()
                    template.set_option(section, "commit_id", commit_id)
                if head:
                    # no need to store previous commits if not HEAD, since
                    # the version will always be the same commit ID
                    if previous_commit and previous_commit != commit_id:
                        if (previous_commits and
                           previous_commit not in previous_commits):
                            previous_commits = (previous_commit +
                                                ',' +
                                                previous_commits)
                        elif not previous_commits:
                            previous_commits = previous_commit
                    if previous_commits and previous_commits != commit_id:
                        template.set_option(section,
                                            "previous_versions",
                                            previous_commits)

                if self.version_alias:
                    template.set_option(section,
                                        "version_alias",
                                        self.version_alias)
                if self.groups:
                    template.set_option(section, "groups", self.groups)
                else:
                    vent_template = join(match_path, 'vent.template')
                    if os.path.exists(vent_template):
                        v_template = Template(template=vent_template)
                        groups = v_template.option("info", "groups")
                        if groups[0]:
                            template.set_option(section, "groups", groups[1])
                template = self._build_image(template,
                                             match_path,
                                             image_name,
                                             section)

            # write out configuration to the manifest file
            template.write_config()

        # reset to repo directory
        chdir(self.path)
        return

    def _build_image(self,
                     template,
                     match_path,
                     image_name,
                     section,
                     build_local=False):
        """ Build docker images and store results in template """
        # !! TODO return status of whether it built successfully or not
        if self.build:
            cwd = getcwd()
            chdir(match_path)
            try:
                # currently can't use docker-py because it doesn't support
                # labels on images yet
                name = template.option(section, "name")
                groups = template.option(section, "groups")
                if groups[1] == "" or not groups[0]:
                    groups = (True, "none")
                if not name[0]:
                    name = (True, image_name)
                # pull if '/' in image_name, fallback to build
                pull = False
                if '/' in image_name and not build_local:
                    try:
                        self.logger.info("Trying to pull " + image_name)
                        output = check_output(shlex.split("docker pull " +
                                                          image_name),
                                              stderr=STDOUT,
                                              close_fds=True)
                        self.logger.info("Pulling " + name[1] + "\n" +
                                         str(output))

                        i_attrs = self.d_client.images.get(image_name).attrs
                        image_id = i_attrs['Id'].split(':')[1][:12]

                        if image_id:
                            template.set_option(section, "built", "yes")
                            template.set_option(section, "image_id", image_id)
                            template.set_option(section, "last_updated",
                                                str(datetime.utcnow()) +
                                                " UTC")
                            status = (True, "Pulled " + image_name)
                            self.logger.info(str(status))
                        else:
                            template.set_option(section, "built", "failed")
                            template.set_option(section, "last_updated",
                                                str(datetime.utcnow()) +
                                                " UTC")
                            status = (False, "Failed to pull image " +
                                      str(output.split('\n')[-1]))
                            self.logger.warning(str(status))
                        pull = True
                    except Exception as e:  # pragma: no cover
                        self.logger.warning("Failed to pull image, going to"
                                            " build instead: " + str(e))
                if not pull:
                    commit_tag = ""
                    if image_name.endswith('HEAD'):
                        commit_id = template.option(section, "commit_id")
                        if commit_id[0]:
                            commit_tag = (" -t " + image_name[:-4] +
                                          str(commit_id[1]))
                    output = check_output(shlex.split("docker build --label"
                                                      " vent --label"
                                                      " vent.name=" +
                                                      name[1] + " --label "
                                                      "vent.groups=" +
                                                      groups[1] + " -t " +
                                                      image_name +
                                                      commit_tag + " ."),
                                          stderr=STDOUT,
                                          close_fds=True)
                    self.logger.info("Building " + name[1] + "\n" +
                                     str(output))
                    image_id = ""
                    for line in output.split("\n"):
                        suc_str = "Successfully built "
                        if line.startswith(suc_str):
                            image_id = line.split(suc_str)[1].strip()
                    template.set_option(section, "built", "yes")
                    template.set_option(section, "image_id", image_id)
                    template.set_option(section, "last_updated",
                                        str(datetime.utcnow()) +
                                        " UTC")
            except Exception as e:  # pragma: no cover
                self.logger.error("unable to build image: " + str(image_name) +
                                  " because: " + str(e))
                template.set_option(section, "built", "failed")
                template.set_option(section, "last_updated",
                                    str(datetime.utcnow()) + " UTC")
            chdir(cwd)
        else:
            template.set_option(section, "built", "no")
            template.set_option(section, "last_updated",
                                str(datetime.utcnow()) + " UTC")
        return template

    def list_tools(self):
        """ Return list of tuples of all tools """
        tools = []
        template = Template(template=self.manifest)
        exists, sections = template.sections()
        if exists:
            for section in sections:
                options = {'section': section,
                           'enabled': None,
                           'built': None,
                           'version': None,
                           'repo': None,
                           'branch': None,
                           'name': None,
                           'groups': None,
                           'image_name': None}
                for option in options.keys():
                    exists, value = template.option(section, option)
                    if exists:
                        options[option] = value
                tools.append(options)
        return tools

    def remove(self, name=None, repo=None, namespace=None, branch="master",
               groups=None, enabled="yes", version="HEAD", built="yes"):
        """
        Remove tool (name) or repository, repository is the url. If no
        arguments are specified, all tools will be removed for the defaults.
        """
        # initialize
        args = locals()
        status = (True, None)

        # get resulting dict of sections with options that match constraints
        results, template = self.p_helper.constraint_options(args, [])
        for result in results:
            response, image_name = template.option(result, 'image_name')

            # check for container and remove
            container_name = image_name.replace(':', '-').replace('/', '-')
            try:
                container = self.d_client.containers.get(container_name)
                response = container.remove(v=True, force=True)
                self.logger.info(response)
                self.logger.info("Removing plugin container: " +
                                 container_name)
            except Exception as e:  # pragma: no cover
                self.logger.warn("Unable to remove the plugin container: " +
                                 container_name + " because: " + str(e))

            # check for image and remove
            try:
                response = None
                # due to problems with core image_id value in manifest file
                groups = template.option(result, 'groups')
                if groups[0] and "core" in groups[1]:
                    response = self.d_client.images.remove(image_name)
                else:
                    image_id = template.option(result, 'image_id')[1]
                    response = self.d_client.images.remove(image_id,
                                                           force=True)
                self.logger.info(response)
                self.logger.info("Removing plugin image: " + image_name)
            except Exception as e:  # pragma: no cover
                self.logger.warn("Unable to remove the plugin image: " +
                                 image_name + " because: " + str(e))

            # remove tool from the manifest
            status = template.del_section(result)
            self.logger.info("Removing plugin tool: " + result)
        # TODO if all tools from a repo have been removed, remove the repo
        template.write_config()
        return status

    def update(self,
               name=None,
               repo=None,
               namespace=None,
               branch=None,
               groups=None):
        """
        Update tool (name) or repository, repository is the url. If no
        arguments are specified, all tools will be updated
        """
        # initialize
        args = locals()
        status = (False, None)
        options = ['branch', 'groups', 'image_name']

        # get resulting dict of sections with options that match constraints
        results, template = self.p_helper.constraint_options(args, options)
        for result in results:
            # check for container and remove
            try:
                container_name = results['image_name'].replace(':', '-') \
                                                      .replace('/', '-')
                container = self.d_client.containers.get(container_name)
                container.remove(v=True, force=True)
            except Exception as e:  # pragma: no cover
                self.logger.info("Error updating: " + str(result) +
                                 " because: " + str(e))

            # TODO git pull
            # TODO build
            # TODO docker pull
            # TODO update tool in the manifest

            self.logger.info("Updating plugin tool: " + result)
        template.write_config()
        return status

    # !! TODO name or group ?
    def versions(self, name, namespace=None, branch="master"):
        """ Return available versions of a tool """
        # initialize
        args = locals()
        versions = []
        options = ['version', 'previous_versions']

        # get resulting dict of sections with options that match constraints
        results, _ = self.p_helper.constraint_options(args, options)
        for result in results:
            version_list = [results[result]['version']]
            if 'previous_versions' in results[result]:
                version_list += (results[result]['previous_versions']) \
                                .split(',')
            versions.append((result, version_list))
        return versions

    # !! TODO name or group ?
    def current_version(self, name, namespace=None, branch="master"):
        """ Return current version for a given tool """
        # initialize
        args = locals()
        versions = []
        options = ['version']

        # get resulting dict of sections with options that match constraints
        results, _ = self.p_helper.constraint_options(args, options)
        for result in results:
            versions.append((result, results[result]['version']))
        return versions

    # !! TODO name or group ?
    def state(self, name, namespace=None, branch="master"):
        """ Return state of a tool, disabled/enabled for each version """
        # initialize
        args = locals()
        states = []
        options = ['enabled']

        # get resulting dict of sections with options that match constraints
        results, _ = self.p_helper.constraint_options(args, options)
        for result in results:
            if results[result]['enabled'] == 'yes':
                states.append((result, 'enabled'))
            else:
                states.append((result, 'disabled'))
        return states

    # !! TODO name or group ?
    def enable(self, name, namespace=None, branch="master", version="HEAD"):
        """ Enable tool at a specific version, default to head """
        # initialize
        args = locals()
        status = (False, None)

        # get resulting dict of sections with options that match constraints
        results, template = self.p_helper.constraint_options(args, [])
        for result in results:
            status = template.set_option(result, 'enabled', 'yes')
        template.write_config()
        return status

    # !! TODO name or group ?
    def disable(self, name, namespace=None, branch="master", version="HEAD"):
        """ Disable tool at a specific version, default to head """
        # initialize
        args = locals()
        status = (False, None)

        # get resulting dict of sections with options that match constraints
        results, template = self.p_helper.constraint_options(args, [])
        for result in results:
            status = template.set_option(result, 'enabled', 'no')
        template.write_config()
        return status
