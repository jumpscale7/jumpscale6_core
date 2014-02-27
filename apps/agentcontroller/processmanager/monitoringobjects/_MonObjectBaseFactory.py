import time
from JumpScale import j

class MonObjectBaseFactory():
    def __init__(self,host,classs):
        """
        @param host is the host who is using this functionality and will host the factory
        """
        self.host=host
        self.classs=classs
        self.monitorobjects={} #key is id of monitor object

    def get(self,id=None,lastcheck=None):
        """
        """
        if self.monitorobjects.has_key(id):
            #we do this short term caching 5 sec to make sure if 10 people are polling from a ui we dont each time create a new object
            if (time.time()-self.monitorobjects[id]._expire)>self.monitorobjects[id].lastcheck:
                self.monitorobjects.pop(id)
            else:
                return self.monitorobjects[id]
        self.monitorobjects[id]=  self.classs(self)     

        if lastcheck<>None:
            self.monitorobjects[id].lastcheck=lastcheck

        return self.monitorobjects[id]

    def exists(self,id):
        """
        """
        if self.monitorobjects.has_key(id):
            return True
        else:
            return False


    def set(self,id,monobject,lastcheck=0):
        """
        """
        if lastcheck<>0:
            monobject.lastcheck=lastcheck
        else:
            monobject.lastcheck=time.time()
        self.monitorobjects[id]=monobject


class MonObjectBase(object):

    def __init__(self,cache):
        self.lastcheck=time.time()
        self._expire=60 #means after X sec the cache will create new one
        self.cache=cache
        self.db=self.cache.osis.new()
        self.db.gid=j.application.whoAmI.gid
        self.db.nid=j.application.whoAmI.nid
        self.ckeyOld=""

    def send2osis(self):
        result = self.cache.osis.set(self.db)
        self.db = self.cache.osis.get(result[0])
        return result

    def getGuid(self):
        return self.db.getSetGuid()

    def __repr__(self):
        return str(self.db)

    __str__ = __repr__
