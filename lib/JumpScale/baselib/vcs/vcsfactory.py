from JumpScale import j

BASEURLS = {'github': 'github.com',
            'bitbucket': 'bitbucket.org'}

class VCSConfig(object):
    def __init__(self, provider, account):
        self._account = account
        self._provider = provider
        self._ini = j.config.getInifile(provider)

    def _getConfig(self, key, password=False):
        if not self._ini.checkParam(self._account, key):
            value = "@%s" % key
        else:
            value =  self._ini.getValue(self._account, key)
        if value == "@%s" % key:
            question = "Please provide %s for %s on %s" % (key, self._account, self._provider)
            if password:
                value = j.console.askPassword(question)
            else:
                value = j.console.askString(question)
            self._ini.addSection(self._account)
            self._ini.addParam(self._account, key, value)
        return value

    @property
    def login(self):
        return self._getConfig('login')

    @property
    def passwd(self):
        return self._getConfig('passwd', True)

class VCSFactory(object):
    def getClient(self, type, provider, account, reponame):
        userconfig = VCSConfig(provider, account)
        url = ""
        basepath = j.system.fs.joinPaths(j.dirs.codeDir, provider, account, reponame)

        user = userconfig.login
        passwd = userconfig.passwd
        baseurl = BASEURLS.get(provider, provider)
        if type in ["git"]:
            from JumpScale.baselib import git
            if user in ('git', 'ssh'): # This is ssh
                url = "git@%s:%s/%s.git" % (baseurl, account, reponame)
            else:
                url = "https://%s:%s@%s/%s/%s.git" % (user, passwd, baseurl, account, reponame)
            return VCSGITClient(j.clients.git.getClient(basepath, url, login=user, passwd=passwd))
        elif type in ['hg']:
            from JumpScale.baselib import mercurial
            if user in ('hg', 'ssh'):
                url = "ssh://hg@%s/%s/%s" % (baseurl, account, reponame)
            else:
                url = "https://%s:%s@%s/%s/%s" % (user, passwd, baseurl, account, reponame)
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

    def init(self):
        """
        Make sure repo exist clone if not existing
        """
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

    def init(self):
        self.client.init()

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


    def init(self):
        pass # mercurial repos are initialized at contruction time
