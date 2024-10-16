class ReadmineController:
    def __init__(self, readmine):
        self.readmine = readmine

    def get_issues(self):
        return self.readmine.get_issues()

    def get_issue(self, issue_id):
        return self.readmine.get_issue(issue_id)

    def create_issue(self, issue):
        return self.readmine.create_issue(issue)

    def update_issue(self, issue_id, issue):
        return self.readmine.update_issue(issue_id, issue)

    def delete_issue(self, issue_id):
        return self.readmine.delete_issue(issue_id)
