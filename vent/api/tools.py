import ast
import copy
import getpass
import json
import re
import shlex
from os import chdir
from os import environ
from os.path import expanduser
from os.path import join
from subprocess import check_output
from subprocess import STDOUT

import docker

from vent.api.image import Image
from vent.api.repository import Repository
from vent.helpers.logs import Logger
from vent.helpers.meta import AvailableTools
from vent.helpers.meta import Containers
from vent.helpers.meta import Version
from vent.helpers.paths import PathDirs
from vent.helpers.templates import Template


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
                                   'repo': uri.split('.git')[0]}
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
            else:
                core = False
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
        template = Template(template=self.manifest)
        results, _ = template.constrain_opts(args, [])

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

    def start(self, repo, name, is_tool_d=False):
        if is_tool_d:
            tool_d = repo
        else:
            args = locals()
            del args['self']
            del args['is_tool_d']
            tool_d = {}
            tool_d.update(self._prep_start(**args)[1])
        status = (True, None)
        try:
            # check start priorities (priority of groups alphabetical for now)
            group_orders = {}
            groups = []
            containers_remaining = []
            username = getpass.getuser()

            # remove tools that have the hidden label
            tool_d_copy = copy.deepcopy(tool_d)
            for container in tool_d_copy:
                if 'labels' in tool_d_copy[container] and 'vent.groups' in tool_d_copy[container]['labels']:
                    groups_copy = tool_d_copy[container]['labels']['vent.groups'].split(
                        ',')
                    if 'hidden' in groups_copy:
                        del tool_d[container]

            for container in tool_d:
                containers_remaining.append(container)
                tool_d[container]['network'] = 'vent'
                self.logger.info(
                    "User: '{0}' starting container: {1}".format(username, container))
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

            # check and update links, volumes_from
            for container in list(tool_d.keys()):
                if 'labels' not in tool_d[container] or 'vent.groups' not in tool_d[container]['labels'] or 'core' not in tool_d[container]['labels']['vent.groups']:
                    tool_d[container]['auto_remove'] = True
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
                              'config': {'syslog-address': 'tcp://127.0.0.1:514',
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
        # TODO need to check that section exists
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
                change_networking = False
                links = []
                network_name = ''
                if 'links' in tool_d[container]:
                    for link in tool_d[container]['links']:
                        links.append((link, tool_d[container]['links'][link]))
                    if 'network' in tool_d[container]:
                        network_name = tool_d[container]['network']
                        del tool_d[container]['network']
                    del tool_d[container]['links']
                    change_networking = True
                cont = self.d_client.containers.create(detach=True,
                                                       **tool_d[container])
                cont_id = cont.id
                if change_networking:
                    network_to_attach = self.d_client.networks.list(
                        names=[network_name])
                    if len(network_to_attach) > 0:
                        self.logger.info('Attaching to network: "{0}" with the following links: {1}'.format(
                            network_name, links))
                        network_to_attach[0].connect(cont_id, links=links)
                        self.logger.info('Detaching from network: bridge')
                        network_to_detach = self.d_client.networks.list(names=[
                                                                        'bridge'])
                        network_to_detach[0].disconnect(cont_id)
                cont.start()
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

    def repo_commits(self, repo):
        """ Get the commit IDs for all of the branches of a repository """
        commits = []
        try:
            status = self.path_dirs.apply_path(repo)
            # switch to directory where repo will be cloned to
            if status[0]:
                cwd = status[1]
            else:
                self.logger.error('apply_path failed. Exiting repo_commits with'
                                  ' status: ' + str(status))
                return status

            status = self.repo_branches(repo)
            if status[0]:
                branches = status[1]
                for branch in branches:
                    try:
                        branch_output = check_output(shlex
                                                     .split('git rev-list origin/' +
                                                            branch),
                                                     stderr=STDOUT,
                                                     close_fds=True).decode('utf-8')
                        branch_output = branch_output.split('\n')[:-1]
                        branch_output += ['HEAD']
                        commits.append((branch, branch_output))
                    except Exception as e:  # pragma: no cover
                        self.logger.error('repo_commits failed with error: ' +
                                          str(e) + ' on branch: ' +
                                          str(branch))
                        status = (False, e)
                        return status
            else:
                self.logger.error('repo_branches failed. Exiting repo_commits'
                                  ' with status: ' + str(status))
                return status

            chdir(cwd)
            status = (True, commits)
        except Exception as e:  # pragma: no cover
            self.logger.error('repo_commits failed with error: ' + str(e))
            status = (False, e)

        return status

    def repo_branches(self, repo):
        """ Get the branches of a repository """
        branches = []
        try:
            # switch to directory where repo will be cloned to
            status = self.path_dirs.apply_path(repo)
            if status[0]:
                cwd = status[1]
            else:
                self.logger.error('apply_path failed. Exiting repo_branches'
                                  ' with status ' + str(status))
                return status

            branch_output = check_output(shlex.split('git branch -a'),
                                         stderr=STDOUT,
                                         close_fds=True)
            branch_output = branch_output.split(b'\n')
            for branch in branch_output:
                br = branch.strip()
                if br.startswith(b'*'):
                    br = br[2:]
                if b'/' in br:
                    branches.append(br.rsplit(b'/', 1)[1].decode('utf-8'))
                elif br:
                    branches.append(br.decode('utf-8'))

            branches = list(set(branches))
            for branch in branches:
                try:
                    check_output(shlex.split('git checkout ' + branch),
                                 stderr=STDOUT,
                                 close_fds=True)
                except Exception as e:  # pragma: no cover
                    self.logger.error('repo_branches failed with error: ' +
                                      str(e) + ' on branch: ' + str(branch))
                    status = (False, e)
                    return status

            chdir(cwd)
            status = (True, branches)
        except Exception as e:  # pragma: no cover
            self.logger.error('repo_branches failed with error: ' + str(e))
            status = (False, e)

        return status

    def repo_tools(self, repo, branch, version):
        """ Get available tools for a repository branch at a version """
        try:
            tools = []
            status = self.path_dirs.apply_path(repo)
            # switch to directory where repo will be cloned to
            if status[0]:
                cwd = status[1]
            else:
                self.logger.error('apply_path failed. Exiting repo_tools with'
                                  ' status: ' + str(status))
                return status

            # TODO commenting out for now, should use update_repo
            # status = self.p_helper.checkout(branch=branch, version=version)
            status = (True, None)

            if status[0]:
                path, _, _ = self.path_dirs.get_path(repo)
                tools = AvailableTools(path, version=version)
            else:
                self.logger.error('checkout failed. Exiting repo_tools with'
                                  ' status: ' + str(status))
                return status

            chdir(cwd)
            status = (True, tools)
        except Exception as e:  # pragma: no cover
            self.logger.error('repo_tools failed with error: ' + str(e))
            status = (False, e)

        return status
