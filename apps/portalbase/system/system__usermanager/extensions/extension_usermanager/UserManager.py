
from JumpScale import j
import copy


class UserManager():

    def __init__(self):
        self.inited = False
        self.cache = {}
        self.cacheg = {}

    def _init(self):
        if self.inited == False:
            self.userModelDB = j.apps.system.usermanager.models.user
            self.groupModelDB = j.apps.system.usermanager.models.group
            self._rememberUserKeys()
            self.inited = True

    def reset(self):
        self._init()
        self.userModelDB.destroy()
        self.groupModelDB.destroy()

    def userGet(self, name, createNew=False, usecache=True):
        self._init()

        model = self.userModelDB

        def new(model, name):
            obj = model.new()
            obj.id = str(name)
            model.set(obj)
            return obj

        if name in self.cache and usecache:
            return self.cache[name]

        if model.exists(id=name):
            self.cache[name] = model.get(id=name)
            return self.cache[name]

        if createNew:
            self.cache[name] = new(model, name)
            print "NEW USER %s" % name
            return self.cache[name]

        return None

    def groupGet(self, name, createNew=False):
        self._init()

        model = self.groupModelDB

        def new(model, name):
            obj = model.new()
            obj.id = str(name)
            model.set(obj)
            return obj

        if name in self.cacheg:
            return self.cacheg[name]

        if model.exists(id=name):
            self.cacheg[name] = model.get(id=name)
            return self.cacheg[name]

        if createNew:
            self.cacheg[name] = new(model, name)
            print "NEW GROUP %s" % name
            return self.cacheg[name]

        return None

    def usercreate(self, name, passwd, groups, emails, userid=None):
        """
        creates user no matter what
        """
        self._init()
        model = self.userModelDB
        user = self.userGet(name, createNew=True)

        groups = [str(group) for group in groups]
        emails = [str(email) for email in emails]
        user.groups = groups
        user.emails = emails
        user.passwd = passwd
        model.set(user)
        # print user
        for group in groups:
            group = self.groupGet(group, createNew=True)

        return user.id

    def checkUserIsAdminFromCTX(self, ctx):
        user = ctx.env["beaker.session"].get('user')
        if not user:
            return False
        return "admin" in self.userGet(user).groups

    def getUserGroupsFromCTX(self, ctx):
        user = ctx.env["beaker.session"]["user"]
        return self.userGet(user).groups

    def getUserFromCTX(self, ctx):
        user = ctx.env["beaker.session"]["user"]
        return self.userGet(user)

    def _rememberUserKeys(self):
        model = self.userModelDB
        ids = model.list()
        for id in ids:
            try:
                obj = model.get(id=id)
            except:
                print "ERROR in usermanager extension, could not remember user because GUID %s does not exists" % guid
                print "can temporarly resolve by destroing the user mgmt db: do:  model.destroy(), this is a temp hack"  # @todo fix hack

            j.core.portal.runningPortal.webserver.userKeyToName[obj.secret] = obj.id
