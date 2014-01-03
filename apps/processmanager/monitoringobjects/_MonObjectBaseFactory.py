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
            if (time.time()-4.99)>self.monitorobjects[id].lastcheck:
                self.monitorobjects.pop(id)
            else:
                return self.monitorobjects[id]
        self.monitorobjects[id]=  self.classs(id,monobject,lastcheck=lastcheck)     
        return self.monitorobjects[id]

    def set(self,monobject,lastcheck=0):
        """
        """
        if lastcheck<>0:
            monobject.lastcheck=lastcheck
        else:
            lastcheck=time.time()
        self.monitorobjects[monobject.getGuid()]=monobject
