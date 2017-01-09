import datetime
import fnmatch
import os
import shlex
import subprocess

from api.templates import Template
from helpers.paths import PathDirs

class Plugin:
    """ Handle Plugins """
    def __init__(self, **kargs):
        self.path_dirs = PathDirs(**kargs)
        self.manifest = os.path.join(self.path_dirs.meta_dir,
                                     "plugin_manifest.cfg")

    def add(self, repo, tools=None, overrides=None, version="HEAD",
            branch="master", build=True, user=None, pw=None, group=None,
            version_alias=None, wild=None, remove_old=True, disable_old=True):
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
        group is globally set for all tools
        version_alias is globally set for all tools and is a mapping from a
          friendly version tag to the real version commit ID
        wild lets you specify individual overrides for additional values in the
          tuple of tools or overrides wild can be a list containing one or more
          of the following: branch, build, group, version_alias
          the order of the items in the wild list will expect values to tacked
          on in the same order to the tuple for tools and overrides in
          additional to the tool name and version
        remove_old lets you specify whether or not to remove previously found
          tools that match to ones being added currently
        disable_old lets you specify whether or not to disable previously found
          tools that match to ones being added currently
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
        # !! TODO implement features: group, version_alias, wild, remove_old, disable_old
        # initialize and store class objects
        if not tools:
            tools = []
        if not overrides:
            overrides = []
        self.repo = repo
        self.tools = tools
        self.overrides = overrides
        self.version = version
        self.branch = branch
        self.build = build
        self.org = None
        self.name = None
        response = (True, None)

        # rewrite repo for consistency
        if self.repo.endswith(".git"):
            self.repo = self.repo.split(".git")[0]

        # get org and repo name and path repo will be cloned to
        self.org, self.name = self.repo.split("/")[-2:]
        self.path = os.path.join(self.path_dirs.plugins_dir, self.org, self.name)

        # make sure the path can be created, otherwise exit function now
        response = self.path_dirs.ensure_dir(self.path)
        if not response[0]:
            return response

        # save current path, set to new repo path
        cwd = os.getcwd()
        os.chdir(self.path)

        # ensure cloning still works even if ssl is broken...probably should be improved
        status = subprocess.call(shlex.split("git config --global http.sslVerify false"))

        # check if user and pw were supplied, typically for private repos
        if user and pw:
            # only https is supported when using user/pw
            self.repo = 'https://'+user+':'+pw+'@'+self.repo.split("https://")[-1]

        # clone repo and build tools
        status = subprocess.call(shlex.split("git clone --recursive " + self.repo + " ."))
        response = self.build_tools(status)

        # set back to original path
        os.chdir(cwd)
        return response

    def build_tools(self, status):
        """
        Create list of tools, paths, and versions to be built and sends them to
        build_manifest
        """
        response = (True, None)

        # check result of clone, ensure successful or that it already exists
        if status in [0, 128]:
            response = self.checkout()
            if response[0]:
                matches = []
                if len(self.tools) == 0 and len(self.overrides) == 0:
                    # get all tools
                    matches = self.available_tools()
                elif len(self.tools) == 0:
                    # there's only something in overrides
                    # grab all the tools then apply overrides
                    matches = self.available_tools()
                    # !! TODO apply overrides to matches
                elif len(self.overrides) == 0:
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
                    self.build_manifest(matches)
        else:
            response = (False, status)
        return response

    def get_tool_matches(self):
        """
        Get the tools paths and versions that were specified by self.tools and
        self.version
        """
        matches = []
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

    def build_manifest(self, matches):
        """ Builds and writes the manifest for the tools being added """
        # !! TODO check for pre-existing that conflict with request and disable and/or remove image
        template = Template(template=self.manifest)
        for match in matches:
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
                template.set_option(section, "path", match_path)
                template.set_option(section, "repo", self.repo)
                template.set_option(section, "enabled", "yes")
                template.set_option(section, "branch", self.branch)
                template.set_option(section, "version", self.version)
                template.set_option(section, "last_updated", str(datetime.datetime.utcnow()) + " UTC")
                template.set_option(section, "image_name", image_name)
                commit_id = None
                if self.version == 'HEAD':
                    os.chdir(match_path)
                    commit_id = subprocess.check_output(shlex.split("git rev-parse --short HEAD")).strip()
                    template.set_option(section, "commit_id", commit_id)
                if head:
                    # no need to store previous commits if not HEAD, since
                    # the version will always be the same commit ID
                    if previous_commit != commit_id:
                        if previous_commits:
                            previous_commits = previous_commit+','+previous_commits
                        else:
                            previous_commits = previous_commit
                    if previous_commits != commit_id:
                        template.set_option(section, "previous_versions", previous_commits)
                template = self.build_image(template, match_path, image_name, section)

        # write out configuration to the manifest file and reset to repo directory
        template.write_config()
        os.chdir(self.path)
        return

    def build_image(self, template, match_path, image_name, section):
        """ Build docker images and store results in template """
        if self.build:
            try:
                os.chdir(match_path)
                output = subprocess.check_output(shlex.split("docker build --label vent -t " + image_name + " ."))
                image_id = ""
                for line in output.split("\n"):
                    if line.startswith("Successfully built "):
                        image_id = line.split("Successfully built ")[1].strip()
                template.set_option(section, "built", "yes")
                template.set_option(section, "image_id", image_id)
            except Exception as e:
                template.set_option(section, "built", "failed")
        else:
            template.set_option(section, "built", "no")
        return template

    def available_tools(self):
        """
        Return list of possible tools in repo for the given version and branch
        """
        matches = []
        for root, dirnames, filenames in os.walk(self.path):
            for filename in fnmatch.filter(filenames, 'Dockerfile'):
                # !! TODO deal with wild/groups/etc.?
                matches.append((root.split(self.path)[1], self.version))
        return matches

    @staticmethod
    def add_image(image, tag="latest"):
        """
        Add an image from a registry/hub rather than building from a
        repository
        """
        return

    @staticmethod
    def remove(tool=None, repo=None, branch="master"):
        """ Remove tool or repository """
        return

    @staticmethod
    def versions(tool, branch="master"):
        """ Get available versions (built) of a tool """
        return

    @staticmethod
    def version(tool, branch="master"):
        """ Return active version for a given tool """
        return

    @staticmethod
    def state(tool, branch="master"):
        """ Return state of a tool, disabled/enabled """
        return

    def checkout(self):
        """ Checkout a specific version and branch of a repo """
        response = (True, None)
        status = subprocess.call(shlex.split("git checkout " + self.branch))
        if status == 0:
            status = subprocess.call(shlex.split("git pull"))
            if status == 0:
                status = subprocess.call(shlex.split("git reset --hard " + self.version))
                if status == 0:
                    response = (True, status)
                else:
                    response = (False, status)
            else:
                response = (False, status)
        else:
            response = (False, status)
        return response

    @staticmethod
    def enable(tool, version="HEAD", branch="master"):
        """ Enable tool at a specific version, default to head """
        return

    @staticmethod
    def disable(tool, version="head", branch="master"):
        """ Disable tool at a specific version, default to head """
        return
