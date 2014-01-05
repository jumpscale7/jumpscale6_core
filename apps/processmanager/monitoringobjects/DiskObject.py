from JumpScale import j

from _MonObjectBaseFactory import *

class DiskObjectFactory(MonObjectBaseFactory):
    def __init__(self,host,classs):
        MonObjectBaseFactory.__init__(self,host,classs)
        self.osis=j.core.osis.getClientForCategory(self.host.daemon.osis,"system","disk")
        self.osisobjects={} #@todo P1 load them from ES at start (otherwise delete will not work), make sure they are proper osis objects


class DiskObject():

    def __init__(self,pid,disk_object=None,lastcheck=0):
        if disk_object<>None:
            self.disk_object=disk_object
            
    def getGuid(Self):
        return self.pid


    def __repr__(self):
        out=""
        for key,val in self.__dict__.iteritems():
            if key not in ["p"]:
                out+="%s:%s\n"%(key,val)
        return out

    __str__ = __repr__

