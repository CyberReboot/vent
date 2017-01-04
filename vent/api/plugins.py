import fnmatch
import os
import shlex
import subprocess

from api.templates import  Template
from helpers.paths import PathDirs

class Plugin:
    """ Handle Plugins """
    def __init__(self, **kargs):
        self.path_dirs = PathDirs(**kargs)
        self.manifest = os.path.join(self.path_dirs.meta_dir,
                                     "plugin_manifest.cfg")

    def add(self, repo, tools=[], overrides=[], version="HEAD",
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
        if repo == "":
            print("No plugins added, url is not formatted correctly")
            print("Please use a git url, e.g. https://github.com/CyberReboot/vent-plugins.git")
            return (False, None)
        # !! TODO implement features: group, version_alias, wild, remove_old, disable_old
        self.repo = repo
        self.tools = tools
        self.overrides = overrides
        self.version = version
        self.branch = branch
        self.build = build
        response = (True, None)
        self.org = None
        self.name = None
        if self.repo.endswith(".git"):
            self.repo = self.repo.split(".git")[0]
        self.org, self.name = self.repo.split("/")[-2:]
        self.path = os.path.join(self.path_dirs.plugins_dir, self.org, self.name)
        response = self.path_dirs.ensure_dir(self.path)
        if not response[0]:
            return response

        cwd = os.getcwd()
        os.chdir(self.path)
        status = subprocess.call(shlex.split("git config --global http.sslVerify false"))
        if not user and not pw:
            status = subprocess.call(shlex.split("git clone --recursive " + self.repo + " ."))
        else:
            # https only is supported when using user/pw
            self.repo = 'https://'+user+':'+pw+'@'+self.repo.split("https://")[-1]
        if status == 0 or status == 128: # new or already exists
            if len(self.tools) == 0: # get all tools
                # also catches the case where overrides is also empty - this is intended
                response = self.checkout()
                if response[0]:
                    matches = self.available_tools()
                    response = self.build_manifest(matches)
            elif len(self.overrides) == 0: # there's something in tools
                # only grab the tools specified
                # !! TODO check for pre-existing that conflict with request and disable and remove image
                template = Template(template=self.manifest)
                # !! TODO this whole block is wrong, need to keep tuple
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
                    matches.append((match, match_version))
                response = self.build_manifest(matches)
            else: # both tools and overrides were specified
                # grab only the tools specified, with the overrides applied
                # !! TODO
                pass
        else:
            response = (False, status)
        os.chdir(cwd)
        return response

    def build_manifest(self, matches):
        """ Builds and writes the manifest for the tools being added """
        response = (True, None)
        template = Template(template=self.manifest)
        for match in matches:
            # !! TODO check for overrides or special settings here first for the specific match
            self.version = match[1]
            response = self.checkout()
            if response[0]:
                section = self.org + ":" + self.name + ":" + match[0] + ":" + self.branch + ":" + self.version
                template.add_section(section)
                match_path = self.path + match[0]
                template.set_option(section, "path", match_path)
                template.set_option(section, "repo", self.repo)
                template.set_option(section, "enabled", "yes")
                template.set_option(section, "branch", self.branch)
                template.set_option(section, "version", self.version)
                image_name = self.org + "-" + self.name + "-"
                if match[0] == '':
                    image_name += self.branch + ":" + self.version
                else:
                    image_name += '-'.join(match[0].split('/')[1:]) + "-" + self.branch + ":" + self.version
                template.set_option(section, "image_name", image_name)
                # !! TODO break this out for being able to build separate of add
                if self.build:
                    os.chdir(match_path)
                    status = subprocess.call(shlex.split("docker build --label vent -t " + image_name + " ."))
                    if status == 0:
                        response = (True, status)
                        template.set_option(section, "built", "yes")
                    else:
                        template.set_option(section, "built", "failed")
                        response = (False, status)
                else:
                    template.set_option(section, "built", "no")
        template.write_config()
        os.chdir(self.path)
        return response

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
