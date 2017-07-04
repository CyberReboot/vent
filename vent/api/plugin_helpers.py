import fnmatch
import shlex

from os import chdir, getcwd, walk
from os.path import join
from subprocess import check_output, STDOUT

from vent.api.templates import Template
from vent.helpers.logs import Logger
from vent.helpers.paths import PathDirs


class PluginHelper:
    """ Handle helper functions for the Plugin class """
    def __init__(self, **kargs):
        self.path_dirs = PathDirs(**kargs)
        self.manifest = join(self.path_dirs.meta_dir,
                             "plugin_manifest.cfg")
        self.logger = Logger(__name__)

    def get_path(self, repo):
        """ Return the path for the repo """
        if repo.endswith(".git"):
            repo = repo.split(".git")[0]
        org, name = repo.split("/")[-2:]
        if repo == 'https://github.com/cyberreboot/vent':
            path = join(self.path_dirs.base_dir, '.internals/plugins/')
        else:
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
