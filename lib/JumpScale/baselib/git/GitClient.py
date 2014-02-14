from JumpScale import j
import git

class GitClient(object):

    def __init__(self, gitBaseDir, remoteUrl, branchName='master', cleanDir=False):
        self.gitBaseDir = gitBaseDir
        self.remoteUrl = remoteUrl
        self.branchName = branchName
        self.cleanDir = cleanDir

        if cleanDir:
            j.system.fs.removeDirTree(gitBaseDir)
            j.system.fs.createDir(gitBaseDir)
            self.clone()
        else:
            self.repo = git.Repo(self.gitBaseDir)

        if branchName != 'master':
            self.switchBranch(branchName)

    def clone(self):
        self.repo = git.Repo.clone_from(self.remoteUrl, self.gitBaseDir)

    def switchBranch(self, branchName):
        self.repo.git.checkout(branchName)

    def getModifiedFiles(self):
        return [diff.a_blob.name for diff in self.repo.index.diff(None)]

    def addFiles(self, files=[], message=''):
        if files:
            self.repo.index.add(files)
            self.repo.index.commit(message)

    def removeFiles(self, files=[], message=''):
        if files:
           self.repo.index.remove(files)
           self.repo.index.commit(message)

    def pull(self):
        self.repo.git.pull()

    def fetch(self):
        self.repo.git.fetch()

    def commit(self, message=''):
        modifiedfiles = self.getModifiedFiles()
        if modifiedfiles:
            self.repo.index.add(modifiedfiles)
            self.repo.index.commit(message)

    def push(self):
        self.repo.git.push('--all')
