import fnmatch
import os
import shlex
import subprocess

from helpers.paths import PathDirs

class Plugin:
    """ Handle Plugins """
    def __init__(self, **kargs):
        self.path_dirs = PathDirs(**kargs)
        self.manifest = os.path.join(self.path_dirs.meta_dir, "plugin_manifest.cfg")

    def add(self, repo, tools=[], overrides=[], version="HEAD", branch="master", build=True):
        """
        Adds a plugin of tool(s)
        tools is a list of tuples, where the pair is a tool name and version
          tools are for explicitly limiting which tools and versions
          (if version in tuple is '', then defaults to version)
        overrides is a list of tuples, where the pair is a tool name and a version
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
          repo=foo overrides=[('bar', ''), ('baz', '1c4e')], version='4fad'
            (get all tools from repo 'foo' at verion '4fad' on branch 'master'
            except 'bar' and for tool 'baz' get version '1c4e')
          repo=foo tools=[('bar', '1a2d')], overrides=[('baz', 'f2a1')]
            (not a particularly useful example, but get 'bar' from 'foo' at
            version '1a2d' and get 'baz' from 'foo' at version 'f2a1' on branch
            'master', ignore all other tools)
        """
        response = ('succeeded', None)
        org = None
        name = None
        if repo.endswith(".git"):
            repo = repo.split(".git")[0]
        org, name = repo.split("/")[-2:]
        path = self.path_dirs.plugins_dir + '/' + org + '/' + name
        response = self.path_dirs.ensure_dir(path)

        cwd = os.getcwd()
        os.chdir(path)
        status = subprocess.call(shlex.split("git clone " + repo + " ."))
        if status == 0:
            # get list of tools for repo
            if len(tools) == 0 and len(overrides) == 0:
                response = self.checkout(version, branch)
                if response[0] == 'succeeded':
                    matches = self.available_tools(path)
                    for match in matches:
                        if build:
                            pass
                        # !! TODO append to manifest
            elif len(tools) == 0:
                pass
            elif len(overrides) == 0:
                pass
            else: # both tools and overrides were specified
                pass
            lim_tools = []
            # tvb is a tuple of (tool, branch, version)
            for tvb in lim_tools:
                pass
            # TODO check tools, overrides, branch, and version
            # TODO create a manifest file of which tools are enabled/disabled at which versions, and are built or not.
        else:
            response = ('failed', status)
        os.chdir(cwd)
        return response

    @staticmethod
    def available_tools(path):
        """
        Return list of possible tools in repo for the given version and branch
        """
        matches = []
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, 'Dockerfile'):
                matches.append(root.split(path)[1])
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

    @staticmethod
    def checkout(version="HEAD", branch="master"):
        """ Checkout a specific version and branch of a repo """
        response = ('succeeded', None)
        status = subprocess.call(shlex.split("git checkout " + branch))
        if status == 0:
            status = subprocess.call(shlex.split("git pull"))
            if status == 0:
                status = subprocess.call(shlex.split("git reset --hard " + version))
                if status == 0:
                    response = ('succeeded', status)
                else:
                    response = ('failed', status)
            else:
                response = ('failed', status)
        else:
            response = ('failed', status)
        return response

    @staticmethod
    def build(match):
        """ Builds a specific tool """
        name = None
        return name

    @staticmethod
    def enable(tool, version="HEAD", branch="master"):
        """ Enable tool at a specific version, default to head """
        return

    @staticmethod
    def disable(tool, version="head", branch="master"):
        """ Disable tool at a specific version, default to head """
        return
