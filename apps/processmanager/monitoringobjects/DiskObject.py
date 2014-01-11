from JumpScale import j

from _MonObjectBaseFactory import *

class DiskObjectFactory(MonObjectBaseFactory):
    def __init__(self,host,classs):
        MonObjectBaseFactory.__init__(self,host,classs)
        self.osis=j.core.osis.getClientForCategory(self.host.daemon.osis,"system","disk")
        self.osisobjects={} #@todo P1 load them from ES at start (otherwise delete will not work), make sure they are proper osis objects


class DiskObject(MonObjectBase):

    def __init__(self,cache,pid,disk_object=None,lastcheck=0):
        self._expire=60 #means after X sec the cache will create new one
        sel.cache=cache
        self.db=cache.osis.new()
        if disk_object<>None:
            self.disk_object=disk_object
            
    def getGuid(Self):
        return self.db.guid


    def __repr__(self):
        return str(self.db)

    __str__ = __repr__

