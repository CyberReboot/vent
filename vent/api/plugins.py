import datetime
import docker
import fnmatch
import os
import shlex
import subprocess

from vent.api.templates import Template
from vent.helpers.errors import ErrorHandler
from vent.helpers.logs import Logger
from vent.helpers.paths import PathDirs

class Plugin:
    """ Handle Plugins """
    def __init__(self, **kargs):
        self.path_dirs = PathDirs(**kargs)
        self.manifest = os.path.join(self.path_dirs.meta_dir,
                                     "plugin_manifest.cfg")
        self.d_client = docker.from_env()
        self.logger = Logger(__name__)

    def apply_path(self, repo):
        """ Set path to where the repo is and return original path """
        # rewrite repo for consistency
        if repo.endswith(".git"):
            repo = repo.split(".git")[0]

        # get org and repo name and path repo will be cloned to
        try:
            org, name = repo.split("/")[-2:]
            self.path = os.path.join(self.path_dirs.plugins_dir, org, name)
        except Exception as e:
            return (False, str(e))

        # save current path
        cwd = os.getcwd()
        # set to new repo path
        os.chdir(self.path)

        return (True, cwd)

    def repo_branches(self, repo):
        """ Get the branches of a repository """
        branches = []

        cwd = self.apply_path(repo)
        if cwd[0]:
            cwd = cwd[1]
        else:
            return cwd
        try:
            junk = subprocess.check_output(shlex.split("git pull --all"), stderr=subprocess.STDOUT, close_fds=True)
            branch_output = subprocess.check_output(shlex.split("git branch -a"), stderr=subprocess.STDOUT, close_fds=True)
            branch_output = branch_output.split("\n")
            for branch in branch_output:
                b = branch.strip()
                if b.startswith('*'):
                    b = b[2:]
                if "/" in b:
                    branches.append(b.rsplit('/', 1)[1])
                elif b:
                    branches.append(b)
        except Exception as e:
            return (False, e)

        branches = list(set(branches))
        for branch in branches:
            try:
                junk = subprocess.check_output(shlex.split("git checkout " + branch), stderr=subprocess.STDOUT, close_fds=True)
            except Exception as e:
                return (False, e)
        try:
            os.chdir(cwd)
        except Exception as e:
            pass

        return (True, branches)

    def repo_commits(self, repo):
        """ Get the commit IDs for all of the branches of a repository """
        commits = []

        branches = self.repo_branches(repo)
        cwd = self.apply_path(repo)
        if cwd[0]:
            cwd = cwd[1]
        else:
            return cwd
        if branches[0]:
            try:
                for branch in branches[1]:
                    branch_output = subprocess.check_output(shlex.split("git rev-list " + branch), stderr=subprocess.STDOUT, close_fds=True)
                    branch_output = ['HEAD'] + branch_output.split("\n")[:-1]
                    commits.append((branch, branch_output))
            except Exception as e:
                return (False, e)
        else:
            return branches
        try:
            os.chdir(cwd)
        except Exception as e:
            pass

        return (True, commits)

    def repo_tools(self, repo, branch, version):
        """ Get available tools for a repository branch at a version """
        tools = []
        cwd = self.apply_path(repo)
        if cwd[0]:
            cwd = cwd[1]
        else:
            return cwd
        self.branch = branch
        self.version = version
        response = self.checkout()
        self.logger.info(str(response))
        if response[0]:
            tools = self._available_tools()
        else:
            return response
        try:
            os.chdir(cwd)
        except Exception as e:
            pass

        return (True, tools)

    def clone(self, repo, user=None, pw=None):
        """ Clone the repository """
        self.org = None
        self.name = None
        self.repo = repo

        # save current path
        cwd = os.getcwd()

        # rewrite repo for consistency
        if self.repo.endswith(".git"):
            self.repo = self.repo.split(".git")[0]

        # get org and repo name and path repo will be cloned to
        try:
            self.org, self.name = self.repo.split("/")[-2:]
            self.path = os.path.join(self.path_dirs.plugins_dir, self.org, self.name)
        except Exception as e:
            return -1, cwd


        # check if the directory exists, if so return now
        response = self.path_dirs.ensure_dir(self.path)
        if not response[0]:
            return -1, cwd

        # set to new repo path
        os.chdir(self.path)

        if response[0] and response[1] == 'exists':
            try:
                status = subprocess.check_output(shlex.split("git -C "+self.path+" rev-parse"), stderr=subprocess.STDOUT, close_fds=True)
                return 0, cwd
            except Exception as e:
                return -1, cwd

        # ensure cloning still works even if ssl is broken...probably should be improved
        try:
            status = subprocess.check_output(shlex.split("git config --global http.sslVerify false"), stderr=subprocess.STDOUT, close_fds=True)
        except Exception as e: # pragma: no cover
            return -1, cwd

        # check if user and pw were supplied, typically for private repos
        if user and pw:
            # only https is supported when using user/pw
            repo = 'https://'+user+':'+pw+'@'+self.repo.split("https://")[-1]

        # clone repo and build tools
        try:
            status = subprocess.check_output(shlex.split("git clone --recursive " + repo + " ."), stderr=subprocess.STDOUT, close_fds=True)
            status_code = 0
        except subprocess.CalledProcessError as e:
            status_code = e.returncode

        return status_code, cwd

    def add(self, repo, tools=None, overrides=None, version="HEAD",
            branch="master", build=True, user=None, pw=None, groups=None,
            version_alias=None, wild=None, remove_old=True, disable_old=True,
            limit_groups=None):
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
        self.tools = tools
        self.overrides = overrides
        self.version = version
        self.branch = branch
        self.build = build
        self.groups = groups

        # TODO these need to be implemented
        self.version_alias = version_alias
        self.wild = wild
        self.remove_old = remove_old
        self.disable_old = disable_old
        self.limit_groups = limit_groups

        response = (True, None)

        status_code, cwd = self.clone(repo, user=user, pw=pw)

        response = self._build_tools(status_code)

        # set back to original path
        try:
            os.chdir(cwd)
        except Exception as e:
            pass
        return response

    @ErrorHandler
    def builder(self, template, match_path, image_name, section, build=None,
              branch=None, version=None):
        """ Build tools """
        if build:
            self.build = build
        elif not hasattr(self, 'build'): self.build = True
        if branch:
            self.branch = branch
        elif not hasattr(self, 'branch'): self.branch = 'master'
        if version:
            self.version = version
        elif not hasattr(self, 'version'): self.version = 'HEAD'
        cwd = os.getcwd()
        os.chdir(match_path)
        template = self._build_image(template, match_path, image_name, section)
        try:
            os.chdir(cwd)
        except Exception as e:
            pass
        return template

    def _build_tools(self, status):
        """
        Create list of tools, paths, and versions to be built and sends them to
        build_manifest
        """
        response = (True, None)
        # !! TODO implement features: wild, remove_old, disable_old, limit_groups

        # check result of clone, ensure successful or that it already exists
        if status in [0, 128]:
            response = self.checkout()
            if response[0]:
                matches = []
                if self.tools is None and self.overrides is None:
                    # get all tools
                    matches = self._available_tools()
                elif self.tools is None:
                    # there's only something in overrides
                    # grab all the tools then apply overrides
                    matches = self._available_tools()
                    # !! TODO apply overrides to matches
                elif self.overrides is None:
                    # there's only something in tools
                    # only grab the tools specified
                    matches = self.get_tool_matches()
                else:
                    # both tools and overrides were specified
                    # grab only the tools specified, with the overrides applied
                    orig_matches = self.get_tool_matches()
                    matches = orig_matches
                    for override in self.overrides:
                        override_t = None
                        if override[0] == '.':
                            override_t = ('', override[1])
                        else:
                            override_t = override
                        for match in orig_matches:
                            if override_t[0] == match[0]:
                                matches.remove(match)
                                matches.append(override_t)
                if len(matches) > 0:
                    self._build_manifest(matches)
        else:
            response = (False, status)
        return response

    def get_tool_matches(self):
        """
        Get the tools paths and versions that were specified by self.tools and
        self.version
        """
        matches = []
        if not hasattr(self, 'tools'): self.tools = []
        if not hasattr(self, 'version'): self.version = 'HEAD'
        for tool in self.tools:
            match_version = self.version
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

    def _build_manifest(self, matches):
        """ Builds and writes the manifest for the tools being added """
        # !! TODO check for pre-existing that conflict with request and disable and/or remove image
        for match in matches:
            template = Template(template=self.manifest)
            # !! TODO check for special settings here first for the specific match
            self.version = match[1]
            response = self.checkout()
            if response[0]:
                section = self.org + ":" + self.name + ":" + match[0] + ":" + self.branch + ":" + self.version
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
                        # TODO check if tool name but a different version exists - then disable/remove if set
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
                # check if section should be removed from config - i.e. all tools,
                # but new commit removed one that was in a previous commit

                # set template section and options for tool at version and branch
                template.add_section(section)
                template.set_option(section, "name", match[0].split('/')[-1])
                template.set_option(section, "namespace", self.org+'/'+self.name)
                template.set_option(section, "path", match_path)
                template.set_option(section, "repo", self.repo)
                template.set_option(section, "enabled", "yes")
                template.set_option(section, "branch", self.branch)
                template.set_option(section, "version", self.version)
                template.set_option(section, "last_updated", str(datetime.datetime.utcnow()) + " UTC")
                template.set_option(section, "image_name", image_name)
                vent_template = Template(template=os.path.join(match_path, 'vent.template'))
                vent_status, response = vent_template.option("info", "name")
                if vent_status:
                    template.set_option(section, "link_name", response)
                else:
                    template.set_option(section, "link_name", match[0].split('/')[-1])
                commit_id = None
                if self.version == 'HEAD':
                    os.chdir(match_path)
                    commit_id = subprocess.check_output(shlex.split("git rev-parse --short HEAD"), stderr=subprocess.STDOUT, close_fds=True).strip()
                    template.set_option(section, "commit_id", commit_id)
                if head:
                    # no need to store previous commits if not HEAD, since
                    # the version will always be the same commit ID
                    if previous_commit and previous_commit != commit_id:
                        if previous_commits and previous_commit not in previous_commits:
                            previous_commits = previous_commit+','+previous_commits
                        elif not previous_commits:
                            previous_commits = previous_commit
                    if previous_commits and previous_commits != commit_id:
                        template.set_option(section, "previous_versions", previous_commits)

                if self.version_alias:
                    template.set_option(section, "version_alias", self.version_alias)
                if self.groups:
                    template.set_option(section, "groups", self.groups)
                else:
                    vent_template = os.path.join(match_path, 'vent.template')
                    if os.path.exists(vent_template):
                        v_template = Template(template=vent_template)
                        groups = v_template.option("info", "groups")
                        if groups[0]:
                            template.set_option(section, "groups", groups[1])
                template = self._build_image(template, match_path, image_name, section)

            # write out configuration to the manifest file
            template.write_config()

        # reset to repo directory
        os.chdir(self.path)
        return

    def _build_image(self, template, match_path, image_name, section):
        """ Build docker images and store results in template """
        # !! TODO return status of whether it built successfully or not
        if self.build:
            try:
                os.chdir(match_path)
                # currently can't use docker-py because it doesn't support labels on images yet
                name = template.option(section, "name")
                groups = template.option(section, "groups")
                if groups[1] == "" or not groups[0]:
                    groups = (True, "none")
                if not name[0]:
                    name = (True, image_name)
                # pull if '/' in image_name, fallback to build
                pull = False
                if '/' in image_name:
                    try:
                        self.logger.info("Trying to pull "+image_name)
                        output = subprocess.check_output(shlex.split("docker pull "+image_name), stderr=subprocess.STDOUT, close_fds=True)
                        self.logger.info("Pulling "+name[1]+"\n"+str(output))
                        for line in output.split('\n'):
                            if line.startswith("Digest: sha256:"):
                                image_id = line.split("Digest: sha256:")[1][:12]
                        if image_id:
                            template.set_option(section, "built", "yes")
                            template.set_option(section, "image_id", image_id)
                            template.set_option(section, "last_updated", str(datetime.datetime.utcnow()) + " UTC")
                            status = (True, "Pulled "+image_name)
                            self.logger.info(str(status))
                        else:
                            template.set_option(section, "built", "failed")
                            template.set_option(section, "last_updated", str(datetime.datetime.utcnow()) + " UTC")
                            status = (False, "Failed to pull image "+str(output.split('\n')[-1]))
                            self.logger.warning(str(status))
                        pull = True
                    except Exception as e:
                        self.logger.warning("Failed to pull image, going to build instead: "+str(e))
                if not pull:
                    output = subprocess.check_output(shlex.split("docker build --label vent --label vent.name="+name[1]+" --label vent.groups="+groups[1]+" -t " + image_name + " ."), stderr=subprocess.STDOUT, close_fds=True)
                    self.logger.info("Building "+name[1]+"\n"+str(output))
                    image_id = ""
                    for line in output.split("\n"):
                        if line.startswith("Successfully built "):
                            image_id = line.split("Successfully built ")[1].strip()
                    template.set_option(section, "built", "yes")
                    template.set_option(section, "image_id", image_id)
                    template.set_option(section, "last_updated", str(datetime.datetime.utcnow()) + " UTC")
            except Exception as e:
                template.set_option(section, "built", "failed")
                template.set_option(section, "last_updated", str(datetime.datetime.utcnow()) + " UTC")
        else:
            template.set_option(section, "built", "no")
            template.set_option(section, "last_updated", str(datetime.datetime.utcnow()) + " UTC")
        return template

    def _available_tools(self, groups=None):
        """
        Return list of possible tools in repo for the given version and branch
        """
        matches = []
        if not hasattr(self, 'path'): return matches
        if groups:
            groups = groups.split(",")
        for root, dirnames, filenames in os.walk(self.path):
            for filename in fnmatch.filter(filenames, 'Dockerfile'):
                # !! TODO deal with wild/etc.?
                if groups:
                    try:
                        template = Template(template=os.path.join(root, 'vent.template'))
                        for group in groups:
                            template_groups = template.option("info", "groups")
                            if template_groups[0] and group in template_groups[1]:
                                matches.append((root.split(self.path)[1], self.version))
                    except Exception as e: # pragma: no cover
                        pass
                else:
                    matches.append((root.split(self.path)[1], self.version))
        return matches

    def checkout(self):
        """ Checkout a specific version and branch of a repo """
        if not hasattr(self, 'branch'): self.branch = 'master'
        if not hasattr(self, 'version'): self.version = 'HEAD'
        response = (True, None)
        try:
            status = subprocess.check_output(shlex.split("git checkout " + self.branch), stderr=subprocess.STDOUT, close_fds=True)
            status = subprocess.check_output(shlex.split("git pull"), stderr=subprocess.STDOUT, close_fds=True)
            status = subprocess.check_output(shlex.split("git reset --hard " + self.version), stderr=subprocess.STDOUT, close_fds=True)
            response = (True, status)
        except Exception as e: # pragma: no cover
            response = (False, os.getcwd()+str(e))
        return response

    @staticmethod
    def add_image(image, tag="latest"):
        """
        Add an image from a registry/hub rather than building from a
        repository
        """
        # !! TODO
        return

    def constraint_options(self, constraint_dict, options):
        """ Return result of constraints and options against a template """
        constraints = {}
        template = Template(template=self.manifest)
        for constraint in constraint_dict:
            if constraint != 'self':
                if constraint_dict[constraint] or constraint_dict[constraint] == '':
                    constraints[constraint] = constraint_dict[constraint]
        results = template.constrained_sections(constraints=constraints, options=options)
        return results, template

    def tools(self):
        """ Return list of tuples of all tools """
        tools = []
        template = Template(template=self.manifest)
        exists, sections = template.sections()
        if exists:
            for section in sections:
                options = {'section':section,
                           'enabled':None,
                           'built':None,
                           'version':None,
                           'repo':None,
                           'branch':None,
                           'name':None,
                           'groups':None,
                           'image_name':None}
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

        # get resulting dictionary of sections with options that match constraints
        results, template = self.constraint_options(args, [])
        for result in results:
            response, image_name = template.option(result, 'image_name')

            # check for container and remove
            container_name = image_name.replace(':', '-').replace('/', '-')
            try:
                container = self.d_client.containers.get(container_name)
                response = container.remove(v=True, force=True)
                self.logger.info(response)
                self.logger.info("Removing plugin container: "+container_name)
            except Exception as e:
                self.logger.warn("Unable to remove the plugin container: " + 
                                 container_name + " because: " + str(e))

            # check for image and remove
            try:
                response = self.d_client.images.remove(image_name)
                self.logger.info(response)
                self.logger.info("Removing plugin image: "+image_name)
            except Exception as e:
                self.logger.warn("Unable to remove the plugin image: " + 
                                 image_name + " because: " + str(e))

            # remove tool from the manifest
            status = template.del_section(result)
            self.logger.info("Removing plugin tool: "+result)
        # TODO if all tools from a repo have been removed, remove the repo
        template.write_config()
        return status

    def update(self, name=None, repo=None, namespace=None, branch=None, groups=None):
        """
        Update tool (name) or repository, repository is the url. If no
        arguments are specified, all tools will be updated
        """
        # initialize
        args = locals()
        status = (False, None)
        options = ['branch', 'groups']

        # get resulting dictionary of sections with options that match constraints
        results, template = self.constraint_options(args, options)
        for result in results:
            # check for container and remove
            container_name = image_name.replace(':', '-').replace('/', '-')
            try:
                container = self.d_client.containers.get(container_name)
                response = container.remove(v=True, force=True)
            except Exception as e:
                pass

            # TODO git pull
            # TODO build
            # TODO docker pull
            # TODO update tool in the manifest

            self.logger.info("Updating plugin tool: "+result)
        template.write_config()
        return status

    # !! TODO name or group ?
    def versions(self, name, namespace=None, branch="master"):
        """ Return available versions of a tool """
        # initialize
        args = locals()
        versions = []
        options = ['version', 'previous_versions']

        # get resulting dictionary of sections with options that match constraints
        results, _ = self.constraint_options(args, options)
        for result in results:
            version_list = [results[result]['version']]
            if 'previous_versions' in results[result]:
                version_list = version_list+(results[result]['previous_versions']).split(',')
            versions.append((result, version_list))
        return versions

    # !! TODO name or group ?
    def current_version(self, name, namespace=None, branch="master"):
        """ Return current version for a given tool """
        # initialize
        args = locals()
        versions = []
        options = ['version']

        # get resulting dictionary of sections with options that match constraints
        results, _ = self.constraint_options(args, options)
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

        # get resulting dictionary of sections with options that match constraints
        results, _ = self.constraint_options(args, options)
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

        # get resulting dictionary of sections with options that match constraints
        results, template = self.constraint_options(args, [])
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

        # get resulting dictionary of sections with options that match constraints
        results, template = self.constraint_options(args, [])
        for result in results:
            status = template.set_option(result, 'enabled', 'no')
        template.write_config()
        return status
