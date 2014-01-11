import time
class MonObjectBaseFactory():
    def __init__(self,host,classs):
        """
        @param host is the host who is using this functionality and will host the factory
        """
        self.host=host
        self.classs=classs
        self.monitorobjects={} #key is id of monitor object

    def get(self,id,monobject=None,lastcheck=0):
        """
        """
        if self.monitorobjects.has_key(id):
            #we do this short term caching 5 sec to make sure if 10 people are polling from a ui we dont each time create a new object
            if (time.time()-self.monitorobjects[id]._expire)>self.monitorobjects[id].lastcheck:
                self.monitorobjects.pop(id)
            else:
                return self.monitorobjects[id]
        self.monitorobjects[id]=  self.classs(self,id,monobject,lastcheck=lastcheck)     
        return self.monitorobjects[id]

    def exists(self,id):
        """
        """
        if self.monitorobjects.has_key(id):
            return True
        else:
            return False


    def set(self,monobject,lastcheck=0):
        """
        """
        if lastcheck<>0:
            monobject.lastcheck=lastcheck
        else:
            monobject.lastcheck=time.time()
        self.monitorobjects[monobject.getGuid()]=monobject

class MonObjectBase():

    def __init__(self,cache,id,lastcheck=0):
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
