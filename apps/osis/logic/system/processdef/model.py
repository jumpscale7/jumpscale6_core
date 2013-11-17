from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Process(OsisBaseObject):

    """
    unique processdef
    defines how a process needs to run in the cluster
    """

    def __init__(self, ddict={}):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.name = ""


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

