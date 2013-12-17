from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Process(OsisBaseObject):

    """
    unique process
    """

    def __init__(self, ddict={}, gid=0,aid=0,nid=0,name="",instance="",systempid=0, id=0):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.init("process","1.0")
            self.id = 0
            self.gid = gid
            self.nid = nid
            self.jpdomain= ""
            self.jpname= ""
            self.name = name
            self.instance = instance
            self.systempid = systempid  # system process id (PID) at this point
            self.guid = None
            # self.sguid = None
            self.epochstart = j.base.time.getTimeEpoch()
            self.epochstop = 0
            self.active = True
            self.lastcheck=0 #epoch of last time the info was checked from reality

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """

        C="%s_%s_%s_%s_%s_%s_%s"%(self.systempid,self.gid,self.nid,\
            self.jpdomain,self.jpname,self.instance,self.name)
        return j.tools.hash.md5_string(C)

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.id = int(self.id)
        # self.sguid=struct.pack("<HHL",self.gid,self.bid,self.id)
        self.guid = "%s_%s" % (self.gid, self.id)
        self.lastcheck=j.base.time.getTimeEpoch() 
        return self.guid

