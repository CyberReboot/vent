import ast
import copy
import getpass
import json
import re
import shlex
import shutil
from datetime import datetime
from os import chdir
from os import close
from os import environ
from os import getcwd
from os import mkdir
from os import remove
from os.path import exists
from os.path import expanduser
from os.path import join
from subprocess import check_output
from subprocess import STDOUT

import docker
import yaml

from vent.helpers.logs import Logger
from vent.helpers.meta import AvailableTools
from vent.helpers.meta import Checkout
from vent.helpers.meta import Containers
from vent.helpers.meta import ParsedSections
from vent.helpers.meta import Timestamp
from vent.helpers.meta import ToolMatches
from vent.helpers.meta import Version
from vent.helpers.paths import PathDirs
from vent.helpers.templates import Template


class Repository:

    def __init__(self, manifest, *args, **kwargs):
        self.path_dirs = PathDirs(**kwargs)
        self.manifest = manifest
        self.d_client = docker.from_env()
        self.logger = Logger(__name__)

    def add(self, repo, tools=None, overrides=None, version='HEAD', core=False,
            image_name=None, branch='master', build=True, user=None, pw=None):
        status = (True, None)
        self.repo = repo.lower()
        self.tools = tools
        self.overrides = overrides
        self.branch = branch
        self.version = version
        self.image_name = image_name
        self.core = core

        status = self._clone(user=user, pw=pw)
        if status[0] and build:
            status = self._build()
        return status

    def _build(self):
        status = (True, None)
        status = self._get_tools()
        matches = status[1]
        status = self.path_dirs.apply_path(self.repo)
        original_path = status[1]
        if status[0] and len(matches) > 0:
            repo, org, name = self.path_dirs.get_path(self.repo)
            cmd = 'git rev-parse --short HEAD'
            commit_id = ''
            try:
                commit_id = check_output(shlex.split(cmd), stderr=STDOUT,
                                         close_fds=True).strip().decode('utf-8')
            except Exception as e:  # pragma: no cover
                self.logger.error(
                    'Unable to get commit ID because: {0}'.format(str(e)))
            template = Template(template=self.manifest)
            for match in matches:
                status, template, match_path, image_name, section = self._build_manifest(
                    match, template, repo, org, name, commit_id)
                if not status[0]:
                    break
                status, template = self._build_image(template,
                                                     match_path,
                                                     image_name,
                                                     section)
                if not status[0]:
                    break
            if status[0]:
                # write out configuration to the manifest file
                template.write_config()
        chdir(original_path)
        return status

    def _get_tools(self):
        status = (True, None)
        matches = []
        path, _, _ = self.path_dirs.get_path(self.repo)
        status = Checkout(path, branch=self.branch,
                          version=self.version)
        if status[0]:
            search_groups = None
            if self.core:
                search_groups = 'core'
            if self.tools is None and self.overrides is None:
                # get all tools
                matches = AvailableTools(path, version=self.version,
                                         groups=search_groups)
            elif self.tools is None:
                # there's only something in overrides
                # grab all the tools then apply overrides
                matches = AvailableTools(path, version=self.version,
                                         groups=search_groups)
                # !! TODO apply overrides to matches
            elif self.overrides is None:
                # there's only something in tools
                # only grab the tools specified
                matches = ToolMatches(tools=self.tools,
                                      version=self.version)
            else:
                # both tools and overrides were specified
                # grab only the tools specified, with the overrides applied
                o_matches = ToolMatches(tools=self.tools,
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
            status = (True, matches)
        return status

    def _build_manifest(self, match, template, repo, org, name, commit_id):
        status = (True, None)
        # keep track of whether or not to write an additional manifest
        # entry for multiple instances, and how many additional entries
        # to write
        addtl_entries = 1
        # remove @ in match for template setting purposes
        if match[0].find('@') >= 0:
            true_name = match[0].split('@')[1]
        else:
            true_name = match[0]
        # TODO check for special settings here first for the specific match
        self.version = match[1]
        section = org + ':' + name + ':' + true_name + ':'
        section += self.branch + ':' + self.version
        # need to get rid of temp identifiers for tools in same repo
        match_path = repo + match[0].split('@')[0]
        if self.image_name:
            image_name = self.image_name
        elif not self.core:
            image_name = org + '/' + name
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
        is_there, options = template.section(section)
        previous_commit = None
        previous_commits = None
        head = False
        if is_there:
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
        template.set_option(section, 'namespace', org + '/' + name)
        template.set_option(section, 'path', match_path)
        template.set_option(section, 'repo', self.repo)
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
        if exists(vent_template_path):
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
        instances = vent_template.option('settings', 'instances')
        if instances[0]:
            addtl_entries = int(instances[1])
        if vent_status:
            template.set_option(section, 'link_name', response)
        else:
            template.set_option(section,
                                'link_name',
                                true_name.split('/')[-1])
        if self.version == 'HEAD':
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
        groups = vent_template.option('info', 'groups')
        if groups[0]:
            template.set_option(section, 'groups', groups[1])
        # set groups to empty string if no groups defined for tool
        else:
            template.set_option(section, 'groups', '')
        # write additional entries for multiple instances
        if addtl_entries > 1:
            # add 2 for naming conventions
            for i in range(2, addtl_entries + 1):
                addtl_section = section.rsplit(':', 2)
                addtl_section[0] += str(i)
                addtl_section = ':'.join(addtl_section)
                template.add_section(addtl_section)
                orig_vals = template.section(section)[1]
                for val in orig_vals:
                    template.set_option(addtl_section, val[0], val[1])
                template.set_option(addtl_section, 'name',
                                    true_name.split('/')[-1]+str(i))
        return status, template, match_path, image_name, section

    def _build_image(self, template, match_path, image_name, section, build_local=False):
        status = (True, None)

        def set_instances(template, section, built, image_id=None):
            """ Set build information for multiple instances """
            i = 2
            while True:
                addtl_section = section.rsplit(':', 2)
                addtl_section[0] += str(i)
                addtl_section = ':'.join(addtl_section)
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
        multi_instance = False
        try:
            settings = template.option(section, 'settings')
            if settings[0]:
                settings_dict = json.loads(settings[1])
                if 'instances' in settings_dict and int(settings_dict['instances']) > 1:
                    multi_instance = True
        except Exception as e:  # pragma: no cover
            self.logger.error(
                'Failed to check for multi instance because: {0}'.format(str(e)))
            status = (False, str(e))

        cwd = getcwd()
        chdir(match_path)
        try:
            name = template.option(section, 'name')
            groups = template.option(section, 'groups')
            repo = template.option(section, 'repo')
            t_type = template.option(section, 'type')
            path = template.option(section, 'path')
            status, config_override = self.path_dirs.override_config(path[1])
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
            if use_existing_image == 'yes' and not config_override:
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
                    status = (True, 'Found {0}'.format(image_name))
                    self.logger.info(str(status))
                    image_exists = True
                except docker.errors.ImageNotFound:
                    image_exists = False
                except Exception as e:  # pragma: no cover
                    self.logger.warning(
                        'Failed to query Docker for images because: {0}'.format(str(e)))
            if not image_exists:
                # pull if '/' in image_name, fallback to build
                if '/' in image_name and not build_local and not config_override:
                    try:
                        image = self.d_client.images.pull(image_name)
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
                            status = (True, 'Pulled {0}'.format(image_name))
                            self.logger.info(str(status))
                        else:
                            template.set_option(section, 'built', 'failed')
                            template.set_option(section, 'last_updated',
                                                str(datetime.utcnow()) +
                                                ' UTC')
                            # set other instances too
                            if multi_instance:
                                set_instances(template, section, 'failed')
                            status = (False, 'Failed to pull image {0}'.format(
                                str(output.split('\n')[-1])))
                            self.logger.warning(str(status))
                        pull = True
                    except Exception as e:  # pragma: no cover
                        self.logger.warning(
                            'Failed to pull image, going to build instead: {0}'.format(str(e)))
                        status = (
                            False, 'Failed to pull image because: {0}'.format(str(e)))
            if not pull and not image_exists:
                # get username to label built image with
                username = getpass.getuser()

                # see if additional file arg needed for building multiple
                # images from same directory
                file_tag = ' .'
                multi_tool = template.option(section, 'multi_tool')
                if multi_tool[0] and multi_tool[1] == 'yes':
                    specific_file = template.option(section, 'name')[1]
                    if specific_file == 'unspecified':
                        file_tag = 'Dockerfile'
                    else:
                        file_tag = 'Dockerfile.' + specific_file

                # update image name with new version for update
                image_name = image_name.rsplit(':', 1)[0]+':'+self.branch
                labels = {}
                labels['vent'] = ''
                labels['vent.section'] = section
                labels['vent.repo'] = self.repo
                labels['vent.type'] = t_type[1]
                labels['vent.name'] = name[1]
                labels['vent.groups'] = groups[1]
                labels['built-by'] = username
                image = self.d_client.images.build(path='.', tag=image_name,
                                                   labels=labels, rm=True)
                image_id = image[0].id.split(':')[1][:12]
                template.set_option(section, 'built', 'yes')
                template.set_option(section, 'image_id', image_id)
                template.set_option(section, 'last_updated',
                                    str(datetime.utcnow()) +
                                    ' UTC')
                # set other instances too
                if multi_instance:
                    set_instances(template, section, 'yes', image_id)
                status = (True, 'Built {0}'.format(image_name))
        except Exception as e:  # pragma: no cover
            self.logger.error('Unable to build image {0} because: {1} | {2}'.format(
                str(image_name), str(e), str(output)))
            template.set_option(section, 'built', 'failed')
            template.set_option(section, 'last_updated',
                                str(datetime.utcnow()) + ' UTC')
            if multi_instance:
                set_instances(template, section, 'failed')
            status = (
                False, 'Failed to build image because: {0}'.format(str(e)))

        chdir(cwd)
        template.set_option(section, 'running', 'no')

        return status, template

    def _clone(self, user=None, pw=None):
        status = (True, None)
        try:
            # if path already exists, ignore
            try:
                path, _, _ = self.path_dirs.get_path(self.repo)
                chdir(path)
                return status
            except Exception as e:  # pragma: no cover
                self.logger.debug("Repo doesn't exist, attempting to clone.")

            status = self.path_dirs.apply_path(self.repo)
            if not status[0]:
                self.logger.error(
                    'Unable to clone because: {0}'.format(str(status[1])))
                return status

            repo = self.repo
            # check if user and pw were supplied, typically for private repos
            if user and pw:
                # only https is supported when using user/pw
                auth_repo = 'https://' + user + ':' + pw + '@'
                repo = auth_repo + repo.split('https://')[-1]

            # clone repo
            check_output(shlex.split('env GIT_SSL_NO_VERIFY=true git clone --recursive ' + repo + ' .'),
                         stderr=STDOUT,
                         close_fds=True).decode('utf-8')

            chdir(status[1])
            status = (True, 'Successfully cloned: {0}'.format(self.repo))
        except Exception as e:  # pragma: no cover
            e_str = str(e)
            # scrub username and password from error message
            if e_str.find('@') >= 0:
                e_str = e_str[:e_str.find('//') + 2] + \
                    e_str[e_str.find('@') + 1:]
            self.logger.error('Clone failed with error: {0}'.format(e_str))
            status = (False, e_str)
        return status

    def update(self, repo, tools=None):
        # TODO
        return


class Image:

    def __init__(self, manifest):
        self.manifest = manifest
        self.d_client = docker.from_env()
        self.logger = Logger(__name__)

    def add(self, image, link_name, tag=None, registry=None, groups=None):
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
            if not link_name:
                link_name = name
            if not groups:
                groups = ''
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
            self.logger.error(
                'Failed to add image because: {0}'.format(str(e)))
            status = (False, str(e))
        return status

    def update(self, image):
        # TODO
        return


class Tools:

    def __init__(self, version='HEAD', branch='master', user=None, pw=None,
                 *args, **kwargs):
        self.version = version
        self.branch = branch
        self.user = user
        self.pw = pw
        self.d_client = docker.from_env()
        self.path_dirs = PathDirs(**kwargs)
        self.path_dirs.host_config()
        self.manifest = join(self.path_dirs.meta_dir,
                             'plugin_manifest.cfg')
        self.logger = Logger(__name__)

    def new(self, tool_type, uri, tools=None, link_name=None, image_name=None,
            overrides=None, tag=None, registry=None, groups=None):
        try:
            # remove tools that are already installed from being added
            if isinstance(tools, list):
                i = len(tools) - 1
                while i >= 0:
                    tool = tools[i]
                    if tool[0].find('@') >= 0:
                        tool_name = tool[0].split('@')[-1]
                    else:
                        tool_name = tool[0].rsplit('/', 1)[-1]
                    constraints = {'name': tool_name,
                                   'repo': repo.split('.git')[0]}
                    prev_installed, _ = Template(template=self.manifest).constrain_opts(constraints,
                                                                                        [])
                    # don't reinstall
                    if prev_installed:
                        tools.remove(tool)
                    i -= 1
                if len(tools) == 0:
                    tools = None
        except Exception as e:  # pragma: no cover
            self.logger.error('Add failed with error: {0}'.format(str(e)))
            return (False, str(e))

        if tool_type == 'image':
            status = Image(self.manifest).add(uri, link_name, tag=tag,
                                              registry=registry,
                                              groups=groups)
        else:
            if tool_type == 'core':
                uri = 'https://github.com/cyberreboot/vent'
                core = True
            status = Repository(self.manifest).add(uri, tools,
                                                   overrides=overrides,
                                                   version=self.version,
                                                   image_name=image_name,
                                                   branch=self.branch,
                                                   user=self.user,
                                                   pw=self.pw, core=core)
        return status

    def configure(self, tool):
        # TODO
        return

    def inventory(self, choices=None):
        """ Return a dictionary of the inventory items and status """
        status = (True, None)
        if not choices:
            return (False, 'No choices made')
        try:
            # choices: repos, tools, images, built, running, enabled
            items = {'repos': [], 'tools': {}, 'images': {},
                     'built': {}, 'running': {}, 'enabled': {}}

            tools = Template(self.manifest).list_tools()
            for choice in choices:
                for tool in tools:
                    try:
                        if choice == 'repos':
                            if 'repo' in tool:
                                if (tool['repo'] and
                                        tool['repo'] not in items[choice]):
                                    items[choice].append(tool['repo'])
                        elif choice == 'tools':
                            items[choice][tool['section']] = tool['name']
                        elif choice == 'images':
                            # TODO also check against docker
                            items[choice][tool['section']] = tool['image_name']
                        elif choice == 'built':
                            items[choice][tool['section']] = tool['built']
                        elif choice == 'running':
                            containers = Containers()
                            status = 'not running'
                            for container in containers:
                                image_name = tool['image_name'] \
                                    .rsplit(':' +
                                            tool['version'], 1)[0]
                                image_name = image_name.replace(':', '-')
                                image_name = image_name.replace('/', '-')
                                self.logger.info('image_name: ' + image_name)
                                if container[0] == image_name:
                                    status = container[1]
                                elif container[0] == image_name + \
                                        '-' + tool['version']:
                                    status = container[1]
                            items[choice][tool['section']] = status
                        elif choice == 'enabled':
                            items[choice][tool['section']] = tool['enabled']
                        else:
                            # unknown choice
                            pass
                    except Exception as e:  # pragma: no cover
                        self.logger.error('Unable to grab info about tool: ' +
                                          str(tool) + ' because: ' + str(e))
            status = (True, items)
        except Exception as e:  # pragma: no cover
            self.logger.error(
                'Inventory failed with error: {0}'.format(str(e)))
            status = (False, str(e))
        return status

    def remove(self, repo, name):
        args = locals()
        status = (True, None)

        # get resulting dict of sections with options that match constraints
        results, template = Template(
            template=self.manifest).constrain_opts(args, [])
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
                    self.logger.info(
                        'Removing container: {0}'.format(container_name))
            except Exception as e:  # pragma: no cover
                self.logger.warning('Unable to remove the container: ' +
                                    container_name + ' because: ' + str(e))

            # check for image and remove
            try:
                response = None
                image_id = template.option(result, 'image_id')[1]
                response = self.d_client.images.remove(image_id, force=True)
                self.logger.info('Removing image: ' + image_name)
            except Exception as e:  # pragma: no cover
                self.logger.warning('Unable to remove the image: ' +
                                    image_name + ' because: ' + str(e))

            # remove tool from the manifest
            for i in range(1, instances + 1):
                res = result.rsplit(':', 2)
                res[0] += str(i) if i != 1 else ''
                res = ':'.join(res)
                if template.section(res)[0]:
                    status = template.del_section(res)
                    self.logger.info('Removing tool: ' + res)
        # TODO if all tools from a repo have been removed, remove the repo
        template.write_config()
        return status

    def start(self, repo, name):
        args = locals()
        del args['self']
        tool_d = {}
        tool_d.update(self._prep_start(**args)[1])
        status = (True, None)
        try:
            # check start priorities (priority of groups alphabetical for now)
            group_orders = {}
            groups = []
            containers_remaining = []
            username = getpass.getuser()
            for container in tool_d:
                containers_remaining.append(container)
                self.logger.info(
                    'User: ' + username +
                    ' starting container: ' + str(container)
                )
                if 'labels' in tool_d[container]:
                    if 'vent.groups' in tool_d[container]['labels']:
                        groups += tool_d[container]['labels']['vent.groups'].split(
                            ',')
                        if 'vent.priority' in tool_d[container]['labels']:
                            priorities = tool_d[container]['labels']['vent.priority'].split(
                                ',')
                            container_groups = tool_d[container]['labels']['vent.groups'].split(
                                ',')
                            for i, priority in enumerate(priorities):
                                if container_groups[i] not in group_orders:
                                    group_orders[container_groups[i]] = []
                                group_orders[container_groups[i]].append(
                                    (int(priority), container))
                            containers_remaining.remove(container)
                    tool_d[container]['labels'].update(
                        {'started-by': username}
                    )

                else:
                    tool_d[container].update(
                        {'labels': {'started-by': username}}
                    )

            # start containers based on priorities
            p_results = self._start_priority_containers(groups,
                                                        group_orders,
                                                        tool_d)

            # start the rest of the containers that didn't have any priorities
            r_results = self._start_remaining_containers(
                containers_remaining, tool_d)
            results = (p_results[0] + r_results[0],
                       p_results[1] + r_results[1])

            if len(results[1]) > 0:
                status = (False, results)
            else:
                status = (True, results)
        except Exception as e:  # pragma: no cover
            self.logger.error('Start failed with error: {0}'.format(str(e)))
            status = (False, str(e))

        return status

    def _prep_start(self, repo, name):
        args = locals()
        status = (True, None)
        try:
            options = ['name',
                       'namespace',
                       'built',
                       'groups',
                       'path',
                       'image_name',
                       'branch',
                       'repo',
                       'type',
                       'version']
            vent_config = Template(template=self.path_dirs.cfg_file)
            manifest = Template(self.manifest)
            files = vent_config.option('main', 'files')
            files = (files[0], expanduser(files[1]))
            s, _ = manifest.constrain_opts(args, options)
            status, tool_d = self._start_sections(s, files)

            # look out for links to delete because they're defined externally
            links_to_delete = set()

            # get instances for each tool
            tool_instances = {}
            sections = manifest.sections()[1]
            for section in sections:
                settings = manifest.option(section, 'settings')
                if settings[0]:
                    settings = json.loads(settings[1])
                    if 'instances' in settings:
                        l_name = manifest.option(section, 'link_name')
                        if l_name[0]:
                            tool_instances[l_name[1]] = int(
                                settings['instances'])

            # check and update links, volumes_from, network_mode
            for container in list(tool_d.keys()):
                if 'labels' not in tool_d[container] or 'vent.groups' not in tool_d[container]['labels'] or 'core' not in tool_d[container]['labels']['vent.groups']:
                    tool_d[container]['remove'] = True
                if 'links' in tool_d[container]:
                    for link in list(tool_d[container]['links'].keys()):
                        # add links to external services already running if
                        # necessary, by default configure local services too
                        configure_local = True
                        ext = 'external-services'
                        if link in vent_config.options(ext)[1]:
                            try:
                                lconf = json.loads(vent_config.option(ext,
                                                                      link)[1])
                                if ('locally_active' not in lconf or
                                        lconf['locally_active'] == 'no'):
                                    ip_adr = lconf['ip_address']
                                    port = lconf['port']
                                    tool_d[container]['extra_hosts'] = {}
                                    # containers use lowercase names for
                                    # connections
                                    tool_d[container]['extra_hosts'][link.lower()
                                                                     ] = ip_adr
                                    # create an environment variable for container
                                    # to access port later
                                    env_variable = link.upper() + \
                                        '_CUSTOM_PORT=' + port
                                    if 'environment' not in tool_d[container]:
                                        tool_d[container]['environment'] = []
                                    tool_d[container]['environment'].append(
                                        env_variable)
                                    # remove the entry from links because no
                                    # longer connecting to local container
                                    links_to_delete.add(link)
                                    configure_local = False
                            except Exception as e:  # pragma: no cover
                                self.logger.error(
                                    'Could not load external settings because: {0}'.format(str(e)))
                                configure_local = True
                                status = False
                        if configure_local:
                            for c in list(tool_d.keys()):
                                if ('tmp_name' in tool_d[c] and
                                        tool_d[c]['tmp_name'] == link):
                                    tool_d[container]['links'][tool_d[c]['name']
                                                               ] = tool_d[container]['links'].pop(link)
                                    if link in tool_instances and tool_instances[link] > 1:
                                        for i in range(2, tool_instances[link] + 1):
                                            tool_d[container]['links'][tool_d[c]['name'] + str(
                                                i)] = tool_d[container]['links'][tool_d[c]['name']] + str(i)
                if 'volumes_from' in tool_d[container]:
                    tmp_volumes_from = tool_d[container]['volumes_from']
                    tool_d[container]['volumes_from'] = []
                    for volumes_from in list(tmp_volumes_from):
                        for c in list(tool_d.keys()):
                            if ('tmp_name' in tool_d[c] and
                                    tool_d[c]['tmp_name'] == volumes_from):
                                tool_d[container]['volumes_from'].append(
                                    tool_d[c]['name'])
                                tmp_volumes_from.remove(volumes_from)
                    tool_d[container]['volumes_from'] += tmp_volumes_from
                if 'network_mode' in tool_d[container]:
                    if tool_d[container]['network_mode'].startswith('container:'):
                        network_c_name = tool_d[container]['network_mode'].split('container:')[
                            1]
                        for c in list(tool_d.keys()):
                            if ('tmp_name' in tool_d[c] and
                                    tool_d[c]['tmp_name'] == network_c_name):
                                tool_d[container]['network_mode'] = 'container:' + \
                                    tool_d[c]['name']

            # remove tmp_names
            for c in list(tool_d.keys()):
                if 'tmp_name' in tool_d[c]:
                    del tool_d[c]['tmp_name']

            # remove links section if all were externally configured
            for c in list(tool_d.keys()):
                if 'links' in tool_d[c]:
                    for link in links_to_delete:
                        if link in tool_d[c]['links']:
                            del tool_d[c]['links'][link]
                    # delete links if no more defined
                    if not tool_d[c]['links']:
                        del tool_d[c]['links']

            # remove containers that shouldn't be started
            for c in list(tool_d.keys()):
                deleted = False
                if 'start' in tool_d[c] and not tool_d[c]['start']:
                    del tool_d[c]
                    deleted = True
                if not deleted:
                    # look for tools services that are being done externally
                    # tools are capitalized in vent.cfg, so make them lowercase
                    # for comparison
                    ext = 'external-services'
                    external_tools = vent_config.section(ext)[1]
                    name = tool_d[c]['labels']['vent.name']
                    for tool in external_tools:
                        if name == tool[0].lower():
                            try:
                                tool_config = json.loads(tool[1])
                                if ('locally_active' in tool_config and
                                        tool_config['locally_active'] == 'no'):
                                    del tool_d[c]
                            except Exception as e:  # pragma: no cover
                                self.logger.warning('Locally running container ' +
                                                    name + ' may be redundant')

            if status:
                status = (True, tool_d)
            else:
                status = (False, tool_d)
        except Exception as e:  # pragma: no cover
            self.logger.error('_prep_start failed with error: '+str(e))
            status = (False, e)
        return status

    def _start_sections(self, s, files):
        tool_d = {}
        status = (True, None)
        for section in s:
            # initialize needed vars
            c_name = s[section]['image_name'].replace(':', '-')
            c_name = c_name.replace('/', '-')
            instance_num = re.search(r'\d+$', s[section]['name'])
            if instance_num:
                c_name += instance_num.group()
            image_name = s[section]['image_name']

            # checkout the right version and branch of the repo
            cwd = getcwd()
            tool_d[c_name] = {'image': image_name,
                              'name': c_name}
            # get rid of all commented sections in various runtime
            # configurations
            manifest = Template(self.manifest)
            overall_dict = {}
            for setting in ['info', 'docker', 'gpu', 'settings', 'service']:
                option = manifest.option(section, setting)
                if option[0]:
                    overall_dict[setting] = {}
                    settings_dict = json.loads(option[1])
                    for opt in settings_dict:
                        if not opt.startswith('#'):
                            overall_dict[setting][opt] = settings_dict[opt]

            if 'docker' in overall_dict:
                options_dict = overall_dict['docker']
                for option in options_dict:
                    options = options_dict[option]
                    # check for commands to evaluate
                    if '`' in options:
                        cmds = options.split('`')
                        if len(cmds) > 2:
                            i = 1
                            while i < len(cmds):
                                try:
                                    cmds[i] = check_output(shlex.split(cmds[i]),
                                                           stderr=STDOUT,
                                                           close_fds=True).strip().decode('utf-8')
                                except Exception as e:  # pragma: no cover
                                    self.logger.error(
                                        'unable to evaluate command specified in vent.template: ' + str(e))
                                i += 2
                        options = ''.join(cmds)
                    # check for commands to evaluate
                    # store options set for docker
                    try:
                        tool_d[c_name][option] = ast.literal_eval(options)
                    except Exception as e:  # pragma: no cover
                        self.logger.debug(
                            'Unable to literal_eval: {0}'.format(str(options)))
                        tool_d[c_name][option] = options

            if 'labels' not in tool_d[c_name]:
                tool_d[c_name]['labels'] = {}

            # get the service uri info
            if 'service' in overall_dict:
                try:
                    options_dict = overall_dict['service']
                    for option in options_dict:
                        tool_d[c_name]['labels'][option] = options_dict[option]
                except Exception as e:   # pragma: no cover
                    self.logger.error('unable to store service options for '
                                      'docker: ' + str(e))

            # check for gpu settings
            if 'gpu' in overall_dict:
                try:
                    options_dict = json.loads(status[1])
                    for option in options_dict:
                        tool_d[c_name]['labels']['gpu.' +
                                                 option] = options_dict[option]
                except Exception as e:   # pragma: no cover
                    self.logger.error('unable to store gpu options for '
                                      'docker: ' + str(e))

            # get temporary name for links, etc.
            plugin_c = Template(template=self.manifest)
            status, plugin_sections = plugin_c.sections()
            for plugin_section in plugin_sections:
                status = plugin_c.option(plugin_section, 'link_name')
                image_status = plugin_c.option(plugin_section, 'image_name')
                if status[0] and image_status[0]:
                    cont_name = image_status[1].replace(':', '-')
                    cont_name = cont_name.replace('/', '-')
                    if cont_name not in tool_d:
                        tool_d[cont_name] = {'image': image_status[1],
                                             'name': cont_name,
                                             'start': False}
                    tool_d[cont_name]['tmp_name'] = status[1]

            # add extra labels
            tool_d[c_name]['labels']['vent'] = Version()
            tool_d[c_name]['labels']['vent.namespace'] = s[section]['namespace']
            tool_d[c_name]['labels']['vent.branch'] = s[section]['branch']
            tool_d[c_name]['labels']['vent.version'] = s[section]['version']
            tool_d[c_name]['labels']['vent.name'] = s[section]['name']
            tool_d[c_name]['labels']['vent.section'] = section
            tool_d[c_name]['labels']['vent.repo'] = s[section]['repo']
            tool_d[c_name]['labels']['vent.type'] = s[section]['type']

            # check for log_config settings in external-services
            externally_configured = False
            vent_config = Template(self.path_dirs.cfg_file)
            for ext_tool in vent_config.section('external-services')[1]:
                if ext_tool[0].lower() == 'syslog':
                    try:
                        log_dict = json.loads(ext_tool[1])
                        # configure if not locally active
                        if ('locally_active' not in log_dict or
                                log_dict['locally_active'] == 'no'):
                            del log_dict['locally_active']
                            log_config = {}
                            log_config['type'] = 'syslog'
                            log_config['config'] = {}
                            ip_address = ''
                            port = ''
                            for option in log_dict:
                                if option == 'ip_address':
                                    ip_address = log_dict[option]
                                elif option == 'port':
                                    port = log_dict['port']
                            syslog_address = 'tcp://' + ip_address + ':' + port
                            syslog_config = {'syslog-address': syslog_address,
                                             'syslog-facility': 'daemon',
                                             'tag': '{{.Name}}'}
                            log_config['config'].update(syslog_config)
                            externally_configured = True
                    except Exception as e:  # pragma: no cover
                        self.logger.error('external settings for log_config'
                                          " couldn't be stored because: " +
                                          str(e))
                        externally_configured = False
            if not externally_configured:
                log_config = {'type': 'syslog',
                              'config': {'syslog-address': 'tcp://0.0.0.0:514',
                                         'syslog-facility': 'daemon',
                                         'tag': '{{.Name}}'}}
            if 'groups' in s[section]:
                # add labels for groups
                tool_d[c_name]['labels']['vent.groups'] = s[section]['groups']
                # add restart=always to core containers
                if 'core' in s[section]['groups']:
                    tool_d[c_name]['restart_policy'] = {'Name': 'always'}
                # map network names to environment variables
                if 'network' in s[section]['groups']:
                    vent_config = Template(template=self.path_dirs.cfg_file)
                    nic_mappings = vent_config.section('network-mapping')
                    nics = ''
                    if nic_mappings[0]:
                        for nic in nic_mappings[1]:
                            nics += nic[0] + ':' + nic[1] + ','
                        nics = nics[:-1]
                    if nics:
                        if 'environment' in tool_d[c_name]:
                            tool_d[c_name]['environment'].append(
                                'VENT_NICS='+nics)
                        else:
                            tool_d[c_name]['environment'] = ['VENT_NICS='+nics]
                # send logs to syslog
                if ('syslog' not in s[section]['groups'] and
                        'core' in s[section]['groups']):
                    log_config['config']['tag'] = '{{.Name}}'
                    tool_d[c_name]['log_config'] = log_config
                if 'syslog' not in s[section]['groups']:
                    tool_d[c_name]['log_config'] = log_config
                # mount necessary directories
                if 'files' in s[section]['groups']:
                    ulimits = []
                    ulimits.append(docker.types.Ulimit(
                        name='nofile', soft=1048576, hard=1048576))
                    tool_d[c_name]['ulimits'] = ulimits
                    # check if running in a docker container
                    if 'VENT_CONTAINERIZED' in environ and environ['VENT_CONTAINERIZED'] == 'true':
                        if 'volumes_from' in tool_d[c_name]:
                            tool_d[c_name]['volumes_from'].append(
                                environ['HOSTNAME'])
                        else:
                            tool_d[c_name]['volumes_from'] = [
                                environ['HOSTNAME']]
                    else:
                        if 'volumes' in tool_d[c_name]:
                            tool_d[c_name]['volumes'][self.path_dirs.base_dir[:-1]
                                                      ] = {'bind': '/vent', 'mode': 'ro'}
                        else:
                            tool_d[c_name]['volumes'] = {
                                self.path_dirs.base_dir[:-1]: {'bind': '/vent', 'mode': 'ro'}}
                    if files[0]:
                        if 'volumes' in tool_d[c_name]:
                            tool_d[c_name]['volumes'][files[1]] = {
                                'bind': '/files', 'mode': 'rw'}
                        else:
                            tool_d[c_name]['volumes'] = {
                                files[1]: {'bind': '/files', 'mode': 'rw'}}
            else:
                tool_d[c_name]['log_config'] = log_config

            # add label for priority
            if 'settings' in overall_dict:
                try:
                    options_dict = overall_dict['settings']
                    for option in options_dict:
                        if option == 'priority':
                            tool_d[c_name]['labels']['vent.priority'] = options_dict[option]
                except Exception as e:   # pragma: no cover
                    self.logger.error('unable to store settings options '
                                      'for docker ' + str(e))

            # only start tools that have been built
            if s[section]['built'] != 'yes':
                del tool_d[c_name]
            # store section information for adding info to manifest later
            else:
                tool_d[c_name]['section'] = section
        return status, tool_d

    def _start_priority_containers(self, groups, group_orders, tool_d):
        """ Select containers based on priorities to start """
        vent_cfg = Template(self.path_dirs.cfg_file)
        cfg_groups = vent_cfg.option('groups', 'start_order')
        if cfg_groups[0]:
            cfg_groups = cfg_groups[1].split(',')
        else:
            cfg_groups = []
        all_groups = sorted(set(groups))
        s_conts = []
        f_conts = []
        # start tools in order of group defined in vent.cfg
        for group in cfg_groups:
            # remove from all_groups because already checked out
            if group in all_groups:
                all_groups.remove(group)
            if group in group_orders:
                for cont_t in sorted(group_orders[group]):
                    if cont_t[1] not in s_conts:
                        s_conts, f_conts = self._start_container(cont_t[1],
                                                                 tool_d,
                                                                 s_conts,
                                                                 f_conts)
        # start tools that haven't been specified in the vent.cfg, if any
        for group in all_groups:
            if group in group_orders:
                for cont_t in sorted(group_orders[group]):
                    if cont_t[1] not in s_conts:
                        s_conts, f_conts = self._start_container(cont_t[1],
                                                                 tool_d,
                                                                 s_conts,
                                                                 f_conts)
        return (s_conts, f_conts)

    def _start_remaining_containers(self, containers_remaining, tool_d):
        """
        Select remaining containers that didn't have priorities to start
        """
        s_containers = []
        f_containers = []
        for container in containers_remaining:
            s_containers, f_containers = self._start_container(container,
                                                               tool_d,
                                                               s_containers,
                                                               f_containers)
        return (s_containers, f_containers)

    def _start_container(self, container, tool_d, s_containers, f_containers):
        """ Start container that was passed in and return status """
        # use section to add info to manifest
        section = tool_d[container]['section']
        del tool_d[container]['section']
        manifest = Template(self.manifest)
        try:
            # try to start an existing container first
            c = self.d_client.containers.get(container)
            c.start()
            s_containers.append(container)
            manifest.set_option(section, 'running', 'yes')
            self.logger.info('started ' + str(container) +
                             ' with ID: ' + str(c.short_id))
        except Exception as err:
            s_containers, f_containers = self._run_container(
                container, tool_d, section, s_containers, f_containers)

        # save changes made to manifest
        manifest.write_config()
        return s_containers, f_containers

    def _run_container(self, container, tool_d, section, s_containers, f_containers):
        manifest = Template(self.manifest)
        try:
            gpu = 'gpu.enabled'
            failed = False
            if (gpu in tool_d[container]['labels'] and
                    tool_d[container]['labels'][gpu] == 'yes'):
                vent_config = Template(template=self.path_dirs.cfg_file)
                port = ''
                host = ''
                result = vent_config.option('nvidia-docker-plugin', 'port')
                if result[0]:
                    port = result[1]
                else:
                    port = '3476'
                result = vent_config.option('nvidia-docker-plugin', 'host')
                if result[0]:
                    host = result[1]
                else:
                    # now just requires ip, ifconfig
                    try:
                        route = check_output(('ip', 'route')).decode(
                            'utf-8').split('\n')
                        default = ''
                        # grab the default network device.
                        for device in route:
                            if 'default' in device:
                                default = device.split()[4]
                                break
                        # grab the IP address for the default device
                        ip_addr = check_output(
                            ('ifconfig', default)).decode('utf-8')
                        ip_addr = ip_addr.split('\n')[1].split()[1]
                        host = ip_addr
                    except Exception as e:  # pragma no cover
                        self.logger.error('failed to grab ip. Ensure that \
                                          ip and ifconfig are installed')
                nd_url = 'http://' + host + ':' + port + '/v1.0/docker/cli'
                params = {'vol': 'nvidia_driver'}

                r = requests.get(nd_url, params=params)
                if r.status_code == 200:
                    options = r.text.split()
                    for option in options:
                        if option.startswith('--volume-driver='):
                            tool_d[container]['volume_driver'] = option.split('=', 1)[
                                1]
                        elif option.startswith('--volume='):
                            vol = option.split('=', 1)[1].split(':')
                            if 'volumes' in tool_d[container]:
                                if isinstance(tool_d[container]['volumes'], list):
                                    if len(vol) == 2:
                                        c_vol = vol[0] + \
                                            ':' + vol[1] + ':rw'
                                    else:
                                        c_vol = vol[0] + ':' + \
                                            vol[1] + ':' + vol[2]
                                    tool_d[container]['volumes'].append(
                                        c_vol)
                                else:  # Dictionary
                                    tool_d[container]['volumes'][vol[0]] = {'bind': vol[1],
                                                                            'mode': vol[2]}
                            else:
                                tool_d[container]['volumes'] = {vol[0]:
                                                                {'bind': vol[1],
                                                                 'mode': vol[2]}}
                        elif option.startswith('--device='):
                            dev = option.split('=', 1)[1]
                            if 'devices' in tool_d[container]:
                                tool_d[container]['devices'].append(dev +
                                                                    ':' +
                                                                    dev +
                                                                    ':rwm')
                            else:
                                tool_d[container]['devices'] = [
                                    dev + ':' + dev + ':rwm']
                        else:
                            self.logger.error('Unable to parse ' +
                                              'nvidia-docker option: ' +
                                              str(option))
                else:
                    failed = True
                    f_containers.append(container)
                    manifest.set_option(section, 'running', 'failed')
                    self.logger.error('failed to start ' + str(container) +
                                      ' because nvidia-docker-plugin ' +
                                      'failed with: ' + str(r.status_code))
            if not failed:
                try:
                    self.d_client.containers.remove(container, force=True)
                    self.logger.info(
                        'removed old existing container: ' + str(container))
                except Exception as e:
                    pass
                cont_id = self.d_client.containers.run(detach=True,
                                                       **tool_d[container])
                s_containers.append(container)
                manifest.set_option(section, 'running', 'yes')
                self.logger.info('started ' + str(container) +
                                 ' with ID: ' + str(cont_id))
        except Exception as e:  # pragma: no cover
            f_containers.append(container)
            manifest.set_option(section, 'running', 'failed')
            self.logger.error('failed to start ' + str(container) +
                              ' because: ' + str(e))
        return s_containers, f_containers

    def stop(self, repo, name):
        args = locals()
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
            s, _ = Template(template=self.manifest).constrain_opts(args,
                                                                   options)
            for section in s:
                container_name = s[section]['image_name'].replace(':', '-')
                container_name = container_name.replace('/', '-')
                try:
                    container = self.d_client.containers.get(container_name)
                    container.stop()
                    self.logger.info('Stopped {0}'.format(str(container_name)))
                except Exception as e:  # pragma: no cover
                    self.logger.error('Failed to stop ' + str(container_name) +
                                      ' because: ' + str(e))
        except Exception as e:  # pragma: no cover
            self.logger.error('Stop failed with error: ' + str(e))
            status = (False, e)
        return status


class System:

    def __init__(self, *args, **kwargs):
        self.d_client = docker.from_env()
        self.path_dirs = PathDirs(**kwargs)
        self.manifest = join(self.path_dirs.meta_dir,
                             'plugin_manifest.cfg')
        self.vent_config = self.path_dirs.cfg_file
        self.startup_file = self.path_dirs.startup_file
        self.logger = Logger(__name__)
        self._auto_install()

    def _auto_install(self):
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
            ignore = False
            if ('Labels' in image.attrs['Config'] and
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
                    # TODO clone it down
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
                    template.set_option(section, 'branch', section_str[-2])
                    template.set_option(section, 'version', section_str[-1])
                    template.set_option(section, 'last_updated', str(
                        datetime.utcnow()) + ' UTC')
                    if image.attrs['RepoTags']:
                        template.set_option(
                            section, 'image_name', image.attrs['RepoTags'][0])
                    else:
                        # image with none tag is outdated, don't add it
                        ignore = True
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
                if not ignore:
                    add_sections.append(section)
                    template.write_config()
        # TODO this check will always be true, need to actually validate the above logic
        if status[0]:
            status = (True, add_sections)
        return status

    def backup(self):
        """
        Saves the configuration information of the current running vent
        instance to be used for restoring at a later time
        """
        status = (True, None)
        # initialize all needed variables (names for backup files, etc.)
        backup_name = ('.vent-backup-' + '-'.join(Timestamp().split(' ')))
        backup_dir = join(expanduser('~'), backup_name)
        backup_manifest = join(backup_dir, 'backup_manifest.cfg')
        backup_vcfg = join(backup_dir, 'backup_vcfg.cfg')
        manifest = self.manifest

        # create new backup directory
        try:
            mkdir(backup_dir)
        except Exception as e:  # pragma: no cover
            self.logger.error(str(e))
            return (False, str(e))
        # create new files in backup directory
        try:
            # backup manifest
            with open(backup_manifest, 'w') as bmanifest:
                with open(manifest, 'r') as manifest_file:
                    bmanifest.write(manifest_file.read())
            # backup vent.cfg
            with open(backup_vcfg, 'w') as bvcfg:
                with open(self.vent_config, 'r') as vcfg_file:
                    bvcfg.write(vcfg_file.read())
            self.logger.info('Backup information written to ' + backup_dir)
            status = (True, backup_dir)
        except Exception as e:  # pragma: no cover
            self.logger.error("Couldn't backup vent: " + str(e))
            status = (False, str(e))
        # TODO #266
        return status

    def configure(self):
        # TODO
        return

    def gpu(self):
        # TODO
        return

    def history(self):
        # TODO #255
        return

    def restore(self, backup_dir):
        """
        Restores a vent configuration from a previously backed up version
        """
        # TODO #266
        status = (True, None)
        return status

    def reset(self):
        """ Factory reset all of Vent's user data, containers, and images """
        status = (True, None)
        error_message = ''

        # remove containers
        try:
            c_list = set(self.d_client.containers.list(
                filters={'label': 'vent'}, all=True))
            for c in c_list:
                c.remove(force=True)
        except Exception as e:  # pragma: no cover
            error_message += 'Error removing Vent containers: ' + str(e) + '\n'

        # remove images
        try:
            i_list = set(self.d_client.images.list(filters={'label': 'vent'},
                                                   all=True))
            for i in i_list:
                # delete tagged images only because they are the parents for
                # the untagged images. Remove the parents and the children get
                # removed automatically
                if i.attrs['RepoTags']:
                    self.d_client.images.remove(image=i.id, force=True)

        except Exception as e:  # pragma: no cover
            error_message += 'Error deleting Vent images: ' + str(e) + '\n'

        # remove .vent folder
        try:
            cwd = getcwd()
            if cwd.startswith(join(expanduser('~'), '.vent')):
                chdir(expanduser('~'))
            shutil.rmtree(join(expanduser('~'), '.vent'))
        except Exception as e:  # pragma: no cover
            error_message += 'Error deleting Vent data: ' + str(e) + '\n'

        if error_message:
            status = (False, error_message)
        return status

    def rollback(self):
        # TODO #266
        return

    def start(self):
        status = (True, None)
        # startup based on startup file
        if exists(self.startup_file):
            status = self._startup()
        else:
            tools = Tools()
            status = tools.new('core', None)
            if status[0]:
                status = tools.start(
                    'https://github.com/cyberreboot/vent', None)
        return status

    def _startup(self):
        """
        Automatically detect if a startup file is specified and stand up a vent
        host with all necessary tools based on the specifications in that file
        """
        status = (True, None)
        try:
            s_dict = {}
            # rewrite the yml file to exclusively lowercase
            with open(self.startup_file, 'r') as sup:
                vent_startup = sup.read()
            with open(self.startup_file, 'w') as sup:
                for line in vent_startup:
                    sup.write(line.lower())
            with open(self.startup_file, 'r') as sup:
                s_dict = yaml.safe_load(sup.read())
            if 'vent.cfg' in s_dict:
                v_cfg = Template(self.vent_config)
                for section in s_dict['vent.cfg']:
                    for option in s_dict['vent.cfg'][section]:
                        val = ('no', 'yes')[
                            s_dict['vent.cfg'][section][option]]
                        v_status = v_cfg.add_option(section, option, value=val)
                        if not v_status[0]:
                            v_cfg.set_option(section, option, val)
                v_cfg.write_config()
                del s_dict['vent.cfg']
            tool_d = {}
            extra_options = ['info', 'service', 'settings', 'docker', 'gpu']
            s_dict_c = copy.deepcopy(s_dict)
            # TODO check for repo or image type
            self.logger.info('startup file dict: {0}'.format(s_dict_c))
            for repo in s_dict_c:
                repository = Repository(System().manifest)
                repository.repo = repo
                repository._clone()
                repo_path, org, r_name = self.path_dirs.get_path(repo)
                get_tools = []
                for tool in s_dict_c[repo]:
                    t_branch = 'master'
                    t_version = 'HEAD'
                    if 'branch' in s_dict[repo][tool]:
                        t_branch = s_dict[repo][tool]['branch']
                    if 'version' in s_dict[repo][tool]:
                        t_version = s_dict[repo][tool]['version']
                    get_tools.append((tool, t_branch, t_version))

                available_tools = AvailableTools(repo_path, tools=get_tools)
                self.logger.info('tools found: {0}'.format(available_tools))
                for tool in s_dict_c[repo]:
                    # if we can't find the tool in that repo, skip over this
                    # tool and notify in the logs
                    t_path, t_path_cased = PathDirs.rel_path(
                        tool, available_tools)
                    if t_path is None:
                        self.logger.error("Couldn't find tool " + tool + ' in'
                                          ' repo ' + repo)
                        continue
                    # ensure no NoneType iteration errors
                    if s_dict_c[repo][tool] is None:
                        s_dict[repo][tool] = {}
                    # check if we need to configure instances along the way
                    instances = 1
                    if 'settings' in s_dict[repo][tool]:
                        if 'instances' in s_dict[repo][tool]['settings']:
                            instances = int(s_dict[repo][tool]
                                            ['settings']['instances'])
                    # add the tool
                    t_branch = 'master'
                    t_version = 'HEAD'
                    t_image = None
                    add_tools = None
                    build_tool = False
                    add_tools = [(t_path_cased, '')]
                    if 'branch' in s_dict[repo][tool]:
                        t_branch = s_dict[repo][tool]['branch']
                    if 'version' in s_dict[repo][tool]:
                        t_version = s_dict[repo][tool]['version']
                    if 'build' in s_dict[repo][tool]:
                        build_tool = s_dict[repo][tool]['build']
                    if 'image' in s_dict[repo][tool]:
                        t_image = s_dict[repo][tool]['image']
                    repository.add(
                        repo, add_tools, branch=t_branch, version=t_version, image_name=t_image)
                    manifest = Template(self.manifest)
                    # update the manifest with extra defined runtime settings
                    base_section = ':'.join([org, r_name, t_path,
                                             t_branch, t_version])
                    for option in extra_options:
                        if option in s_dict[repo][tool]:
                            opt_dict = manifest.option(base_section, option)
                            # add new values defined into default options for
                            # that tool, don't overwrite them
                            if opt_dict[0]:
                                opt_dict = json.loads(opt_dict[1])
                            else:
                                opt_dict = {}
                            # stringify values for vent
                            for v in s_dict[repo][tool][option]:
                                pval = s_dict[repo][tool][option][v]
                                s_dict[repo][tool][option][v] = json.dumps(
                                    pval)
                            opt_dict.update(s_dict[repo][tool][option])
                            manifest.set_option(base_section, option,
                                                json.dumps(opt_dict))
                    # copy manifest info into new sections if necessary
                    if instances > 1:
                        for i in range(2, instances + 1):
                            i_section = base_section.rsplit(':', 2)
                            i_section[0] += str(i)
                            i_section = ':'.join(i_section)
                            manifest.add_section(i_section)
                            for opt_val in manifest.section(base_section)[1]:
                                if opt_val[0] == 'name':
                                    manifest.set_option(i_section, opt_val[0],
                                                        opt_val[1] + str(i))
                                else:
                                    manifest.set_option(i_section, opt_val[0],
                                                        opt_val[1])
                    manifest.write_config()

            # start tools, if necessary
            for repo in s_dict:
                for tool in s_dict[repo]:
                    if 'start' in s_dict[repo][tool]:
                        if s_dict[repo][tool]['start']:
                            local_instances = 1
                            if 'settings' in s_dict[repo][tool] and 'instances' in s_dict[repo][tool]['settings']:
                                local_instances = int(
                                    s_dict[repo][tool]['settings']['instances'])
                            t_branch = 'master'
                            t_version = 'HEAD'
                            if 'branch' in s_dict[repo][tool]:
                                t_branch = s_dict[repo][tool]['branch']
                            if 'version' in s_dict[repo][tool]:
                                t_version = s_dict[repo][tool]['version']
                            for i in range(1, local_instances + 1):
                                i_name = tool + str(i) if i != 1 else tool
                                i_name = i_name.replace('@', '')
                                tool_d.update(self.prep_start(
                                    name=i_name,
                                    branch=t_branch,
                                    version=t_version)[1])
            if tool_d:
                self.start(tool_d)
        except Exception as e:  # pragma: no cover
            self.logger.error('Startup failed because: {0}'.format(str(e)))
            status = (False, str(e))
        return status

    def stop(self):
        status = (True, None)
        # remove containers
        try:
            c_list = set(self.d_client.containers.list(
                filters={'label': 'vent'}, all=True))
            for c in c_list:
                c.remove(force=True)
        except Exception as e:  # pragma: no cover
            status = (False, str(e))
        return status

    def get_configure(self,
                      repo=None,
                      name=None,
                      groups=None,
                      main_cfg=False):
        """
        Get the vent.template settings for a given tool by looking at the
        plugin_manifest
        """
        constraints = locals()
        del constraints['main_cfg']
        status = (True, None)
        template_dict = {}
        return_str = ''
        if main_cfg:
            vent_cfg = Template(self.vent_config)
            for section in vent_cfg.sections()[1]:
                template_dict[section] = {}
                for vals in vent_cfg.section(section)[1]:
                    template_dict[section][vals[0]] = vals[1]
        else:
            # all possible vent.template options stored in plugin_manifest
            options = ['info', 'service', 'settings', 'docker', 'gpu']
            tools = Template(System().manifest).constrain_opts(
                constraints, options)[0]
            if tools:
                # should only be one tool
                tool = list(tools.keys())[0]
                # load all vent.template options into dict
                for section in tools[tool]:
                    template_dict[section] = json.loads(tools[tool][section])
            else:
                status = (False, "Couldn't get vent.template information")
        if status[0]:
            # display all those options as they would in the file
            for section in template_dict:
                return_str += '[' + section + ']\n'
                # ensure instances shows up in configuration
                for option in template_dict[section]:
                    if option.startswith('#'):
                        return_str += option + '\n'
                    else:
                        return_str += option + ' = '
                        return_str += template_dict[section][option] + '\n'
                return_str += '\n'
            # only one newline at end of file
            status = (True, return_str[:-1])
        return status

    def save_configure(self,
                       repo=None,
                       name=None,
                       groups=None,
                       config_val='',
                       from_registry=False,
                       main_cfg=False,
                       instances=1):
        """
        Save changes made to vent.template through npyscreen to the template
        and to plugin_manifest
        """
        def template_to_manifest(vent_template, manifest, tool, instances):
            """
            Helper function to transfer information from vent.template
            to plugin_manifest
            """
            sections = vent_template.sections()
            if sections[0]:
                for section in sections[1]:
                    section_dict = {}
                    if section == 'settings':
                        section_dict.update({'instances': str(instances)})
                    options = vent_template.options(section)
                    if options[0]:
                        for option in options[1]:
                            option_name = option
                            if option == 'name':
                                option_name = 'link_name'
                            opt_val = vent_template.option(section,
                                                           option)[1]
                            section_dict[option_name] = opt_val
                    if section_dict:
                        manifest.set_option(tool, section,
                                            json.dumps(section_dict))
                    elif manifest.option(tool, section)[0]:
                        manifest.del_option(tool, section)

        constraints = locals()
        del constraints['config_val']
        del constraints['from_registry']
        del constraints['main_cfg']
        del constraints['instances']
        del constraints['template_to_manifest']
        status = (True, None)
        fd = None
        # ensure instances is an int and remove instances from config_val to
        # ensure correct info
        instances = int(instances)
        config_val = re.sub(r'instances\ *=\ *\d+\n', '', config_val)
        if not main_cfg:
            if not from_registry:
                # creating new instances
                if instances > 1:
                    fd, template_path = tempfile.mkstemp(suffix='.template')
                    # scrub name for clean section name
                    if re.search(r'\d+$', name):
                        name = re.sub(r'\d+$', '', name)
                    t_identifier = {'name': name,
                                    'branch': branch,
                                    'version': version}
                    result = Template(System().manifest).constrain_opts(
                        t_identifier, [])
                    tools = result[0]
                    manifest = result[1]
                    tool = list(tools.keys())[0]
                else:
                    options = ['path', 'multi_tool', 'name']
                    self.logger.info(constraints)
                    tools, manifest = Template(
                        System().manifest).constrain_opts(constraints, options)
                    self.logger.info(tools)
                    # only one tool in tools because perform this function for
                    # every tool
                    if tools:
                        tool = list(tools.keys())[0]
                        if ('multi_tool' in tools[tool] and
                                tools[tool]['multi_tool'] == 'yes'):
                            name = tools[tool]['name']
                            if name == 'unspecified':
                                name = 'vent'
                            template_path = join(tools[tool]['path'],
                                                 name+'.template')
                        else:
                            template_path = join(tools[tool]['path'],
                                                 'vent.template')
                    else:
                        status = (False, "Couldn't save configuration")
            else:
                fd, template_path = tempfile.mkstemp(suffix='.template')
                options = ['namespace']
                constraints.update({'type': 'registry'})
                del constraints['branch']
                tools, manifest = Template(System().manifest).constrain_opts(constraints,
                                                                             options)
                if tools:
                    tool = list(tools.keys())[0]
                else:
                    status = (False, "Couldn't save configuration")
            if status[0]:
                try:
                    # save in vent.template
                    with open(template_path, 'w') as f:
                        f.write(config_val)
                    # save in plugin_manifest
                    vent_template = Template(template_path)
                    if instances > 1:
                        # add instances as needed
                        for i in range(1, instances + 1):
                            i_section = tool.rsplit(':', 2)
                            i_section[0] += str(i) if i != 1 else ''
                            i_section = ':'.join(i_section)
                            if not manifest.section(i_section)[0]:
                                manifest.add_section(i_section)
                                for val_pair in manifest.section(tool)[1]:
                                    name = val_pair[0]
                                    val = val_pair[1]
                                    if name == 'name':
                                        val += str(i)
                                    elif name == 'last_updated':
                                        val = Timestamp()
                                    elif name == 'running':
                                        val = 'no'
                                    manifest.set_option(i_section, name, val)
                                template_to_manifest(vent_template, manifest,
                                                     i_section, instances)
                            else:
                                settings = manifest.option(i_section,
                                                           'settings')
                                if settings[0]:
                                    settings_dict = json.loads(settings[1])
                                    settings_dict['instances'] = str(instances)
                                    manifest.set_option(i_section, 'settings',
                                                        json.dumps(
                                                            settings_dict))
                                else:
                                    inst = str(instances)
                                    settings_dict = {'instances': inst}
                                    manifest.set_option(i_section, 'settings',
                                                        json.dumps(
                                                            settings_dict))
                    else:
                        try:
                            settings_str = manifest.option(tool, 'settings')[1]
                            settings_dict = json.loads(settings_str)
                            old_instances = int(settings_dict['instances'])
                        except Exception:
                            old_instances = 1
                        template_to_manifest(vent_template, manifest,
                                             tool, old_instances)
                    manifest.write_config()
                    status = (True, manifest)
                except Exception as e:  # pragma: no cover
                    self.logger.error('save_configure error: ' + str(e))
                    status = (False, str(e))
            # close os file handle and remove temp file
            if from_registry or instances > 1:
                try:
                    close(fd)
                    remove(template_path)
                except Exception as e:  # pragma: no cover
                    self.logger.error('save_configure error: ' + str(e))
        else:
            with open(self.vent_config, 'w') as f:
                f.write(config_val)
        return status

    def restart_tools(self,
                      repo=None,
                      name=None,
                      groups=None,
                      branch='master',
                      version='HEAD',
                      main_cfg=False,
                      old_val='',
                      new_val=''):
        """
        Restart necessary tools based on changes that have been made either to
        vent.cfg or to vent.template. This includes tools that need to be
        restarted because they depend on other tools that were changed.
        """
        self.logger.info('Starting: restart_tools')
        status = (True, None)
        if not main_cfg:
            try:
                t_identifier = {'name': name,
                                'branch': branch,
                                'version': version}
                result = Template(System().manifest).constrain_opts(t_identifier,
                                                                    ['running',
                                                                     'link_name'])
                tools = result[0]
                tool = list(tools.keys())[0]
                if ('running' in tools[tool] and
                        tools[tool]['running'] == 'yes'):
                    start_tools = [t_identifier]
                    dependent_tools = [tools[tool]['link_name']]
                    start_tools += Dependencies(dependent_tools)
                    start_d = {}
                    for tool_identifier in start_tools:
                        self.clean(**tool_identifier)
                        start_d.update(self.prep_start(**tool_identifier)[1])
                    if start_d:
                        self.start(start_d)
            except Exception as e:  # pragma: no cover
                self.logger.error('Trouble restarting tool ' + name +
                                  ' because: ' + str(e))
                status = (False, str(e))
        else:
            try:
                # string manipulation to get tools into arrays
                ext_start = old_val.find('[external-services]')
                if ext_start >= 0:
                    ot_str = old_val[old_val.find('[external-services]') + 20:]
                else:
                    ot_str = ''
                old_tools = []
                for old_tool in ot_str.split('\n'):
                    if old_tool != '':
                        old_tools.append(old_tool.split('=')[0].strip())
                ext_start = new_val.find('[external-services]')
                if ext_start >= 0:
                    nt_str = new_val[new_val.find('[external-services]') + 20:]
                else:
                    nt_str = ''
                new_tools = []
                for new_tool in nt_str.split('\n'):
                    if new_tool != '':
                        new_tools.append(new_tool.split('=')[0].strip())
                # find tools changed
                tool_changes = []
                for old_tool in old_tools:
                    if old_tool not in new_tools:
                        tool_changes.append(old_tool)
                for new_tool in new_tools:
                    if new_tool not in old_tools:
                        tool_changes.append(new_tool)
                    else:
                        # tool name will be the same
                        oconf = old_val[old_val.find(new_tool):].split('\n')[0]
                        nconf = new_val[new_val.find(new_tool):].split('\n')[0]
                        if oconf != nconf:
                            tool_changes.append(new_tool)
                # put link names in a dictionary for finding dependencies
                dependent_tools = []
                for i, entry in enumerate(tool_changes):
                    dependent_tools.append(entry)
                    # change names to lowercase for use in clean, prep_start
                    tool_changes[i] = {'name': entry.lower().replace('-', '_')}
                dependencies = Dependencies(dependent_tools)
                # restart tools
                restart = tool_changes + dependencies
                tool_d = {}
                for tool in restart:
                    self.clean(**tool)
                    tool_d.update(self.prep_start(**tool)[1])
                if tool_d:
                    self.start(tool_d)
            except Exception as e:  # pragma: no cover
                self.logger.error('Problem restarting tools: ' + str(e))
                status = (False, str(e))
        self.logger.info('restart_tools finished with status: ' +
                         str(status[0]))
        self.logger.info('Finished: restart_tools')
        return status

    def upgrade(self):
        ''' Upgrades Vent itself, and core containers '''
        # TODO
        return
