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
        self.manifest = os.path.join(self.path_dirs.meta_dir, "plugin_manifest.cfg")

    def add(self, repo, tools=[], overrides=[], version="HEAD", branch="master", build=True):
        """
        Adds a plugin of tool(s)
        tools is a list of tuples, where the pair is a tool name (path to
        Dockerfile) and version
          tools are for explicitly limiting which tools and versions
          (if version in tuple is '', then defaults to version)
        overrides is a list of tuples, where the pair is a tool name (path to
        Dockerfile) and a version
          overrides are for explicitly removing tools and overriding versions of tools
          (if version in tuple is '', then tool is removed, otherwise that tool
           is checked out at the specific version in the tuple)
        if tools and overrides are left as empty lists, then all tools in the
          repo are pulled down at the version and branch specified or defaulted to
        Examples:
          repo=foo
            (get all tools from repo 'foo' at version 'HEAD' on branch 'master')
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
        self.repo = repo
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

        cwd = os.getcwd()
        os.chdir(self.path)
        status = subprocess.call(shlex.split("git clone " + self.repo + " ."))
        if status == 0 or status == 128:
            if len(tools) == 0 and len(overrides) == 0: # get all tools
                if response[0]:
                    matches = self.available_tools()
                    response = self.build_tools(matches)
            elif len(overrides) == 0: # there's something in tools
                # only grab the tools specified
                # !! TODO check for pre-existing that conflict with request and disable and remove image
                template = Template(template=self.manifest)
                matches = []
                for tool in tools:
                    if tool[1] != '':
                        self.version = tool[1]
                    match = ''
                    if tool[0].endswith('/'):
                        match = tool[0][:-1]
                    elif tool[0] != '.':
                        match = tool[0]
                    matches.append(match)
                response = self.build_tools(matches)
            elif len(tools) == 0: # there's something in overrides
                # grab all of the tools except override the ones specified
                pass
            else: # both tools and overrides were specified
                # grab only the tools specified, with the overrides applied
                pass
        else:
            response = (False, status)
        os.chdir(cwd)
        return response

    def build_tools(self, matches):
        response = (True, None)
        template = Template(template=self.manifest)
        for match in matches:
            response = self.checkout()
            section = self.org + ":" + self.name + ":" + match
            template.add_section(section)
            match_path = self.path + match
            template.set_option(section, "path", match_path)
            template.set_option(section, "repo", self.repo)
            template.set_option(section, "enabled", "yes")
            template.set_option(section, "branch", self.branch)
            template.set_option(section, "version", self.version)
            image_name = self.org + "-" + self.name + "-"
            if match == '':
                image_name += self.branch + ":" + self.version
            else:
                image_name += '-'.join(match.split('/')[1:]) + "-" + self.branch + ":" + self.version
            template.set_option(section, "image_name", image_name)
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
                matches.append(root.split(self.path)[1])
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
