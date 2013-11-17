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
            self.aid = aid  # application id is unique per grid
            self.nid = nid
            self.name = name
            self.instance = instance
            self.systempid = systempid  # system process id (PID) at this point
            self.guid = None
            # self.sguid = None
            self.epochstart = j.base.time.getTimeEpoch()
            self.epochstop = 0

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return self.getContentKey()

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.id = int(self.id)
        # self.sguid=struct.pack("<HHL",self.gid,self.bid,self.id)
        self.guid = "%s_%s" % (self.gid, self.id)
        return self.guid

