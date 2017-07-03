from vent.api.plugin_helpers import PluginHelper
from vent.helpers.logs import Logger


class MenuHelper:
    """ Handle helper functions in the API for the Menu """
    def __init__(self, **kargs):
        self.p_helper = PluginHelper(**kargs)
        self.logger = Logger(__name__)

    def repo_tools(self, repo, branch, version):
        """ Get available tools for a repository branch at a version """
        self.logger.info("Starting: repo_tools")
        self.logger.info("repo given: " + str(repo))
        self.logger.info("branch given: " + str(branch))
        self.logger.info("version given: " + str(version))
        try:
            tools = []
            status = self.p_helper.apply_path(repo)
            # switch to directory where repo will be cloned to
            if status[0]:
                cwd = status[1]
            else:
                self.logger.info("apply_path failed. Exiting repo_tools with"
                                 " status: " + str(status))
                return status

            status = self.p_helper.checkout(branch=branch, version=version)
            if status[0]:
                path = self.p_helper.get_path(repo)
                tools = self.p_helper.available_tools(path, version=version)
            else:
                self.logger.info("checkout failed. Exiting repo_tools with"
                                 " status: " + str(status))
                return status
            try:
                chdir(cwd)
            except Exception as e:  # pragma: no cover
                self.logger.error("unable to change directory to: " +
                                  str(cwd) + " because: " + str(e))

            status = (True, tools)
        except Exception as e:  # pragma: no cover
            self.logger.error("repo_tools failed with error: " + str(e))
            status = (False, e)

        self.logger.info("Status of repo_tools: " + str(status))
        self.logger.info("Finished: repo_tools")
        return status
