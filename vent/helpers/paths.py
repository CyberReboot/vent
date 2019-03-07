import errno
import platform
from os import chdir
from os import environ
from os import getcwd
from os import getenv
from os import makedirs
from os.path import exists
from os.path import expanduser
from os.path import isdir
from os.path import isfile
from os.path import join

import yaml

from vent.helpers.templates import Template


class PathDirs:
    """ Global path directories for vent """

    def __init__(self,
                 base_dir=join(expanduser('~'), '.vent/'),
                 plugins_dir='plugins/',
                 meta_dir=join(expanduser('~'), '.vent')):
        self.base_dir = base_dir
        self.plugins_dir = base_dir + plugins_dir
        self.meta_dir = meta_dir
        self.init_file = base_dir + 'vent.init'
        self.cfg_file = base_dir + 'vent.cfg'
        self.startup_file = join(expanduser('~'),
                                 '.vent_startup.yml')
        self.plugin_config_file = join(expanduser('~'),
                                       '.plugin_config.yml')

        # make sure the paths exists, if not create them
        self.ensure_dir(self.base_dir)
        self.ensure_dir(self.plugins_dir)
        self.ensure_dir(self.meta_dir)

    @staticmethod
    def ensure_dir(path):
        """
        Tries to create directory, if fails, checks if path already exists
        """
        try:
            makedirs(path)
        except OSError as e:  # pragma: no cover
            if e.errno == errno.EEXIST and isdir(path):
                return (True, 'exists')
            else:
                return (False, e)
        return (True, path)

    @staticmethod
    def ensure_file(path):
        """ Checks if file exists, if fails, tries to create file """
        try:
            exists = isfile(path)
            if not exists:
                with open(path, 'w+') as fname:
                    fname.write('initialized')
                return (True, path)
            return (True, 'exists')
        except OSError as e:  # pragma: no cover
            return (False, e)

    @staticmethod
    def rel_path(name, available_tools):
        """
        Extracts relative path to a tool (from the main cloned directory) out
        of available_tools based on the name it is given
        """
        if name == '@' or name == '.' or name == '/':
            name = ''
        multi_tool = '@' in name
        for tool in available_tools:
            t_name = tool[0].lower()
            if multi_tool:
                if name.split('@')[-1] == t_name.split('@')[-1]:
                    return t_name, t_name
            else:
                if name == t_name.split('/')[-1]:
                    return t_name, tool[0]
                elif name == '' and t_name.split('@')[-1] == 'unspecified':
                    return '', ''
        return None, None

    def host_config(self):
        """ Ensure the host configuration file exists """
        if platform.system() == 'Darwin':
            default_file_dir = join(expanduser('~'),
                                    'vent_files')
        else:
            default_file_dir = '/opt/vent_files'
        status = self.ensure_dir(default_file_dir)
        if not isfile(self.cfg_file):
            config = Template(template=self.cfg_file)
            sections = {'main': {'files': default_file_dir},
                        'network-mapping': {},
                        'nvidia-docker-plugin': {'port': '3476'}}
            for s in sections:
                if sections[s]:
                    for option in sections[s]:
                        config.add_option(s, option, sections[s][option])
                else:
                    config.add_section(s)
            config.write_config()
        return status

    def apply_path(self, repo):
        """ Set path to where the repo is and return original path """
        try:
            # rewrite repo for consistency
            if repo.endswith('.git'):
                repo = repo.split('.git')[0]

            # get org and repo name and path repo will be cloned to
            org, name = repo.split('/')[-2:]
            path = join(self.plugins_dir, org, name)

            # save current path
            cwd = getcwd()

            # set to new repo path
            self.ensure_dir(path)
            chdir(path)
            status = (True, cwd, path)
        except Exception as e:  # pragma: no cover
            status = (False, str(e))
        return status

    def get_path(self, repo):
        """ Return the path for the repo """
        if repo.endswith('.git'):
            repo = repo.split('.git')[0]
        org, name = repo.split('/')[-2:]
        path = self.plugins_dir
        path = join(path, org, name)
        return path, org, name

    def override_config(self, path):
        """
        Will take a yml located in home directory titled '.plugin_config.yml'.
        It'll then override, using the yml, the plugin's config file
        """
        status = (True, None)
        config_override = False

        try:
            # parse the yml file
            c_dict = {}
            if exists(self.plugin_config_file):
                with open(self.plugin_config_file, 'r') as config_file:
                    c_dict = yaml.safe_load(config_file.read())

            # check for environment variable overrides
            check_c_dict = c_dict.copy()
            for tool in check_c_dict:
                for section in check_c_dict[tool]:
                    for key in check_c_dict[tool][section]:
                        if key in environ:
                            c_dict[tool][section][key] = getenv(key)

            # assume the name of the plugin is its directory
            plugin_name = path.split('/')[-1]
            if plugin_name == '':
                plugin_name = path.split('/')[-2]
            plugin_config_path = path + '/config/' + plugin_name + '.config'

            if exists(plugin_config_path):
                plugin_template = Template(plugin_config_path)
                plugin_options = c_dict[plugin_name]
                for section in plugin_options:
                    for option in plugin_options[section]:
                        plugin_template.set_option(section, option,
                                                   str(plugin_options[section][option]))
                plugin_template.write_config()
                config_override = True
        except Exception as e:  # pragma: no cover
            status = (False, str(e))

        return status, config_override
