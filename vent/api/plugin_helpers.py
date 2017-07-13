import docker
import fnmatch
import requests
import shlex

from ast import literal_eval
from os import chdir, getcwd, walk
from os.path import join
from subprocess import check_output, Popen, PIPE, STDOUT

from vent.api.templates import Template
from vent.helpers.logs import Logger
from vent.helpers.paths import PathDirs
from vent.helpers.meta import Version


class PluginHelper:
    """ Handle helper functions for the Plugin class """
    def __init__(self, **kargs):
        self.d_client = docker.from_env()
        self.path_dirs = PathDirs(**kargs)
        self.manifest = join(self.path_dirs.meta_dir,
                             "plugin_manifest.cfg")
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
        if repo.endswith(".git"):
            repo = repo.split(".git")[0]
        org, name = repo.split("/")[-2:]
        path = self.path_dirs.plugins_dir
        path = join(path, org, name)
        return path, org, name

    def apply_path(self, repo):
        """ Set path to where the repo is and return original path """
        self.logger.info("Starting: apply_path")
        self.logger.info("repo given: " + str(repo))
        try:
            # rewrite repo for consistency
            if repo.endswith(".git"):
                repo = repo.split(".git")[0]

            # get org and repo name and path repo will be cloned to
            org, name = repo.split("/")[-2:]
            path = join(self.path_dirs.plugins_dir, org, name)
            self.logger.info("cloning to path: " + str(path))

            # save current path
            cwd = getcwd()

            # set to new repo path
            self.path_dirs.ensure_dir(path)
            chdir(path)
            status = (True, cwd, path)
        except Exception as e:  # pragma: no cover
            self.logger.error("apply_path failed with error: " + str(e))
            status = (False, str(e))
        self.logger.info("Status of apply_path: " + str(status))
        self.logger.info("Finished: apply_path")
        return status

    def checkout(self, branch="master", version="HEAD"):
        """ Checkout a specific version and branch of a repo """
        self.logger.info("Starting: checkout")
        self.logger.info("branch given: " + str(branch))
        self.logger.info("version given: " + str(version))
        try:
            status = check_output(shlex.split("git checkout " + branch),
                                  stderr=STDOUT,
                                  close_fds=True)
            status = check_output(shlex.split("git pull"),
                                  stderr=STDOUT,
                                  close_fds=True)
            status = check_output(shlex.split("git reset --hard " +
                                              version),
                                  stderr=STDOUT,
                                  close_fds=True)
            response = (True, status)
        except Exception as e:  # pragma: no cover
            self.logger.error("checkout failed with error: " + str(e))
            response = (False, str(e))
        self.logger.info("Status of checkout: " + str(response))
        self.logger.info("Finished: checkout")
        return response

    def clone(self, repo, user=None, pw=None):
        """ Clone the repository """
        self.logger.info("Starting: clone")
        self.logger.info("repo given: " + str(repo))
        self.logger.info("user given: " + str(user))
        status = (True, None)
        try:
            status = self.apply_path(repo)

            # if path already exists, try git checkout to update
            if status[0]:
                self.logger.info("path to clone to: " + str(status[2]))
                try:
                    check_output(shlex.split("git -C " +
                                             status[2] +
                                             " rev-parse"),
                                 stderr=STDOUT,
                                 close_fds=True)
                    self.logger.info("path already exists: " + str(status[2]))
                    self.logger.info("Status of clone: " + str(status[0]))
                    self.logger.info("Finished: clone")
                    chdir(status[1])
                    return (True, status[1])
                except Exception as e:  # pragma: no cover
                    self.logger.info("repo doesn't exist, attempting to " +
                                     "clone: " + str(e))
            else:
                self.logger.error("unable to clone")
                return status

            # ensure cloning still works even if ssl is broken
            cmd = "git config --global http.sslVerify false"
            check_output(shlex.split(cmd), stderr=STDOUT, close_fds=True)

            # check if user and pw were supplied, typically for private repos
            if user and pw:
                # only https is supported when using user/pw
                auth_repo = 'https://' + user + ':' + pw + '@'
                repo = auth_repo + repo.split("https://")[-1]

            # clone repo and build tools
            check_output(shlex.split("git clone --recursive " + repo + " ."),
                         stderr=STDOUT,
                         close_fds=True)

            chdir(status[1])
            status = (True, status[1])
        except Exception as e:  # pragma: no cover
            self.logger.error("clone failed with error: " + str(e))
            status = (False, str(e))
        self.logger.info("Status of clone: " + str(status))
        self.logger.info("Finished: clone")
        return status

    def available_tools(self, path, version="HEAD", groups=None):
        """
        Return list of possible tools in repo for the given version and branch
        """
        matches = []
        if groups:
            groups = groups.split(",")
        for root, _, filenames in walk(path):
            for _ in fnmatch.filter(filenames, 'Dockerfile'):
                # !! TODO deal with wild/etc.?
                if groups:
                    try:
                        template = Template(template=join(root,
                                                          'vent.template'))
                        for group in groups:
                            template_groups = template.option("info", "groups")
                            if (template_groups[0] and
                               group in template_groups[1]):
                                matches.append((root.split(path)[1], version))
                    except Exception as e:  # pragma: no cover
                        self.logger.info("error: " + str(e))
                else:
                    matches.append((root.split(path)[1], version))
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
        for section in s:
            # initialize needed vars
            template_path = join(s[section]['path'], 'vent.template')
            c_name = s[section]['image_name'].replace(':', '-')
            c_name = c_name.replace('/', '-')
            image_name = s[section]['image_name']

            # checkout the right version and branch of the repo
            cwd = getcwd()
            self.logger.info("current directory is: " + str(cwd))
            chdir(join(s[section]['path']))
            status = self.checkout(branch=branch, version=version)
            self.logger.info(status)
            chdir(cwd)

            # set docker settings for container
            vent_template = Template(template_path)
            status = vent_template.section('docker')
            self.logger.info(status)
            tool_d[c_name] = {'image': image_name,
                              'name': c_name}
            if status[0]:
                for option in status[1]:
                    options = option[1]
                    # check for commands to evaluate
                    if '`' in options:
                        cmds = options.split('`')
                        if len(cmds) > 2:
                            i = 1
                            while i < len(cmds):
                                try:
                                    cmds[i] = check_output(shlex.split(cmds[i]),
                                                           stderr=STDOUT,
                                                           close_fds=True).strip()
                                except Exception as e:  # pragma: no cover
                                    self.logger.error("unable to evaluate command specified in vent.template: " + str(e))
                                i += 2
                        options = "".join(cmds)
                    # store options set for docker
                    try:
                        tool_d[c_name][option[0]] = literal_eval(options)
                    except Exception as e:  # pragma: no cover
                        self.logger.error("unable to store the options set for docker: " + str(e))
                        tool_d[c_name][option[0]] = options

            if 'labels' not in tool_d[c_name]:
                tool_d[c_name]['labels'] = {}

            # get the service uri info
            status = vent_template.section('service')
            self.logger.info(status)
            if status[0]:
                for option in status[1]:
                    tool_d[c_name]['labels'][option[0]] = option[1]

            # check for gpu settings
            status = vent_template.section('gpu')
            self.logger.info(status)
            if status[0]:
                for option in status[1]:
                    tool_d[c_name]['labels']['gpu.'+option[0]] = option[1]

            # get temporary name for links, etc.
            plugin_c = Template(template=self.manifest)
            status, plugin_sections = plugin_c.sections()
            self.logger.info(status)
            for plugin_section in plugin_sections:
                status = plugin_c.option(plugin_section, "link_name")
                self.logger.info(status)
                image_status = plugin_c.option(plugin_section, "image_name")
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

            log_config = {'type': 'syslog',
                          'config': {'syslog-address': 'tcp://0.0.0.0:514',
                                     'syslog-facility': 'daemon',
                                     'tag': 'plugin'}}
            if 'groups' in s[section]:
                # add labels for groups
                tool_d[c_name]['labels']['vent.groups'] = s[section]['groups']
                # add restart=always to core containers
                if 'core' in s[section]['groups']:
                    tool_d[c_name]['restart_policy'] = {"Name": "always"}
                # send logs to syslog
                if 'syslog' not in s[section]['groups'] and 'core' in s[section]['groups']:
                    log_config['config']['tag'] = 'core'
                    tool_d[c_name]['log_config'] = log_config
                if 'syslog' not in s[section]['groups']:
                    tool_d[c_name]['log_config'] = log_config
                # mount necessary directories
                if 'files' in s[section]['groups']:
                    if 'volumes' in tool_d[c_name]:
                        tool_d[c_name]['volumes'][self.path_dirs.base_dir[:-1]] = {'bind': '/vent', 'mode': 'ro'}
                    else:
                        tool_d[c_name]['volumes'] = {self.path_dirs.base_dir[:-1]: {'bind': '/vent', 'mode': 'ro'}}
                    if files[0]:
                        tool_d[c_name]['volumes'][files[1]] = {'bind': '/files', 'mode': 'ro'}
            else:
                tool_d[c_name]['log_config'] = log_config

            # add label for priority
            status = vent_template.section('settings')
            self.logger.info(status)
            if status[0]:
                for option in status[1]:
                    if option[0] == 'priority':
                        tool_d[c_name]['labels']['vent.priority'] = option[1]

            # only start tools that have been built
            if s[section]['built'] != 'yes':
                del tool_d[c_name]
        return status, tool_d

    def prep_start(self,
                   repo=None,
                   name=None,
                   groups=None,
                   enabled="yes",
                   branch="master",
                   version="HEAD"):
        """
        Start a set of tools that match the parameters given, if no parameters
        are given, start all installed tools on the master branch at verison
        HEAD that are enabled
        """
        args = locals()
        self.logger.info("Starting: prep_start")
        self.logger.info("Arguments: "+str(args))
        status = (False, None)
        try:
            options = ['name',
                       'namespace',
                       'built',
                       'groups',
                       'path',
                       'image_name',
                       'branch',
                       'version']
            vent_config = Template(template=join(self.path_dirs.meta_dir,
                                                 "vent.cfg"))
            files = vent_config.option('main', 'files')
            s, _ = self.constraint_options(args, options)
            status, tool_d = self.start_sections(s,
                                                 files,
                                                 groups,
                                                 enabled,
                                                 branch,
                                                 version)

            # check and update links, volumes_from, network_mode
            for container in tool_d.keys():
                if 'links' in tool_d[container]:
                    for link in tool_d[container]['links']:
                        for c in tool_d.keys():
                            if ('tmp_name' in tool_d[c] and
                               tool_d[c]['tmp_name'] == link):
                                tool_d[container]['links'][tool_d[c]['name']] = tool_d[container]['links'].pop(link)
                if 'volumes_from' in tool_d[container]:
                    tmp_volumes_from = tool_d[container]['volumes_from']
                    tool_d[container]['volumes_from'] = []
                    for volumes_from in list(tmp_volumes_from):
                        for c in tool_d.keys():
                            if ('tmp_name' in tool_d[c] and
                               tool_d[c]['tmp_name'] == volumes_from):
                                tool_d[container]['volumes_from'].append(tool_d[c]['name'])
                                tmp_volumes_from.remove(volumes_from)
                    tool_d[container]['volumes_from'] += tmp_volumes_from
                if 'network_mode' in tool_d[container]:
                    if tool_d[container]['network_mode'].startswith('container:'):
                        network_c_name = tool_d[container]['network_mode'].split('container:')[1]
                        for c in tool_d.keys():
                            if ('tmp_name' in tool_d[c] and
                               tool_d[c]['tmp_name'] == network_c_name):
                                tool_d[container]['network_mode'] = 'container:' + tool_d[c]['name']

            # remove tmp_names
            for c in tool_d.keys():
                if 'tmp_name' in tool_d[c]:
                    del tool_d[c]['tmp_name']

            # remove containers that shouldn't be started
            for c in tool_d.keys():
                if 'start' in tool_d[c] and not tool_d[c]['start']:
                    del tool_d[c]
            status = (True, tool_d)
        except Exception as e:  # pragma: no cover
            self.logger.error("prep_start failed with error: "+str(e))
            status = (False, e)

        self.logger.info("Status of prep_start: "+str(status[0]))
        self.logger.info("Finished: prep_start")
        return status

    def start_priority_containers(self, groups, group_orders, tool_d):
        """ Select containers based on priorities to start """
        groups = sorted(set(groups))
        s_conts = []
        f_conts = []
        for group in groups:
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
        try:
            c = self.d_client.containers.get(container)
            c.start()
            s_containers.append(container)
            self.logger.info("started " + str(container) +
                             " with ID: " + str(c.short_id))
        except Exception as err:  # pragma: no cover
            try:
                gpu = 'gpu.enabled'
                failed = False
                if (gpu in tool_d[container]['labels'] and
                   tool_d[container]['labels'][gpu] == 'yes'):
                    # TODO check for availability of gpu(s),
                    #      otherwise queue it up until it's
                    #      available
                    # !! TODO check for device settings in vent.template
                    route = Popen(('/sbin/ip', 'route'), stdout=PIPE)
                    h = check_output(('awk', '/default/ {print $3}'),
                                     stdin=route.stdout)
                    route.wait()
                    host = h.strip()
                    nd_url = 'http://' + host + ':3476/v1.0/docker/cli'
                    params = {'vol': 'nvidia_driver'}

                    r = requests.get(nd_url, params=params)
                    if r.status_code == 200:
                        options = r.text.split()
                        for option in options:
                            if option.startswith('--volume-driver='):
                                tool_d[container]['volume_driver'] = option.split("=", 1)[1]
                            elif option.startswith('--volume='):
                                vol = option.split("=", 1)[1].split(":")
                                if 'volumes' in tool_d[container]:
                                    # !! TODO handle if volumes is a list
                                    tool_d[container]['volumes'][vol[0]] = {'bind': vol[1],
                                                                            'mode': vol[2]}
                                else:
                                    tool_d[container]['volumes'] = {vol[0]:
                                                                    {'bind': vol[1],
                                                                     'mode': vol[2]}}
                            elif option.startswith('--device='):
                                dev = option.split("=", 1)[1]
                                if 'devices' in tool_d[container]:
                                    tool_d[container]['devices'].append(dev +
                                                                        ":" +
                                                                        dev +
                                                                        ":rwm")
                                else:
                                    tool_d[container]['devices'] = [dev + ":" + dev + ":rwm"]
                            else:
                                self.logger.error("Unable to parse " +
                                                  "nvidia-docker option: " +
                                                  str(option))
                    else:
                        failed = True
                        f_containers.append(container)
                        self.logger.error("failed to start " + str(container) +
                                          " because nvidia-docker-plugin " +
                                          "failed with: " + str(r.status_code))
                if not failed:
                    cont_id = self.d_client.containers.run(detach=True,
                                                           **tool_d[container])
                    s_containers.append(container)
                    self.logger.info("started " + str(container) +
                                     " with ID: " + str(cont_id))
            except Exception as e:  # pragma: no cover
                f_containers.append(container)
                self.logger.error("failed to start " + str(container) +
                                  " because: " + str(e))
        return s_containers, f_containers
