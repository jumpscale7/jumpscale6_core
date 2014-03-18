from JumpScale import j
import git

from gittle import *

class GitClient(object):

    def __init__(self, gitBaseDir, remoteUrl, branchName='master', cleanDir=False,login="",passwd=""):
        self.gitBaseDir = gitBaseDir
        self.remoteUrl = remoteUrl
        self.branchName = branchName
        self.cleanDir = cleanDir
        self.login=login
        self.passwd=passwd

        if cleanDir or not j.system.fs.exists(self.gitBaseDir):
            if cleanDir:
                j.system.fs.removeDirTree(gitBaseDir)
                j.system.fs.createDir(gitBaseDir)
            self._clone()
        else:
            self.repo = git.Repo(self.gitBaseDir)
            # self.repo=Gittle.init(self.gitBaseDir)  
            # self.repo=Gittle(self.gitBaseDir, origin_uri=self.remoteUrl)          

        if branchName != 'master':
            self.switchBranch(branchName)

    def _clone(self):        
        self.repo=git.Repo.clone_from(self.remoteUrl, self.gitBaseDir)

        # auth = GittleAuth(username=self.login, password=self.passwd)  
        # self.repo = Gittle.init(self.gitBaseDir)
        
        # Gittle.clone(self.remoteUrl, self.gitBaseDir,auth=auth)  
        # self.repo = Gittle(self.gitBaseDir, origin_uri=self.remoteUrl)
        # repo.auth(username=self.login, password=self.passwd)
        # repo.pull()

    def switchBranch(self, branchName):
        self.repo.git.checkout(branchName)

    def getModifiedFiles(self):
        result={}
        result["D"]=[]
        result["N"]=[]
        result["M"]=[]
        result["R"]=[]
        for diff in self.repo.index.diff(None):
            path=diff.a_blob.path
            if diff.deleted_file:
                result["D"].append(path)
            elif diff.new_file:
                result["N"].append(path)
            elif diff.renamed:
                result["R"].append(path)
            result["M"].append(path)
        return result

    def addRemoveFiles(self):
        cmd='cd %s;git add -A :/'%self.gitBaseDir
        j.system.process.execute(cmd)
        # result=self.getModifiedFiles()
        # self.removeFiles(result["D"])
        # self.addFiles(result["N"])

    def addFiles(self, files=[]):
        if files<>[]:
            self.repo.index.add(files)

    def removeFiles(self, files=[]):
        if files<>[]:
            self.repo.index.remove(files)

    def pull(self):
        self.repo.git.pull()

    def fetch(self):
        self.repo.git.fetch()

    def commit(self, message='',addremove=True):
        if addremove:
            self.addRemoveFiles()
        self.repo.index.commit(message)

    def push(self,force=False):
        if force:
            self.repo.git.push('-f')
        else:
            self.repo.git.push('--all')

    def getUntrackedFiles(self):
        return self.repo.untracked_files

    def patchGitignore(self):
        gitignore = '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]

# C extensions
*.so

# Distribution / packaging
.Python
env/
bin/
build/
develop-eggs/
dist/
eggs/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
.tox/
.coverage
.cache
nosetests.xml
coverage.xml

# Translations
*.mo

# Mr Developer
.mr.developer.cfg
.project
.pydevproject

# Rope
.ropeproject

# Django stuff:
*.log
*.pot

# Sphinx documentation
docs/_build/'''
        ignorefilepath = j.system.fs.joinPaths(self.gitBaseDir, '.gitignore')
        if not j.system.fs.exists(ignorefilepath):
            j.system.fs.writeFile(ignorefilepath, gitignore)
        else:
            lines = gitignore.split('\n')
            inn = j.system.fs.fileGetContents(ignorefilepath)
            linesExisting = inn.split('\n')
            linesout = []
            for line in linesExisting:
                if line.strip():
                    linesout.append(line)
            for line in lines:
                if line not in linesExisting and line.strip():
                    linesout.append(line)
            out = '\n'.join(linesout)
            if out.strip() != inn.strip():
                j.system.fs.writeFile(ignorefilepath, out)