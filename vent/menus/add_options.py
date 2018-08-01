import npyscreen

from vent.api.menu_helpers import MenuHelper
from vent.menus.choose_tools import ChooseToolsForm


class AddOptionsForm(npyscreen.ActionForm):
    """ For specifying options when adding a repo """
    branch_cb = {}
    commit_tc = {}
    build_tc = {}
    branches = []
    commits = {}
    error = None

    def repo_values(self):
        """
        Set the appropriate repo dir and get the branches and commits of it
        """
        branches = []
        commits = {}
        m_helper = MenuHelper()
        status = m_helper.repo_branches(self.parentApp.repo_value['repo'])
        # branches and commits must both be retrieved successfully
        if status[0]:
            branches = status[1]
            status = m_helper.repo_commits(self.parentApp.repo_value['repo'])
            if status[0]:
                r_commits = status[1]
                for commit in r_commits:
                    commits[commit[0]] = commit[1]
            else:
                # if commits failed, return commit errors
                return status
        else:
            # if branch failed, return branch errors
            return status
        # if everything is good, return branches with commits
        return branches, commits

    def create(self):
        """ Update with current branches and commits """
        self.add_handlers({'^Q': self.quit})
        self.add(npyscreen.TitleText, name='Branches:', editable=False)

        if not self.branches or not self.commits:
            repo_vals = self.repo_values()
            i = 3
            # check if repo_values returned successfully
            if (isinstance(repo_vals[0], list) and
                    isinstance(repo_vals[1], dict)):
                self.branches, self.commits = repo_vals
                for branch in self.branches:
                    self.branch_cb[branch] = self.add(npyscreen.CheckBox,
                                                      name=branch, rely=i,
                                                      relx=5, max_width=25)
                    self.commit_tc[branch] = self.add(npyscreen.TitleCombo,
                                                      value=0, rely=i+1,
                                                      relx=10, max_width=30,
                                                      name='Commit:',
                                                      values=self.commits[branch])
                    self.build_tc[branch] = self.add(npyscreen.TitleCombo,
                                                     value=0, rely=i+1,
                                                     relx=45, max_width=25,
                                                     name='Build:',
                                                     values=[True, False])
                    i += 3
            else:
                self.error = self.add(npyscreen.MultiLineEdit,
                                      name='Errors',
                                      editable=False, labelColor='DANGER',
                                      rely=i, relx=5, color='DANGER', value="""
                Errors were found...
                """ + str(repo_vals[1]) + """

                Please confirm the repo url and credentials are valid!
                Vent will return to the main screen.
                """)
                self.error.display()

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm('MAIN')

    def on_ok(self):
        """
        Take the branch, commit, and build selection and add them as plugins
        """
        self.parentApp.repo_value['versions'] = {}
        self.parentApp.repo_value['build'] = {}
        for branch in self.branch_cb:
            if self.branch_cb[branch].value:
                # process checkboxes
                self.parentApp.repo_value['versions'][branch] = self.commit_tc[branch].values[self.commit_tc[branch].value]
                self.parentApp.repo_value['build'][branch] = self.build_tc[branch].values[self.build_tc[branch].value]
        if self.error:
            self.quit()
        self.parentApp.addForm('CHOOSETOOLS',
                               ChooseToolsForm,
                               name='Choose tools to add for new plugin'
                               '\t\t\t\t\t\t^Q to quit',
                               color='CONTROL')
        self.parentApp.change_form('CHOOSETOOLS')

    def on_cancel(self):
        self.quit()
