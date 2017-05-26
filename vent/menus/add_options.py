import npyscreen

from vent.api.plugins import Plugin

class AddOptionsForm(npyscreen.ActionForm):
    """ For specifying options when adding a repo """
    branch_cb = {}
    commit_tc = {}
    build_tc = {}
    branches = []
    commits = {}
    error = False
    def repo_values(self):
        """ Set the appropriate repo dir and get the branches and commits of it """
        branches = []
        commits = {}
        plugin = Plugin()
        branches = plugin.repo_branches(self.parentApp.repo_value['repo'])
        c = plugin.repo_commits(self.parentApp.repo_value['repo'])
        # branches and commits must both be retrieved successfully
        if branches[0] and c[0]:
            for commit in c[1]:
                commits[commit[0]] = commit[1]
        else:
            commits = c[1]
            self.error = True
        return branches[1], commits

    def create(self):
        self.add_handlers({"^Q": self.quit})
        self.add(npyscreen.TitleText, name='Branches:', editable=False)

    def while_waiting(self):
        """ Update with current branches and commits """
        if not self.branches or not self.commits:
            self.branches, self.commits = self.repo_values()
            i = 3
            for branch in self.branches:
                self.branch_cb[branch] = self.add(npyscreen.CheckBox,
                                                    name=branch, rely=i,
                                                    relx=5, max_width=25)
                self.branch_cb[branch].display()
                self.commit_tc[branch] = self.add(npyscreen.TitleCombo, value=0, rely=i+1,
                                                  relx=10, max_width=30, name='Commit:',
                                                  values=self.commits[branch])
                self.commit_tc[branch].display()
                self.build_tc[branch] = self.add(npyscreen.TitleCombo, value=0, rely=i+1,
                                                 relx=45, max_width=25, name='Build:',
                                                 values=[True, False])
                self.build_tc[branch].display()
                i += 3
                # self.error_msg = self.add(npyscreen.MultiLineEdit, name="Errors", rely=3,
                # relx=5, max_width= 25, editable=False,
                #                           value="""
                #                           There was an error.
                #                           Please make sure you entered a valid repo url/credentials.
                #                           """)
                # self.branch_error = self.add(npyscreen.TitleText, name="Branch Errors: ", value=str(self.branches))
                # self.commits_error = self.add(npyscreen.TitleText, name="Commits Errors: ", value=str(self.commits))
                # self.error_msg.display()
                # self.branch_error.display()
                # self.commits_error.display()

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)

    def on_ok(self):
        """
        Take the branch, commit, and build selection and add them as plugins
        """
        self.parentApp.repo_value['versions'] = {}
        self.parentApp.repo_value['build'] = {}
        if not self.error:
            for branch in self.branch_cb:
                if self.branch_cb[branch].value:
                    # process checkboxes
                    self.parentApp.repo_value['versions'][branch] = self.commit_tc[branch].values[self.commit_tc[branch].value]
                    self.parentApp.repo_value['build'][branch] = self.build_tc[branch].values[self.build_tc[branch].value]
            self.parentApp.change_form("CHOOSETOOLS")
        else:
            self.quit()

    def on_cancel(self):
        self.quit()
