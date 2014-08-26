from JumpScale import j
import time
class PortalAuthenticatorOSIS():

    def __init__(self, osis):
        self.osis=j.core.osis.getClientForCategory(osis,"system","user")
        self.osisgroups=j.core.osis.getClientForCategory(osis,"system","group")
        self.key2user={}
        
    def existsKey(self,key):
        return self.key2user.has_key(key)
        
    def getUserFromKey(self,key):
        if not self.existsKey(key):
            return "guest"
        return self.key2user[key]

    def _getkey(self, username, osis):
        results = osis.simpleSearch({'id': username}, withguid=True)
        if results:
            return results[0]['guid']
        else:
            return "%s_%s" % (j.application.whoAmI.gid, username)

    def getUserInfo(self, user):
        return self.osis.get(self._getkey(user, self.osis))

    def getGroupInfo(self, groupname):
        return self.osisgroups.get(self._getkey(groupname, self.osisgroups))

    def userExists(self, user):
        return self.osis.exists(self._getkey(user, self.osis))

    def createUser(self, username, password, email, groups, domain):
        user = self.osis.new()
        user.id=username
        if isinstance(groups, basestring):
            groups = [groups]
        user.groups=groups
        user.emails=email
        user.domain=domain
        user.passwd=j.tools.hash.md5_string(password)
        self.osis.set(user)

    def listUsers(self):
        return self.osis.simpleSearch({})

    def listGroups(self):
        return self.osisgroups.simpleSearch({})

    def getGroups(self,user):
        try:
            userinfo = self.getUserInfo(user).__dict__
            return userinfo['groups']
        except:
            return ["guest","guests"]

    def loadFromLocalConfig(self):
        #@tddo load from users.cfg & populate in osis
        #see jsuser for example
        pass

    def authenticate(self,login,passwd):
        """
        """
        result=self.osis.authenticate(name=login,passwd=passwd)
        return result['authenticated']
