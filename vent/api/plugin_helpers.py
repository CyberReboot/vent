import fnmatch
import json
import re
import shlex
from ast import literal_eval
from os import chdir
from os import environ
from os import getcwd
from os import walk
from os.path import expanduser
from os.path import join
from subprocess import check_output
from subprocess import STDOUT

import docker
import requests

from vent.api.templates import Template
from vent.helpers.logs import Logger
from vent.helpers.meta import Version
from vent.helpers.paths import PathDirs


class PluginHelper:
    """ Handle helper functions for the Plugin class """

    def __init__(self, **kargs):
        self.d_client = docker.from_env()
        self.path_dirs = PathDirs(**kargs)
        self.manifest = join(self.path_dirs.meta_dir,
                             'plugin_manifest.cfg')
        self.logger = Logger(__name__)

    def constraint_options(self, constraint_dict, options):
        """ Return result of constraints and options against a template """
        constraints = {}
        template = Template(template=self.manifest)
        for constraint in constraint_dict:
            if constraint != 'self':
                if (constraint_dict[constraint] or
                        constraint_dict[constraint] == ''):
                    constraints[constraint] = constraint_dict[constraint]
        results = template.constrained_sections(constraints=constraints,
                                                options=options)
        return results, template

    def get_path(self, repo, core=False):
        """ Return the path for the repo """
        if repo.endswith('.git'):
            repo = repo.split('.git')[0]
        org, name = repo.split('/')[-2:]
        path = self.path_dirs.plugins_dir
        path = join(path, org, name)
        return path, org, name

    def apply_path(self, repo):
        """ Set path to where the repo is and return original path """
        self.logger.info('Starting: apply_path')
        self.logger.info('repo given: ' + str(repo))
        try:
            # rewrite repo for consistency
            if repo.endswith('.git'):
                repo = repo.split('.git')[0]

            # get org and repo name and path repo will be cloned to
            org, name = repo.split('/')[-2:]
            path = join(self.path_dirs.plugins_dir, org, name)
            self.logger.info('cloning to path: ' + str(path))

            # save current path
            cwd = getcwd()

            # set to new repo path
            self.path_dirs.ensure_dir(path)
            chdir(path)
            status = (True, cwd, path)
        except Exception as e:  # pragma: no cover
            self.logger.error('apply_path failed with error: ' + str(e))
            status = (False, str(e))
        self.logger.info('Status of apply_path: ' + str(status))
        self.logger.info('Finished: apply_path')
        return status

    def checkout(self, branch='master', version='HEAD'):
        """ Checkout a specific version and branch of a repo """
        self.logger.info('Starting: checkout')
        self.logger.info('branch given: ' + str(branch))
        self.logger.info('version given: ' + str(version))
        try:
            status = check_output(shlex.split('git checkout ' + branch),
                                  stderr=STDOUT,
                                  close_fds=True).decode('utf-8')
            status = check_output(shlex.split('git pull'),
                                  stderr=STDOUT,
                                  close_fds=True).decode('utf-8')
            status = check_output(shlex.split('git reset --hard ' +
                                              version),
                                  stderr=STDOUT,
                                  close_fds=True).decode('utf-8')
            response = (True, status)
        except Exception as e:  # pragma: no cover
            self.logger.error('checkout failed with error: ' + str(e))
            response = (False, str(e))
        self.logger.info('Status of checkout: ' + str(response))
        self.logger.info('Finished: checkout')
        return response

    def clone(self, repo, user=None, pw=None):
        """ Clone the repository """
        self.logger.info('Starting: clone')
        self.logger.info('repo given: ' + str(repo))
        self.logger.info('user given: ' + str(user))
        status = (True, None)
        try:
            status = self.apply_path(repo)

            # if path already exists, try git checkout to update
            if status[0]:
                self.logger.info('path to clone to: ' + str(status[2]))
                try:
                    check_output(shlex.split('git -C ' +
                                             status[2] +
                                             ' rev-parse'),
                                 stderr=STDOUT,
                                 close_fds=True).decode('utf-8')
                    self.logger.info('path already exists: ' + str(status[2]))
                    self.logger.info('Status of clone: ' + str(status[0]))
                    self.logger.info('Finished: clone')
                    chdir(status[1])
                    return (True, status[1])
                except Exception as e:  # pragma: no cover
                    self.logger.info("repo doesn't exist, attempting to " +
                                     'clone: ' + str(e))
            else:
                self.logger.error('unable to clone')
                return status

            # ensure cloning still works even if ssl is broken
            cmd = 'git config --global http.sslVerify false'
            check_output(shlex.split(cmd), stderr=STDOUT,
                         close_fds=True).decode('utf-8')

            # check if user and pw were supplied, typically for private repos
            if user and pw:
                # only https is supported when using user/pw
                auth_repo = 'https://' + user + ':' + pw + '@'
                repo = auth_repo + repo.split('https://')[-1]

            # clone repo and build tools
            check_output(shlex.split('git clone --recursive ' + repo + ' .'),
                         stderr=STDOUT,
                         close_fds=True).decode('utf-8')

            chdir(status[1])
            status = (True, status[1])
        except Exception as e:  # pragma: no cover
            e_str = str(e)
            # scrub username and password from error message
            if e_str.find('@') >= 0:
                e_str = e_str[:e_str.find('//') + 2] + \
                    e_str[e_str.find('@') + 1:]
            self.logger.error('clone failed with error: ' + e_str)
            status = (False, e_str)
        self.logger.info('Status of clone: ' + str(status))
        self.logger.info('Finished: clone')
        return status

    def available_tools(self, path, version='HEAD', groups=None):
        """
        Return list of possible tools in repo for the given version and branch
        """
        matches = []
        if groups:
            groups = groups.split(',')
        for root, _, filenames in walk(path):
            files = fnmatch.filter(filenames, 'Dockerfile*')
            # append additional identifiers to tools if multiple in same
            # directory
            add_info = len(files) > 1
            for f in files:
                # !! TODO deal with wild/etc.?
                addtl_info = ''
                if add_info:
                    # @ will be delimiter symbol for multi-tools
                    try:
                        addtl_info = '@' + f.split('.')[1]
                    except Exception as e:
                        addtl_info = '@unspecified'
                if groups:
                    if add_info and not addtl_info == '@unspecified':
                        tool_template = addtl_info.split('@')[1] + '.template'
                    else:
                        tool_template = 'vent.template'
                    try:
                        template = Template(template=join(root,
                                                          tool_template))
                        for group in groups:
                            template_groups = template.option('info', 'groups')
                            if (template_groups[0] and
                                    group in template_groups[1]):
                                matches.append((root.split(path)[1] +
                                                addtl_info, version))
                    except Exception as e:  # pragma: no cover
                        self.logger.info('error: ' + str(e))
                else:
                    matches.append((root.split(path)[1] +
                                    addtl_info, version))
        return matches

    @staticmethod
    def tool_matches(tools=None, version='HEAD'):
        """ Get the tools paths and versions that were specified """
        matches = []
        if tools:
            for tool in tools:
                match_version = version
                if tool[1] != '':
                    match_version = tool[1]
                match = ''
                if tool[0].endswith('/'):
                    match = tool[0][:-1]
                elif tool[0] != '.':
                    match = tool[0]
                if not match.startswith('/') and match != '':
                    match = '/'+match
                matches.append((match, match_version))
        return matches

    def start_sections(self,
                       s,
                       files,
                       groups,
                       enabled,
                       branch,
                       version):
        """ Run through sections for prep_start """
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
            self.logger.info('current directory is: ' + str(cwd))
            # images built from registry won't have path
            if s[section]['path'] != '':
                chdir(join(s[section]['path']))

                # TODO commenting out for now, should use update_repo
                #status = self.checkout(branch=branch, version=version)
                status = (True, None)

                self.logger.info(status)
                chdir(cwd)

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
                            overall_dict[setting][opt] = \
                                settings_dict[opt]

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
                        tool_d[c_name][option] = literal_eval(options)
                    except Exception as e:  # pragma: no cover
                        self.logger.info('unable to literal_eval: ' +
                                         str(options))
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
            self.logger.info(status)
            for plugin_section in plugin_sections:
                status = plugin_c.option(plugin_section, 'link_name')
                self.logger.info(status)
                image_status = plugin_c.option(plugin_section, 'image_name')
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
            tool_d[c_name]['labels']['vent'] = Version()
            tool_d[c_name]['labels']['vent.namespace'] = s[section]['namespace']
            tool_d[c_name]['labels']['vent.branch'] = branch
            tool_d[c_name]['labels']['vent.version'] = version
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

    def prep_start(self,
                   repo=None,
                   name=None,
                   groups=None,
                   enabled='yes',
                   branch='master',
                   version='HEAD'):
        """
        Start a set of tools that match the parameters given, if no parameters
        are given, start all installed tools on the master branch at verison
        HEAD that are enabled
        """
        args = locals()
        self.logger.info('Starting: prep_start')
        self.logger.info('Arguments: '+str(args))
        status = (False, None)
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
            files = vent_config.option('main', 'files')
            files = (files[0], expanduser(files[1]))
            s, _ = self.constraint_options(args, options)
            status, tool_d = self.start_sections(s,
                                                 files,
                                                 groups,
                                                 enabled,
                                                 branch,
                                                 version)

            # look out for links to delete because they're defined externally
            links_to_delete = set()
            # check and update links, volumes_from, network_mode
            for container in list(tool_d.keys()):
                if 'links' in tool_d[container]:
                    for link in tool_d[container]['links']:
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
                                self.logger.error("couldn't load external"
                                                  ' settings because: ' +
                                                  str(e))
                                configure_local = True
                                status = False
                        if configure_local:
                            for c in list(tool_d.keys()):
                                if ('tmp_name' in tool_d[c] and
                                        tool_d[c]['tmp_name'] == link):
                                    tool_d[container]['links'][tool_d[c]['name']
                                                               ] = tool_d[container]['links'].pop(link)
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
                                self.logger.warn('Locally running container ' +
                                                 name + ' may be redundant')

            if status:
                status = (True, tool_d)
            else:
                status = (False, tool_d)
        except Exception as e:  # pragma: no cover
            self.logger.error('prep_start failed with error: '+str(e))
            status = (False, e)

        self.logger.info('Status of prep_start: '+str(status[0]))
        self.logger.info('Finished: prep_start')
        return status

    def start_priority_containers(self, groups, group_orders, tool_d):
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
                        s_conts, f_conts = self.start_containers(cont_t[1],
                                                                 tool_d,
                                                                 s_conts,
                                                                 f_conts)
        # start tools that haven't been specified in the vent.cfg, if any
        for group in all_groups:
            if group in group_orders:
                for cont_t in sorted(group_orders[group]):
                    if cont_t[1] not in s_conts:
                        s_conts, f_conts = self.start_containers(cont_t[1],
                                                                 tool_d,
                                                                 s_conts,
                                                                 f_conts)
        return (s_conts, f_conts)

    def start_remaining_containers(self, containers_remaining, tool_d):
        """
        Select remaining containers that didn't have priorities to start
        """
        s_containers = []
        f_containers = []
        for container in containers_remaining:
            s_containers, f_containers = self.start_containers(container,
                                                               tool_d,
                                                               s_containers,
                                                               f_containers)
        return (s_containers, f_containers)

    def start_containers(self,
                         container,
                         tool_d,
                         s_containers,
                         f_containers):
        """ Start container that was passed in and return status """
        # use section to add info to manifest
        section = tool_d[container]['section']
        del tool_d[container]['section']
        manifest = Template(self.manifest)
        try:
            c = self.d_client.containers.get(container)
            c.start()
            s_containers.append(container)
            manifest.set_option(section, 'running', 'yes')
            self.logger.info('started ' + str(container) +
                             ' with ID: ' + str(c.short_id))
        except Exception as err:
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
                                    # !! TODO handle if volumes is a list
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
                        self.logger.info('removed old existing container: ' + str(container))
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
        # save changes made to manifest
        manifest.write_config()
        return s_containers, f_containers
