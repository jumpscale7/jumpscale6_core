from JumpScale import j

from _MonObjectBaseFactory import MonObjectBaseFactory, MonObjectBase

class StatObjectFactory(MonObjectBaseFactory):
    def __init__(self,host,classs):
        MonObjectBaseFactory.__init__(self,host,classs)
        self.osis=j.core.osis.getClientForCategory(self.host.daemon.osis,"system","stat")

class StatObject(MonObjectBase):
    pass
