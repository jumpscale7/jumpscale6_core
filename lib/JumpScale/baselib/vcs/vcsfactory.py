from JumpScale import j

BASEURLS = {'github': 'github.com',
            'bitbucket': 'bitbucket.org'}

class VCSFactory(object):
    def getClient(self, type, account, reponame):
        # TODO searhc how @login and @password get replaced
        userinfo = j.config.getConfig(type)
        url = ""
        basepath = j.system.fs.joinPaths(j.dirs.codeDir, type, account, reponame)
        if type in ["github"]:
            from JumpScale.baselib import git
            user = userinfo[account]['login']
            passwd = userinfo[account]['passwd']
            if user == 'git': # This is ssh
                url = "%s@%s:%s/%s.git" % (user, BASEURLS[type], account, reponame)
            else:
                url = "https://%s:%s@%s/%s/%s.git" % (user, passwd, BASEURLS[type], account, reponame)
            return VCSGITClient(j.clients.git.getClient(basepath, url, login=user, passwd=passwd))

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
