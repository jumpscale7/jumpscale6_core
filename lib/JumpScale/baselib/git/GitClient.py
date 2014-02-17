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
            self._clone()
        else:
            self.repo = git.Repo(self.gitBaseDir)

        if branchName != 'master':
            self.switchBranch(branchName)

    def _clone(self):
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