import copy
import json
import re
import shutil
import tempfile
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

import docker
import yaml

from vent.api.repository import Repository
from vent.api.tools import Tools
from vent.helpers.logs import Logger
from vent.helpers.meta import AvailableTools
from vent.helpers.meta import Timestamp
from vent.helpers.paths import PathDirs
from vent.helpers.templates import Template


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
        vent_bridge = None

        # create vent network bridge if it doesn't already exist
        try:
            vent_bridge = self.d_client.networks.create(
                'vent', check_duplicate=True, driver='bridge')
        except docker.errors.APIError as e:  # pragma: no cover
            if str(e) != '409 Client Error: Conflict ("network with name vent already exists")':
                self.logger.error(
                    'Unable to create network bridge because: {0}'.format(str(e)))
                status = (False, str(e))
            else:
                vent_bridge = self.d_client.networks.list('vent')[0]

        if status[0]:
            # add vent to the vent network bridge
            try:
                vent_bridge.connect(environ['HOSTNAME'])
            except Exception as e:  # pragma: no coverr
                self.logger.error(
                    'Unable to connect vent to the network bridge because: {0}'.format(str(e)))
                status = (False, str(e))

        if status[0]:
            # remove vent to the default network bridge
            try:
                default_bridge = self.d_client.networks.list('bridge')[0]
                default_bridge.disconnect(environ['HOSTNAME'])
            except Exception as e:  # pragma: no coverr
                self.logger.error(
                    'Unable to disconnect vent from the default network bridge because: {0}'.format(str(e)))
                status = (False, str(e))

        if status[0]:
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
                    add_tools = [(t_path_cased, '')]
                    if 'branch' in s_dict[repo][tool]:
                        t_branch = s_dict[repo][tool]['branch']
                    if 'version' in s_dict[repo][tool]:
                        t_version = s_dict[repo][tool]['version']
                    if 'image' in s_dict[repo][tool]:
                        t_image = s_dict[repo][tool]['image']
                    repository.add(
                        repo, tools=add_tools, branch=t_branch, version=t_version, image_name=t_image)
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

            tool_d = {}
            tools = Tools()
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
                                tool_d.update(
                                    tools._prep_start(repo, i_name)[1])

            if tool_d:
                tools.start(tool_d, None, is_tool_d=True)
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
        api_system = System()
        manifest = api_system.manifest
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
                    result = Template(manifest).constrain_opts(
                        t_identifier, [])
                    tools = result[0]
                    tool = list(tools.keys())[0]
                else:
                    options = ['path', 'multi_tool', 'name']
                    tools, _ = Template(manifest).constrain_opts(
                        constraints, options)
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
                tools, _ = Template(manifest).constrain_opts(constraints,
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
                    manifest = Template(manifest)
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
                    # TODO
                    start_d = {}
                    for tool_identifier in start_tools:
                        self.clean(**tool_identifier)
                        start_d.update(self.prep_start(**tool_identifier)[1])
                    if start_d:
                        Tools().start(start_d, '', is_tool_d=True)
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
                    # TODO fix the arguments
                    Tools().start(tool_d)
            except Exception as e:  # pragma: no cover
                self.logger.error('Problem restarting tools: ' + str(e))
                status = (False, str(e))
        return status

    def upgrade(self):
        ''' Upgrades Vent itself, and core containers '''
        # TODO
        return
