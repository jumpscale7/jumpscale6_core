from JumpScale import j

BASEURLS = {'github': 'github.com',
            'bitbucket': 'bitbucket.org'}

class VCSFactory(object):
    def getClient(self, type, provider, account, reponame):
        # TODO searhc how @login and @password get replaced
        userinfo = j.config.getConfig(provider)
        url = ""
        basepath = j.system.fs.joinPaths(j.dirs.codeDir, provider, account, reponame)
        user = userinfo[account]['login']
        passwd = userinfo[account]['passwd']
        if type in ["git"]:
            from JumpScale.baselib import git
            if user == 'git': # This is ssh
                url = "%s@%s:%s/%s.git" % (user, BASEURLS[provider], account, reponame)
            else:
                url = "https://%s:%s@%s/%s/%s.git" % (user, passwd, BASEURLS[provider], account, reponame)
            return VCSGITClient(j.clients.git.getClient(basepath, url, login=user, passwd=passwd))
        elif type in ['hg']:
            from JumpScale.baselib import mercurial
            if user in ('hg', 'ssh'):
                url = "ssh://hg@%s/%s/%s" % (BASEURLS[provider], account, reponame)
            else:
                url = "https://%s:%s@%s/%s/%s" % (user, passwd, BASEURLS[provider], account, reponame)
            return VCSHGClient(j.clients.mercurial.getClient(basepath, url))

class VCSClient(object):
    def update(self):
        raise NotImplementedError()

    def clone(self):
        raise NotImplementedError()

    def checkout(self, revision):
        raise NotImplementedError()

    def push(self, force=False):
        raise NotImplementedError()

class VCSGITClient(VCSClient):
    def __init__(self, client):
        self.client = client
        self.baseDir = client.baseDir

    def clone(self):
        self.client._clone()

    def update(self):
        self.client.pull()

    def push(self, force=False):
        self.client.push(force)

class VCSHGClient(VCSClient):
    def __init__(self, client):
        self.client = client
        self.baseDir = client.basedir

    def clone(self):
        self.client._clone()

    def update(self):
        self.client.pullupdate()

    def push(self, force=False):
        self.client.push()
