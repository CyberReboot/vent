import getpass
import json
import os
import shlex
from datetime import datetime
from os import chdir
from os import getcwd
from os.path import isdir
from os.path import join
from subprocess import check_output
from subprocess import STDOUT

import docker
import yaml

from vent.api.plugin_helpers import PluginHelper
from vent.api.templates import Template
from vent.helpers.errors import ErrorHandler
from vent.helpers.logs import Logger
from vent.helpers.meta import ParsedSections
from vent.helpers.meta import Timestamp
from vent.helpers.paths import PathDirs


class Plugin:
    """
    Handle Plugins
    """

    def __init__(self, **kargs):
        self.path_dirs = PathDirs(**kargs)
        self.manifest = join(self.path_dirs.meta_dir,
                             'plugin_manifest.cfg')
        self.p_helper = PluginHelper(**kargs)
        self.d_client = docker.from_env()
        self.logger = Logger(__name__)
        self.plugin_config_file = self.path_dirs.plugin_config_file

    def add(self, repo, tools=None, overrides=None, version='HEAD', image=None,
            branch='master', build=True, user=None, pw=None, groups=None,
            version_alias=None, wild=None, remove_old=True, disable_old=True,
            limit_groups=None, core=False, update_repo=None):
        """
        Adds a plugin of tool(s)
        tools is a list of tuples, where the pair is a tool name (path to
        Dockerfile) and version tools are for explicitly limiting which tools
        and versions (if version in tuple is '', then defaults to version)
        overrides is a list of tuples, where the pair is a tool name (path to
        Dockerfile) and a version overrides are for explicitly removing tools
        and overriding versions of tools (if version in tuple is '', then
        tool is removed, otherwise that tool is checked out at the specific
        version in the tuple) if tools and overrides are left as empty lists,
        then all tools in the repo are pulled down at the version and branch
        specified or defaulted to version is globally set for all tools, unless
        overridden in tools or overrides branch is globally set for all tools
        build is a boolean of whether or not to build the tools now user is the
        username for a private repo if needed pw is the password to go along
        with the username for a private repo groups is globally set for all
        tools version_alias is globally set for all tools and is a mapping
        from a friendly version tag to the real version commit ID wild lets
        you specify individual overrides for additional values in the tuple
        of tools or overrides.  wild is a list containing one or more
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
        - repo=fe:
        (get all tools from repo 'fe' at version 'HEAD' on branch 'master')
        - repo=foo, version="3d1f", branch="foo":
        (get all tools from repo 'foo' at verion '3d1f' on branch 'foo')
        - repo=foo, tools=[('bar', ''), ('baz', '1d32')]:
        (get only 'bar' from repo 'foo' at version 'HEAD' on branch
        'master' and 'baz' from repo 'foo' at version '1d32' on branch
        'master', ignore all other tools in repo 'foo')
        - repo=foo overrides=[('baz/bar', ''), ('.', '1c4e')], version='4fad':
        (get all tools from repo 'foo' at verion '4fad' on branch 'master'
        except 'baz/bar' and for tool '.' get version '1c4e')
        - repo=foo tools=[('bar', '1a2d')], overrides=[('baz', 'f2a1')]:
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
        self.logger.info('Adding new tools: ' + str(self.tools))
        self.overrides = overrides
        self.version = version
        self.image = image
        self.branch = branch
        self.build = build
        self.groups = groups
        self.core = core
        self.update_repo = update_repo
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
        Add an image with a tag from a Docker registry. Defaults to the Docker
        Hub if not specified. Use a Template object to write an image's
        information to `plugin_manifest.cfg'

        Args:
            image(type): docker image
            link_name(type): fill me

        Kwargs:
            tag(type):
            registry(type):
            groups(type): Group that the docker image belongs to.

        Returns:
            tuple(bool,str): if the function completed successfully,
                (True, name of image).
                If the function failed, (False, message about failure)
        """

        status = (True, None)
        try:
            pull_name = image
            org = ''
            name = image
            if '/' in image:
                org, name = image.split('/')
            else:
                org = 'official'
            if not tag:
                tag = 'latest'
            if not registry:
                registry = 'docker.io'
            full_image = registry + '/' + image + ':' + tag
            image = self.d_client.images.pull(full_image)
            section = ':'.join([registry, org, name, '', tag])
            namespace = org + '/' + name

            # set template section and options for tool at version and branch
            template = Template(template=self.manifest)
            template.add_section(section)
            template.set_option(section, 'name', name)
            template.set_option(section, 'pull_name', pull_name)
            template.set_option(section, 'namespace', namespace)
            template.set_option(section, 'path', '')
            template.set_option(section, 'repo', registry + '/' + org)
            template.set_option(section, 'enabled', 'yes')
            template.set_option(section, 'branch', '')
            template.set_option(section, 'version', tag)
            template.set_option(section, 'last_updated',
                                str(datetime.utcnow()) + ' UTC')
            template.set_option(section, 'image_name',
                                image.attrs['RepoTags'][0])
            template.set_option(section, 'type', 'registry')
            template.set_option(section, 'link_name', link_name)
            template.set_option(section, 'commit_id', '')
            template.set_option(section, 'built', 'yes')
            template.set_option(section, 'image_id',
                                image.attrs['Id'].split(':')[1][:12])
            template.set_option(section, 'groups', groups)

            # write out configuration to the manifest file
            template.write_config()
            status = (True, 'Successfully added ' + full_image)
        except Exception as e:  # pragma: no cover
            self.logger.error("Couldn't add image because " + str(e))
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
        """
        Build tools
        """

        self.logger.info('Starting: builder')
        self.logger.info('install path: ' + str(match_path))
        self.logger.info('image name: ' + str(image_name))
        self.logger.info('build: ' + str(build))
        self.logger.info('branch: ' + str(branch))
        self.logger.info('version: ' + str(version))

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
        self.logger.info('current working directory: ' + str(cwd))
        try:
            chdir(match_path)
        except Exception as e:  # pragma: no cover
            self.logger.error('unable to change to directory: ' +
                              str(match_path) + ' because: ' + str(e))
            return None

        template = self._build_image(template, match_path, image_name, section)
        chdir(cwd)

        # get untagged images
        untagged = None
        try:
            untagged = self.d_client.images.list(filters={'label': 'vent',
                                                          'dangling': 'true'})
        except Exception as e:  # pragma: no cover
            self.logger.error('unabled to get images to remove: ' + str(e))

        # remove untagged images
        if untagged:
            deleted_images = ''
            for image in untagged:
                deleted_images = '\n'.join([deleted_images, image.id])
                try:
                    self.d_client.images.remove(image.id, force=True)
                except Exception as e:  # pragma: no cover
                    self.logger.warning('unable to remove image: ' + image.id +
                                        ' because: ' + str(e))
            self.logger.info('removed dangling images:' + deleted_images)

        self.logger.info('template of builder: ' + str(template))
        self.logger.info('Finished: builder')
        return template

    def _build_tools(self, status):
        """
        Create list of tools, paths, and versions to be built and sends them to
        build_manifest

        Args:
            status (tuple(bool, str)):

        Returns:
            response (tuple(bool, str)): If True, then the function performed
            as expected and the str is a string
        """
        self.logger.info('Starting: _build_tools')
        response = (True, None)
        # TODO implement features: wild, remove_old, disable_old, limit_groups

        # check result of clone, ensure successful or that it already exists
        if status:
            # TODO check if the repo was already set to a branch/version other than master/HEAD
            if self.update_repo or self.branch != 'master' or self.version != 'HEAD':
                response = self.p_helper.checkout(branch=self.branch,
                                                  version=self.version)
            else:
                response = (True, None)
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

        self.logger.info('Status of _build_tools: ' + str(response[0]))
        self.logger.info('Finished: _build_tools')
        return response

    def _build_manifest(self, matches):
        """
        Builds and writes the manifest for the tools being added
        """
        self.logger.info('Starting: _build_manifest')
        # !! TODO check for pre-existing that conflict with request and
        #         disable and/or remove image
        for match in matches:
            # keep track of whether or not to write an additional manifest
            # entry for multiple instances, and how many additional entries
            # to write
            addtl_entries = 0
            # remove the .git for adding repo info to manifest
            if self.repo.endswith('.git'):
                self.repo = self.repo[:-4]
            # remove @ in match for template setting purposes
            if match[0].find('@') >= 0:
                true_name = match[0].split('@')[1]
            else:
                true_name = match[0]
            template = Template(template=self.manifest)
            # TODO check for special settings here first for the specific match
            self.version = match[1]
            if self.update_repo:
                response = self.p_helper.checkout(branch=self.branch,
                                                  version=self.version)
            else:
                response = (True, None)
            if response[0]:
                section = self.org + ':' + self.name + ':' + true_name + ':'
                section += self.branch + ':' + self.version
                # need to get rid of temp identifiers for tools in same repo
                match_path = self.path + match[0].split('@')[0]
                if self.image:
                    image_name = self.image
                elif not self.core:
                    image_name = self.org + '/' + self.name
                    if match[0] != '':
                        # if tool is in a subdir, add that to the name of the
                        # image
                        image_name += '-' + '-'.join(match[0].split('/')[1:])
                    image_name += ':' + self.branch
                else:
                    image_name = ('cyberreboot/vent-' +
                                  match[0].split('/')[-1] + ':' + self.branch)
                image_name = image_name.replace('_', '-')

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

                # check if tool comes from multi directory
                multi_tool = 'no'
                if match[0].find('@') >= 0:
                    multi_tool = 'yes'

                # !! TODO
                # check if section should be removed from config i.e. all tools
                # but new commit removed one that was in a previous commit

                image_name = image_name.lower()
                image_name = image_name.replace('@', '-')

                # set template section & options for tool at version and branch
                template.add_section(section)
                template.set_option(section, 'name', true_name.split('/')[-1])
                template.set_option(section, 'namespace', self.org + '/' +
                                    self.name)
                template.set_option(section, 'path', match_path)
                template.set_option(section, 'repo', self.repo)
                template.set_option(section, 'enabled', 'yes')
                template.set_option(section, 'multi_tool', multi_tool)
                template.set_option(section, 'branch', self.branch)
                template.set_option(section, 'version', self.version)
                template.set_option(section, 'last_updated',
                                    str(datetime.utcnow()) + ' UTC')
                template.set_option(section, 'image_name', image_name)
                template.set_option(section, 'type', 'repository')
                # save settings in vent.template to plugin_manifest
                # watch for multiple tools in same directory
                # just wanted to store match path with @ for path for use in
                # other actions
                tool_template = 'vent.template'
                if match[0].find('@') >= 0:
                    tool_template = match[0].split('@')[1] + '.template'
                vent_template_path = join(match_path, tool_template)
                if os.path.exists(vent_template_path):
                    with open(vent_template_path, 'r') as f:
                        vent_template_val = f.read()
                else:
                    vent_template_val = ''
                settings_dict = ParsedSections(vent_template_val)
                for setting in settings_dict:
                    template.set_option(section, setting,
                                        json.dumps(settings_dict[setting]))
                # TODO do we need this if we save as a dictionary?
                vent_template = Template(vent_template_path)
                vent_status, response = vent_template.option('info', 'name')
                if vent_status:
                    template.set_option(section, 'link_name', response)
                else:
                    template.set_option(section,
                                        'link_name',
                                        true_name.split('/')[-1])
                commit_id = None
                if self.version == 'HEAD':
                    # remove @ in multi-tools
                    chdir(match_path)
                    cmd = 'git rev-parse --short HEAD'
                    commit_id = check_output(shlex.split(cmd),
                                             stderr=STDOUT,
                                             close_fds=True).strip().decode('utf-8')
                    template.set_option(section, 'commit_id', commit_id)
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
                                            'previous_versions',
                                            previous_commits)

                if self.version_alias:
                    template.set_option(section,
                                        'version_alias',
                                        self.version_alias)
                if self.groups:
                    template.set_option(section, 'groups', self.groups)
                else:
                    groups = vent_template.option('info', 'groups')
                    if groups[0]:
                        template.set_option(section, 'groups', groups[1])
                    # set groups to empty string if no groups defined for tool
                    else:
                        template.set_option(section, 'groups', '')
                template = self._build_image(template,
                                             match_path,
                                             image_name,
                                             section)
                # write additional entries for multiple instances
                if addtl_entries > 0:
                    # add 2 for naming conventions
                    for i in range(2, addtl_entries + 2):
                        addtl_section = section.rsplit(':', 2)
                        addtl_section[0] += str(i)
                        addtl_section = ':'.join(addtl_section)
                        template.add_section(addtl_section)
                        orig_vals = template.section(section)[1]
                        for val in orig_vals:
                            template.set_option(addtl_section, val[0], val[1])
                        template.set_option(addtl_section, 'name',
                                            true_name.split('/')[-1]+str(i))

            # write out configuration to the manifest file
            template.write_config()

        # reset to repo directory
        chdir(self.path)
        self.logger.info('Finished: _build_manifest')
        return

    def _build_image(self,
                     template,
                     match_path,
                     image_name,
                     section,
                     build_local=False):
        """
        Build docker images and store results in template
        """
        self.logger.info('Starting: _build_image')
        status = True

        def set_instances(template, section, built, image_id=None):
            """ Set build information for multiple instances """
            self.logger.info('entering set_instances')
            i = 2
            while True:
                addtl_section = section.rsplit(':', 2)
                addtl_section[0] += str(i)
                addtl_section = ':'.join(addtl_section)
                self.logger.info(addtl_section)
                if template.section(addtl_section)[0]:
                    template.set_option(addtl_section, 'built', built)
                    if image_id:
                        template.set_option(addtl_section, 'image_id',
                                            image_id)
                    template.set_option(addtl_section,
                                        'last_updated', Timestamp())
                else:
                    break
                i += 1

        # determine whether a tool should be considered a multi instance
        try:
            settings_dict = json.loads(template.option(section, 'settings')[1])
            if int(settings_dict['instances']) > 1:
                multi_instance = True
            else:
                multi_instance = False
        except Exception:
            multi_instance = False
            status = False
        # !! TODO return status of whether it built successfully or not
        if self.build:
            cwd = getcwd()
            chdir(match_path)
            try:
                name = template.option(section, 'name')
                groups = template.option(section, 'groups')
                repo = template.option(section, 'repo')
                t_type = template.option(section, 'type')
                path = template.option(section, 'path')
                must_build = self.fill_config(path[1])
                if groups[1] == '' or not groups[0]:
                    groups = (True, 'none')
                if not name[0]:
                    name = (True, image_name)
                pull = False
                image_exists = False
                output = ''
                cfg_template = Template(template=self.path_dirs.cfg_file)
                use_existing_image = False
                result = cfg_template.option('build-options',
                                             'use_existing_images')
                if result[0]:
                    use_existing_image = result[1]
                if use_existing_image == 'yes' and not must_build:
                    try:
                        self.d_client.images.get(image_name)
                        i_attrs = self.d_client.images.get(image_name).attrs
                        image_id = i_attrs['Id'].split(':')[1][:12]

                        template.set_option(section, 'built', 'yes')
                        template.set_option(section, 'image_id', image_id)
                        template.set_option(section, 'last_updated',
                                            str(datetime.utcnow()) + ' UTC')
                        # set other instances too
                        if multi_instance:
                            set_instances(template, section, 'yes', image_id)
                        status = (True, 'Found ' + image_name)
                        self.logger.info(str(status))
                        image_exists = True
                    except docker.errors.ImageNotFound:
                        image_exists = False
                    except Exception as e:  # pragma: no cover
                        self.logger.warning('Failed to query Docker for images'
                                            ' because: ' + str(e))
                if not image_exists:
                    # pull if '/' in image_name, fallback to build
                    if '/' in image_name and not build_local and not must_build:
                        try:
                            # currently can't use docker-py because it doesn't support
                            # support labels on images yet
                            self.logger.info('Trying to pull ' + image_name)
                            output = check_output(shlex.split('docker pull ' +
                                                              image_name),
                                                  stderr=STDOUT,
                                                  close_fds=True).decode('utf-8')
                            self.logger.info('Pulling ' + name[1] + '\n' +
                                             output)

                            i_attrs = self.d_client.images.get(
                                image_name).attrs
                            image_id = i_attrs['Id'].split(':')[1][:12]

                            if image_id:
                                template.set_option(section, 'built', 'yes')
                                template.set_option(section,
                                                    'image_id',
                                                    image_id)
                                template.set_option(section, 'last_updated',
                                                    str(datetime.utcnow()) +
                                                    ' UTC')
                                # set other instances too
                                if multi_instance:
                                    set_instances(template, section, 'yes',
                                                  image_id)
                                status = (True, 'Pulled ' + image_name)
                                self.logger.info(str(status))
                            else:
                                template.set_option(section, 'built', 'failed')
                                template.set_option(section, 'last_updated',
                                                    str(datetime.utcnow()) +
                                                    ' UTC')
                                # set other instances too
                                if multi_instace:
                                    set_instances(template, section, 'failed')
                                status = (False, 'Failed to pull image ' +
                                          str(output.split('\n')[-1]))
                                self.logger.warning(str(status))
                            pull = True
                        except Exception as e:  # pragma: no cover
                            self.logger.warning('Failed to pull image, going'
                                                ' to build instead: ' + str(e))
                        status = False
                if not pull and not image_exists:
                    # get username to label built image with
                    username = getpass.getuser()
                    # see if additional tags needed for images tagged at HEAD
                    commit_tag = ''
                    if image_name.endswith('HEAD'):
                        commit_id = template.option(section, 'commit_id')
                        if commit_id[0]:
                            commit_tag = (' -t ' + image_name[:-4] +
                                          str(commit_id[1]))
                    # see if additional file arg needed for building multiple
                    # images from same directory
                    file_tag = ' .'
                    multi_tool = template.option(section, 'multi_tool')
                    if multi_tool[0] and multi_tool[1] == 'yes':
                        specific_file = template.option(section, 'name')[1]
                        if specific_file == 'unspecified':
                            file_tag = ' -f Dockerfile .'
                        else:
                            file_tag = ' -f Dockerfile.' + specific_file + ' .'
                    # update image name with new version for update
                    image_name = image_name.rsplit(':', 1)[0]+':'+self.branch
                    output = check_output(shlex.split('docker build --label'
                                                      ' vent --label'
                                                      ' vent.section=' +
                                                      section + ' --label'
                                                      ' vent.repo=' +
                                                      repo[1] + ' --label'
                                                      ' vent.type=' +
                                                      t_type[1] + ' --label'
                                                      ' vent.name=' +
                                                      name[1] + ' --label'
                                                      ' vent.groups=' +
                                                      groups[1] + ' --label' +
                                                      ' built-by=' +
                                                      username + ' -t ' +
                                                      image_name +
                                                      commit_tag + file_tag),
                                          stderr=STDOUT,
                                          close_fds=True).decode('utf-8')
                    self.logger.info('Building ' + name[1] + '\n' +
                                     output)
                    image_id = ''
                    for line in output.split('\n'):
                        suc_str = 'Successfully built '
                        if line.startswith(suc_str):
                            image_id = line.split(suc_str)[1].strip()
                    template.set_option(section, 'built', 'yes')
                    template.set_option(section, 'image_id', image_id)
                    template.set_option(section, 'last_updated',
                                        str(datetime.utcnow()) +
                                        ' UTC')
                    # set other instances too
                    if multi_instance:
                        set_instances(template, section, 'yes', image_id)
            except Exception as e:  # pragma: no cover
                self.logger.info(
                    'current working directory: ' + str(os.getcwd()))
                self.logger.error('unable to build image: ' + str(image_name) +
                                  ' because: ' + str(e) + ' and ' + str(output))
                template.set_option(section, 'built', 'failed')
                template.set_option(section, 'last_updated',
                                    str(datetime.utcnow()) + ' UTC')
                if multi_instance:
                    set_instances(template, section, 'failed')
                status = False

            chdir(cwd)
        else:
            template.set_option(section, 'built', 'no')
            template.set_option(section, 'last_updated',
                                str(datetime.utcnow()) + ' UTC')
            if multi_instance:
                set_instances(template, section, 'no')
        template.set_option(section, 'running', 'no')
        self.logger.info('Status of _build_image: ' + str(status))
        self.logger.info('Finished: _build_image:')
        return template

    def list_tools(self):
        """
        Return list of tuples of all tools
        """

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
                for option in list(options.keys()):
                    exists, value = template.option(section, option)
                    if exists:
                        options[option] = value
                tools.append(options)
        return tools

    def remove(self, name=None, repo=None, namespace=None, branch='master',
               groups=None, enabled='yes', version='HEAD', built='yes'):
        """
        Remove tool (name) or repository, repository is the url. If no
        arguments are specified, all tools will be removed for the defaults.
        """

        # initialize
        args = locals()
        # want to remove things from manifest regardless of if built
        del args['built']
        status = (True, None)

        # get resulting dict of sections with options that match constraints
        results, template = self.p_helper.constraint_options(args, [])
        for result in results:
            response, image_name = template.option(result, 'image_name')
            name = template.option(result, 'name')[1]
            try:
                settings_dict = json.loads(template.option(result,
                                                           'settings')[1])
                instances = int(settings_dict['instances'])
            except Exception:
                instances = 1

            try:
                # check for container and remove
                c_name = image_name.replace(':', '-').replace('/', '-')
                for i in range(1, instances + 1):
                    container_name = c_name + str(i) if i != 1 else c_name
                    container = self.d_client.containers.get(container_name)
                    response = container.remove(v=True, force=True)
                    self.logger.info(response)
                    self.logger.info('Removing plugin container: ' +
                                     container_name)
            except Exception as e:  # pragma: no cover
                self.logger.warn('Unable to remove the plugin container: ' +
                                 container_name + ' because: ' + str(e))

            # check for image and remove
            try:
                response = None
                image_id = template.option(result, 'image_id')[1]
                response = self.d_client.images.remove(image_id, force=True)
                self.logger.info(response)
                self.logger.info('Removing plugin image: ' + image_name)
            except Exception as e:  # pragma: no cover
                self.logger.warn('Unable to remove the plugin image: ' +
                                 image_name + ' because: ' + str(e))

            # remove tool from the manifest
            for i in range(1, instances + 1):
                res = result.rsplit(':', 2)
                res[0] += str(i) if i != 1 else ''
                res = ':'.join(res)
                if template.section(res)[0]:
                    status = template.del_section(res)
                    self.logger.info('Removing plugin tool: ' + res)
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
                self.logger.info('Error updating: ' + str(result) +
                                 ' because: ' + str(e))

            # TODO git pull
            # TODO build
            # TODO docker pull
            # TODO update tool in the manifest

            self.logger.info('Updating plugin tool: ' + result)
        template.write_config()
        return status

    # !! TODO name or group ?
    def versions(self, name, namespace=None, branch='master'):
        """
        Return available versions of a tool
        """

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
    def current_version(self, name, namespace=None, branch='master'):
        """
        Return current version for a given tool
        """

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
    def state(self, name, namespace=None, branch='master'):
        """
        Return state of a tool, disabled/enabled for each version
        """

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
    def enable(self, name, namespace=None, branch='master', version='HEAD'):
        """
        Enable tool at a specific version, default to head
        """

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
    def disable(self, name, namespace=None, branch='master', version='HEAD'):
        """
        Disable tool at a specific version, default to head
        """

        # initialize
        args = locals()
        status = (False, None)

        # get resulting dict of sections with options that match constraints
        results, template = self.p_helper.constraint_options(args, [])
        for result in results:
            status = template.set_option(result, 'enabled', 'no')
        template.write_config()
        return status

    def auto_install(self):
        """
        Automatically detects images and installs them in the manifest if they
        are not there already
        """
        template = Template(template=self.manifest)
        sections = template.sections()
        images = self.d_client.images.list(filters={'label': 'vent'})
        add_sections = []
        status = (True, None)
        for image in images:
            if ('Labels' in image.attrs and
                'vent.section' in image.attrs['Config']['Labels'] and
                    not image.attrs['Config']['Labels']['vent.section'] in sections[1]):
                section = image.attrs['Config']['Labels']['vent.section']
                section_str = image.attrs['Config']['Labels']['vent.section'].split(
                    ':')
                template.add_section(section)
                if 'vent.name' in image.attrs['Config']['Labels']:
                    template.set_option(section,
                                        'name',
                                        image.attrs['Config']['Labels']['vent.name'])
                if 'vent.repo' in image.attrs['Config']['Labels']:
                    template.set_option(section,
                                        'repo',
                                        image.attrs['Config']['Labels']['vent.repo'])
                    git_path = join(self.path_dirs.plugins_dir,
                                    '/'.join(section_str[:2]))
                    if not isdir(git_path):
                        # clone it down
                        status = self.p_helper.clone(
                            image.attrs['Config']['Labels']['vent.repo'])
                    template.set_option(section, 'path', join(
                        git_path, section_str[-3][1:]))
                    # get template settings
                    # TODO account for template files not named vent.template
                    v_template = Template(template=join(
                        git_path, section_str[-3][1:], 'vent.template'))
                    tool_sections = v_template.sections()
                    if tool_sections[0]:
                        for s in tool_sections[1]:
                            section_dict = {}
                            options = v_template.options(s)
                            if options[0]:
                                for option in options[1]:
                                    option_name = option
                                    if option == 'name':
                                        # get link name
                                        template.set_option(section,
                                                            'link_name',
                                                            v_template.option(s, option)[1])
                                        option_name = 'link_name'
                                    opt_val = v_template.option(s, option)[1]
                                    section_dict[option_name] = opt_val
                            if section_dict:
                                template.set_option(section, s,
                                                    json.dumps(section_dict))
                if ('vent.type' in image.attrs['Config']['Labels'] and
                        image.attrs['Config']['Labels']['vent.type'] == 'repository'):
                    template.set_option(
                        section, 'namespace', '/'.join(section_str[:2]))
                    template.set_option(section, 'enabled', 'yes')
                    template.set_option(section, 'branch', section_str[-2])
                    template.set_option(section, 'version', section_str[-1])
                    template.set_option(section, 'last_updated', str(
                        datetime.utcnow()) + ' UTC')
                    template.set_option(
                        section, 'image_name', image.attrs['RepoTags'][0])
                    template.set_option(section, 'type', 'repository')
                if 'vent.groups' in image.attrs['Config']['Labels']:
                    template.set_option(section,
                                        'groups',
                                        image.attrs['Config']['Labels']['vent.groups'])
                template.set_option(section, 'built', 'yes')
                template.set_option(section, 'image_id',
                                    image.attrs['Id'].split(':')[1][:12])
                template.set_option(section, 'running', 'no')
                # check if image is running as a container
                containers = self.d_client.containers.list(
                    filters={'label': 'vent'})
                for container in containers:
                    if container.attrs['Image'] == image.attrs['Id']:
                        template.set_option(section, 'running', 'yes')
                add_sections.append(section)
                template.write_config()
        if status[0]:
            status = (True, add_sections)
        return status

    def fill_config(self, path):
        """
        Will take a yml located in home directory titled '.plugin_config.yml'.
        It'll then fill in, using the yml, the plugin's config file
        """
        self.logger.info('Starting: fill_config')
        status = (True, None)
        must_build = False

        try:
            # parse the yml file
            c_dict = {}
            if os.path.exists(self.plugin_config_file):
                with open(self.plugin_config_file, 'r') as config_file:
                    c_dict = yaml.safe_load(config_file.read())

            # check for environment variable overrides
            check_c_dict = c_dict.copy()
            for tool in check_c_dict:
                for section in check_c_dict[tool]:
                    for key in check_c_dict[tool][section]:
                        if key in os.environ:
                            c_dict[tool][section][key] = os.getenv(key)

            # assume the name of the plugin is its directory
            plugin_name = path.split('/')[-1]
            if plugin_name == '':
                plugin_name = path.split('/')[-2]
            plugin_config_path = path + '/config/' + plugin_name + '.config'

            if os.path.exists(plugin_config_path):
                plugin_template = Template(plugin_config_path)
                plugin_options = c_dict[plugin_name]
                for section in plugin_options:
                    for option in plugin_options[section]:
                        plugin_template.set_option(section, option,
                                                   str(plugin_options[section][option]))
                plugin_template.write_config()
                must_build = True

        except Exception as e:  # pragma: no cover
            status = (False, e)
            self.logger.error('Failed to fill_config: ' + str(e))

        self.logger.info('Status of fill_config: ' + str(status[0]))
        self.logger.info('Finished: fill_config')
        return must_build
