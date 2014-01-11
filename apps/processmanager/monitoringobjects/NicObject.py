from JumpScale import j

from _MonObjectBaseFactory import *

class NicObjectFactory(MonObjectBaseFactory):
    def __init__(self,host,classs):
        MonObjectBaseFactory.__init__(self,host,classs)
        self.osis=j.core.osis.getClientForCategory(self.host.daemon.osis,"system","nic")


class NicObject():

    def __init__(self,pid,nic_object=None,lastcheck=0):
        self._expire=5 #means after 5 sec the cache will create new one
        if nic_object<>None:
            self.nic_object=nic_object
            
    def getGuid(Self):
        return self.pid


    def __repr__(self):
        out=""
        for key,val in self.__dict__.iteritems():
            if key not in ["p"]:
                out+="%s:%s\n"%(key,val)
        return out

    __str__ = __repr__

