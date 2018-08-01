import ast
import copy
import getpass
import json
import os
import re
import shutil
import tempfile
import urllib.request

import docker
import queue
import yaml

from vent.api.plugins import Plugin
from vent.api.templates import Template
from vent.helpers.logs import Logger
from vent.helpers.meta import Containers
from vent.helpers.meta import Dependencies
from vent.helpers.meta import Images
from vent.helpers.meta import ParsedSections
from vent.helpers.meta import Timestamp
from vent.helpers.paths import PathDirs


class Action:
    """ Handle actions in menu """

    def __init__(self, **kargs):
        self.plugin = Plugin(**kargs)
        self.d_client = self.plugin.d_client
        self.vent_config = self.plugin.path_dirs.cfg_file
        self.startup_file = self.plugin.path_dirs.startup_file
        self.p_helper = self.plugin.p_helper
        self.queue = queue.Queue()
        self.logger = Logger(__name__)

    def add(self, repo, tools=None, overrides=None, version='HEAD', image=None,
            branch='master', build=True, user=None, pw=None, groups=None,
            version_alias=None, wild=None, remove_old=True, disable_old=True,
            update_repo=None):
        """ Add a new set of tool(s) """
        self.logger.info('Starting: add')
        status = (True, None)
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
                    prev_installed, _ = self.p_helper. \
                        constraint_options(constraints, [])
                    # don't reinstall
                    if prev_installed:
                        tools.remove(tool)
                    i -= 1
            if tools is None or len(tools) > 0:
                is_core = repo == 'https://github.com/cyberreboot/vent'
                status = self.plugin.add(repo,
                                         tools=tools,
                                         overrides=overrides,
                                         version=version,
                                         image=image,
                                         branch=branch,
                                         build=build,
                                         user=user,
                                         pw=pw,
                                         groups=groups,
                                         version_alias=version_alias,
                                         wild=wild,
                                         remove_old=remove_old,
                                         disable_old=disable_old,
                                         core=is_core,
                                         update_repo=update_repo)
            else:
                self.logger.info('no new tools to add, exiting')
                status = (True, 'previously installed')
        except Exception as e:  # pragma: no cover
            self.logger.error('add failed with error: ' + str(e))
            status = (False, str(e))
        self.logger.info('Status of add: ' + str(status[0]))
        self.logger.info('Finished: add')
        return status

    def add_image(self,
                  image,
                  link_name,
                  tag=None,
                  registry=None,
                  groups=None):
        """ Add a new image from a Docker registry """
        self.logger.info('Starting: add image')
        status = (True, None)
        try:
            status = self.plugin.add_image(image,
                                           link_name,
                                           tag=tag,
                                           registry=registry,
                                           groups=groups)
        except Exception as e:  # pragma: no cover
            self.logger.error('add image failed with error: ' + str(e))
            status = (False, str(e))
        self.logger.info('Status of add image: ' + str(status[0]))
        self.logger.info('Finished: add image')
        return status

    def remove(self, repo=None, namespace=None, name=None, groups=None,
               enabled='yes', branch='master', version='HEAD', built='yes'):
        """ Remove tools or a repo """
        self.logger.info('Starting: remove')
        status = (True, None)
        try:
            # don't want to include groups because constrained_sections will
            # return everything that matches that group, possibly removing
            # things we don't want to remove
            if groups:
                groups = None
            status = self.plugin.remove(name=name,
                                        repo=repo,
                                        namespace=namespace,
                                        groups=groups,
                                        enabled=enabled,
                                        branch=branch,
                                        version=version,
                                        built=built)

            # remove any dependant/child of the current container
            child_name = str(name) + '_child'
            for container in self.d_client.containers.list():
                if ('vent.groups' in container.attrs['Config']['Labels'] and
                        child_name in container.attrs['Config']['Labels']['vent.groups']):
                    container.remove(force=True)

        except Exception as e:  # pragma: no cover
            self.logger.error('remove failed with error: ' + str(e))
            status = (False, e)
        self.logger.info('Status of remove: ' + str(status[0]))
        self.logger.info('Finished: remove')
        return status

    def prep_start(self,
                   repo=None,
                   name=None,
                   groups=None,
                   enabled='yes',
                   branch='master',
                   version='HEAD'):
        """ Prep a bunch of containers to be started to they can be ordered """
        args = locals()
        del args['self']
        self.logger.info('Starting: prep_start')
        status = self.p_helper.prep_start(**args)
        self.logger.info('Status of prep_start: ' + str(status[0]))
        self.logger.info('Finished: prep_start')
        return status

    def start(self, tool_d):
        """
        Start a set of tools that match the parameters given, if no parameters
        are given, start all installed tools on the master branch at verison
        HEAD that are enabled
        """
        self.logger.info('Starting: start')
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

            self.logger.info('group orders: ' + str(group_orders))
            self.logger.info('containers remaining: ' +
                             str(containers_remaining))
            # start containers based on priorities
            p_results = self.p_helper.start_priority_containers(groups,
                                                                group_orders,
                                                                tool_d)

            # start the rest of the containers that didn't have any priorities
            r_results = self.p_helper.start_remaining_containers(
                containers_remaining, tool_d)
            results = (p_results[0] + r_results[0],
                       p_results[1] + r_results[1])

            if len(results[1]) > 0:
                status = (False, results)
            else:
                status = (True, results)
        except Exception as e:  # pragma: no cover
            self.logger.error('start failed with error: ' + str(e))
            status = (False, str(e))

        self.logger.info('Status of start: ' + str(status[0]))
        self.logger.info('Finished: start')
        self.queue.put(status)
        return status

    def update(self,
               repo=None,
               name=None,
               groups=None,
               enabled='yes',
               branch='master',
               version='HEAD',
               new_version='HEAD'):
        """
        Update a set of tools that match the parameters given, if no parameters
        are given, updated all installed tools on the master branch at verison
        HEAD that are enabled
        """
        args = locals()
        del args['new_version']
        self.logger.info('Starting: update')
        self.logger.info(args)
        status = (True, None)
        try:
            options = ['path', 'image_name', 'image_id', 'running',
                       'multi_tool', 'name', 'link_name']
            s, template = self.p_helper.constraint_options(args, options)

            # get existing containers and images and states
            running_containers = Containers()
            built_images = Images()
            self.logger.info('running docker containers: ' +
                             str(running_containers))
            self.logger.info('built docker images: ' + str(built_images))

            # if repo, pull and build
            # if registry image, pull
            for section in s:
                try:
                    cwd = os.getcwd()
                    self.logger.info('current working directory: ' + str(cwd))
                    os.chdir(s[section]['path'])
                    c_status = self.p_helper.checkout(branch=branch,
                                                      version=new_version)
                    self.logger.info(c_status)
                    os.chdir(cwd)
                    self.plugin.builder(template,
                                        s[section]['path'],
                                        s[section]['image_name'],
                                        section,
                                        build=True,
                                        branch=branch,
                                        version=new_version)

                    # exit if no changes were made
                    if (template.option(section, 'image_id')[1] ==
                            s[section]['image_id']):
                        self.logger.info('No changes made through update')
                        self.logger.info('Status of update: True')
                        self.logger.info('Finished: update')
                        return (True, 'no changes made')

                    # update any new vent.template settings that may have been set
                    vent_template_path = s[section]['path']
                    if s[section]['multi_tool'] == 'yes':
                        name = s[section]['name']
                        if name == 'unspecified':
                            name = 'vent'
                        vent_template_path = os.path.join(vent_template_path,
                                                          name+'.template')
                    else:
                        vent_template_path = os.path.join(vent_template_path,
                                                          'vent.template')

                    if os.path.exists(vent_template_path):
                        vent_template = Template(vent_template_path)
                        for setting in vent_template.sections()[1]:
                            # perserve customizations
                            prev_dict = template.option(section, setting)
                            if prev_dict[0]:
                                prev_dict = json.loads(prev_dict[1])
                            else:
                                prev_dict = {}
                            self.logger.info('old settings for option ' +
                                             setting + ' are: ' +
                                             str(prev_dict))
                            opt_vals = vent_template.section(setting)[1]
                            self.logger.info('new settings:')
                            for opt_val in opt_vals:
                                name = opt_val[0]
                                val = opt_val[1]
                                if name == 'name':
                                    name = 'link_name'
                                self.logger.info(name + ' = ' + val)
                                # set groups and link_name individually
                                if name in ['link_name', 'groups']:
                                    template.set_option(section, name, val)
                                if name not in prev_dict:
                                    prev_dict.update({name: val})
                                # check to see if a list variable has been updated
                                elif prev_dict[name] != val:
                                    prev_dict.update({name: val})
                            template.set_option(section, setting,
                                                json.dumps(prev_dict))

                    # reset containers that may be affected by changes,
                    # including dependencies
                    tool_d = {}
                    if (s[section]['running'] == 'yes'):
                        # find dependencies that will need to be restarted
                        # once this tool is reset
                        prev_dependencies = []
                        for t_sect in template.sections()[1]:
                            self.logger.info('Testing check tool: ' + t_sect)
                            t_name = template.option(t_sect, 'name')[1]
                            t_branch = template.option(t_sect, 'branch')[1]
                            t_version = template.option(t_sect, 'version')[1]
                            t_identifier = {'name': t_name,
                                            'branch': t_branch,
                                            'version': t_version}
                            # don't worry about dealing with tool if it's not
                            # running
                            running = template.option(t_sect, 'running')
                            if (not running[0] or running[1] != 'yes' or
                                    t_name == s[section]['name']):
                                self.logger.info('tool not dependency,' +
                                                 ' skipping to next')
                                continue
                            options = template.options(t_sect)[1]
                            self.logger.info(options)
                            if 'docker' in options:
                                d_settings = json.loads(template.option(t_sect,
                                                                        'docker')[1])
                                self.logger.info(d_settings)
                                if 'links' in d_settings:
                                    for link in json.loads(d_settings['links']):
                                        if link == s[section]['link_name']:
                                            prev_dependencies.append(
                                                t_identifier)

                        # remove old containers, start new
                        self.logger.info('running tools to be restarted: ' +
                                         str(prev_dependencies))
                        for tool in prev_dependencies:
                            self.clean(**tool)
                            tool_d.update(self.prep_start(**tool)[1])
                        # clean tool before new manifest entry to get rid of
                        # old tool
                        self.clean(name=s[section]['name'], branch=branch,
                                   version=version)
                    # finish writing new manifest entry, including creating new
                    # section name and deleting old image
                    template.set_option(section, 'version', new_version)
                    template.set_option(section, 'running',
                                        s[section]['running'])
                    old_image = template.option(section, 'image_name')[1]
                    self.logger.info('Testing old....   ' + old_image)
                    new_image = old_image.rsplit(':', 1)[0]+':'+new_version
                    template.set_option(section, 'image_name', new_image)
                    # create new section
                    new_section = section.rsplit(':', 1)[0]+':'+new_version
                    template.add_section(new_section)
                    old_section = template.section(section)[1]
                    for val in old_section:
                        template.set_option(new_section, val[0], val[1])
                    # remove old section and image
                    self.d_client.images.remove(old_image, force=True)
                    template.del_section(section)
                    template.write_config()
                    # now we can start new tool with correct info in manifest
                    tool_d.update(self.prep_start(name=s[section]['name'],
                                                  branch=branch,
                                                  version=new_version)[1])
                    self.start(tool_d)
                except Exception as e:  # pragma: no cover
                    self.logger.error('unable to update: ' + str(section) +
                                      ' because: ' + str(e))
        except Exception as e:  # pragma: no cover
            self.logger.error('update failed with error: ' + str(e))
            status = (False, e)

        self.logger.info('Status of update: ' + str(status[0]))
        self.logger.info('Finished: update')
        return status

    def stop(self,
             repo=None,
             name=None,
             groups=None,
             enabled='yes',
             branch='master',
             version='HEAD'):
        """
        Stop a set of tools that match the parameters given, if no parameters
        are given, stop all installed tools on the master branch at verison
        HEAD that are enabled
        """
        args = locals()
        self.logger.info('Starting: stop')
        self.logger.info(args)
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
            s, _ = self.p_helper.constraint_options(args, options)
            self.logger.info(s)
            for section in s:
                container_name = s[section]['image_name'].replace(':', '-')
                container_name = container_name.replace('/', '-')
                try:
                    container = self.d_client.containers.get(container_name)
                    container.stop()
                    self.logger.info('stopped ' + str(container_name))
                except Exception as e:  # pragma: no cover
                    self.logger.error('failed to stop ' + str(container_name) +
                                      ' because: ' + str(e))
        except Exception as e:  # pragma: no cover
            self.logger.error('stop failed with error: ' + str(e))
            status = (False, e)
        self.logger.info('Status of stop: ' + str(status[0]))
        self.logger.info('Finished: stop')
        return status

    def clean(self,
              repo=None,
              name=None,
              groups=None,
              enabled='yes',
              branch='master',
              version='HEAD'):
        """
        Clean (stop and remove) a set of tools that match the parameters given,
        if no parameters are given, clean all installed tools on the master
        branch at verison HEAD that are enabled
        """
        args = locals()
        self.logger.info('Starting: clean')
        self.logger.info(args)
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
            s, manifest = self.p_helper.constraint_options(args, options)
            self.logger.info(s)
            for section in s:
                container_name = s[section]['image_name'].replace(':', '-')
                container_name = container_name.replace('/', '-')
                instance_num = re.search(r'\d+$', s[section]['name'])
                if instance_num:
                    container_name += instance_num.group()
                try:
                    container = self.d_client.containers.get(container_name)
                    container.remove(force=True)
                    manifest.set_option(section, 'running', 'no')
                    self.logger.info('cleaned ' + str(container_name))
                except Exception as e:  # pragma: no cover
                    self.logger.error('failed to clean ' +
                                      str(container_name) +
                                      ' because: ' + str(e))
            manifest.write_config()
        except Exception as e:  # pragma: no cover
            self.logger.error('clean failed with error: ' + str(e))
            status = (False, e)
        self.logger.info('Status of clean: ' + str(status[0]))
        self.logger.info('Finished: clean')
        return status

    def build(self,
              repo=None,
              name=None,
              groups=None,
              enabled='yes',
              branch='master',
              version='HEAD'):
        """ Build a set of tools that match the parameters given """
        args = locals()
        self.logger.info('Starting: build')
        self.logger.info(args)
        status = (True, None)
        try:
            options = ['image_name', 'path']
            s, template = self.p_helper.constraint_options(args, options)
            self.logger.info(s)
            for section in s:
                self.logger.info('Building ' + str(section) + ' ...')
                template = self.plugin.builder(template,
                                               s[section]['path'],
                                               s[section]['image_name'],
                                               section,
                                               build=True,
                                               branch=branch,
                                               version=version)
            if len(s) > 0:
                template.write_config()
        except Exception as e:  # pragma: no cover
            self.logger.error('build failed with error: ' + str(e))
            status = (False, e)
        self.logger.info('Status of build: ' + str(status[0]))
        self.logger.info('Finished: build')
        return status

    def backup(self):
        """
        Saves the configuration information of the current running vent
        instance to be used for restoring at a later time
        """
        self.logger.info('Starting: backup')
        status = (True, None)
        # initialize all needed variables (names for backup files, etc.)
        backup_name = ('.vent-backup-' + '-'.join(Timestamp().split(' ')))
        backup_dir = os.path.join(os.path.expanduser('~'), backup_name)
        backup_manifest = os.path.join(backup_dir, 'backup_manifest.cfg')
        backup_vcfg = os.path.join(backup_dir, 'backup_vcfg.cfg')
        manifest = self.p_helper.manifest

        # create new backup directory
        try:
            os.mkdir(backup_dir)
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
        self.logger.info('Status of backup: ' + str(status[0]))
        self.logger.info('Finished: backup')
        return status

    def restore(self, backup_dir):
        """
        Restores a vent configuration from a previously backed up version
        """
        self.logger.info('Starting: restore')
        self.logger.info('Directory given: ' + backup_dir)
        status = (True, None)
        # initialize needed variables
        added_str = ''
        failed_str = ''
        template_options = ['service', 'settings', 'docker', 'info', 'gpu']
        backup_dir = os.path.join(os.path.expanduser('~'), backup_dir)
        if os.path.exists(backup_dir):
            # restore backed up manifest file
            backup_manifest = os.path.join(backup_dir, 'backup_manifest.cfg')
            bmanifest = Template(backup_manifest)
            tools = bmanifest.sections()[1]
            for tool in tools:
                constraints = {}
                options = bmanifest.options(tool)[1]
                for vals in bmanifest.section(tool)[1]:
                    constraints[vals[0]] = vals[1]
                backedup_tool = bmanifest.constrained_sections(constraints,
                                                               options)
                t_info = backedup_tool[tool]
                if t_info['type'] == 'repository':
                    # for purposes of the add method (only adding a sepcific
                    # tool each time, and the add method expects a tuple with
                    # relative path to tool for that)
                    rel_path = t_info['path'].split(t_info['namespace'])[-1]
                    t_tuple = (rel_path, '')
                    if t_info['built'] == 'yes':
                        build = True
                    else:
                        build = False
                    if 'groups' in t_info and 'core' in t_info['groups']:
                        core = True
                    else:
                        core = False
                    add_kargs = {'tools': [t_tuple],
                                 'branch': t_info['branch'],
                                 'version': t_info['version'],
                                 'build': build,
                                 'core': core}
                    try:
                        self.plugin.add(t_info['repo'], **add_kargs)
                        # update manifest with customizations
                        new_manifest = Template(self.plugin.manifest)
                        for option in template_options:
                            if option in t_info:
                                new_manifest.set_option(tool, option,
                                                        t_info[option])
                        new_manifest.write_config()
                        added_str += 'Restored: ' + t_info['name'] + '\n'
                    except Exception as e:  # pragma: no cover
                        self.logger.error('Problem restoring tool ' + t_info['name'] +
                                          ' because ' + str(e))
                        failed_str += 'Failed: ' + t_info['name'] + '\n'
                elif t_info['type'] == 'registry':
                    add_kargs = {'image': t_info['pull_name'],
                                 'link_name': t_info['link_name'],
                                 'tag': t_info['version'],
                                 'registry': t_info['repo'].split('/')[0],
                                 'groups': t_info['groups']}
                    try:
                        self.add_image(**add_kargs)
                        # update manifest with customizations
                        new_manifest = Template(self.plugin.manifest)
                        for option in template_options:
                            if option in t_info:
                                new_manifest.set_option(tool, option,
                                                        t_info[option])
                        new_manifest.write_config()
                        added_str += 'Restored: ' + t_info['name'] + '\n'
                    except Exception as e:  # pragma: no cover
                        self.logger.error('Problem restoring tool ' + t_info['name'] +
                                          ' because ' + str(e))
                        failed_str += 'Failed: ' + t_info['name'] + '\n'

            # restore backed up vent.cfg file
            backup_vcfg = os.path.join(backup_dir, 'backup_vcfg.cfg')
            bvcfg = Template(backup_vcfg)
            try:
                vcfg_template = Template(self.vent_config)
                for section in bvcfg.sections()[1]:
                    for vals in bvcfg.section(section)[1]:
                        # add section to new template in case it doesn't exist
                        try:
                            vcfg_template.add_section(section)
                        except Exception as e:  # pragma: no cover
                            # okay if error because of already existing
                            self.logger.error('Failed adding section ' +
                                              str(e))
                        vcfg_template.set_option(vals[0], vals[1])
                vcfg_template.write_config()
                added_str += 'Restored: vent configuration file'
            except Exception as e:  # pragma: no cover
                self.logger.error("Couldn't restore vent.cfg"
                                  'because: ' + str(e))
                failed_str += 'Failed: vent configuration file'
        else:
            status = (False, 'No backup directory found at specified path')
        if status[0]:
            status = (True, failed_str + added_str)
        self.logger.info('Status of restore: ' + str(status[0]))
        self.logger.info('Finished: restore')
        return status

    @staticmethod
    def configure():
        # TODO
        # tools, core, etc.
        return

    @staticmethod
    def upgrade():
        # TODO
        return

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
            cwd = os.getcwd()
            if cwd.startswith(os.path.join(os.path.expanduser('~'), '.vent')):
                os.chdir(os.path.expanduser('~'))
            shutil.rmtree(os.path.join(os.path.expanduser('~'), '.vent'))
        except Exception as e:  # pragma: no cover
            error_message += 'Error deleting Vent data: ' + str(e) + '\n'

        if error_message:
            status = (False, error_message)

        return status

    def logs(self, c_type=None, grep_list=None):
        """ Generically filter logs stored in log containers """
        def get_logs(logs, log_entries):
            try:
                for log in logs:
                    if str(container.name) in log_entries:
                        log_entries[str(container.name)].append(log)
                    else:
                        log_entries[str(container.name)] = [log]
            except Exception as e:  # pragma: no cover
                self.logger.error('Unable to get logs for ' +
                                  str(container.name) +
                                  ' because: ' + str(e))
            return log_entries

        self.logger.info('Starting: logs')
        status = (True, None)
        log_entries = {}
        containers = self.d_client.containers.list(all=True,
                                                   filters={'label': 'vent'})
        self.logger.info('containers found: ' + str(containers))
        comp_c = containers
        if c_type:
            try:
                comp_c = [c for c in containers
                          if (c_type
                              in c.attrs['Config']['Labels']['vent.groups'])]
            except Exception as e:  # pragma: no cover
                self.logger.error('Unable to limit containers by: ' +
                                  str(c_type) + ' because: ' +
                                  str(e))

        if grep_list:
            for expression in grep_list:
                for container in comp_c:
                    try:
                        # 'logs' stores each line containing the expression
                        logs = [log for log in container.logs().split('\n')
                                if expression in log]
                        log_entries = get_logs(logs, log_entries)
                    except Exception as e:  # pragma: no cover
                        self.logger.info('Unable to get logs for ' +
                                         str(container) +
                                         ' because: ' + str(e))
        else:
            for container in comp_c:
                try:
                    logs = container.logs().split('\n')
                    log_entries = get_logs(logs, log_entries)
                except Exception as e:  # pragma: no cover
                    self.logger.info('Unabled to get logs for ' +
                                     str(container) +
                                     ' because: ' + str(e))

        status = (True, log_entries)
        self.logger.info('Status of logs: ' + str(status[0]))
        self.logger.info('Finished: logs')
        return status

    @staticmethod
    def help():
        # TODO
        return

    def inventory(self, choices=None):
        """ Return a dictionary of the inventory items and status """
        self.logger.info('Starting: inventory')
        status = (True, None)
        self.logger.info('choices specified: ' + str(choices))
        if not choices:
            return (False, 'No choices made')
        try:
            # choices: repos, core, tools, images, built, running, enabled
            items = {'repos': [], 'core': {}, 'tools': {}, 'images': {},
                     'built': {}, 'running': {}, 'enabled': {}}

            tools = self.plugin.list_tools()
            self.logger.info('found tools: ' + str(tools))
            for choice in choices:
                for tool in tools:
                    try:
                        if choice == 'repos':
                            if 'repo' in tool:
                                if (tool['repo'] and
                                        tool['repo'] not in items[choice]):
                                    items[choice].append(tool['repo'])
                        elif choice == 'core':
                            if 'groups' in tool and 'core' in tool['groups']:
                                items[choice][tool['section']] = tool['name']
                        elif choice == 'tools':
                            if (('groups' in tool and
                                 'core' not in tool['groups']) or
                                    'groups' not in tool):
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
                                # cores need to not have version, plugins need
                                # to have version in order to match
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
                        self.logger.error('unable to grab info about tool: ' +
                                          str(tool) + ' because: ' + str(e))
            status = (True, items)
        except Exception as e:  # pragma: no cover
            self.logger.error('inventory failed with error: ' + str(e))
            status = (False, str(e))
        self.logger.info('Status of inventory: ' + str(status[0]))
        self.logger.info('Finished: inventory')
        return status

    def get_configure(self,
                      repo=None,
                      name=None,
                      groups=None,
                      enabled='yes',
                      branch='master',
                      version='HEAD',
                      main_cfg=False):
        """
        Get the vent.template settings for a given tool by looking at the
        plugin_manifest
        """
        self.logger.info('Starting: get_configure')
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
            tools = self.p_helper.constraint_options(constraints, options)[0]
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
        self.logger.info('Status of get_configure: ' + str(status[0]))
        self.logger.info('Finished: get_configure')
        return status

    def save_configure(self,
                       repo=None,
                       name=None,
                       groups=None,
                       enabled='yes',
                       branch='master',
                       version='HEAD',
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

        self.logger.info('Starting: save_configure')
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
                    result = self.p_helper.constraint_options(t_identifier, [])
                    tools = result[0]
                    manifest = result[1]
                    tool = list(tools.keys())[0]
                else:
                    options = ['path', 'multi_tool', 'name']
                    self.logger.info(constraints)
                    tools, manifest = self.p_helper. \
                        constraint_options(constraints, options)
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
                            template_path = os.path.join(tools[tool]['path'],
                                                         name+'.template')
                        else:
                            template_path = os.path.join(tools[tool]['path'],
                                                         'vent.template')
                    else:
                        status = (False, "Couldn't save configuration")
            else:
                fd, template_path = tempfile.mkstemp(suffix='.template')
                options = ['namespace']
                constraints.update({'type': 'registry'})
                del constraints['branch']
                tools, manifest = self.p_helper.constraint_options(constraints,
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
                    os.close(fd)
                    os.remove(template_path)
                except Exception as e:  # pragma: no cover
                    self.logger.error('save_configure error: ' + str(e))
        else:
            with open(self.vent_config, 'w') as f:
                f.write(config_val)
        self.logger.info('Status of save_configure: ' + str(status[0]))
        self.logger.info('Finished: save_configure')
        return status

    def restart_tools(self,
                      repo=None,
                      name=None,
                      groups=None,
                      enabled='yes',
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
                result = self.p_helper.constraint_options(t_identifier,
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

    def disable(self,
                repo=None,
                name=None,
                groups=None,
                enabled='yes',
                branch='master',
                version='HEAD'):
        """ Take an enabled tool and disable it """
        self.logger.info('Starting: disable')
        constraints = locals()
        status = (True, None)
        try:
            tools, manifest = self.p_helper.constraint_options(constraints, [])
            for tool in tools:
                manifest.set_option(tool, 'enabled', 'no')
                manifest.write_config()
                tool_name = manifest.option(tool, 'name')[1]
                self.logger.info('Disabled tool: ' + tool_name)
        except Exception as e:  # pragma: no cover
            self.logger.error('Troubling disabling tool because: ' + str(e))
            status = (False, str(e))
        self.logger.info('Status of disable: ' + str(status[0]))
        self.logger.info('Finished: disable')
        return status

    def enable(self,
               repo=None,
               name=None,
               groups=None,
               enabled='no',
               branch='master',
               version='HEAD'):
        """ Take a disabled tool and enable it """
        self.logger.info('Starting: enable')
        constraints = locals()
        status = (True, None)
        try:
            tools, manifest = self.p_helper.constraint_options(constraints, [])
            for tool in tools:
                manifest.set_option(tool, 'enabled', 'yes')
                manifest.write_config()
                tool_name = manifest.option(tool, 'name')[1]
                self.logger.info('Enabled tool: ' + tool_name)
        except Exception as e:  # pragma: no cover
            self.logger.error('Troubling enabling tool because: ' + str(e))
            status = (False, str(e))
        self.logger.info('Status of enable: ' + str(status[0]))
        self.logger.info('Finished: enable')
        return status

    def startup(self):
        """
        Automatically detect if a startup file is specified and stand up a vent
        host with all necessary tools based on the specifications in that file
        """
        self.logger.info('Starting: startup')
        status = (True, None)
        try:
            s_dict = {}
            if os.path.exists(self.startup_file):
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
                self.logger.info('applying vent.cfg configurations')
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
            for repo in s_dict_c:
                self.p_helper.clone(repo)
                repo_path, org, r_name = self.p_helper.get_path(repo)
                available_tools = self.p_helper.available_tools(repo_path)
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
                    self.add(repo, branch=t_branch, version=t_version,
                             tools=add_tools, build=build_tool, image=t_image)
                    manifest = Template(self.plugin.manifest)
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
            self.logger.error('startup failed with error ' + str(e))
            status = (False, str(e))
        self.logger.info('startup finished with status ' + str(status[0]))
        self.logger.info('Finished: startup')
        return status

    def tool_status_checker(self, tool_name):
        """
        Reads from the plugin manifest. Checks to see if:
        1. plugin manifest exists
        2. if the given tool is built
        3. if the given tool is running

        Args:
            tool_name(str): tool name. Checks plugin manifest option `name`

        Returns:
            A tuple of success status, and a tuple containing:
            bool describing if plugin manifest exists,
            bool describing if tool is built,
            bool describing if tool is running.
            eg: (True, (True, True, False))
        """
        status = (True, None)
        try:
            self.logger.info('Start: tool_status_checker')
            manifest = Template(self.p_helper.manifest)
            for section in manifest.sections()[1]:
                if manifest.option(section, 'name')[1] == tool_name:
                    status_tup = (True, manifest.option(section, 'built')[1],
                                  manifest.option(section, 'running')[1])
                    status = (True, status_tup)
                    break

        except Exception as e:  # pragma: no cover
            self.logger.error('Failed to check tool status: ' + str(e))
            status = (False, str(e))

        self.logger.info('Status of tool status: ' + str(status[0]))
        self.logger.info('Finished: tool status')
        return status

    def tool_status_output(self, tool_name):
        """
        Function uses tool_status_checker to see tool status. Using that, it
        will return messages to output

        Args:
            tool_name(str): tool name

        Returns:
            A tuple of success status and a string to display
        """
        status = (True, None)
        try:
            self.logger.info('Start: tool_status_output')
            output = ''
            tool_status = self.tool_status_checker(tool_name)[1]

            # this means plugin_manifest doesn't exist because tool_status isn't
            # a tuple but an error message. AKA template couldnt find plugin
            # manifest as it doesn't exist
            if not isinstance(tool_status, tuple):
                output = 'Please install core tools'

            # this means the core tool isn't built
            elif tool_status[1] == 'no':
                output = 'Please build core tool ' + str(tool_name)

            # this means the core tool isn't running
            elif tool_status[2] == 'no':
                output = 'Please start core tool ' + str(tool_name)
            status = (True, output)
        except Exception as e:  # pragma: no cover
            status = (False, e)
            self.logger.info('Error: ' + str(e))

        self.logger.info('Status of tool_status_output: ' + str(status[0]))
        self.logger.info('Finished: tool_status_output')
        return status

    @staticmethod
    def post_request(url, json_data):
        """
        Send a application/json post request to the given url

        Args:
            url(str): url to send the data to. Eg: http://0.0.0.0:37728
            json_data(dict): json obj with data that will be sent to specified
                             url
            action(str): what is being done. Eg: 'starting a container'

        Returns:
            A tuple of success status and whatever the url is supposed to give
            after a POST request or a failure message
        """
        try:
            # evaluate the data and dump it into something json likes
            data = ast.literal_eval(str(json_data))
            data = json.dumps(data)

            # create the post request and send it off
            req = urllib.request(url, data)
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req, data)

            # return whatever the webpage returned
            return (True, response.read())
        except Exception as e:  # pragma: no cover
            return (False, 'failed post request to ' + url + ' ' +
                    ': ' + str(e))

    @staticmethod
    def get_request(url):
        """
        Send a get request to the given url

        Args:
            url(str): url to send the data to. Eg: http://0.0.0.0:37728

        Returns:
            A tuple of success status and whatever the url is supposed to give
            after a GET request or a failure message
        """
        try:
            response = urllib.request.urlopen(url)
            return (True, response.read())
        except Exception as e:  # pragma no cover
            return (False, 'failed get request to ' + url + ' ' + str(e))

    @staticmethod
    def get_vent_tool_url(tool_name):
        """
        Iterate through all containers and grab the port number
        corresponding to the given tool name. Works for only CORE tools
        since it specifically looks for core

        Args:
            tool_name(str): tool name to search for. Eg: network-tap

        Returns:
            A tuple of success status and the url corresponding to the given
            tool name or a failure mesage. An example return url is
            http://0.0.0.0:37728. Works well with send_request and get_request.
        """
        try:
            d = docker.from_env()
            containers = d.containers.list(filters={'label': 'vent'}, all=True)
        except Exception as e:  # pragma no cover
            return (False, 'docker failed with error ' + str(e))

        url = ''
        found = False
        for c in containers:
            if tool_name in c.attrs['Name'] and \
                    'core' in c.attrs['Config']['Labels']['vent.groups']:
                # get a dictionary of ports
                url = c.attrs['NetworkSettings']['Ports']

                # iterate through the dict to avoid hard coding anything
                # is it safe to assume only 1 entry in the dict will exist?
                for port in url:
                    h_port = url[port][0]['HostPort']
                    h_ip = url[port][0]['HostIp']
                    url = 'http://' + str(h_ip) + ':' + str(h_port)
                    found = True
                    break
            # no need to cycle every single container if we found our ports
            if found:
                break
        return (True, str(url))
