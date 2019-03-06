import getpass
import json
import shlex
from datetime import datetime
from os import chdir
from os import getcwd
from os.path import exists
from os.path import join
from subprocess import check_output
from subprocess import STDOUT

import docker

from vent.helpers.logs import Logger
from vent.helpers.meta import AvailableTools
from vent.helpers.meta import Checkout
from vent.helpers.meta import ParsedSections
from vent.helpers.meta import Timestamp
from vent.helpers.meta import ToolMatches
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
            cmd = 'git rev-parse --short ' + self.version
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
            if self.tools is None and self.overrides is None:
                # get all tools
                matches = AvailableTools(
                    path, branch=self.branch, version=self.version, core=self.core)
            elif self.tools is None:
                # there's only something in overrides
                # grab all the tools then apply overrides
                matches = AvailableTools(
                    path, branch=self.branch, version=self.version, core=self.core)
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

        # special case for vent images
        if image_name.startswith('cyberreboot/vent'):
            image_name = image_name.replace('vent-vent-core-', 'vent-')
            image_name = image_name.replace('vent-vent-extras-', 'vent-')

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
        output = ''

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
            t_type = template.option(section, 'type')
            path = template.option(section, 'path')
            status, config_override = self.path_dirs.override_config(path[1])
            if groups[1] == '' or not groups[0]:
                groups = (True, 'none')
            if not name[0]:
                name = (True, image_name)
            pull = False
            image_exists = False
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
                file_tag = 'Dockerfile'
                multi_tool = template.option(section, 'multi_tool')
                if multi_tool[0] and multi_tool[1] == 'yes':
                    specific_file = template.option(section, 'name')[1]
                    if specific_file != 'unspecified':
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
                image = self.d_client.images.build(path='.',
                                                   dockerfile=file_tag,
                                                   tag=image_name,
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
